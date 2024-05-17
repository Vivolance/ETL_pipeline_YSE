from datetime import datetime

import pytest

from integration_tests.conftest import integration_test_db_config
from integration_tests.src.utils.clear_tables import ClearTables
from integration_tests.src.utils.engine import dummy_uuid, dummy_uuid_2
from integration_tests.src.utils.fetch import Fetch
from integration_tests.src.utils.insert import Insert
from src.models.search_results import SearchResults
from src.models.user import User
from src.service.dao.raw_search_dao import RawSearchResultDAO


RAW_SEARCH_DAO: RawSearchResultDAO = RawSearchResultDAO(integration_test_db_config())


class TestRawSearchResult:
    @pytest.mark.asyncio_cooperative
    async def test_insert_search(self) -> None:
        await ClearTables.clear_users_table()
        await ClearTables.clear_search_results_table()
        users: list[User] = [
            User(
                user_id=str(dummy_uuid),
                created_at=datetime(year=2024, month=5, day=14, hour=12),
            )
        ]
        for user in users:
            await Insert.insert_user(user)

        search_results: list[SearchResults] = [
            SearchResults(
                search_id="dummy id",
                user_id=str(dummy_uuid),
                search_term="dummy search term",
                result="dummy results",
                created_at=datetime(year=2024, month=5, day=14, hour=13),
            )
        ]

        for search_result in search_results:
            await RAW_SEARCH_DAO.insert_search(search_result)

        results_row: list[SearchResults] = (
            await Fetch.fetch_all_searches_from_search_results()
        )
        assert results_row == search_results
        await ClearTables.clear_search_results_table()
        await ClearTables.clear_users_table()

    @pytest.mark.asyncio_cooperative
    async def test_fetch_all_searches(self) -> None:
        await ClearTables.clear_users_table()
        await ClearTables.clear_search_results_table()
        users: list[User] = [
            User(
                user_id=str(dummy_uuid),
                created_at=datetime(year=2024, month=5, day=15, hour=15),
            )
        ]
        for user in users:
            await Insert.insert_user(user)

        search_results: list[SearchResults] = [
            SearchResults(
                search_id="dummy id",
                user_id=str(dummy_uuid),
                search_term="dummy search term",
                result="dummy results",
                created_at=datetime(year=2024, month=5, day=15, hour=16),
            )
        ]

        for search_result in search_results:
            await Insert.insert_search_search_results(search_result)

        results_row: list[SearchResults] = await RAW_SEARCH_DAO.fetch_all_searches()
        assert results_row == search_results
        await ClearTables.clear_search_results_table()
        await ClearTables.clear_users_table()

    @pytest.mark.asyncio_cooperative
    async def test_fetch_searches_for_user(self) -> None:
        """
        TODO: To be worked on. user_id is a primary key, how do we create multiple rows
        with similar useR_id but different searches for different time period?
        """
        await ClearTables.clear_users_table()
        await ClearTables.clear_search_results_table()
        users: list[User] = [
            User(
                user_id=str(dummy_uuid),
                created_at=datetime(year=2024, month=5, day=15, hour=15),
            ),
            User(
                user_id=str(dummy_uuid_2),
                created_at=datetime(year=2024, month=5, day=15, hour=15),
            ),
        ]
        for user in users:
            await Insert.insert_user(user)

        search_results: list[SearchResults] = [
            SearchResults(
                search_id="dummy id",
                user_id=str(dummy_uuid),
                search_term="dummy search term",
                result="dummy results",
                created_at=datetime(year=2024, month=5, day=15, hour=15),
            ),
            SearchResults(
                search_id="dummy id 2",
                user_id=str(dummy_uuid),
                search_term="dummy search term 2",
                result="dummy results 2",
                created_at=datetime(year=2024, month=5, day=15, hour=16),
            ),
            SearchResults(
                search_id="dummy id",
                user_id=str(dummy_uuid_2),
                search_term="dummy search term",
                result="dummy results",
                created_at=datetime(year=2024, month=5, day=15, hour=16),
            ),
        ]

        for search_result in search_results:
            await Insert.insert_search_search_results(search_result)

        results_row: list[SearchResults] = await RAW_SEARCH_DAO.fetch_searches_for_user(
            str(dummy_uuid_2), datetime(year=2024, month=5, day=15, hour=16)
        )
        assert results_row == search_results
        await ClearTables.clear_search_results_table()
        await ClearTables.clear_users_table()
