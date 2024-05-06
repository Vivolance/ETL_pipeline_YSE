import asyncio
from collections.abc import Sequence

import toml
from retry import retry
from sqlalchemy import CursorResult, Row, TextClause, text
from typing import Any

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from src.models.last_extracted_user_status import LastExtractedUserStatus
from src.models.user import User
from src.service.dao.user_dao import UserDAO
from src.utils.construct_connection_string import (
    construct_sqlalchemy_url_from_db_config,
)


class LastExtractedUserStatusDAO:
    """
    CRUD to yahoo_search_engine.last_extracted_user_status

    - Insert into table
    - Read the latest row for a given user
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
    async def insert_status(self, status: LastExtractedUserStatus) -> None:
        """
        TODO: Integration test this
        - Retry unit test -> does it catch the SQLAlchemyError
        """
        async with self._engine.begin() as connection:
            insert_clause: TextClause = text(
                "INSERT into last_extracted_user_status("
                "   id, "
                "   user_id, "
                "   last_run"
                ") values ("
                "   :id,"
                "   :user_id, "
                "   :last_run "
                ")"
            )
            # use named-params here to prevent SQL-injection attacks
            await connection.execute(
                insert_clause,
                {
                    "id": status.id,
                    "user_id": status.user_id,
                    "last_run": status.last_run,
                },
            )

    @retry(
        exceptions=SQLAlchemyError,
        tries=5,
        delay=0.01,
        jitter=(-0.01, 0.01),
        backoff=2,
    )
    async def fetch_latest_status(self, user_id: str) -> LastExtractedUserStatus | None:
        """
        Integration test this
        """
        async with self._engine.begin() as connection:
            text_clause: TextClause = text(
                "SELECT id, user_id, last_run "
                "FROM last_extracted_user_status "
                "WHERE user_id = :user_id "
                "ORDER BY last_run DESC "
                "LIMIT 1"
            )
            cursor: CursorResult = await connection.execute(
                text_clause, {"user_id": user_id}
            )
            results: Row | None = cursor.fetchone()

        results_row: LastExtractedUserStatus | None = (
            LastExtractedUserStatus.parse_obj(
                {
                    "id": results[0],
                    "user_id": results[1],
                    "last_run": results[2],
                }
            )
            if results
            else None
        )
        return results_row

    @retry(
        exceptions=SQLAlchemyError,
        tries=5,
        delay=0.01,
        jitter=(-0.01, 0.01),
        backoff=2,
    )
    async def fetch_all_status(self) -> list[LastExtractedUserStatus]:
        """
        Integration test this
        """
        async with self._engine.begin() as connection:
            text_clause: TextClause = text(
                "SELECT id, user_id, last_run " "FROM last_extracted_user_status"
            )
            cursor: CursorResult = await connection.execute(text_clause)
            results: Sequence[Row] = cursor.fetchall()
            results_row: list[LastExtractedUserStatus] = [
                LastExtractedUserStatus.parse_obj(
                    {
                        "id": curr_row[0],
                        "user_id": curr_row[1],
                        "last_run": curr_row[2],
                    }
                )
                for curr_row in results
            ]
        return results_row


if __name__ == "__main__":
    user_dao: UserDAO = UserDAO()
    last_extract_user_status_dao: LastExtractedUserStatusDAO = (
        LastExtractedUserStatusDAO()
    )
    sample_user: User = User.create_user()
    sample_last_extracted_user_status: LastExtractedUserStatus = (
        LastExtractedUserStatus.create_user_status(sample_user.user_id)
    )

    event_loop = asyncio.new_event_loop()
    """
    each line here runs asynchronously
    We know it does, as run_until_complete is not awaited, and no Future is returned
    a Future object represents a computation that promises to be completed in the future
    """
    event_loop.run_until_complete(user_dao.insert_user(sample_user))
    event_loop.run_until_complete(
        last_extract_user_status_dao.insert_status(sample_last_extracted_user_status)
    )
    fetched_statuses: list[LastExtractedUserStatus] = event_loop.run_until_complete(
        last_extract_user_status_dao.fetch_all_status()
    )
    print(f"fetched_statuses: {fetched_statuses}")
    latest_status: LastExtractedUserStatus | None = event_loop.run_until_complete(
        last_extract_user_status_dao.fetch_latest_status(sample_user.user_id)
    )
    users: list[User] = event_loop.run_until_complete(user_dao.fetch_all_users())
    print(f"users: {users}")
