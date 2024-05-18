from integration_tests.src.utils.engine import engine
from sqlalchemy import CursorResult, Row, TextClause, text

from collections.abc import Sequence

from src.models.extracted_search_results import ExtractedSearchResult
from src.models.last_extracted_user_status import LastExtractedUserStatus
from src.models.search_results import SearchResults
from src.models.user import User


class Fetch:
    @staticmethod
    async def fetch_all_searches_from_extracted_search_results() -> (
        list[ExtractedSearchResult]
    ):
        async with engine.begin() as connection:
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

    @staticmethod
    async def fetch_all_searches_from_search_results() -> list[SearchResults]:
        async with engine.begin() as connection:
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

    @staticmethod
    async def fetch_users() -> list[User]:
        async with engine.begin() as connection:
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

    @staticmethod
    async def fetch_all_status_from_last_extracted_user_status() -> (
        list[LastExtractedUserStatus]
    ):
        async with engine.begin() as connection:
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
