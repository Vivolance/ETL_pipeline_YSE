import asyncio
from collections.abc import Sequence

import toml
from retry import retry
from sqlalchemy import CursorResult, Row, TextClause, text
from typing import Any

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from src.models.user import User
from src.utils.construct_connection_string import (
    construct_sqlalchemy_url_from_db_config,
)


class UserDAO:
    """
    Responsible for CRUD to yahoo_search_engine.users
    """

    def __init__(
        self,
        db_config: dict[str, Any] = toml.load("local_config/config.toml")["database"],
    ):
        self.__db_config: dict[str, Any] = db_config
        self._engine: AsyncEngine = create_async_engine(
            construct_sqlalchemy_url_from_db_config(self.__db_config, use_async_pg=True)
        )

    @retry(
        exceptions=SQLAlchemyError,
        tries=5,
        delay=0.01,
        jitter=(-0.01, 0.01),
        backoff=2,
    )
    async def insert_user(self, user: User) -> None:
        """
        TODO: Integration test this
        """
        async with self._engine.begin() as connection:
            insert_clause: TextClause = text(
                "INSERT into users("
                "   user_id, "
                "   created_at"
                ") values ("
                "   :user_id,"
                "   :created_at"
                ")"
            )
            # use named-params here to prevent SQL-injection attacks
            await connection.execute(
                insert_clause, {"user_id": user.user_id, "created_at": user.created_at}
            )

    @retry(
        exceptions=SQLAlchemyError,
        tries=5,
        delay=0.01,
        jitter=(-0.01, 0.01),
        backoff=2,
    )
    async def fetch_all_users(self) -> list[User]:
        """
        Integration Test
        """
        async with self._engine.begin() as connection:
            text_clause: TextClause = text("SELECT user_id, created_at " "FROM users")
            cursor: CursorResult = await connection.execute(text_clause)
            results: Sequence[Row] = cursor.fetchall()
            results_row: list[User] = [
                User.parse_obj(
                    {
                        "user_id": curr_row[0],
                        "created_at": curr_row[1],
                    }
                )
                for curr_row in results
            ]
        return results_row


if __name__ == "__main__":
    dao: UserDAO = UserDAO()
    sample_user: User = User.create_user()
    event_loop = asyncio.new_event_loop()
    """
    each line here runs asynchronously
    We know it does, as run_until_complete is not awaited, and no Future is returned
    a Future object represents a computation that promises to be completed in the future
    """
    event_loop.run_until_complete(dao.insert_user(sample_user))
    users: list[User] = event_loop.run_until_complete(dao.fetch_all_users())
    print(f"fetch_all_searches: {users}")
