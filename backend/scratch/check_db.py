import asyncio
from app.db.session import engine
from sqlalchemy import inspect

async def main():
    async with engine.connect() as conn:
        def do_inspect(sync_conn):
            insp = inspect(sync_conn)
            tables = insp.get_table_names()
            print("Tables:", tables)
            if "users" in tables:
                cols = insp.get_columns("users")
                print("Users cols:", [(c["name"], str(c["type"])) for c in cols])
        await conn.run_sync(do_inspect)

if __name__ == "__main__":
    asyncio.run(main())
