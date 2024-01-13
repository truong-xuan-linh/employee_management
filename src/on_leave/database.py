from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, func, and_, desc, extract, or_
from sqlalchemy.orm import sessionmaker, declarative_base

# Create engine and session
engine = create_engine('sqlite:///instance/pccc.db')
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()

class NghiPhep(Base):
    Id = Column(Integer, primary_key=True, autoincrement=True)
    MaNV = Column(String(10))
    HoTen = Column(String(255))
    BoPhan = Column(String(255))
    PhongBan = Column(String(255))
    GioVao = Column(DateTime)
    GioRa = Column(DateTime)
    GioVaoThucTe = Column(DateTime)
    GioRaThucTe = Column(DateTime)
    ThoiGian = Column(DateTime)
    Mail =  Column(String(255))
    NghiGay = Column(Boolean)
    __tablename__ = "NghiPhep"
    extend_existing = True
    
Base.metadata.create_all(engine)