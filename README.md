# IT Docs

Приложение FastAPI + статический фронтенд по шаблону.

## Установка
```bash
apt update && apt install -y python3 python3-venv python3-pip
python3 -m venv /opt/itdocs/venv
/opt/itdocs/venv/bin/pip install -r requirements.txt
alembic upgrade head
/opt/itdocs/venv/bin/python -m app.seed
/opt/itdocs/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Полезное
- Логины: `admin/admin`, `editor/editor`, `viewer/viewer`
- Файлы загружаются в `data/uploads`
- SPA доступно на `/`, API под `/api/*`
