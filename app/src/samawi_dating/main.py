from fastapi import FastAPI
import os
import psycopg

app = FastAPI(title="SaMaWi Dating", version="0.1.0")


@app.get("/")
def root():
    return {"name": "SaMaWi Dating", "status": "running"}


@app.get("/health")
def health():
    database_url = os.environ["DATABASE_URL"]
    with psycopg.connect(database_url) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT current_database(), current_user, version()")
            database, user, version = cur.fetchone()

    return {
        "status": "healthy",
        "database": database,
        "database_user": user,
        "database_version": version,
    }
