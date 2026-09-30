"""Hotel pilot integration tests: real JWT auth + Node rules, SQLite only.

The shared client fixture replaces get_db with an in-memory SQLite session.
ASGITransport does not invoke the application lifespan or the configured Neon DB.
No engine/auth dependency is mocked, so these exercise the API/engine boundary.
"""
import hashlib
import uuid

import pytest
import pytest_asyncio
from sqlalchemy import func, select

from app.models.hospitality import HospitalityAudit, HospitalityFile
from app.models.org import Organisation, User
from app.utils.security import create_access_token, hash_password


PASSWORD = "Fictional-Pilot-Only-456!"
FILE_CONTENT = b"FICTIONAL PILOT EVIDENCE\nWater readings checked on 29 September.\n"


@pytest.fixture(scope="module")
def password_hash():
    return hash_password(PASSWORD)


@pytest_asyncio.fixture
async def people(db_session, password_hash):
    organisation = Organisation(name="Fictional hotel organisation A")
    outside = Organisation(name="Fictional hotel organisation B")
    db_session.add_all([organisation, outside])
    await db_session.flush()
    result = {}
    for name, role, org in [
        ("admin", "admin", organisation),
        ("verifier", "auditor", organisation),
        ("owner", "process_owner", organisation),
        ("other_owner", "process_owner", organisation),
        ("viewer", "viewer", organisation),
        ("outsider", "admin", outside),
    ]:
        user = User(organisation_id=org.id, first_name=name, last_name="Pilot",
                    email=f"{name}@pilot.example.com", role_code=role,
                    hashed_password=password_hash, active_flag=True)
        db_session.add(user)
        await db_session.flush()
        result[name] = {
            "id": str(user.id), "organisation_id": str(org.id), "email": user.email,
            "headers": {"Authorization": "Bearer " + create_access_token({"sub": str(user.id), "email": user.email})},
        }
    await db_session.commit()
    return result


async def create_audit(client, person):
    response = await client.post("/hospitality/audits", headers=person["headers"], json={
        "title": "Fictional Bali hotel pilot", "site_name": "Fictional Pilot Hotel",
        "scope_statement": "Software pilot with original fictional criteria only.",
    })
    assert response.status_code == 201, response.text
    return response.json()


async def command(client, person, audit, operation, data=None, *, expected=200, version=None):
    response = await client.post(f"/hospitality/audits/{audit['id']}/commands", headers=person["headers"], json={
        "expected_version": audit["version"] if version is None else version,
        "operation": operation, "input": data or {},
    })
    assert response.status_code == expected, response.text
    return response.json()


async def add_evidence(client, person, audit):
    return await command(client, person, audit, "evidence", {
        "kind": "record", "description": "Fictional meter and inspection records", "reference": "DEMO-RECORD-01",
    })


async def upload(client, person, audit, *, expected=201, version=None, content=FILE_CONTENT, mime="text/plain"):
    response = await client.post(f"/hospitality/audits/{audit['id']}/files", headers=person["headers"],
                                 data={"expected_version": audit["version"] if version is None else version, "description": "Fictional implementation evidence"},
                                 files={"file": ("pilot-evidence.txt", content, mime)})
    assert response.status_code == expected, response.text
    return response.json()


def violation_codes(body):
    return [item["code"] for item in body["detail"]]


@pytest.mark.asyncio
async def test_pilot_persists_and_reloads_through_real_engine(client, db_session, people):
    audit = await create_audit(client, people["admin"])
    assert audit["version"] == 1
    assert audit["status"] == "in_progress"
    assert len(audit["bundle"]["requirements"]) == 40
    assert all(a["status"] == "unassessed" for a in audit["bundle"]["assessments"])
    assert audit["bundle"]["audit"]["leadAuditor"]["userId"] == people["admin"]["id"]
    assert audit["bundle"]["template"]["id"] == "gstc-hotel-v4"
    assert audit["bundle"]["template"]["fictional"] is False
    assert "STANDARD_TEMPLATE" in [warning["code"] for warning in audit["warnings"]]
    assert audit["report"]["draft"] is True

    audit = await add_evidence(client, people["admin"], audit)
    await db_session.commit()
    db_session.expunge_all()
    response = await client.get(f"/hospitality/audits/{audit['id']}", headers=people["admin"]["headers"])
    assert response.status_code == 200, response.text
    reloaded = response.json()
    assert reloaded["bundle"] == audit["bundle"]
    assert reloaded["version"] == 2
    stored = await db_session.get(HospitalityAudit, uuid.UUID(audit["id"]))
    assert str(stored.organisation_id) == people["admin"]["organisation_id"]
    assert stored.bundle["evidence"][0]["reference"] == "DEMO-RECORD-01"
    listing = await client.get("/hospitality/audits", headers=people["admin"]["headers"])
    assert [item["id"] for item in listing.json()] == [audit["id"]]


@pytest.mark.asyncio
async def test_assessment_rejects_missing_and_cross_audit_evidence_without_mutation(client, people):
    audit = await create_audit(client, people["admin"])
    requirement_id = audit["bundle"]["requirements"][0]["id"]
    invalid = await command(client, people["admin"], audit, "assess", {
        "requirementId": requirement_id, "status": "conforming", "rationale": "Reviewed records and interviewed staff.", "evidenceIds": [],
    }, expected=422)
    assert "EVIDENCE_REQUIRED" in violation_codes(invalid)
    other = await add_evidence(client, people["admin"], await create_audit(client, people["admin"]))
    invalid = await command(client, people["admin"], audit, "assess", {
        "requirementId": requirement_id, "status": "conforming", "rationale": "Reviewed records and interviewed staff.",
        "evidenceIds": [other["bundle"]["evidence"][0]["id"]],
    }, expected=422)
    assert "EVIDENCE_NOT_FOUND" in violation_codes(invalid)
    invalid = await command(client, people["admin"], audit, "assess", {
        "requirementId": requirement_id, "status": "not_applicable", "rationale": "N/A", "evidenceIds": [],
    }, expected=422)
    assert "RATIONALE_REQUIRED" in violation_codes(invalid)
    response = await client.get(f"/hospitality/audits/{audit['id']}", headers=people["admin"]["headers"])
    assert response.json()["version"] == audit["version"]
    assert response.json()["bundle"] == audit["bundle"]


@pytest.mark.asyncio
async def test_complete_hotel_workflow_uses_independent_accounts_and_retains_major_result(client, db_session, people):
    # Verify actual login as well as token validation for distinct real database users.
    for key in ("admin", "owner", "verifier"):
        response = await client.post("/auth/login", data={"username": people[key]["email"], "password": PASSWORD})
        assert response.status_code == 200, response.text
        people[key]["headers"] = {"Authorization": "Bearer " + response.json()["access_token"]}

    audit = await add_evidence(client, people["admin"], await create_audit(client, people["admin"]))
    evidence_id = audit["bundle"]["evidence"][0]["id"]
    for index, requirement in enumerate(audit["bundle"]["requirements"]):
        audit = await command(client, people["admin"], audit, "assess", {
            "requirementId": requirement["id"], "status": "major" if index == 7 else "conforming",
            "rationale": "Maintenance records have a serious gap." if index == 7 else "Records and staff interview support this result.",
            "evidenceIds": [evidence_id],
        })
    finding = audit["bundle"]["findings"][0]
    audit = await command(client, people["admin"], audit, "status", {"status": "reporting"})
    invalid = await command(client, people["admin"], audit, "complete", expected=422)
    assert "FINDING_WITHOUT_ACTION" in violation_codes(invalid)
    audit = await command(client, people["admin"], audit, "action.create", {
        "findingId": finding["id"], "description": "Repair controls and document the maintenance programme.", "ownerUserId": people["owner"]["id"],
    })
    action_id = audit["bundle"]["actions"][0]["id"]
    assert audit["bundle"]["actions"][0]["owner"]["authenticated"] is True
    invalid = await command(client, people["admin"], audit, "finding.close", {"findingId": finding["id"]}, expected=422)
    assert "ACTIONS_OPEN" in violation_codes(invalid)
    audit = await command(client, people["owner"], audit, "action.progress", {"actionId": action_id, "note": "Repairs started."})

    # Issued report can retain monitored open actions; implementation continues afterward.
    audit = await command(client, people["admin"], audit, "complete")
    assert audit["status"] == "complete"
    assert "ACTIONS_OPEN" in [warning["code"] for warning in audit["warnings"]]
    audit = await upload(client, people["owner"], audit)
    proof_id = audit["bundle"]["evidence"][-1]["id"]
    # Admin submits on behalf of the owner, so both owner and submitter must be excluded as verifier.
    audit = await command(client, people["admin"], audit, "action.submit", {
        "actionId": action_id, "note": "The controls were repaired and maintenance records supplied.", "evidenceIds": [proof_id],
    })
    invalid = await command(client, people["admin"], audit, "action.verify", {
        "actionId": action_id, "outcome": "effective", "note": "I checked the maintenance records and operation.",
    }, expected=422)
    assert "VERIFIER_NOT_INDEPENDENT" in violation_codes(invalid)
    audit = await command(client, people["verifier"], audit, "action.verify", {
        "actionId": action_id, "outcome": "effective", "note": "Independently inspected the controls and a completed maintenance cycle.",
    })
    audit = await command(client, people["verifier"], audit, "finding.close", {"findingId": finding["id"]})
    assert audit["bundle"]["findings"][0]["status"] == "closed"
    assert audit["bundle"]["actions"][0]["verifications"][-1]["separation"] == "enforced"
    assert audit["report"]["hospitality"]["favourable"] is False

    invalid = await command(client, people["admin"], audit, "assess", {
        "requirementId": finding["requirementId"], "status": "conforming", "rationale": "Attempting to rewrite an issued result.", "evidenceIds": [evidence_id],
    }, expected=422)
    assert "AUDIT_COMPLETE" in violation_codes(invalid)
    await db_session.commit()
    db_session.expunge_all()
    report = await client.get(f"/hospitality/audits/{audit['id']}/report", headers=people["viewer"]["headers"])
    assert report.status_code == 200
    assert report.json()["draft"] is False
    assert report.json()["counts"]["major"] == 1
    assert report.json()["hospitality"]["favourable"] is False
    markdown = await client.get(f"/hospitality/audits/{audit['id']}/report?format=markdown", headers=people["admin"]["headers"])
    assert markdown.status_code == 200
    assert "attachment" in markdown.headers["content-disposition"]
    assert "GSTC Hotel Standard v4.0 (December 30, 2025)" in markdown.text
    assert "Provisional internal scoring method" in markdown.text
    assert "Independent" in audit["bundle"]["actions"][0]["verifications"][-1]["note"]


@pytest.mark.asyncio
async def test_upload_is_atomic_traceable_authenticated_and_rejects_mismatched_types(client, db_session, people):
    audit = await create_audit(client, people["admin"])
    await upload(client, people["admin"], audit, expected=415, content=b"not a real PDF", mime="application/pdf")
    await upload(client, people["admin"], audit, expected=422, content=b"")
    assert await db_session.scalar(select(func.count()).select_from(HospitalityFile)) == 0
    audit = await upload(client, people["admin"], audit)
    evidence = audit["bundle"]["evidence"][-1]
    assert evidence["attachment"]["sha256"] == hashlib.sha256(FILE_CONTENT).hexdigest()
    assert evidence["attachment"]["sizeBytes"] == len(FILE_CONTENT)
    await db_session.commit()
    db_session.expunge_all()
    url = f"/hospitality/audits/{audit['id']}/files/{evidence['id']}"
    unauthenticated = await client.get(url)
    assert unauthenticated.status_code == 401
    downloaded = await client.get(url, headers=people["viewer"]["headers"])
    assert downloaded.status_code == 200
    assert downloaded.content == FILE_CONTENT
    assert downloaded.headers["x-content-type-options"] == "nosniff"
    assert downloaded.headers["cache-control"] == "private, no-store"
    assert "attachment" in downloaded.headers["content-disposition"]


@pytest.mark.asyncio
async def test_tenant_isolation_for_audits_commands_files_reports_members_and_users(client, people):
    audit = await upload(client, people["admin"], await create_audit(client, people["admin"]))
    other = await create_audit(client, people["outsider"])
    outsider_headers = people["outsider"]["headers"]
    listing = await client.get("/hospitality/audits", headers=outsider_headers)
    assert [item["id"] for item in listing.json()] == [other["id"]]
    for suffix in ("", "/report", "/report?format=markdown", f"/files/{audit['bundle']['evidence'][0]['id']}"):
        response = await client.get(f"/hospitality/audits/{audit['id']}{suffix}", headers=outsider_headers)
        assert response.status_code == 404, response.text
    await command(client, people["outsider"], audit, "evidence", {"kind": "record", "description": "Foreign record"}, expected=404)
    await upload(client, people["outsider"], audit, expected=404)
    members = await client.get("/hospitality/members", headers=outsider_headers)
    assert [member["id"] for member in members.json()] == [people["outsider"]["id"]]
    users = await client.get("/users/", headers=outsider_headers)
    assert [user["id"] for user in users.json()] == [people["outsider"]["id"]]
    for method, payload in (("GET", None), ("PATCH", {"role_code": "admin"}), ("DELETE", None)):
        response = await client.request(method, f"/users/{people['admin']['id']}", headers=outsider_headers, json=payload)
        assert response.status_code == 404, response.text
    response = await client.post("/hospitality/members", headers=outsider_headers, json={
        "first_name": "Foreign", "last_name": "Member", "email": "foreign@pilot.example.com", "password": PASSWORD,
        "role_code": "admin", "organisation_id": people["admin"]["organisation_id"],
    })
    assert response.status_code == 422, response.text
    # Assignment must also reject a valid account ID from another organisation.
    audit = await command(client, people["admin"], audit, "assess", {
        "requirementId": audit["bundle"]["requirements"][0]["id"], "status": "minor", "rationale": "A fictional management gap was found.",
        "evidenceIds": [audit["bundle"]["evidence"][0]["id"]],
    })
    await command(client, people["admin"], audit, "action.create", {
        "findingId": audit["bundle"]["findings"][0]["id"], "description": "Resolve management gap.", "ownerUserId": people["outsider"]["id"],
    }, expected=422)


@pytest.mark.asyncio
async def test_viewer_and_process_owner_permissions_cannot_bypass_engine_identity(client, people):
    audit = await add_evidence(client, people["admin"], await create_audit(client, people["admin"]))
    viewer = people["viewer"]
    response = await client.post("/hospitality/audits", headers=viewer["headers"], json={"title": "Denied", "site_name": "Denied"})
    assert response.status_code == 403
    await command(client, viewer, audit, "evidence", {"kind": "record", "description": "Denied"}, expected=403)
    await command(client, viewer, audit, "status", {"status": "reporting"}, expected=403)
    await upload(client, viewer, audit, expected=403)
    audit = await command(client, people["admin"], audit, "assess", {
        "requirementId": audit["bundle"]["requirements"][0]["id"], "status": "minor", "rationale": "A management record is incomplete.",
        "evidenceIds": [audit["bundle"]["evidence"][0]["id"]],
    })
    audit = await command(client, people["admin"], audit, "action.create", {
        "findingId": audit["bundle"]["findings"][0]["id"], "description": "Complete the management record.", "ownerUserId": people["owner"]["id"],
    })
    action_id = audit["bundle"]["actions"][0]["id"]
    await command(client, people["other_owner"], audit, "action.progress", {"actionId": action_id, "note": "I do not own this."}, expected=403)
    await command(client, people["other_owner"], audit, "action.submit", {"actionId": action_id, "note": "I do not own this.", "evidenceIds": [audit["bundle"]["evidence"][0]["id"]]}, expected=403)
    await command(client, people["owner"], audit, "status", {"status": "reporting"}, expected=403)
    await command(client, people["owner"], audit, "action.verify", {"actionId": action_id, "outcome": "effective", "note": "Attempting to verify my own action."}, expected=403)
    audit = await command(client, people["owner"], audit, "action.progress", {"actionId": action_id, "note": "Record update started."})
    audit = await command(client, people["owner"], audit, "action.submit", {"actionId": action_id, "note": "Record completed and checked.", "evidenceIds": [audit["bundle"]["evidence"][0]["id"]]})
    assert audit["bundle"]["actions"][0]["implementation"]["submittedBy"]["userId"] == people["owner"]["id"]


@pytest.mark.asyncio
async def test_spoofed_actor_config_bundle_attachment_and_owner_are_rejected(client, people):
    audit = await create_audit(client, people["admin"])
    headers = people["admin"]["headers"]
    for extra in ({"actor": {"userId": people["verifier"]["id"]}}, {"config": {"minRationaleLength": 0}}, {"bundle": {}}):
        response = await client.post(f"/hospitality/audits/{audit['id']}/commands", headers=headers, json={
            "expected_version": audit["version"], "operation": "evidence", "input": {"kind": "record", "description": "Spoof test"}, **extra,
        })
        assert response.status_code == 422, response.text
        response = await client.post("/hospitality/audits", headers=headers, json={"title": "Spoof test", "site_name": "Spoof test", **extra})
        assert response.status_code == 422, response.text
    for extra in ({"actor": {"userId": people["verifier"]["id"]}}, {"config": {"minRationaleLength": 0}}, {"attachment": {"key": "another-tenant/file"}}):
        await command(client, people["admin"], audit, "evidence", {"kind": "record", "description": "Spoof test", **extra}, expected=422)
    await command(client, people["admin"], audit, "action.create", {
        "findingId": str(uuid.uuid4()), "description": "Fake owner", "ownerUserId": people["owner"]["id"],
        "owner": {"name": "Forged", "userId": people["verifier"]["id"], "authenticated": True},
    }, expected=422)
    reloaded = await client.get(f"/hospitality/audits/{audit['id']}", headers=headers)
    assert reloaded.json()["version"] == 1
    assert reloaded.json()["bundle"] == audit["bundle"]


@pytest.mark.asyncio
async def test_stale_save_and_upload_return_409_without_overwriting_newer_state(client, db_session, people):
    first_session = await create_audit(client, people["admin"])
    response = await client.get(f"/hospitality/audits/{first_session['id']}", headers=people["verifier"]["headers"])
    second_session = response.json()
    saved = await add_evidence(client, people["admin"], first_session)
    await command(client, people["verifier"], second_session, "evidence", {"kind": "record", "description": "Stale write must not win."}, expected=409)
    await upload(client, people["verifier"], second_session, expected=409)
    assert await db_session.scalar(select(func.count()).select_from(HospitalityFile)) == 0
    await db_session.commit()
    db_session.expunge_all()
    response = await client.get(f"/hospitality/audits/{saved['id']}", headers=people["verifier"]["headers"])
    reloaded = response.json()
    assert reloaded["version"] == saved["version"]
    assert reloaded["bundle"] == saved["bundle"]
    assert len(reloaded["bundle"]["evidence"]) == 1


@pytest.mark.asyncio
async def test_custom_criteria_require_authorised_review_before_scope(client, people):
    audit = await create_audit(client, people["admin"])
    audit = await command(client, people["verifier"], audit, "requirement.create", {
        "text": "An original internal pilot review record is maintained.", "category": "Management", "auditPrompt": "Show the review record.",
        "source": {"documentId": "internal-pilot-policy", "documentTitle": "Internal fictional pilot policy", "revision": "1", "section": "1"},
    })
    requirement_id = audit["bundle"]["requirements"][-1]["id"]
    assert len(audit["bundle"]["audit"]["requirementIds"]) == 40
    await command(client, people["verifier"], audit, "requirement.review", {"requirementId": requirement_id, "decision": "approved", "note": "Auditor is not a lead reviewer."}, expected=403)
    audit = await command(client, people["admin"], audit, "requirement.review", {"requirementId": requirement_id, "decision": "approved", "note": "Approved as original internal pilot policy."})
    assert len(audit["bundle"]["audit"]["requirementIds"]) == 41
    assert audit["bundle"]["requirements"][-1]["reviewedBy"]["userId"] == people["admin"]["id"]
    audit = await command(client, people["admin"], audit, "assess", {"requirementId": requirement_id, "status": "not_applicable", "rationale": "This fictional activity is outside the hotel pilot scope.", "evidenceIds": []})
    assert audit["bundle"]["assessments"][-1]["status"] == "not_applicable"


@pytest.mark.asyncio
async def test_user_registration_and_role_changes_cannot_escalate_viewer_or_cross_tenants(client, db_session, people):
    payload = {"organisation_id": people["admin"]["organisation_id"], "first_name": "Intruder", "last_name": "Pilot",
               "email": "intruder@pilot.example.com", "password": PASSWORD, "role_code": "admin"}
    response = await client.post("/auth/register", json=payload)
    assert response.status_code == 401, response.text
    response = await client.post("/auth/register", headers=people["viewer"]["headers"], json=payload)
    assert response.status_code == 403, response.text
    response = await client.post("/users/", headers=people["viewer"]["headers"], json=payload)
    assert response.status_code == 403, response.text
    response = await client.patch(f"/users/{people['viewer']['id']}", headers=people["viewer"]["headers"], json={"role_code": "admin"})
    assert response.status_code == 403, response.text
    response = await client.post("/hospitality/members", headers=people["viewer"]["headers"], json={key: value for key, value in payload.items() if key != "organisation_id"})
    assert response.status_code == 403, response.text
    response = await client.post("/auth/register", headers=people["outsider"]["headers"], json=payload)
    assert response.status_code == 403, response.text
    assert await db_session.scalar(select(func.count()).select_from(User)) == 6
    me = await client.get("/hospitality/me", headers=people["viewer"]["headers"])
    assert me.json()["role_code"] == "viewer"
    # Administrator can create a separate verification account in their own organisation.
    member_payload = {key: value for key, value in payload.items() if key != "organisation_id"}
    member_payload.update(email="new-verifier@pilot.example.com", role_code="auditor")
    response = await client.post("/hospitality/members", headers=people["admin"]["headers"], json=member_payload)
    assert response.status_code == 201, response.text
    assert response.json()["organisation_id"] == people["admin"]["organisation_id"]
    assert "password" not in response.json()
    assert "hashed_password" not in response.json()
    response = await client.post("/auth/login", data={"username": member_payload["email"], "password": PASSWORD})
    assert response.status_code == 200, response.text
