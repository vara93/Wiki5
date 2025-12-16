from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, Enum
from sqlalchemy.orm import relationship
import enum

from .db import Base


class Role(str, enum.Enum):
    admin = "admin"
    editor = "editor"
    viewer = "viewer"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(Role), default=Role.viewer, nullable=False)
    full_name = Column(String, default="")

    pages = relationship("Page", back_populates="updated_by_user")


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)

    datacenters = relationship("Datacenter", back_populates="company", cascade="all, delete")


class Datacenter(Base):
    __tablename__ = "datacenters"

    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    name = Column(String, nullable=False)

    company = relationship("Company", back_populates="datacenters")
    objects = relationship("Object", back_populates="datacenter", cascade="all, delete")


class ObjectType(str, enum.Enum):
    service = "service"
    server = "server"
    network = "network"


class Object(Base):
    __tablename__ = "objects"

    id = Column(Integer, primary_key=True)
    dc_id = Column(Integer, ForeignKey("datacenters.id"), nullable=False)
    type = Column(Enum(ObjectType), nullable=False)
    name = Column(String, nullable=False)
    status = Column(String, default="ok")
    ip = Column(String, nullable=True)
    fqdn = Column(String, nullable=True)
    tags = Column(String, nullable=True)
    description = Column(Text, nullable=True)

    datacenter = relationship("Datacenter", back_populates="objects")
    pages = relationship("Page", back_populates="object", cascade="all, delete")
    documents = relationship("Document", back_populates="object", cascade="all, delete")
    incidents = relationship("Incident", back_populates="object", cascade="all, delete")
    relations_from = relationship(
        "Relation", foreign_keys="Relation.src_object_id", back_populates="src_object", cascade="all, delete"
    )
    relations_to = relationship(
        "Relation", foreign_keys="Relation.dst_object_id", back_populates="dst_object", cascade="all, delete"
    )


class PageSection(str, enum.Enum):
    overview = "overview"
    links = "links"
    arch = "arch"
    net = "net"
    inc = "inc"
    docs = "docs"


class Page(Base):
    __tablename__ = "pages"

    id = Column(Integer, primary_key=True)
    object_id = Column(Integer, ForeignKey("objects.id"), nullable=False)
    section = Column(Enum(PageSection), nullable=False)
    content_md = Column(Text, default="")
    updated_at = Column(DateTime, default=datetime.utcnow)
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    object = relationship("Object", back_populates="pages")
    updated_by_user = relationship("User", back_populates="pages")


class Relation(Base):
    __tablename__ = "relations"

    id = Column(Integer, primary_key=True)
    src_object_id = Column(Integer, ForeignKey("objects.id"), nullable=False)
    dst_object_id = Column(Integer, ForeignKey("objects.id"), nullable=False)
    relation_type = Column(String, default="depends")
    note = Column(String, default="")

    src_object = relationship("Object", foreign_keys=[src_object_id], back_populates="relations_from")
    dst_object = relationship("Object", foreign_keys=[dst_object_id], back_populates="relations_to")


class DocumentKind(str, enum.Enum):
    file = "file"
    link = "link"


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True)
    object_id = Column(Integer, ForeignKey("objects.id"), nullable=False)
    title = Column(String, nullable=False)
    file_path = Column(String, nullable=True)
    url = Column(String, nullable=True)
    kind = Column(Enum(DocumentKind), default=DocumentKind.file)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    object = relationship("Object", back_populates="documents")


class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True)
    object_id = Column(Integer, ForeignKey("objects.id"), nullable=False)
    title = Column(String, nullable=False)
    severity = Column(String, default="info")
    symptom = Column(Text, default="")
    cause = Column(Text, default="")
    check = Column(Text, default="")
    resolution = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)

    object = relationship("Object", back_populates="incidents")
