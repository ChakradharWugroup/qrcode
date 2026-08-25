import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Load URL from environment, or use TiDB cluster as fallback
_env_url = os.getenv("DATABASE_URL", "").strip()
if _env_url.startswith("mysql") or _env_url.startswith("postgres") or _env_url.startswith("sqlite"):
    DATABASE_URL = _env_url
else:
    DATABASE_URL = "mysql+pymysql://NxhLTEzTjPVqirD.root:HWxDC9wu8g6Dv612@gateway01.ap-northeast-1.prod.aws.tidbcloud.com:4000/test?ssl_verify_cert=true&ssl_verify_identity=true"

# SQLAlchemy requires 'postgresql://' instead of 'postgres://'
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# check_same_thread is only needed for SQLite
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
