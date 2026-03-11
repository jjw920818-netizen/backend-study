from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 데이터베이스 연결 정보
DATABASE_URL = "mysql+pymysql://root:1234@db:3306/oz"

engine = create_engine(DATABASE_URL)

SessionFactory = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)
