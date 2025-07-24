from app.database import engine

try:
    with engine.connect() as connection:
        print("✅ Connected to MySQL successfully!")
except Exception as e:
    print("❌ Failed to connect to MySQL:")
    print(e)
