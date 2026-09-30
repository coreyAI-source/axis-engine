"""Read-only diagnostic: run the dashboard queries without printing credentials."""
import asyncio
import sys
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.database import AsyncSessionLocal, async_engine
from app.routers.dashboard import dashboard_summary


async def main():
    try:
        async with AsyncSessionLocal() as db:
            print(await dashboard_summary(db=db, _=None))
    except Exception as exc:
        traceback.print_tb(exc.__traceback__)
        print(type(exc).__name__)
        # No connection URLs, tokens, SQL parameters or environment values.
        cause = getattr(exc, "orig", None)
        print("Database error type:", type(cause).__name__)
        print("SQLSTATE:", getattr(cause, "sqlstate", None))
        raise SystemExit(1)
    finally:
        await async_engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
