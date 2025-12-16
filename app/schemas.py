from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict

from .models import Role, ObjectType, PageSection, DocumentKind


class ORMBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class UserBase(BaseModel):
    username: str
    full_name: str = ""
    role: Role


class UserCreate(UserBase):
    password: str


class UserOut(UserBase, ORMBase):
    id: int


class CompanyOut(ORMBase):
    id: int
    name: str


class DatacenterOut(ORMBase):
    id: int
    name: str


class ObjectOut(ORMBase):
    id: int
    dc_id: int
    type: ObjectType
    name: str
    status: str
    ip: Optional[str]
    fqdn: Optional[str]
    tags: Optional[str]
    description: Optional[str]


class PageOut(ORMBase):
    id: int
    section: PageSection
    content_md: str
    updated_at: datetime
    updated_by: Optional[int]


class PageUpdate(BaseModel):
    content_md: str


class RelationOut(ORMBase):
    id: int
    relation_type: str
    note: str
    src_object_id: int
    dst_object_id: int


class DocumentOut(ORMBase):
    id: int
    object_id: int
    title: str
    file_path: Optional[str]
    url: Optional[str]
    kind: DocumentKind
    uploaded_at: datetime


class DocumentCreate(BaseModel):
    title: str
    url: Optional[str] = None
    kind: DocumentKind = DocumentKind.link


class IncidentOut(ORMBase):
    id: int
    object_id: int
    title: str
    severity: str
    symptom: str
    cause: str
    check: str
    resolution: str
    created_at: datetime


class ObjectDetail(BaseModel):
    object: ObjectOut
    pages: List[PageOut]
    relations: List[RelationOut]
    documents: List[DocumentOut]
    incidents: List[IncidentOut]


class TreeNode(BaseModel):
    id: int
    name: str
    type: ObjectType
    status: str
    ip: Optional[str]


class TreeDatacenter(BaseModel):
    id: int
    name: str
    services: List[TreeNode]
    servers: List[TreeNode]
    network: List[TreeNode]


class TreeCompany(BaseModel):
    id: int
    name: str
    dcs: List[TreeDatacenter]


class TreeResponse(BaseModel):
    companies: List[TreeCompany]
