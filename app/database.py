from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base

# MySQL 데이터베이스 URL 설정
DATABASE_URL = "dburl"

# 데이터베이스 엔진 생성
engine = create_engine(DATABASE_URL)

# 세션 로컬 클래스 생성
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 데이터베이스 세션 의존성
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 
