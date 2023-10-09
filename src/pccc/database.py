from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Create engine and session
engine = create_engine('sqlite:///instance/pccc.db')
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()

class NhanVien(Base):
    Id = Column(Integer, primary_key=True, autoincrement=True)
    MaNV = Column(String(10))
    HoTen = Column(String(255))
    BoPhan = Column(String(255))
    PhongBan = Column(String(255))
    __tablename__  = "NhanVien"
    extend_existing = True

class Account(Base):
    Id = Column(Integer, primary_key=True, autoincrement=True)
    MaNV = Column(String(10))
    HoTen = Column(String(255))
    BoPhan = Column(String(255))
    PhongBan = Column(String(255))
    PassWord = Column(String(255))
    Role = Column(String(10))
    __tablename__  = "Account"
    extend_existing = True
    
class TapHuan(Base):
    Id = Column(Integer, primary_key=True, autoincrement=True)
    MaNV = Column(String(10))
    HoTen = Column(String(255))
    BoPhan = Column(String(255))
    PhongBan = Column(String(255))
    ThoiGian = Column(DateTime)
    __tablename__  = "TapHuan"
    extend_existing = True
    
# TapHuan.__table__.drop(engine)

class KetQua(Base):
    Id = Column(Integer, primary_key=True, autoincrement=True)
    BoPhan = Column(String(255))
    ThoiGian = Column(DateTime)
    HoanThanh = Column(Boolean)
    __tablename__  = "KetQua"
    extend_existing = True
    
# KetQua.__table__.drop(engine)

Base.metadata.create_all(engine)