import asyncio
from collections.abc import Sequence

import toml
from retry import retry
from sqlalchemy import CursorResult, Row, TextClause, text
from typing import Any

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from src.models.extracted_search_results import ExtractedSearchResult
from src.models.user import User
from src.service.dao.user_dao import UserDAO
from src.utils.construct_connection_string import (
    construct_sqlalchemy_url_from_db_config,
)


class ExtractedSearchResultDAO:
    """
    Responsible for CRUD to yahoo_search_engine.extracted_search_results

    CSV COPY a dataframe into postgres
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
    async def insert_search(self, result: ExtractedSearchResult) -> None:
        """
        TODO: Integration test this
        - Retry unit test -> does it catch the SQLAlchemyError
        """
        async with self._engine.begin() as connection:
            insert_clause: TextClause = text(
                "INSERT into extracted_search_result("
                "   id, "
                "   user_id, "
                "   url, "
                "   date, "
                "   body, "
                "   created_date"
                ") values ("
                "   :id,"
                "   :user_id, "
                "   :url, "
                "   :date, "
                "   :body, "
                "   :created_date "
                ")"
            )
            # use named-params here to prevent SQL-injection attacks
            await connection.execute(
                insert_clause,
                {
                    "id": result.id,
                    "user_id": result.user_id,
                    "url": result.url,
                    "date": result.date,
                    "body": result.body,
                    "created_date": result.created_date,
                },
            )

    @retry(
        exceptions=SQLAlchemyError,
        tries=5,
        delay=0.01,
        jitter=(-0.01, 0.01),
        backoff=2,
    )
    async def bulk_insert(self, results: list[ExtractedSearchResult]) -> None:
        """
        CSV copy into a temporary table
        Then, insert from temporary table into yahoo_search_engine.extracted_search_results

        TODO: Integration test this
        - Retry unit test -> does it catch the SQLAlchemyError
        """
        async with self._engine.begin() as connection:
            insert_clause: TextClause = text(
                "INSERT into extracted_search_result("
                "   id, "
                "   user_id, "
                "   url, "
                "   date, "
                "   body, "
                "   created_date"
                ") values ("
                "   :id,"
                "   :user_id, "
                "   :url, "
                "   :date, "
                "   :body, "
                "   :created_date "
                ")"
            )
            insert_params = [
                {
                    "id": result.id,
                    "user_id": result.user_id,
                    "url": result.url,
                    "date": result.date,
                    "body": result.body,
                    "created_date": result.created_date,
                }
                for result in results
            ]

            # use named-params here to prevent SQL-injection attacks
            await connection.execute(insert_clause, insert_params)

    @retry(
        exceptions=SQLAlchemyError,
        tries=5,
        delay=0.01,
        jitter=(-0.01, 0.01),
        backoff=2,
    )
    async def fetch_all_searches(self) -> list[ExtractedSearchResult]:
        """
        Integration test this
        """
        async with self._engine.begin() as connection:
            text_clause: TextClause = text(
                "SELECT id, user_id, "
                "url, date, body, created_date"
                "FROM extracted_search_results"
            )
            cursor: CursorResult = await connection.execute(text_clause)
            results: Sequence[Row] = cursor.fetchall()
            results_row: list[ExtractedSearchResult] = [
                ExtractedSearchResult.parse_obj(
                    {
                        "id": curr_row[0],
                        "user_id": curr_row[1],
                        "url": curr_row[2],
                        "date": curr_row[3],
                        "body": curr_row[4],
                        "created_at": curr_row[5],
                    }
                )
                for curr_row in results
            ]
        return results_row


if __name__ == "__main__":
    user_dao: UserDAO = UserDAO()
    search_dao: ExtractedSearchResultDAO = ExtractedSearchResultDAO()
    sample_user: User = User.create_user()
    sample_search_results: ExtractedSearchResult = ExtractedSearchResult.create()

    event_loop = asyncio.new_event_loop()
    """
    each line here runs asynchronously
    We know it does, as run_until_complete is not awaited, and no Future is returned
    a Future object represents a computation that promises to be completed in the future
    """
    event_loop.run_until_complete(user_dao.insert_user(sample_user))
    event_loop.run_until_complete(search_dao.insert_search(sample_search_results))
    search_results: list[ExtractedSearchResult] = event_loop.run_until_complete(
        search_dao.fetch_all_searches()
    )
    print(f"fetch_all_searches: {search_results}")
    users: list[User] = event_loop.run_until_complete(user_dao.fetch_all_users())
    print(f"fetch_all_searches: {users}")
