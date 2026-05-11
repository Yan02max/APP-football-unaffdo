"""Modelos ORM: Equipo, Temporada, Partido."""
from sqlalchemy import Column, Integer, String, Boolean, Date, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class Equipo(Base):
    __tablename__ = "equipos"

    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False, unique=True)
    abreviacion = Column(String(10), nullable=False)
    color_principal = Column(String(7), default="#000000")
    color_secundario = Column(String(7), default="#FFFFFF")
    logo_path = Column(String(255), nullable=True)
    categoria = Column(String(50), nullable=False, default="Masculino")

    partidos_local = relationship(
        "Partido", foreign_keys="Partido.equipo_local_id", back_populates="equipo_local"
    )
    partidos_visitante = relationship(
        "Partido", foreign_keys="Partido.equipo_visitante_id", back_populates="equipo_visitante"
    )


class Temporada(Base):
    __tablename__ = "temporadas"

    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    fecha_inicio = Column(Date, nullable=False)
    fecha_fin = Column(Date, nullable=False)
    activa = Column(Boolean, default=True)
    categoria = Column(String(50), nullable=False, default="Masculino")

    partidos = relationship("Partido", back_populates="temporada")


class Partido(Base):
    __tablename__ = "partidos"

    id = Column(Integer, primary_key=True)
    temporada_id = Column(Integer, ForeignKey("temporadas.id"), nullable=False)
    jornada = Column(Integer, nullable=False)
    bloque = Column(Integer, nullable=False)
    equipo_local_id = Column(Integer, ForeignKey("equipos.id"), nullable=False)
    equipo_visitante_id = Column(Integer, ForeignKey("equipos.id"), nullable=False)
    fecha = Column(Date, nullable=False)
    puntos_local = Column(Integer, nullable=True)
    puntos_visitante = Column(Integer, nullable=True)

    temporada = relationship("Temporada", back_populates="partidos")
    equipo_local = relationship(
        "Equipo", foreign_keys=[equipo_local_id], back_populates="partidos_local"
    )
    equipo_visitante = relationship(
        "Equipo", foreign_keys=[equipo_visitante_id], back_populates="partidos_visitante"
    )