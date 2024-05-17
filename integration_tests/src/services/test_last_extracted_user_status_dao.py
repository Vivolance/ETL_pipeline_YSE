from datetime import datetime

import pytest

from integration_tests.conftest import integration_test_db_config
from integration_tests.src.utils.clear_tables import ClearTables
from integration_tests.src.utils.engine import dummy_uuid
from integration_tests.src.utils.fetch import Fetch
from integration_tests.src.utils.insert import Insert
from src.models.last_extracted_user_status import LastExtractedUserStatus
from src.models.user import User
from src.service.dao.last_extracted_user_status_dao import LastExtractedUserStatusDAO


LAST_EXTRACTED_USER_STATUS_DAO: LastExtractedUserStatusDAO = LastExtractedUserStatusDAO(
    integration_test_db_config()
)


class TestLastExtractedUserDAO:

    @pytest.mark.asyncio_cooperative
    async def test_insert_status(self) -> None:
        await ClearTables.clear_users_table()
        await ClearTables.clear_last_extracted_user_status()
        users: list[User] = [
            User(
                user_id=str(dummy_uuid),
                created_at=datetime(year=2024, month=5, day=14, hour=13),
            )
        ]
        for user in users:
            await Insert.insert_user(user)

        search_statuses: list[LastExtractedUserStatus] = [
            LastExtractedUserStatus(
                id="dummy id",
                user_id=str(dummy_uuid),
                last_run=datetime(year=2024, month=5, day=14, hour=13),
            )
        ]
        for search_status in search_statuses:
            await LAST_EXTRACTED_USER_STATUS_DAO.insert_status(search_status)

        results_row: list[LastExtractedUserStatus] = (
            await Fetch.fetch_all_status_from_last_extracted_user_status()
        )
        assert results_row == search_statuses
        await ClearTables.clear_last_extracted_user_status()
        await ClearTables.clear_users_table()

    @pytest.mark.asyncio_cooperative
    async def test_fetch_all_status(self) -> None:
        await ClearTables.clear_users_table()
        await ClearTables.clear_last_extracted_user_status()
        users: list[User] = [
            User(
                user_id=str(dummy_uuid),
                created_at=datetime(year=2024, month=5, day=14, hour=13),
            )
        ]
        for user in users:
            await Insert.insert_user(user)

        search_statuses: list[LastExtractedUserStatus] = [
            LastExtractedUserStatus(
                id="dummy id",
                user_id=str(dummy_uuid),
                last_run=datetime(year=2024, month=5, day=14, hour=13),
            )
        ]
        for search_status in search_statuses:
            await Insert.insert_status(search_status)

        results_row: list[LastExtractedUserStatus] = (
            await LAST_EXTRACTED_USER_STATUS_DAO.fetch_all_status()
        )
        assert results_row == search_statuses
        await ClearTables.clear_last_extracted_user_status()
        await ClearTables.clear_users_table()

    @pytest.mark.asyncio_cooperative
    async def test_fetch_latest_status(self) -> None:
        await ClearTables.clear_users_table()
        await ClearTables.clear_last_extracted_user_status()
        users: list[User] = [
            User(
                user_id=str(dummy_uuid),
                created_at=datetime(year=2024, month=5, day=14, hour=13),
            )
        ]
        for user in users:
            await Insert.insert_user(user)
