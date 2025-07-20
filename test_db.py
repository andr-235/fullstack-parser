import asyncio
from app.core.database import async_engine

async def test_db():
    try:
        async with async_engine.connect() as conn:
            result = await conn.execute("SELECT 1")
            print("✅ Database connection successful!")
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_db()) 