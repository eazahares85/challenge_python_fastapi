API RESTful con FastAPI, Pydantic v2 y SQLAlchemy 2.0

Una aplicación CRUD 

1. Clonar el repositorio
```bash
git clone <tu-repositorio>
cd challenge_python_fastapi
```

2. Crear entorno virtual
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate     # Windows
```

3. Instalar dependencias
```bash
pip install -r requirements.txt
```

4. Crear archivo .env
```bash
# Copiar el archivo de ejemplo
cp .env.example .env
# Editar con tus configuraciones
```

5. Ejecutar la aplicación
```bash
uvicorn app.main:app --reload
```

- API Base: http://127.0.0.1:8000

