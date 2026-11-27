# Task Manager API

A FastAPI application for managing user-owned tasks. It uses asynchronous
SQLAlchemy sessions, SQLite by default, password hashing, and JWT bearer tokens.

## Requirements

- Python 3.14 or newer
- [uv](https://docs.astral.sh/uv/)

Run the following commands from the `app` directory:

```bash
uv sync
uv run fastapi dev main.py
```

The development server starts at `http://127.0.0.1:8000`. Interactive API
documentation is available at `http://127.0.0.1:8000/docs`. Database tables are
created on startup if they do not already exist.

## Configuration

Settings can be provided through environment variables or an `.env` file in
the working directory:

| Setting | Default | Description |
| --- | --- | --- |
| `DATABASE_URL` | `sqlite+aiosqlite:///./tasks.db` | Async SQLAlchemy database URL. The default file is relative to the working directory. |
| `SECRET_KEY` | Development value in the source | JWT signing key. Set a unique, secret value before deployment. |
| `ALGORITHM` | `HS256` | JWT signing algorithm. |
| `ACCESS_TOKEN_EXPIRES_MINUTES` | `30` | Access-token lifetime in minutes. |
| `SQL_ECHO` | `false` | Whether SQLAlchemy logs SQL statements. |

Generate a signing key with `uv run python -c "import secrets; print(secrets.token_hex(32))"`
and set it as `SECRET_KEY`. Keep the key and any `.env` file out of version
control. Changing the key invalidates existing tokens.

## API

Register with an email and password, then log in to receive a bearer token. In
`/docs`, use **Authorize** with the email as the username and the registered
password. Task routes require authentication.

| Method | Path | Description |
| --- | --- | --- |
| POST | `/api/v1/auth/register` | Register a user. |
| POST | `/api/v1/auth/login` | Obtain an access token using form-encoded credentials. |
| POST | `/api/v1/tasks/` | Create a task for the current user. |
| GET | `/api/v1/tasks/` | List the current user's tasks. |
| GET | `/api/v1/tasks/all` | List all tasks (admin only). |
| GET | `/api/v1/tasks/{task_id}` | Get a task (owner or admin). |
| PATCH | `/api/v1/tasks/{task_id}` | Update a task (owner or admin). |

## Sample tasks and pagination

Start the API and register a user first. From `app`, using the same
`DATABASE_URL` and working directory as the API, run:

```bash
uv run python -m scripts.seed_tasks user@example.com
```

Each run adds 25 tasks with descriptions for that user; it does not change or
remove existing tasks. After
authorizing in `/docs`, request:

```text
GET /api/v1/tasks/?page=1&size=10
GET /api/v1/tasks/?page=2&size=10
GET /api/v1/tasks/?page=3&size=10
```

Responses include `items`, `total`, `page`, `size`, and `pages`. Pagination
defaults to page 1 with 10 items per page; `size` can be between 1 and 100. A
new user with only the seeded tasks will see 10, 10, and 5 items on those pages.

## Tests

Run the test suite from `app`:

```bash
uv run python -m unittest discover -s tests -v
```

The application tests use an in-memory SQLite database.
