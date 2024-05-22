from datetime import datetime
from uuid import UUID

import pytest

from src.models.extracted_text_group import ExtractedTextGroup
from src.service.extractors.bs4_extractor import BS4SearchResultExtractor
from src.models.extracted_search_results import ExtractedSearchResult

"""
High Level: We want to test the extract method on various HTML structures.
There are 3 things that the extract method does:
1) Recursively goes through the html to find the 3 identifiers we want -> link,
body, date.
2) Filter those result groups with >= 2 identifiers with its text present.
3) Converting from list[ExtractedTextGroup] to list[ExtractedSearchResult] ->
the data structure which we want to insert into our table
"""


@pytest.fixture
def extractor():
    return BS4SearchResultExtractor()


@pytest.mark.parametrize("html", "expected_search_results", [
    # Case 1: Multiple Search Results
    (
        """
        <div>
            <div>
                <a href="link1">Link 1</a>
                <span>Date 1</span>
                <p>Body 1</p>
            </div>
                <a href="link2">Link 2</a>
                <span>Date 2</span>
                <p>Body 2</p>
            </div>
        </div>
        """,
        [
            ExtractedSearchResult(
                id="dummy_id",
                user_id="dummy_user_id",
                url="link1",
                date="Date 1",
                body="Body 1",
                created_at=datetime(2024, 5, 21)
            ),
            ExtractedSearchResult(
                id="dummy_id",
                user_id="dummy_user_id",
                url="link2",
                date="Date 2",
                body="Body 2",
                created_at=datetime(2024, 5, 22)
            ),
        ]
    ),
    # Case 2: Multiple Search Results with some info_count < 2
    (
        """
        <div>
            <div>
                <a href="link1">Link 1</a>
            </div>
            <div>
                <span>Date 2</span>
            </div>
        </div>
        """,
        []
    ),
])
def test_extract(
        extractor,
        html,
        expected_search_results: list[ExtractedSearchResult]
) -> None:
    # Call the extract method with the given HTML content
    results = extractor.extract(html, "dummy_user_id")

    # Assertions to verify the results
    assert results == expected_search_results


if __name__ == "__main__":
    pytest.main()
