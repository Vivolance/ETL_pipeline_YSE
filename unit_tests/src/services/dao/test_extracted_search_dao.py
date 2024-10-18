import unittest
from datetime import datetime
from unittest.mock import patch, AsyncMock
import pytest
import toml

from src.models.extracted_search_results import ExtractedSearchResult
from src.models.user import User

from src.service.dao.extracted_search_dao import ExtractedSearchResultDAO


# Mocking toml.load to provide a fake config
mock_db_config = {"database": {"user": "test", "password": "test", "host": "localhost", "port": 5432, "dbname": "test_db"}}

"""

Response model using union keywords

start up function load data to check for the connection before we receive the calls start up.

"Execute docker image"


product - !I services
1) ticketing customers to get before tickets are opened using the ai service that reads the statement in the ticket and scan through the solution to rovide to
the customer even ebfore tickets are opened. to group similar tickets issues

tech stack:
python
apache spark
SQL postgres, elastic search S3.
tensorflow pytorch
Service FastAPI kubernetes docker
Task distribution in demographic location


Singapore: 


"""

class TestExtractedSearchResultDAO(unittest.TestCase):

    @pytest.mark.asyncio_cooperative
    @patch("src.services.dao.extracted_search_dao.create_async_engine", new_callable=AsyncMock)
    @patch("toml.load", return_value={"database": {"user": "test", "password": "test", "host": "localhost", "port": 5432, "dbname": "test_db"}})
    async def test_insert_user_called_once(self, mock_toml_load, mock_create_async_engine):
        # Setup mock engine
        mock_engine = mock_create_async_engine.return_value
        mock_engine.begin.return_value.__aenter__.return_value = mock_engine

        # Replace DAO engine with mock
        dao = ExtractedSearchResultDAO()
        dao._engine = mock_engine

        user = User(user_id="dummy_id", created_at=datetime(2024, 5, 20))

        # Action
        await dao.insert_user(user)

        # Assertion
        mock_create_async_engine.assert_called_once()
        mock_engine.begin.assert_called_once()
        # This asserts the method on the actual mock, ensuring it was called
        mock_engine.execute.assert_called_once_with(
            unittest.mock.ANY,
            {"user_id": user.user_id, "created_at": user.created_at}
        )

    @pytest.mark.asyncio_cooperative
    @patch("src.services.dao.extracted_search_dao.create_async_engine", new_callable=AsyncMock)
    @patch("toml.load", return_value={
        "database": {"user": "test", "password": "test", "host": "localhost", "port": 5432, "dbname": "test_db"}})
    async def test_insert_search_called_once(self, mock_toml_load, mock_create_async_engine):
        # Mock engine setup
        mock_engine = mock_create_async_engine.return_value
        mock_engine.begin.return_value.__aenter__.return_value = mock_engine

        # Initialize DAO with the mock engine
        dao = ExtractedSearchResultDAO()
        dao._engine = mock_engine
        extracted_search_results = ExtractedSearchResult(
            id="dummy_id",
            user_id="dummy_user_id",
            url="dummy_url",
            date="2024-05-20",
            body="dummy_result",
            created_at=datetime(2024, 5, 19)
        )

        # Action
        await dao.insert_search(extracted_search_results)

        # Assertion
        mock_create_async_engine.assert_called_once()
        mock_engine.begin.assert_called_once()
        # This asserts the method on the actual mock, ensuring it was called
        mock_engine.execute.assert_called_once_with(
            unittest.mock.ANY,
            {
                "id": extracted_search_results.id,
                "user_id": extracted_search_results.user_id,
                "url": extracted_search_results.url,
                "date": extracted_search_results.date,
                "body": extracted_search_results.body,
                "created_at": extracted_search_results.created_at,
            }
        )


if __name__ == "__main__":
    unittest.main()
