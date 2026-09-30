"""
Run all seed scripts against the database.

Usage:
    python -m seed.run_seed

Requires DATABASE_URL_SYNC in environment or .env file.
Creates a demo organisation and seeds all reference data.
"""
import sys
import os

# Allow running from the api/ directory
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SyncSessionLocal
from app.models.org import Organisation, User
from app.utils.security import hash_password
from seed.seed_core import seed_core
from seed.seed_standards import seed_standards
from seed.seed_processes import seed_processes
from seed.seed_process_clause_maps import seed_process_clause_maps


def run():
    with SyncSessionLocal() as db:
        print("Seeding core reference data...")
        seed_core(db)

        print("Seeding ISO standards and clauses...")
        seed_standards(db)

        print("Creating demo organisation...")
        org = db.query(Organisation).filter_by(name="Demo Organisation").first()
        if not org:
            org = Organisation(
                name="Demo Organisation",
                legal_name="Demo Organisation Pty Ltd",
                active_flag=True,
            )
            db.add(org)
            db.flush()

        print("Seeding example processes...")
        seed_processes(db, org.id)

        print("Seeding process-clause mappings...")
        count = seed_process_clause_maps(db, org.id)
        print(f"  {count} mappings created.")

        print("Creating admin user...")
        admin = db.query(User).filter_by(email="admin@demo.local").first()
        if not admin:
            admin = User(
                organisation_id=org.id,
                first_name="Admin",
                last_name="User",
                email="admin@demo.local",
                hashed_password=hash_password("changeme123"),
                role_code="admin",
                active_flag=True,
            )
            db.add(admin)
            db.flush()

        db.commit()
        print("Seed complete.")
        print(f"  Organisation: {org.name} ({org.id})")
        print(f"  Admin login:  admin@demo.local / changeme123")


if __name__ == "__main__":
    run()
