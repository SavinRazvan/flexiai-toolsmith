# FILE: flexiai/database/connection.py

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Determine the directory of this file.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Set the directory for the database file (inside flexiai/database/db)
DB_DIR = os.path.join(BASE_DIR, "db")
if not os.path.exists(DB_DIR):
    os.makedirs(DB_DIR)

# Full path to the SQLite database file.
DATABASE_FILE = os.path.join(DB_DIR, "database.db")

# Use DATABASE_URL from environment if available; otherwise, default to our SQLite file.
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DATABASE_FILE}")

# Create the SQLAlchemy engine.
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)

# Create a configured "Session" class.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a base class for our ORM models.
Base = declarative_base()
