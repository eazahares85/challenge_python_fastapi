# 🚀 API RESTful con FastAPI, Pydantic v2 y SQLAlchemy 2.0

Una aplicación CRUD moderna desarrollada con las últimas tecnologías de Python.

## 📋 Características

- ✅ **FastAPI** - Framework web moderno y rápido
- ✅ **Pydantic v2** - Validación de datos de última generación
- ✅ **SQLAlchemy 2.0** - ORM moderno y potente
- ✅ **Python 3.12.2** - Versión más reciente de Python
- ✅ **CRUD completo** - Operaciones Create, Read, Update, Delete
- ✅ **Autenticación** - Hash de contraseñas con bcrypt
- ✅ **Documentación automática** - Swagger UI incluido

## 🛠️ Instalación

### 1. Clonar el repositorio
```bash
git clone <tu-repositorio>
cd challenge_python_fastapi
```

### 2. Crear entorno virtual
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate     # Windows
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Crear archivo .env
```bash
# Copiar el archivo de ejemplo
cp .env.example .env
# Editar con tus configuraciones
```

### 5. Ejecutar la aplicación
```bash
uvicorn app.main:app --reload
```

## 🌐 Endpoints disponibles

- **API Base:** http://127.0.0.1:8000
- **Documentación:** http://127.0.0.1:8000/docs
- **Health Check:** http://127.0.0.1:8000/health
- **Usuarios:** http://127.0.0.1:8000/api/v1/users
- **Items:** http://127.0.0.1:8000/api/v1/items

## 📊 Estructura del proyecto

```
app/
├── api/
│   └── endpoints/
│       ├── users.py      # Endpoints de usuarios
│       └── items.py      # Endpoints de items
├── core/
│   ├── config.py         # Configuración con Pydantic Settings v2
│   └── database.py       # Configuración de SQLAlchemy 2.0
├── crud/
│   ├── crud_user.py      # Operaciones CRUD de usuarios
│   └── crud_item.py      # Operaciones CRUD de items
├── models/
│   └── models.py         # Modelos de SQLAlchemy
├── schemas/
│   └── schemas.py         # Schemas de Pydantic v2
└── main.py               # Aplicación principal
```

## 🔧 Tecnologías utilizadas

- **Python 3.12.2**
- **FastAPI 0.115.6**
- **Pydantic 2.10.3**
- **SQLAlchemy 2.0.36**
- **Uvicorn 0.32.1**
- **Alembic 1.14.0**
- **Passlib 1.7.4** (bcrypt)

## 📝 Uso de la API

### Crear un usuario
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/users/" \
     -H "Content-Type: application/json" \
     -d '{"email": "usuario@ejemplo.com", "name": "Usuario", "password": "password123"}'
```

### Crear un item
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/items/" \
     -H "Content-Type: application/json" \
     -d '{"title": "Mi Item", "description": "Descripción del item", "price": 29.99}'
```

## 🧪 Testing

```bash
# Ejecutar tests
pytest

# Con coverage
pytest --cov=app
```

## 🚀 Despliegue

Para producción, usar un servidor ASGI como Gunicorn:

```bash
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```