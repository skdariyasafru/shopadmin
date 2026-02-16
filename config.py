import os

class Config:

    SECRET_KEY = os.getenv("SECRET_KEY", "super-secret-key")

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "postgresql://username:password@host:5432/dbname"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_SAMESITE = "Lax"
