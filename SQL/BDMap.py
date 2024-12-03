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
    YacimientoArqueologico = "Yacimiento-arquelógico"
    IglesiaErmita = "Iglesia-Ermita"
    MonasterioConvento = "Monasterio-Convento"
    CastilloFortalezaTorre = "Castillo-Fortaleza-Torre"
    EdificioSingular = "Edificio-Palacio"
    Puente = "Puente"
    Otros = "Otros"

# Tabla Provincia
class Provincia(Base):
    __tablename__ = "provincia"
    id: int = Column(Integer, primary_key=True, autoincrement=True)
    nombre: str = Column(String(100), nullable=False, unique=True)
    codigo: str = Column(String(50), nullable=True, unique=True)
    localidades = relationship("Localidad", back_populates="provincia")


# Tabla Localidad
class Localidad(Base):
    __tablename__ = "localidad"
    id: int = Column(Integer, primary_key=True, autoincrement=True)
    nombre: str = Column(String(100), nullable=False, unique=True)
    codigo: str = Column(String(50), nullable=True, unique=True)
    en_provincia: int = Column(Integer, ForeignKey("provincia.id"), nullable=False)
    provincia = relationship("Provincia", back_populates="localidades")
    monumentos = relationship("Monumento", back_populates="localidad")


# Tabla Monumento
class Monumento(Base):
    __tablename__ = "monumento"
    id: int = Column(Integer, primary_key=True, autoincrement=True)
    nombre: str = Column(String(150), nullable=False)
    tipo: TipoMonumento = Column(Enum(TipoMonumento, name="tipo_monumento"), nullable=True)
    direccion: str = Column(String(200))
    codigo_postal: str = Column(String(20))
    longitud: float = Column(Float)
    latitud: float = Column(Float)
    descripcion: str = Column(String(500))
    en_localidad: int = Column(Integer, ForeignKey("localidad.id"), nullable=False)
    localidad = relationship("Localidad", back_populates="monumentos")
