from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, func, Float
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Ad(Base):
    __tablename__ = "ads"
    id = Column(Integer, primary_key=True)
    unique_id = Column(String(255), unique=True, nullable=False)
    keyword = Column(String(255), index=True)
    country = Column(String(10), index=True)
    domain = Column(String(255), index=True)
    title = Column(String(1024))
    body = Column(Text)
    media_url = Column(String(2048))
    created_at = Column(DateTime, server_default=func.now())


class KeywordRun(Base):
    __tablename__ = "keyword_runs"
    id = Column(Integer, primary_key=True, index=True)
    keyword = Column(String(255), index=True)
    started_at = Column(DateTime, server_default=func.now())
    duration_s = Column(Float)
    results_count = Column(Integer)
    status = Column(String(50), default="finished")


class Domain(Base):
    __tablename__ = "domains"
    id = Column(Integer, primary_key=True)
    domain = Column(String(255), unique=True, nullable=False)
    ads_count = Column(Integer, default=0)
    last_seen_at = Column(DateTime)


class EventRecord(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True)
    type = Column(String(255), index=True)
    payload = Column(JSON)
    created_at = Column(DateTime, server_default=func.now())
