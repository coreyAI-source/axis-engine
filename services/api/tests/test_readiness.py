"""Readiness review report: deterministic facts, validated AI narrative, exports and permissions."""
import pytest

from app.services import report_ai
from tests.test_hospitality import command, create_audit, password_hash, people  # noqa: F401  (fixtures)


def requirement_id(audit, clause):
    return next(r["id"] for r in audit["bundle"]["requirements"] if r["source"].get("clause") == clause)


def evidence_id(audit, description):
    return next(e["id"] for e in audit["bundle"]["evidence"] if e["description"] == description)


async def assessed_audit(client, person):
    audit = await create_audit(client, person)
    audit = await command(client, person, audit, "evidence", {"kind": "interview", "description": "GM described sustainability goals verbally"})
    audit = await command(client, person, audit, "evidence", {"kind": "observation", "description": "Unmetered bore pump in plant room"})
    audit = await command(client, person, audit, "evidence", {"kind": "document", "description": "Twelve months of electricity bills"})
    interview, observation, bills = (evidence_id(audit, d) for d in (
        "GM described sustainability goals verbally", "Unmetered bore pump in plant room", "Twelve months of electricity bills"))
    for clause, status, evidence in (("A1", "major", [interview]), ("D2", "major", [observation]), ("D1", "minor", [bills]),
                                     ("C1", "conforming", [observation]), ("A5", "observation", [bills])):
        audit = await command(client, person, audit, "assess", {"requirementId": requirement_id(audit, clause), "status": status,
                                                                 "rationale": f"Fictional test rationale for {clause} with enough detail.", "evidenceIds": evidence})
    return audit


@pytest.mark.asyncio
async def test_readiness_facts_are_computed_from_the_audit(client, people):
    audit = await assessed_audit(client, people["admin"])
    response = await client.get(f"/hospitality/audits/{audit['id']}/readiness", headers=people["viewer"]["headers"])
    assert response.status_code == 200, response.text
    report = response.json()["report"]
    status = {c["code"]: c["status"] for c in report["coverage"]}
    assert len(report["coverage"]) == 40
    assert status["A1"] == "Not evidenced"  # major supported only by an interview
    assert status["D2"] == "Not met"
    assert status["D1"] == "Partly met"
    assert status["C1"] == "Met" and status["A5"] == "Met"
    assert list(status.values()).count("Not sampled") == 35
    totals = report["summary"]["totals"]
    assert (totals["Met"], totals["Partly met"], totals["Not met"], totals["Not evidenced"]) == (2, 1, 1, 1)
    assert report["summary"]["statement"].startswith("Of the 40 criteria reviewed, 3 need work")
    rows = {r["code"]: r for p in report["gaps"] for r in p["rows"]}
    assert rows["D2"]["priority"] == "Critical" and rows["D1"]["priority"] == "Important" and rows["A5"]["priority"] == "Improvement"
    assert [e["id"] for e in report["evidence_register"]] == ["I01", "D01"]
    assert report["observations"][0]["id"] == "O01" and report["observations"][0]["criteria"] == "C1, D2"
    assert report["draft"] is True and report["ai"] is None
    assert any("No AI narrative" in note for note in report["review_notes"])


@pytest.mark.asyncio
async def test_profile_and_generation_permissions(client, people, monkeypatch):
    audit = await assessed_audit(client, people["admin"])
    base = f"/hospitality/audits/{audit['id']}/readiness"
    denied = await client.put(f"{base}/profile", headers=people["viewer"]["headers"], json={"location": "Ubud"})
    assert denied.status_code == 403
    assert (await client.post(f"{base}/generate", headers=people["viewer"]["headers"])).status_code == 403
    assert (await client.get(base, headers=people["outsider"]["headers"])).status_code == 404
    assert (await client.put(f"{base}/profile", headers=people["admin"]["headers"], json={"unknown": "x"})).status_code == 422

    saved = await client.put(f"{base}/profile", headers=people["admin"]["headers"], json={
        "location": "Ubud, Gianyar, Bali", "hotel_contact_name": "Fictional GM", "review_date": "1 October 2026",
        "people_interviewed": "General Manager | Fictional GM | Management system\nChief Engineer", "reviewed_by": "Reviewer"})
    assert saved.status_code == 200, saved.text
    report = saved.json()["report"]
    assert ["Location", "Ubud, Gianyar, Bali"] in report["cover"]
    assert report["scope"]["people"] == [["General Manager", "Fictional GM", "Management system"], ["Chief Engineer", "", ""]]
    assert report["draft"] is False

    monkeypatch.setattr(report_ai.settings, "openrouter_api_key", "")
    missing = await client.post(f"{base}/generate", headers=people["admin"]["headers"])
    assert missing.status_code == 503 and "OPENROUTER_API_KEY" in missing.text


@pytest.mark.asyncio
async def test_ai_narrative_is_validated_and_drives_the_action_plan(client, people, monkeypatch):
    audit = await assessed_audit(client, people["admin"])
    base = f"/hospitality/audits/{audit['id']}/readiness"
    await client.put(f"{base}/profile", headers=people["admin"]["headers"], json={"reviewed_by": "Earlier reviewer"})
    captured = {}

    async def fake_draft(facts):
        captured.update(facts)
        return {
            "letter_summary": "Strong cultural practice; measurement is the main gap.",
            "pillars": {"A": {"headline": "No written system yet", "in_place": "Owner commitment.", "missing": "Documents."}},
            "strengths": [{"text": "Etiquette guidance observed (O01).", "evidence": "observed"}, {"text": "Bad label", "evidence": "guaranteed"}],
            "top_gaps": [{"criterion": "D2", "text": "Meter the bore."}, {"criterion": "Z9", "text": "Invented criterion"}],
            "criteria": {"D2": {"evidence_seen": "Bore unmetered", "gap": "A bore meter and monthly log"}, "Z9": {"gap": "invented"}},
            "actions": [{"criteria": ["D1"], "action": "Start a monthly energy log", "owner": "Chief Engineer", "evidence": "Log"},
                        {"criteria": ["D2", "Z9"], "action": "Install a bore meter", "owner": "Chief Engineer", "evidence": "Meter"},
                        {"criteria": ["Z9"], "action": "Dropped because no valid criterion"}],
        }, "test/model"

    monkeypatch.setattr(report_ai, "draft_narrative", fake_draft)
    response = await client.post(f"{base}/generate", headers=people["admin"]["headers"])
    assert response.status_code == 200, response.text
    report = response.json()["report"]
    assert captured["criteria"][0]["code"] == "A1" and "indicators" in next(c for c in captured["criteria"] if c["code"] == "D2")
    assert "indicators" not in next(c for c in captured["criteria"] if c["code"] == "C1")
    assert report["ai"]["model"] == "test/model" and report["ai"]["stale"] is False
    assert report["draft"] is True  # regeneration clears the earlier reviewer sign-off
    assert report["letter"]["paragraphs"][2].startswith("Strong cultural practice")
    assert report["summary"]["strengths"][1]["evidence"] == "unverified"
    assert [g["criterion"] for g in report["summary"]["top_gaps"]] == ["D2"]
    d2 = next(r for p in report["gaps"] for r in p["rows"] if r["code"] == "D2")
    assert d2["gap"] == "A bore meter and monthly log" and d2["evidence_seen"].startswith("O01")
    assert [(a["number"], a["criteria"]) for a in report["plan"]["phase1"]] == [(1, ["D2"])]
    assert [(a["number"], a["criteria"]) for a in report["plan"]["phase2"]] == [(2, ["D1"])]
    coverage = {c["code"]: c["actions"] for c in report["coverage"]}
    assert coverage["D2"] == "1" and coverage["D1"] == "2"
    assert any("A1" in note for note in report["review_notes"])  # A1 has no action yet

    audit = await command(client, people["admin"], audit, "evidence", {"kind": "observation", "description": "Later observation after drafting"})
    later = (await client.get(base, headers=people["admin"]["headers"])).json()["report"]
    assert later["ai"]["stale"] is True

    docx = await client.get(f"{base}/export?format=docx", headers=people["viewer"]["headers"])
    assert docx.status_code == 200 and docx.content[:2] == b"PK"
    markdown = await client.get(f"{base}/export?format=markdown", headers=people["admin"]["headers"])
    assert markdown.status_code == 200
    for heading in ("## 2. Summary of results", "## 7. Certification action plan", "## Appendix C: Criterion coverage register", "DRAFT"):
        assert heading in markdown.text
    assert (await client.get(f"{base}/export?format=pdf", headers=people["admin"]["headers"])).status_code == 422
