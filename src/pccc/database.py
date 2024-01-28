from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import sessionmaker, declarative_base

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
    __tablename__ = "NhanVien"
    extend_existing = True


class Account(Base):
    Id = Column(Integer, primary_key=True, autoincrement=True)
    MaNV = Column(String(10))
    HoTen = Column(String(255))
    BoPhan = Column(String(255))
    PhongBan = Column(String(255))
    PassWord = Column(String(255))
    Role = Column(String(10))
    __tablename__ = "Account"
    extend_existing = True


class DienTap(Base):
    Id = Column(Integer, primary_key=True, autoincrement=True)
    MaNV = Column(String(10))
    HoTen = Column(String(255))
    BoPhan = Column(String(255))
    PhongBan = Column(String(255))
    ThoiGian = Column(DateTime)
    __tablename__ = "DienTap"
    extend_existing = True

class DienTap2(Base):
    Id = Column(Integer, primary_key=True, autoincrement=True)
    
    BoPhan = Column(String(255))
    PhongBan = Column(String(255))
    SoLuongCoMat = Column(Integer)
    ThoiGian = Column(DateTime)
    __tablename__ = "DienTap2"
    extend_existing = True
    
# TapHuan.__table__.drop(engine)

class KetQua(Base):
    Id = Column(Integer, primary_key=True, autoincrement=True)
    BoPhan = Column(String(255))
    ThoiGian = Column(DateTime)
    HoanThanh = Column(Boolean)
    __tablename__ = "KetQua"
    extend_existing = True

class LichSu(Base):
    STT = Column(Integer, primary_key=True, autoincrement=True)
    MocThoiGian = Column(DateTime)
    KetQua = Column(String(10))
    LyDo = Column(String(255))
    ThoiGianHoanThanh = Column(DateTime)
    TongSo = Column(Integer)
    CoMat = Column(Integer)
    VangMat = Column(Integer)
    __tablename__ = "LichSu"
    extend_existing = True


Base.metadata.create_all(engine)