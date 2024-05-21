import unittest
from datetime import datetime
from unittest.mock import patch, AsyncMock

from src.models.user import User
from src.service.dao.extracted_search_dao import ExtractedSearchResultDAO


class TestExtractedSearchResultDAO(unittest.TestCase):

    @patch.object(ExtractedSearchResultDAO, 'insert_user', new_callable=AsyncMock)
    async def test_insert_user_called_once(self, mock_insert_user):
        user = User(user_id="dummy_id", created_at=datetime(2024, 5, 20))
        dao = ExtractedSearchResultDAO()

        # Action
        await dao.insert_user(user)

        # Assertion
        mock_insert_user.assert_called_once_with(user)


if __name__ == "__main__":
    unittest.main()
