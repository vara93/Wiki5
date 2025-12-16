from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
from .models import Role, ObjectType, PageSection, DocumentKind


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


class UserOut(UserBase):
    id: int

    class Config:
        orm_mode = True


class CompanyOut(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


class DatacenterOut(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


class ObjectOut(BaseModel):
    id: int
    dc_id: int
    type: ObjectType
    name: str
    status: str
    ip: Optional[str]
    fqdn: Optional[str]
    tags: Optional[str]
    description: Optional[str]

    class Config:
        orm_mode = True


class PageOut(BaseModel):
    id: int
    section: PageSection
    content_md: str
    updated_at: datetime
    updated_by: Optional[int]

    class Config:
        orm_mode = True


class PageUpdate(BaseModel):
    content_md: str


class RelationOut(BaseModel):
    id: int
    relation_type: str
    note: str
    src_object_id: int
    dst_object_id: int

    class Config:
        orm_mode = True


class DocumentOut(BaseModel):
    id: int
    object_id: int
    title: str
    file_path: Optional[str]
    url: Optional[str]
    kind: DocumentKind
    uploaded_at: datetime

    class Config:
        orm_mode = True


class DocumentCreate(BaseModel):
    title: str
    url: Optional[str] = None
    kind: DocumentKind = DocumentKind.link


class IncidentOut(BaseModel):
    id: int
    object_id: int
    title: str
    severity: str
    symptom: str
    cause: str
    check: str
    resolution: str
    created_at: datetime

    class Config:
        orm_mode = True


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
