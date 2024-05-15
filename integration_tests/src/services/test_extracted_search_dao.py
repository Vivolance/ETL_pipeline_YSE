from datetime import datetime
from uuid import UUID

from collections.abc import Sequence

import pytest
import toml
from typing import Any

from sqlalchemy import CursorResult, Row, TextClause, text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from integration_tests.conftest import integration_test_db_config
from src.models.extracted_search_results import ExtractedSearchResult
from src.models.user import User
from src.service.dao.extracted_search_dao import ExtractedSearchResultDAO

from src.utils.construct_connection_string import (
    construct_sqlalchemy_url_from_db_config,
)


"""
Steps to create integration test for insert_search method
Pre: Create a new database used for integration testing
1) Prepare the state for testing by cleaning up the table in the db
2) Act -> Executing the main function to run the code
3) Assert -> Asserts that the insert works by reading from the table
4) Clean up
"""

"""
The constructor is to cache attributes that are used throughout the object

Im missing insert_user IT. 
Plan: Create a fetch_user method in the integration test folder. Clear user table
Act: Call the extracted_search_dao.insert_user method to insert dummy users into the user table
Asset: Use self.fetch_all_users to fetch the inserted rows and assert it
Clear user tables
"""


DUMMY_UUID: UUID = UUID("12345678123456781234567812345678")

EXTRACTED_SEARCH_DAO: ExtractedSearchResultDAO = ExtractedSearchResultDAO(
    integration_test_db_config()
)

DB_CONFIG: dict[str, Any] = toml.load("integration_tests/config.toml")["database"]

ENGINE: AsyncEngine = create_async_engine(
    construct_sqlalchemy_url_from_db_config(DB_CONFIG, use_async_pg=True)
)


class TestExtractedSearchResultDAO:
    async def fetch_users(self) -> list[User]:
        async with ENGINE.begin() as connection:
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

    async def insert_user(self, user: User) -> None:
        """
        TODO: Integration test this
        """
        async with ENGINE.begin() as connection:
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

    async def insert_search(self, result: ExtractedSearchResult) -> None:
        async with ENGINE.begin() as connection:
            insert_clause: TextClause = text(
                "INSERT into extracted_search_results("
                "   id, "
                "   user_id, "
                "   url, "
                "   date, "
                "   body, "
                "   created_at"
                ") values ("
                "   :id,"
                "   :user_id, "
                "   :url, "
                "   :date, "
                "   :body, "
                "   :created_at "
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
                    "created_at": result.created_at,
                },
            )

    async def fetch_all_searches(self) -> list[ExtractedSearchResult]:
        async with ENGINE.begin() as connection:
            text_clause: TextClause = text(
                "SELECT id, user_id, "
                "url, date, body, created_at "
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

    async def clear_users_table(self) -> None:
        """
        Runs at the start of every integration test
        - Truncate users table
        """
        truncate_clause: TextClause = text("TRUNCATE TABLE users CASCADE")
        async with ENGINE.begin() as connection:
            await connection.execute(truncate_clause)

    async def clear_extracted_search_results_table(self) -> None:
        """
        Runs at the start of every integration test
        - Truncate users table
        """
        truncate_clause: TextClause = text("TRUNCATE TABLE extracted_search_results")
        async with ENGINE.begin() as connection:
            await connection.execute(truncate_clause)

    @pytest.mark.asyncio_cooperative
    async def test_insert_users(self) -> None:
        await self.clear_users_table()
        users: list[User] = [
            User(
                user_id=str(DUMMY_UUID),
                created_at=datetime(year=2024, month=5, day=17, hour=17),
            )  # 0x123
        ]
        for user in users:
            await EXTRACTED_SEARCH_DAO.insert_user(user)
        results: list[User] = await self.fetch_users()
        assert results == users
        await self.clear_users_table()

    @pytest.mark.asyncio_cooperative
    async def test_insert_search(self) -> None:
        await self.clear_users_table()
        await self.clear_extracted_search_results_table()
        users: list[User] = [
            User(
                user_id=str(DUMMY_UUID),
                created_at=datetime(year=2024, month=5, day=14, hour=12),
            )
        ]
        for user in users:
            await self.insert_user(user)

        extracted_search_results: list[ExtractedSearchResult] = [
            ExtractedSearchResult(
                id="dummy id",
                user_id=str(DUMMY_UUID),
                url="dummy url",
                date="2024-05-30",
                body="dummy results",
                created_at=datetime(year=2024, month=5, day=14, hour=13),
            )
        ]

        for extracted_search_result in extracted_search_results:
            await EXTRACTED_SEARCH_DAO.insert_search(extracted_search_result)

        results_row: list[ExtractedSearchResult] = await self.fetch_all_searches()
        assert results_row == extracted_search_results
        await self.clear_extracted_search_results_table()
        await self.clear_users_table()

    @pytest.mark.asyncio_cooperative
    async def test_bulk_insert(self) -> None:
        """
        Test Plan:
        1) Prepare the table for IT (done by alembic, clear table)
        2) Act (execute the bulk_insert function call to insert rows into the table
        3) Assert that each row in the table is inserted correctly
        4) Clear the table
        """
        await self.clear_users_table()
        await self.clear_extracted_search_results_table()
        users: list[User] = [
            User(
                user_id=str(DUMMY_UUID),
                created_at=datetime(year=2024, month=5, day=15, hour=14),
            )
        ]

        for user in users:
            await self.insert_user(user)

        extracted_search_results: list[ExtractedSearchResult] = [
            ExtractedSearchResult(
                id="dummy id",
                user_id=str(DUMMY_UUID),
                url="dummy url",
                date="2024-05-30",
                body="dummy result",
                created_at=datetime(year=2024, month=5, day=14, hour=13),
            )
        ]

        for extracted_search_result in extracted_search_results:
            await EXTRACTED_SEARCH_DAO.insert_search(extracted_search_result)

        results_row: list[ExtractedSearchResult] = await self.fetch_all_searches()
        assert results_row == extracted_search_results
        await self.clear_extracted_search_results_table()
        await self.clear_users_table()

    @pytest.mark.asyncio_cooperative
    async def test_fetch_all_searches(self) -> None:
        await self.clear_users_table()
        await self.clear_extracted_search_results_table()
        users: list[User] = [
            User(
                user_id=str(DUMMY_UUID),
                created_at=datetime(year=2024, month=5, day=15, hour=15),
            )
        ]
        for user in users:
            await self.insert_user(user)

        extracted_search_results: list[ExtractedSearchResult] = [
            ExtractedSearchResult(
                id="dummy id",
                user_id=str(DUMMY_UUID),
                url="dummy url",
                date="2024-05-15",
                body="dummy results",
                created_at=datetime(year=2024, month=5, day=15, hour=16),
            )
        ]

        for extracted_search_result in extracted_search_results:
            await self.insert_search(extracted_search_result)

        results_row: list[ExtractedSearchResult] = (
            await EXTRACTED_SEARCH_DAO.fetch_all_searches()
        )
        assert results_row == extracted_search_results
        await self.clear_extracted_search_results_table()
        await self.clear_users_table()
