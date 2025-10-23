API RESTful Avanzada con FastAPI, Pydantic v2 y SQLAlchemy 2.0

Una aplicación CRUD

Soft Delete Implementation

`SoftDeleteMixin`:
- `is_deleted`: Boolean que indica si está eliminado
- `deleted_at`: Timestamp de eliminación
- `created_at` y `updated_at`: Timestamps automáticos
- Métodos: `soft_delete()`, `restore()`, `filter_active()`, `filter_deleted()`

Instalación

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

5. Ejecutar migraciones
```bash
# Crear migración inicial
alembic upgrade head

# O crear nuevas migraciones
alembic revision --autogenerate -m "Descripción"
alembic upgrade head
```

6. Ejecutar la aplicación
```bash
uvicorn app.main:app --reload
```

Endpoints Disponibles
Autenticación
- **POST** `/api/v1/auth/token` - Obtener token OAuth2
- **POST** `/api/v1/auth/register` - Registrar nuevo usuario

Usuarios
- **GET** `/api/v1/users/` - Lista de usuarios (requiere auth)
- **GET** `/api/v1/users/with-posts` - Usuarios con posts (requiere auth)
- **GET** `/api/v1/users/{user_id}` - Usuario específico (requiere auth)
- **POST** `/api/v1/users/` - Crear usuario (solo superusuarios)
- **PUT** `/api/v1/users/{user_id}` - Actualizar usuario (propio o superuser)
- **DELETE** `/api/v1/users/{user_id}` - Soft delete usuario (solo superuser)
- **POST** `/api/v1/users/{user_id}/restore` - Restaurar usuario (solo superuser)
- **GET** `/api/v1/users/deleted/list` - Usuarios eliminados (solo superuser)

Posts
- **GET** `/api/v1/posts/` - Lista de posts (requiere auth)
- **GET** `/api/v1/posts/with-relations` - Posts con relaciones (requiere auth)
- **GET** `/api/v1/posts/my-posts` - Posts del usuario actual (requiere auth)
- **GET** `/api/v1/posts/author/{author_id}` - Posts de un autor (requiere auth)
- **GET** `/api/v1/posts/{post_id}` - Post específico (requiere auth)
- **GET** `/api/v1/posts/{post_id}/with-relations` - Post con relaciones (requiere auth)
- **POST** `/api/v1/posts/` - Crear post (requiere auth)
- **PUT** `/api/v1/posts/{post_id}` - Actualizar post (autor o superuser)
- **DELETE** `/api/v1/posts/{post_id}` - Soft delete post (autor o superuser)
- **POST** `/api/v1/posts/{post_id}/restore` - Restaurar post (requiere auth)

Comentarios
- **GET** `/api/v1/comments/` - Lista de comentarios (requiere auth)
- **GET** `/api/v1/comments/post/{post_id}` - Comentarios de un post (requiere auth)
- **GET** `/api/v1/comments/my-comments` - Comentarios del usuario actual (requiere auth)
- **GET** `/api/v1/comments/{comment_id}` - Comentario específico (requiere auth)
- **GET** `/api/v1/comments/{comment_id}/with-relations` - Comentario con relaciones (requiere auth)
- **POST** `/api/v1/comments/` - Crear comentario (requiere auth)
- **PUT** `/api/v1/comments/{comment_id}` - Actualizar comentario (autor o superuser)
- **DELETE** `/api/v1/comments/{comment_id}` - Soft delete comentario (autor o superuser)
- **POST** `/api/v1/comments/{comment_id}/restore` - Restaurar comentario (requiere auth)

Tags
- **GET** `/api/v1/tags/` - Lista de tags (requiere auth)
- **GET** `/api/v1/tags/with-posts` - Tags con posts (requiere auth)
- **GET** `/api/v1/tags/{tag_id}` - Tag específico (requiere auth)
- **GET** `/api/v1/tags/{tag_id}/with-posts` - Tag con posts (requiere auth)
- **POST** `/api/v1/tags/` - Crear tag (solo superusuarios)
- **PUT** `/api/v1/tags/{tag_id}` - Actualizar tag (solo superusuarios)
- **DELETE** `/api/v1/tags/{tag_id}` - Soft delete tag (solo superusuarios)
- **POST** `/api/v1/tags/{tag_id}/restore` - Restaurar tag (solo superusuarios)
- **GET** `/api/v1/tags/deleted/list` - Tags eliminados (solo superusuarios)

