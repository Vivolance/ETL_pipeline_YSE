from datetime import datetime
from uuid import UUID

import pytest
from sqlalchemy import TextClause, text

from integration_tests.conftest import integration_test_db_config
from src.models.extracted_search_results import ExtractedSearchResult
from src.models.user import User
from src.service.dao import extracted_search_dao
from src.service.dao.extracted_search_dao import ExtractedSearchResultDAO

"""
Steps to create integration test for insert_search method
Pre: Create a new database used for integration testing
1) Prepare the state for testing by cleaning up the table in the db
2) Act -> Executing the main function to run the code
3) Assert -> Asserts that the insert works by reading from the table
4) Clean up
"""


dummy_uuid: UUID = UUID("12345678123456781234567812345678")

extracted_search_dao: ExtractedSearchResultDAO = ExtractedSearchResultDAO(integration_test_db_config())


class TestExtractedSearchResultDAO:

    async def clear_users_table(self) -> None:
        """
        Runs at the start of every integration test
        - Truncate users table
        """
        truncate_clause: TextClause = text("TRUNCATE TABLE users CASCADE")
        async with extracted_search_dao._engine.begin() as connection:
            await connection.execute(truncate_clause)

    async def clear_extracted_search_results_table(self) -> None:
        """
        Runs at the start of every integration test
        - Truncate users table
        """
        truncate_clause: TextClause = text("TRUNCATE TABLE extracted_search_results")
        async with extracted_search_dao._engine.begin() as connection:
            await connection.execute(truncate_clause)

    # @pytest.mark.asyncio_cooperative
    # async def test_insert_search(self) -> None:
    #     await self.clear_users_table()
    #     users: list[User] = [
    #         User(
    #             user_id=str(dummy_uuid),
    #             created_at=datetime(year=2024, month=5, day=14, hour=12),
    #         )
    #     ]
    #     for user in users:
    #         await extracted_search_dao.insert_search(user)
    #
    #     results_row: list[User] = await extracted_search_dao.fetch_all_users()
    #     assert results_row == users
    #     await self.clear_user_table()

    @pytest.mark.asyncio_cooperative
    async def test_insert_search(self) -> None:
        await self.clear_users_table()
        await self.clear_extracted_search_results_table()
        users: list[User] = [
            User(
                user_id=str(dummy_uuid),
                created_at=datetime(year=2024, month=5, day=14, hour=12),
            )
        ]
        for user in users:
            await extracted_search_dao.insert_user(user)

        extracted_search_results: list[ExtractedSearchResult] = [
            ExtractedSearchResult(
                id="dummy_id",
                user_id=str(dummy_uuid),
                url="dummy_url",
                date="2024-05-30",
                body="dummy results",
                created_at=datetime(year=2024, month=5, day=14, hour=12)
            )
        ]

        for extracted_search_result in extracted_search_results:
            await extracted_search_dao.insert_search(extracted_search_result)

        results_row: list[ExtractedSearchResult] = await extracted_search_dao.fetch_all_searches()
        assert results_row == extracted_search_results
        await self.clear_extracted_search_results_table()
        await self.clear_users_table()


