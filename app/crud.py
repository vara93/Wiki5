from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List
from datetime import datetime

from . import models, schemas


def get_tree(db: Session) -> schemas.TreeResponse:
    companies_resp = []
    companies = db.execute(select(models.Company)).scalars().all()
    for company in companies:
        dcs_resp = []
        for dc in company.datacenters:
            services = [
                schemas.TreeNode(id=o.id, name=o.name, type=o.type, status=o.status, ip=o.ip)
                for o in dc.objects
                if o.type == models.ObjectType.service
            ]
            servers = [
                schemas.TreeNode(id=o.id, name=o.name, type=o.type, status=o.status, ip=o.ip)
                for o in dc.objects
                if o.type == models.ObjectType.server
            ]
            network = [
                schemas.TreeNode(id=o.id, name=o.name, type=o.type, status=o.status, ip=o.ip)
                for o in dc.objects
                if o.type == models.ObjectType.network
            ]
            dcs_resp.append(
                schemas.TreeDatacenter(
                    id=dc.id, name=dc.name, services=services, servers=servers, network=network
                )
            )
        companies_resp.append(schemas.TreeCompany(id=company.id, name=company.name, dcs=dcs_resp))
    return schemas.TreeResponse(companies=companies_resp)


def list_companies(db: Session) -> list[models.Company]:
    return db.execute(select(models.Company)).scalars().all()


def get_object_detail(db: Session, object_id: int) -> schemas.ObjectDetail | None:
    obj = db.get(models.Object, object_id)
    if not obj:
        return None
    pages = db.query(models.Page).filter(models.Page.object_id == object_id).all()
    relations = db.query(models.Relation).filter(models.Relation.src_object_id == object_id).all()
    documents = db.query(models.Document).filter(models.Document.object_id == object_id).all()
    incidents = db.query(models.Incident).filter(models.Incident.object_id == object_id).all()
    return schemas.ObjectDetail(
        object=obj, pages=pages, relations=relations, documents=documents, incidents=incidents
    )


def update_page(db: Session, page_id: int, content_md: str, user: models.User):
    page = db.get(models.Page, page_id)
    if not page:
        return None
    page.content_md = content_md
    page.updated_at = datetime.utcnow()
    page.updated_by = user.id
    db.add(page)
    db.commit()
    db.refresh(page)
    return page


def create_document(db: Session, object_id: int, title: str, kind: models.DocumentKind, path: str | None, url: str | None):
    doc = models.Document(object_id=object_id, title=title, kind=kind, file_path=path, url=url)
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


def list_documents(db: Session, object_id: int) -> List[models.Document]:
    return db.query(models.Document).filter(models.Document.object_id == object_id).all()
