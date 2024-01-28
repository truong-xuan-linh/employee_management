from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, func, and_, desc, extract, or_
from sqlalchemy.orm import sessionmaker, declarative_base

# Create engine and session
engine = create_engine('sqlite:///instance/pccc.db')
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()

class RaVao(Base):
    Id = Column(Integer, primary_key=True, autoincrement=True)
    MaNV = Column(String(10))
    HoTen = Column(String(255))
    BoPhan = Column(String(255))
    PhongBan = Column(String(255))
    GioVaoThucTe = Column(DateTime)
    GioRaThucTe = Column(DateTime)
    ThoiGian = Column(DateTime)
    __tablename__ = "RaVao"
    extend_existing = True
    
Base.metadata.create_all(engine)