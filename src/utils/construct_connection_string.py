import os
from typing import Any
from urllib.parse import quote


def construct_sqlalchemy_url_from_env_vars(use_async_pg: bool) -> str:
    user: str = os.getenv("DB_USER", "")
    password: str = os.getenv("DB_PASSWORD", "")
    host: str = os.getenv("DB_HOST", "")
    database: str = os.getenv("DB_DATABASE", "")
    port: str = os.getenv("DB_PORT", "")
    return _construct_sqlalchemy_url(
        user=user,
        password=password,
        host=host,
        database=database,
        port=port,
        use_async_pg=use_async_pg,
    )


def construct_sqlalchemy_url_from_db_config(
    db_config: dict[str, Any], use_async_pg: bool
) -> str:
    host: str = db_config.get("host", "")
    user: str = db_config.get("user", "")
    password: str = db_config.get("password", "")
    encoded_user: str = quote(user)
    encoded_password: str = quote(password)
    database: str = db_config.get("database", "")
    port: str = db_config["port"]
    return _construct_sqlalchemy_url(
        user=encoded_user,
        password=encoded_password,
        host=host,
        database=database,
        port=port,
        use_async_pg=use_async_pg,
    )


def _construct_sqlalchemy_url(
    user: str, password: str, host: str, database: str, port: str, use_async_pg: bool
) -> str:
    dialect_prefix: str = "postgresql+asyncpg" if use_async_pg else "postgresql"
    url: str = (
        f"{dialect_prefix}://{user}:{password}@{host}:{port}/{database}"
        if user and password
        else f"{dialect_prefix}://{host}:{port}/{database}"
    )
    return url
