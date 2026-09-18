# TeamDeck Backend

This repository contains the backend for TeamDeck, a project-based collaboration application.

## Project Structure

- `backend/app/` - FastAPI application code
- `backend/alembic/` - database migration files
- `docs/` - backend documentation and architecture notes
- `frontend/` - frontend application

## Backend Stack

- Python
- FastAPI
- SQLAlchemy
- PostgreSQL
- JWT-based authentication
- Pydantic validation

## Documentation

The project docs currently include:

- [docs/models.md](models.md)
- [docs/repositories.md](repositories.md)
- [docs/services.md](services.md)
- [docs/schemas.md](schemas.md)
- [docs/dependencies.md](dependencies.md)
- [docs/routers.md](routers.md)
- [docs/api.md](api.md)
- [docs/architecture.md](architecture.md)

## Backend Entry Point

The app starts in [backend/app/main.py](../backend/app/main.py).

## Notes

This repository is still evolving. The core API structure is in place, and the current docs reflect the implemented routes, services, repositories, models, and dependency layer as they exist today.
