from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Float,
    ForeignKey,
    Enum,
)
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from enum import Enum as PyEnum

Base = declarative_base()

# Enum para el tipo de monumento con valores personalizados
class TipoMonumento(PyEnum):
    YacimientoArquelogico = "YacimientoArquelogico"
    IglesiaErmita = "IglesiaErmita"
    MonasterioConvento = "MonasterioConvento"
    CastilloFortalezaTorre = "CastilloFortalezaTorre"
    EdificioPalacio = "EdificioPalacio"
    Puente = "Puente"
    Otros = "Otros"

# Tabla Provincia
class Provincia(Base):
    __tablename__ = "provincia"
    id: int = Column(Integer, primary_key=True, autoincrement=True)
    nombre: str = Column(String(500), nullable=True, unique=True)
    localidades = relationship("Localidad", back_populates="provincia")


# Tabla Localidad
class Localidad(Base):
    __tablename__ = "localidad"
    id: int = Column(Integer, primary_key=True, autoincrement=True)
    nombre: str = Column(String(500), nullable=True, unique=True)
    en_provincia: int = Column(Integer, ForeignKey("provincia.id"), nullable=True)
    provincia = relationship("Provincia", back_populates="localidades")
    monumentos = relationship("Monumento", back_populates="localidad")


# Tabla Monumento
class Monumento(Base):
    __tablename__ = "monumento"
    id: int = Column(Integer, primary_key=True, autoincrement=True)
    nombre: str = Column(String(500), nullable=True)
    tipo: TipoMonumento = Column(Enum(TipoMonumento, name="tipo_monumento"), nullable=True)
    direccion: str = Column(String(500))
    codigo_postal: str = Column(String(50))
    longitud: float = Column(Float)
    latitud: float = Column(Float)
    descripcion: str = Column(String(10000))
    en_localidad: int = Column(Integer, ForeignKey("localidad.id"), nullable=True)
    localidad = relationship("Localidad", back_populates="monumentos")
