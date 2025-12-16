from pathlib import Path
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .auth import login_for_access_token, get_current_user, require_role
from .db import get_db
from .settings import settings

app = FastAPI(title="IT Docs")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/auth/login", response_model=schemas.Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    return await login_for_access_token(form_data, db)


@app.get("/api/auth/me", response_model=schemas.UserOut)
def current_user(user: models.User = Depends(get_current_user)):
    return user


@app.get("/api/companies", response_model=list[schemas.CompanyOut])
def list_companies(db: Session = Depends(get_db)):
    return crud.list_companies(db)


@app.get("/api/tree", response_model=schemas.TreeResponse)
def tree(db: Session = Depends(get_db)):
    return crud.get_tree(db)


@app.get("/api/objects/{object_id}", response_model=schemas.ObjectDetail)
def object_detail(object_id: int, db: Session = Depends(get_db)):
    detail = crud.get_object_detail(db, object_id)
    if not detail:
        raise HTTPException(status_code=404, detail="Object not found")
    return detail


@app.put("/api/pages/{page_id}", response_model=schemas.PageOut)
def update_page(
    page_id: int, payload: schemas.PageUpdate, user: models.User = Depends(require_role(models.Role.editor)), db: Session = Depends(get_db)
):
    page = crud.update_page(db, page_id, payload.content_md, user)
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")
    return page


@app.post("/api/objects/{object_id}/documents", response_model=schemas.DocumentOut)
def add_document(
    object_id: int,
    title: str = Form(...),
    kind: models.DocumentKind = Form(models.DocumentKind.link),
    url: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    user: models.User = Depends(require_role(models.Role.editor)),
    db: Session = Depends(get_db),
):
    path = None
    if kind == models.DocumentKind.file:
        if not file:
            raise HTTPException(status_code=400, detail="file is required")
        dest = settings.upload_dir / file.filename
        with dest.open("wb") as f:
            f.write(file.file.read())
        path = str(dest)
    doc = crud.create_document(db, object_id, title, kind, path, url)
    return doc


@app.get("/api/objects/{object_id}/documents", response_model=list[schemas.DocumentOut])
def list_docs(object_id: int, db: Session = Depends(get_db)):
    return crud.list_documents(db, object_id)


@app.get("/uploads/{path:path}")
def download_upload(path: str):
    file_path = settings.upload_dir / path
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path)


@app.get("/")
@app.get("/{full_path:path}")
def serve_spa(full_path: str):
    index_path = settings.static_dir / "index.html"
    if not index_path.exists():
        raise HTTPException(status_code=500, detail="Frontend missing")
    return FileResponse(index_path)


app.mount("/static", StaticFiles(directory=settings.static_dir), name="static")
