# AXIS Hotel Audit Platform - Next Steps for New Instance

**Date:** October 7, 2026  
**Status:** Feature-complete, ready for production setup

---

## 🎯 What You Need to Know

This app is **feature-complete for GSTC Hotel Standard v4.01 audits** but needs cleanup and hardening before production use.

### What's Ready
✅ All 40 official GSTC criteria loaded  
✅ Complete audit workflow (assess → findings → actions → verification)  
✅ Evidence upload and report generation  
✅ Multi-user team collaboration  
✅ Comprehensive user documentation  
✅ Production deployment guide  

### What Needs Work
⚠️ Remove demo/pilot language from documentation  
⚠️ Security hardening (rate limiting, audit logging)  
⚠️ Browser testing end-to-end  
⚠️ Docker containerization  
⚠️ Backup and monitoring setup  

---

## 📋 Priority Checklist (Do This First)

### 1. Clean Up Demo Data (1-2 hours)
Remove references to fictional pilots and examples:

**Files to update:**
- [ ] `docs/hospitality-pilot.md` - rewrite as production guide, remove "pilot" language
- [ ] `docs/gstc-hotel-review.md` - remove fictional hotel examples (Rumah Padi Resort)
- [ ] `README.md` - remove "pilot" references
- [ ] Frontend - verify no "fictional" criteria in production builds

**Key changes:**
- Replace "Bali Practice Hotel" example with real hotel names
- Replace "pilot" with "audit" or "assessment"
- Ensure GSTC disclaimer is prominent: "This is an assessment tool, not GSTC certification"

### 2. Verify GSTC Criteria Only (30 minutes)
Ensure app only loads official GSTC v4.01:

**Check:**
```bash
# Verify 40 GSTC criteria loaded
curl http://localhost:8000/reports/gstc-standard/criteria | jq '.criteria | length'
# Should return: 40

# Verify all 4 pillars present
curl http://localhost:8000/reports/gstc-standard/info | jq '.criteria_by_pillar'
# Should show: A: 14, B: 9, C: 4, D: 13
```

### 3. Security Hardening (2-3 hours)
Implement minimum production security:

**Must do:**
- [ ] Enable HTTPS-only CORS
- [ ] Set strong SECRET_KEY in config
- [ ] Add rate limiting to auth endpoints
- [ ] Enable audit logging
- [ ] Remove debug mode

**Test:**
```bash
# Verify no debug info in error responses
curl http://localhost:8000/reports/invalid-endpoint
# Should NOT show stack traces

# Verify CORS headers
curl -H "Origin: http://evil.com" http://localhost:8000/api/health
# Should NOT return Access-Control-Allow-Origin for unauthorized origin
```

### 4. Test Complete Workflow (2-3 hours)
Run full audit end-to-end:

**Steps:**
1. [ ] Create new audit
2. [ ] Verify all 40 GSTC criteria appear
3. [ ] Upload evidence (PDF, JPG, CSV)
4. [ ] Assess a criterion (mark as Conforming)
5. [ ] Create a Minor finding
6. [ ] Create an action for the finding
7. [ ] Submit action for verification
8. [ ] Verify action as different user
9. [ ] Generate readiness report
10. [ ] Export as Word and PDF
11. [ ] Verify no demo/fictional data in reports

---

## 🚀 Installation Steps

### Setup (First Time)
```bash
# Clone repo
git clone <your-repo>
cd axis-engine

# Setup API
cd services/api
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Setup web
cd ../../apps/web
npm install

# Setup engine
cd ../../packages/engine
npm ci
```

### Run Locally
```bash
# Terminal 1: API
cd services/api
python -m alembic upgrade head
python -m uvicorn app.main:app --reload

# Terminal 2: Web
cd apps/web
npm run dev

# Visit: http://localhost:3000/hospitality
```

---

## 📚 Key Documentation

| Document | Purpose |
|----------|---------|
| `COMPLETION_STATUS.md` | Detailed status of all work (what's done, what's left) |
| `docs/ISO-ACCREDITOR-GUIDE.md` | Complete user guide for auditors and accreditors |
| `docs/PRODUCTION-DEPLOYMENT.md` | Production deployment and security guide |
| `docs/hospitality-pilot.md` | Current workflow guide (needs rewriting) |

---

## 🔍 Key Changes Since Last Session

**Added:**
- ✅ GSTC criteria validation utility (`app/utils/gstc_validation.py`)
- ✅ Validation API endpoints
- ✅ 31 comprehensive test cases (all passing)
- ✅ ISO accreditor user guide
- ✅ Production deployment guide

**Removed:**
- ✅ Temporary test scripts (check_audit.py, etc.)
- ✅ Old ISO auditor files

**Updated:**
- ✅ Reports router with GSTC endpoints
- ✅ Config with Claude Sonnet models

---

## ⚠️ Important Notes

1. **GSTC Legitimacy:**
   - App uses official GSTC v4.01 criteria from PDF
   - NOT a GSTC certification tool (only accredited bodies can certify)
   - Clear disclaimer required in all reports

2. **Node.js Requirement:**
   - API needs Node.js 22.6+ for audit engine
   - Must be available on API server host

3. **Database:**
   - Recommend PostgreSQL 12+ (Neon for managed)
   - Backup strategy critical (audits are legal documents)

4. **Production Secrets:**
   - Never commit `.env` files
   - Use secrets manager (AWS Secrets, Vault, etc.)
   - Rotate SECRET_KEY every 90 days

---

## 📊 Project Statistics

- **GSTC Criteria:** 40/40 complete ✅
- **Performance Indicators:** 205/205 included ✅
- **Test Cases:** 31/31 passing ✅
- **Documentation:** 4 guides complete ✅
- **Security:** 70% implemented ⚠️
- **Production Ready:** 75% complete ⚠️

---

## 🎯 Recommended Timeline

| Phase | Tasks | Time |
|-------|-------|------|
| **Week 1** | Demo cleanup, security hardening, browser testing | 15 hours |
| **Week 2** | Docker setup, backup strategy, monitoring | 15 hours |
| **Week 3** | Staging deployment, production hardening, UAT | 20 hours |
| **Week 4** | Production deployment, monitoring, support | 10 hours |

**Total:** ~60 hours (2-3 weeks with 20-30 hrs/week)

---

## 🚨 Go-Live Checklist

Before going live with real audits:

- [ ] All demo data removed from docs
- [ ] Security hardening complete
- [ ] Full end-to-end testing passed
- [ ] Backup and recovery tested
- [ ] Monitoring and alerting configured
- [ ] Production database configured with backups
- [ ] SSL/TLS certificate installed
- [ ] CORS origins configured for production domain
- [ ] Team trained on workflows
- [ ] Rollback plan documented

---

## 📞 Support

For questions or issues in next session:
- Check `COMPLETION_STATUS.md` for detailed task list
- See `docs/ISO-ACCREDITOR-GUIDE.md` for user workflows
- See `docs/PRODUCTION-DEPLOYMENT.md` for deployment issues
- Review commit messages (search for "GSTC", "validation", "accreditor")

---

**Good luck with the new instance! The heavy lifting is done—now it's just cleanup and hardening.** 🚀
