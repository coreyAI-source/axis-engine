# Production Deployment Guide for AXIS Hotel Audit Platform

**Purpose:** Deploy AXIS for production use by ISO accreditors and certification bodies  
**Audience:** DevOps engineers, system administrators, IT managers

---

## Pre-Deployment Checklist

### Security Requirements

- [ ] **Secret Key:** Generate cryptographically-secure random 32+ char key (use `python -c "import secrets; print(secrets.token_urlsafe(32))"`)
- [ ] **Database Credentials:** Strong passwords (20+ chars, mixed case/numbers/symbols)
- [ ] **HTTPS:** SSL/TLS certificate obtained and installed
- [ ] **CORS:** Allowed origins configured (NOT `*`)
- [ ] **Firewall:** API port (8000) accessible only from web tier
- [ ] **Secrets Manager:** Use platform-provided secrets (AWS Secrets Manager, Vault, etc.), not .env files

### Database Setup

- [ ] PostgreSQL 12+ running and accessible
- [ ] Database created: `CREATE DATABASE axis_db`
- [ ] User created with limited permissions (read/write on axis_db only)
- [ ] Backup policy configured (automated daily snapshots)
- [ ] Test restore procedure documented and tested
- [ ] Connection pooling enabled (min 5, max 20 connections)

### Node.js Runtime

- [ ] Node.js 22.6+ installed on API host
- [ ] `packages/engine` directory present and accessible to API process
- [ ] No Node-based processes running as root

### Monitoring & Alerting

- [ ] Error tracking configured (Sentry, DataDog, etc.)
- [ ] Log aggregation set up (ELK Stack, CloudWatch, etc.)
- [ ] Uptime monitoring configured (alert on API /health endpoint down)
- [ ] Memory/CPU thresholds set (restart if >90% for >5 min)
- [ ] Disk space monitoring (alert if <20% free)

### Backup & Recovery

- [ ] Backup schedule: Automated daily at [time]
- [ ] Backup retention: [duration] (recommend 30+ days)
- [ ] Recovery testing: Restore to staging database monthly
- [ ] RTO: Recovery Time Objective ([hours])
- [ ] RPO: Recovery Point Objective ([hours])
- [ ] Backup encryption: Enabled and keys stored securely
- [ ] Offsite backups: Stored in separate geographic region

---

## Installation Steps

### 1. Clone Repository

```bash
git clone https://github.com/your-org/axis-engine.git
cd axis-engine
```

### 2. Install Python Dependencies

```bash
cd services/api
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Install Node Dependencies (For Audit Engine)

```bash
cd ../../packages/engine
npm ci  # Use npm ci (not npm install) for production
```

### 4. Configure Environment

Create `services/api/.env` with production values:

```bash
# Database
DATABASE_URL=postgresql://axis_user:strong_password@db.prod.internal:5432/axis_db
DATABASE_URL_SYNC=postgresql://axis_user:strong_password@db.prod.internal:5432/axis_db

# Security
SECRET_KEY=your-generated-random-key-here-32-chars-minimum
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440  # 24 hours

# CORS (configure for your domain only)
CORS_ORIGINS=["https://audit.yourdomain.com", "https://audit-staging.yourdomain.com"]

# Storage (if using MinIO for older evidence routes)
STORAGE_ENDPOINT=https://minio.yourdomain.com
STORAGE_ACCESS_KEY=your-key
STORAGE_SECRET_KEY=your-secret
STORAGE_BUCKET=axis-evidence-prod
STORAGE_REGION=us-east-1

# AI Report Drafting (optional)
OPENROUTER_API_KEY=sk-or-...  # Leave empty to disable AI drafting
OPENROUTER_MODEL=anthropic/claude-sonnet-4.5
OPENROUTER_MODEL_MECHANICAL=anthropic/claude-sonnet-4.5
OPENROUTER_REFERER=https://audit.yourdomain.com

# Database Connection Pooling
DATABASE_POOL_SIZE=10
DATABASE_POOL_RECYCLE=3600

# Auto-create tables (DISABLE in production)
AUTO_CREATE_TABLES=false
```

### 5. Run Database Migrations

```bash
python -m alembic upgrade head
```

This creates all necessary tables. Verify no errors.

### 6. Create Initial Admin User (Optional)

```bash
# If you have a seed script
python -m seed.create_admin --email admin@yourdomain.com --password "temp-password"
```

Users should change temp password on first login.

### 7. Start the API Service

#### Option A: Using systemd (Linux/macOS)

Create `/etc/systemd/system/axis-api.service`:

```ini
[Unit]
Description=AXIS Hotel Audit API
After=network.target postgresql.service

[Service]
User=axis
WorkingDirectory=/opt/axis-engine/services/api
Environment="PATH=/opt/axis-engine/services/api/.venv/bin"
ExecStart=/opt/axis-engine/services/api/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable axis-api
sudo systemctl start axis-api
sudo systemctl status axis-api
```

#### Option B: Using Docker

```bash
docker run -d \
  --name axis-api \
  --restart unless-stopped \
  -e DATABASE_URL="postgresql://..." \
  -e SECRET_KEY="your-key" \
  -e CORS_ORIGINS='["https://yourdomain.com"]' \
  -p 8000:8000 \
  axis-api:latest
```

### 8. Deploy Web Frontend (Next.js)

```bash
cd apps/web

# Install dependencies
npm ci

# Build for production
npm run build

# Set environment variables
export NEXT_PUBLIC_API_URL=https://api.yourdomain.com

# Start production server (or deploy to Vercel/similar)
npm run start
```

Or deploy to Vercel:

```bash
npm install -g vercel
vercel --prod --env NEXT_PUBLIC_API_URL=https://api.yourdomain.com
```

### 9. Configure Reverse Proxy (Nginx example)

```nginx
# /etc/nginx/sites-available/axis

upstream axis_api {
    server 127.0.0.1:8000;
}

server {
    listen 443 ssl http2;
    server_name audit.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/audit.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/audit.yourdomain.com/privkey.pem;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # Rate limiting for auth endpoints
    limit_req_zone $binary_remote_addr zone=auth_limit:10m rate=5r/m;

    location /api {
        limit_req zone=auth_limit burst=20 nodelay;
        proxy_pass http://axis_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 30s;
        proxy_connect_timeout 10s;
    }

    location / {
        proxy_pass http://localhost:3000;  # Next.js dev server
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name audit.yourdomain.com;
    return 301 https://$server_name$request_uri;
}
```

### 10. Health Checks

Verify deployment:

```bash
# Check API health
curl https://audit.yourdomain.com/api/health

# Expected response:
# {"status": "ok", "service": "axis-api"}

# Check database connection
curl https://audit.yourdomain.com/api/docs  # Should load Swagger UI

# Check web app
curl https://audit.yourdomain.com/hospitality
```

---

## Production Hardening

### Security

1. **Disable Debug Mode**
   ```python
   # In app/config.py
   DEBUG = False
   ```

2. **Enable HTTPS Enforcement**
   ```python
   CORS_ORIGINS = [
       "https://audit.yourdomain.com",  # Only HTTPS, no http://
   ]
   ```

3. **Set Strong Security Headers**
   ```python
   # Add to app middleware
   add_header("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
   add_header("X-Content-Type-Options", "nosniff")
   add_header("X-Frame-Options", "DENY")
   ```

4. **Implement Rate Limiting**
   - Auth endpoints: 5 attempts/minute per IP
   - API endpoints: 100 requests/minute per user
   - File uploads: 10 per minute per user

5. **Enable Database Encryption**
   ```sql
   -- Enable SSL for PostgreSQL connections
   sslmode=require
   ```

6. **Secrets Management**
   - Use AWS Secrets Manager, HashiCorp Vault, or Azure Key Vault
   - Rotate secrets every 90 days
   - Never commit secrets to Git

### Performance Tuning

1. **Database Connection Pooling**
   ```python
   DATABASE_POOL_SIZE = 10
   DATABASE_POOL_MAX_OVERFLOW = 20
   DATABASE_POOL_RECYCLE = 3600  # Recycle connections every hour
   ```

2. **API Concurrency**
   - Run multiple uvicorn workers: `uvicorn app.main:app --workers 4`
   - Or use Gunicorn: `gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app`

3. **Caching**
   - Cache GSTC criteria (rarely changes)
   - Add Redis for session storage (if needed)

4. **Database Indexes**
   ```sql
   -- Ensure key indexes exist
   CREATE INDEX idx_hospitality_audits_org ON hospitality_audits(organisation_id);
   CREATE INDEX idx_hospitality_audits_status ON hospitality_audits(status);
   ```

---

## Monitoring & Maintenance

### Key Metrics to Track

| Metric | Alert Threshold | Check Frequency |
|--------|-----------------|-----------------|
| API Response Time | >2000ms | Continuous |
| Database Query Time | >1000ms | Continuous |
| Error Rate | >1% | Real-time |
| Disk Usage | >80% | Hourly |
| Memory Usage | >85% | Hourly |
| Backup Success | Any failure | Daily |
| Database Connections | >90% of pool | Continuous |

### Logging

Ensure all audit events are logged:

```python
import logging

logger = logging.getLogger("axis")
logger.info(f"User {user_id} created audit {audit_id}")
logger.warning(f"Database connection failed: {error}")
logger.error(f"Payment processing failed for org {org_id}")
```

Aggregate logs to centralized system:
- **ELK Stack** (Elasticsearch, Logstash, Kibana)
- **Datadog**
- **New Relic**
- **CloudWatch** (AWS)

### Backups

Verify backups daily:

```bash
# List backups
aws s3 ls s3://axis-backups/daily/

# Test restore (weekly)
pg_restore -d axis_test_$(date +%s) axis_backup_latest.dump

# Verify audit tables exist
psql -d axis_test_$(date +%s) -c "SELECT COUNT(*) FROM hospitality_audits;"
```

### Maintenance Windows

Schedule during low-traffic hours (typically 2–4 AM):
- Database maintenance (VACUUM, ANALYZE)
- Security patching
- Software updates
- Backup verification

**Notification:** Inform users 48 hours in advance of any downtime.

---

## Disaster Recovery

### Recovery Procedures

If the production system fails:

1. **Assess Impact**
   - How long has the system been down?
   - Can we restore from a recent backup?
   - How many users are affected?

2. **Activate Backup**
   ```bash
   # Stop the running API
   systemctl stop axis-api

   # Restore database from last known-good backup
   pg_restore -d axis_db axis_backup_2026_10_06_0200.dump

   # Restart API
   systemctl start axis-api

   # Verify health
   curl https://audit.yourdomain.com/api/health
   ```

3. **Communicate Status**
   - Notify users via email/Slack
   - Post status on status page
   - Provide recovery time estimate

4. **Post-Incident**
   - Review incident logs
   - Update documentation
   - Improve alerting

### Recovery Time Objectives (RTO)

- **Data Restore:** < 1 hour (from daily backup)
- **System Restart:** < 15 minutes
- **Full Recovery:** < 2 hours

### Recovery Point Objectives (RPO)

- **Data Loss:** < 24 hours (daily backups)
- **Recent Changes:** Last backup before incident

---

## Compliance & Audit Trail

### Regulatory Requirements

AXIS maintains audit trails for compliance:

1. **User Actions Logged**
   - Login/logout
   - Audit created/modified/deleted
   - Assessment changed
   - Finding created/closed
   - Action status changed
   - Evidence uploaded

2. **Data Retention**
   - Audit records: Retained for audit lifecycle + 7 years
   - Evidence: Retained per regulatory/client requirements
   - Logs: Retained for 1 year (configurable)

3. **Access Controls**
   - Multi-factor authentication (if required)
   - Role-based access control (RBAC)
   - Principle of least privilege
   - Audit log access restricted to admins

### Compliance Checklist

- [ ] GDPR: Data retention policy defined; right to deletion implemented
- [ ] SOC 2: Audit trail enabled; backups encrypted; access logged
- [ ] ISO 27001: Information security measures in place
- [ ] Local Regulations: Verify data residency requirements (some countries require local storage)

---

## Troubleshooting Production Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| API returns 503 | Node.js engine unavailable | Verify `packages/engine` accessible; restart API |
| Slow database queries | Missing indexes | Run `ANALYZE` table; add missing indexes |
| Out of disk space | Audit evidence accumulation | Archive old audits; implement retention policy |
| High memory usage | Connection leak | Restart API; verify connection pooling |
| Users cannot login | Database offline | Check PostgreSQL; restore from backup if needed |
| Evidence files not uploading | Storage full or permissions | Check disk space; verify IAM permissions |

---

## Upgrade Procedure

To upgrade AXIS to a new version:

1. **Backup Current System**
   ```bash
   pg_dump axis_db > axis_backup_pre_upgrade.sql
   ```

2. **Download New Version**
   ```bash
   git pull origin main
   ```

3. **Update Dependencies**
   ```bash
   pip install -r requirements.txt --upgrade
   cd ../../../packages/engine && npm ci
   ```

4. **Run Migrations**
   ```bash
   python -m alembic upgrade head
   ```

5. **Test in Staging** (before production)
   - Verify audits load
   - Test file upload
   - Generate reports

6. **Deploy to Production**
   ```bash
   systemctl stop axis-api
   # Deploy code
   systemctl start axis-api
   systemctl status axis-api
   ```

7. **Verify**
   - Check `/api/health`
   - Open http://audit.yourdomain.com
   - Test a sample audit workflow

---

## Support Contacts

- **Technical Issues:** DevOps team or vendor support
- **GSTC Standard Questions:** https://www.gstc.org/
- **Security Incidents:** [Your Security Team] - [Contact Info]

---

**Document Version:** 1.0  
**Last Updated:** October 2026  
**Next Review:** April 2027
