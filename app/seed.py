from datetime import datetime
from sqlalchemy.orm import Session

from .db import SessionLocal, engine
from . import models
from .auth import get_password_hash


def create_user(db: Session, username: str, password: str, role: models.Role, full_name: str):
    user = db.query(models.User).filter_by(username=username).first()
    hashed = get_password_hash(password)
    if user:
        user.role = role
        user.full_name = full_name
        user.hashed_password = hashed
    else:
        user = models.User(username=username, hashed_password=hashed, role=role, full_name=full_name)
        db.add(user)
    db.commit()


def seed_core():
    db = SessionLocal()
    models.Base.metadata.create_all(bind=engine)

    create_user(db, "admin", "admin", models.Role.admin, "Admin")
    create_user(db, "editor", "editor", models.Role.editor, "Editor")
    create_user(db, "viewer", "viewer", models.Role.viewer, "Viewer")

    if db.query(models.Company).count() > 0:
        db.close()
        return

    pd = models.Company(name="Первый Дом")
    pp = models.Company(name="Первая приемная")
    db.add_all([pd, pp])
    db.commit()

    dc_pd = models.Datacenter(company_id=pd.id, name="Прохорова")
    dc_pp = models.Datacenter(company_id=pp.id, name="Машкова")
    db.add_all([dc_pd, dc_pp])
    db.commit()

    def add_object(dc, type_, name, status="ok", ip=None):
        obj = models.Object(dc_id=dc.id, type=type_, name=name, status=status, ip=ip)
        db.add(obj)
        db.commit()
        for section in models.PageSection:
            db.add(models.Page(object_id=obj.id, section=section, content_md=f"## {name} — {section.value}\n\nОписание."))
        db.commit()
        return obj

    # PD objects
    pd_services = [
        ("RDS (Terminal Farm)", "ok"),
        ("Exchange", "ok"),
        ("VPN", "warn"),
    ]
    pd_servers = [
        ("PD-RDCB01", "10.98.10.10"),
        ("PD-RDGW01", "10.98.10.11"),
        ("PD-RDSH01", "10.98.10.21"),
        ("PD-RDSH02", "10.98.10.22"),
        ("PD-EXCH01", "10.98.20.10"),
        ("PD-DC01", "10.98.1.71"),
        ("PD-FS01", "10.98.30.10"),
    ]
    pd_network = [
        ("PD-FW-01", "10.98.0.1", "warn"),
        ("PD-SW-CORE-01", "10.98.0.2", "ok"),
    ]

    svc_objs = [add_object(dc_pd, models.ObjectType.service, n, status=s) for n, s in pd_services]
    srv_objs = [add_object(dc_pd, models.ObjectType.server, n, ip=ip) for n, ip in pd_servers]
    net_objs = [add_object(dc_pd, models.ObjectType.network, n, status=s, ip=ip) for n, ip, s in pd_network]

    # Relations example
    db.add_all([
        models.Relation(src_object_id=svc_objs[0].id, dst_object_id=srv_objs[0].id, relation_type="uses"),
        models.Relation(src_object_id=svc_objs[1].id, dst_object_id=srv_objs[4].id, relation_type="uses"),
        models.Relation(src_object_id=svc_objs[2].id, dst_object_id=net_objs[0].id, relation_type="uses"),
    ])
    db.commit()

    # incidents
    db.add(models.Incident(object_id=svc_objs[0].id, title="Проблемы с сессиями", severity="high", symptom="Пользователи не могут подключиться", cause="RDCB", check="Проверить службы", resolution="Перезапуск"))
    db.add(models.Incident(object_id=srv_objs[2].id, title="Высокая нагрузка", severity="medium", symptom="CPU 100%", cause="Много сессий", check="Проверить процессы", resolution="Добавить узел"))
    db.commit()

    # documents
    db.add(models.Document(object_id=svc_objs[0].id, title="Схема RDS", url="https://example.com/rds", kind=models.DocumentKind.link))
    db.add(models.Document(object_id=svc_objs[1].id, title="Exchange plan", url="https://example.com/exch", kind=models.DocumentKind.link))
    db.commit()

    # PP objects
    pp_services = [("1C (App + DB)", "ok"), ("RDS (Office)", "warn"), ("Backup", "ok")]
    pp_servers = [
        ("PP-1C01", "10.96.3.11"),
        ("PP-PG01", "10.96.3.12"),
        ("PP-RDSH01", "10.96.4.21"),
        ("PP-DC01", "10.96.11.71"),
        ("PP-FS01", "10.96.5.10"),
    ]
    pp_network = [("PP-FW-01", "10.96.0.1", "ok"), ("PP-SW-CORE-01", "10.96.0.2", "ok")]

    add_object(dc_pp, models.ObjectType.service, pp_services[0][0], status=pp_services[0][1])
    add_object(dc_pp, models.ObjectType.service, pp_services[1][0], status=pp_services[1][1])
    add_object(dc_pp, models.ObjectType.service, pp_services[2][0], status=pp_services[2][1])
    for n, ip in pp_servers:
        add_object(dc_pp, models.ObjectType.server, n, ip=ip)
    for n, ip, s in pp_network:
        add_object(dc_pp, models.ObjectType.network, n, status=s, ip=ip)

    db.close()


if __name__ == "__main__":
    seed_core()
