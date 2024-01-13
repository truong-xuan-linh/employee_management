from sqlalchemy import create_engine, Column, Integer, String, DateTime, func, and_, desc
from sqlalchemy.orm import sessionmaker, declarative_base

# Create engine and session
engine = create_engine('sqlite:///instance/pccc.db')
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()

class DiemDanh(Base):
    Id = Column(Integer, primary_key=True, autoincrement=True)
    MaNV = Column(String(10))
    HoTen = Column(String(255))
    BoPhan = Column(String(255))
    PhongBan = Column(String(255))
    ThoiGian = Column(DateTime)
    __tablename__ = "DiemDanh"
    extend_existing = True

class KetQuaDiemDanh(Base):
    Id = Column(Integer, primary_key=True, autoincrement=True)
    BoPhan = Column(String(255))
    ThoiGian = Column(DateTime)
    SoLuongVang = Column(Integer)
    SoLuongCoMat = Column(Integer)
    Mail =  Column(String(255))
    __tablename__ = "KetQuaDiemDanh"
    extend_existing = True
    
Base.metadata.create_all(engine)