import asyncio
from collections.abc import Sequence

import toml
from retry import retry
from sqlalchemy import CursorResult, Row, TextClause, text
from typing import Any

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from src.models.search_results import SearchResults
from src.models.user import User
from src.service.dao.user_dao import UserDAO
from src.utils.construct_connection_string import (
    construct_sqlalchemy_url_from_db_config,
)


class RawSearchResultDAO:
    """
    Responsible for CRUD to yahoo_search_engine.search_results
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
    async def insert_search(self, result: SearchResults) -> None:
        """
        TODO: Integration test this
        - Retry unit test -> does it catch the SQLAlchemyError
        """
        async with self._engine.begin() as connection:
            insert_clause: TextClause = text(
                "INSERT into search_results("
                "   search_id, "
                "   user_id, "
                "   search_term, "
                "   result, "
                "   created_at"
                ") values ("
                "   :search_id,"
                "   :user_id,"
                "   :search_term,"
                "   :result,"
                "   :created_at"
                ")"
            )
            # use named-params here to prevent SQL-injection attacks
            await connection.execute(
                insert_clause,
                {
                    "search_id": result.search_id,
                    "user_id": result.user_id,
                    "search_term": result.search_term,
                    "result": result.result,
                    "created_at": result.created_at,
                },
            )

    @retry(
        exceptions=SQLAlchemyError,
        tries=5,
        delay=0.01,
        jitter=(-0.01, 0.01),
        backoff=2,
    )
    async def fetch_all_searches(self) -> list[SearchResults]:
        """
        Integration test this
        """
        async with self._engine.begin() as connection:
            text_clause: TextClause = text(
                "SELECT search_id, user_id, "
                "search_term, result, created_at "
                "FROM search_results"
            )
            cursor: CursorResult = await connection.execute(text_clause)
            results: Sequence[Row] = cursor.fetchall()
            results_row: list[SearchResults] = [
                SearchResults.parse_obj(
                    {
                        "search_id": curr_row[0],
                        "user_id": curr_row[1],
                        "search_term": curr_row[2],
                        "result": curr_row[3],
                        "created_at": curr_row[4],
                    }
                )
                for curr_row in results
            ]
        return results_row


if __name__ == "__main__":
    user_dao: UserDAO = UserDAO()
    search_dao: RawSearchResultDAO = RawSearchResultDAO()
    sample_user: User = User.create_user()
    sample_search_results: SearchResults = SearchResults.create(
        sample_user.user_id, "how to work at macdonalds", "Dummy Search Results"
    )
    event_loop = asyncio.new_event_loop()
    """
    each line here runs asynchronously
    We know it does, as run_until_complete is not awaited, and no Future is returned
    a Future object represents a computation that promises to be completed in the future
    """
    event_loop.run_until_complete(user_dao.insert_user(sample_user))
    event_loop.run_until_complete(search_dao.insert_search(sample_search_results))
    search_results: list[SearchResults] = event_loop.run_until_complete(
        search_dao.fetch_all_searches()
    )
    print(f"fetch_all_searches: {search_results}")
    users: list[User] = event_loop.run_until_complete(user_dao.fetch_all_users())
    print(f"fetch_all_searches: {users}")
