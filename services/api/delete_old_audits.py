#!/usr/bin/env python3
"""Delete all existing audits."""

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

from app.config import settings
from app.models.audit import Audit


async def main():
    """Delete all audits."""

    engine = create_async_engine(str(settings.database_url), echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as db:
        print("🗑️  Deleting all audits...\n")

        result = await db.execute(select(Audit))
        audits = result.scalars().all()

        if not audits:
            print("✅ No audits to delete\n")
            return

        for audit in audits:
            print(f"   Deleting: {audit.auditee_name} ({audit.id})")
            await db.delete(audit)

        await db.commit()

        print(f"\n✅ Deleted {len(audits)} audit(s)\n")


if __name__ == "__main__":
    asyncio.run(main())
