#!/usr/bin/env python3
"""Clean audit database - delete all audits and related data."""

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, delete

from app.config import settings
from app.models.audit import Audit, AuditPrompt, AuditProcess
from app.models.evidence import Finding


async def main():
    """Delete all audits and related data."""

    engine = create_async_engine(str(settings.database_url), echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as db:
        print("🗑️  Cleaning audit database...\n")

        # Get all audits
        result = await db.execute(select(Audit))
        audits = result.scalars().all()

        if not audits:
            print("✅ No audits to delete\n")
            return

        for audit in audits:
            print(f"   Deleting: {audit.auditee_name} ({audit.id})")

            # Delete findings
            await db.execute(delete(Finding).where(Finding.audit_id == audit.id))

            # Delete prompts
            await db.execute(delete(AuditPrompt).where(AuditPrompt.audit_id == audit.id))

            # Delete processes
            await db.execute(delete(AuditProcess).where(AuditProcess.audit_id == audit.id))

            # Delete audit
            await db.delete(audit)

        await db.commit()

        print(f"\n✅ Deleted {len(audits)} audit(s) and all related data\n")


if __name__ == "__main__":
    asyncio.run(main())
