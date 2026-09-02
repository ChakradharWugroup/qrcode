import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "mysql+pymysql://NxhLTE2TjPVqirD.root:7PkdDwgmEcQQUuRW@gateway01.ap-northeast-1.prod.aws.tidbcloud.com:4000/test"

# SQLAlchemy requires 'postgresql://' instead of 'postgres://'
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# check_same_thread is only needed for SQLite, and we need ssl dict for TiDB to bypass strict CA checks in Docker
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {"ssl": {"ssl_verify_cert": False, "ssl_verify_identity": False}}

engine = create_engine(
    DATABASE_URL, 
    connect_args=connect_args,
    pool_pre_ping=True,
    pool_recycle=300,
    pool_size=5,
    max_overflow=10
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
