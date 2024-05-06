from dataclasses import dataclass, field
from enum import Enum

from bs4 import BeautifulSoup, Tag
import re

DATE_PATTERN: re.Pattern = re.compile(
    r"\b(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s\d{1,2},\s\d{4}\b"
)
LI_PATTERN: re.Pattern = re.compile(r"[0-9]+_li")
URL_PATTERN: re.Pattern = re.compile(
    r"\b(?:www\.)?[\w-]+\.(?:[\w-]+\.)?[a-zA-Z]{2,6}\b"
)


class TextClassification(str, Enum):
    url = "url"
    body = "body"
    date = "date"


@dataclass
class ExtractedText:
    parent_tags: list[str]
    text: str

    @property
    def is_search_result(self) -> bool:
        """
        Assume only search results have "[0-9]+_li" in them
        """
        for tag in self.parent_tags:
            if LI_PATTERN.match(tag):
                return True
        return False

    @property
    def identifier_tags(self) -> str:
        """
        Represents the identifier of the extractedpip3  text
        Text of the same identifier tags are of the same search result

        All tags before and including "[0-9]+_li" is part of the identifier tag
        :return: E.G "html-body-div-div-div-div-div-div-div-div-ul-1_li"
        """
        identifier_tags: list[str] = []
        for tag in self.parent_tags:
            identifier_tags.append(tag)
            if LI_PATTERN.match(tag):
                break
        return "-".join(identifier_tags)

    @property
    def is_date(self) -> bool:
        return DATE_PATTERN.search(self.text) is not None

    @property
    def is_url(self) -> bool:
        return URL_PATTERN.search(self.text) is not None or "› " in self.text

    @property
    def classification(self) -> TextClassification:
        if self.is_date:
            return TextClassification.date
        elif self.is_url:
            return TextClassification.url
        else:
            return TextClassification.body


@dataclass
class ExtractedTextGroup:
    identifier: str
    link: list[ExtractedText] = field(default_factory=list)
    body: list[ExtractedText] = field(default_factory=list)
    date: list[ExtractedText] = field(default_factory=list)

    @property
    def link_str(self) -> str:
        return " ".join([current_link.text for current_link in self.link])

    @property
    def body_str(self) -> str:
        return " ".join([current_link.text for current_link in self.body])

    @property
    def date_str(self) -> str:
        return " ".join([current_link.text for current_link in self.date])

    def __str__(self) -> str:
        return f"Identifier: {self.identifier}\n\nDate: {self.date_str}\n\nLink: {self.link_str}\n\nBody: {self.body_str}\n\n"


def bs4_recursive_extract_text(html_content: str) -> list[ExtractedTextGroup]:
    """
    Assume only search results have "[0-9]+_li"
    """
    extracted_text: list[ExtractedText] = _bs4_recursive_extract_text(html_content)
    current_identifier = ""
    current_group: ExtractedTextGroup | None = None
    all_groups: list[ExtractedTextGroup] = []
    for current_extracted_text in extracted_text:
        if not current_extracted_text.is_search_result:
            continue
        # Tags each extracted text to categorize it
        identifier: str = current_extracted_text.identifier_tags
        # if different from prev identifier, create new
        if current_identifier != identifier:
            if current_group is not None:
                all_groups.append(current_group)
            current_group = ExtractedTextGroup(identifier)
            current_identifier = identifier
        # categorizes the extracted text into different parts of the search result,
        # such as the date, URL, or body text.
        if (
            current_extracted_text.classification == TextClassification.date
            and current_group
            and len(current_group.date) == 0
        ):
            # append to appropriate list within the ExtractedTextGroup
            current_group.date.append(current_extracted_text)
        elif (
            current_group
            and current_extracted_text.classification == TextClassification.url
        ):
            current_group.link.append(current_extracted_text)
        elif current_group:
            current_group.body.append(current_extracted_text)
    # appends the last group
    if current_group is not None:
        all_groups.append(current_group)
    return all_groups


def _bs4_recursive_extract_text(html_content: str) -> list[ExtractedText]:
    """
    Approach 3: Use BS4 with recursion

    Gives the feature of the parent HTMl tags a given str belongs to
    """
    soup = BeautifulSoup(html_content, "html.parser")

    # This function will recursively walk through the soup tree
    def recurse_through_soup(
        soup_element: BeautifulSoup | Tag,
    ) -> list[ExtractedText]:
        texts: list[ExtractedText] = []
        for index, element in enumerate(soup_element.children):
            if isinstance(
                element, str
            ):  # If the element is a NavigableString, capture it
                text: str = element.strip()
                if text:  # Avoid capturing empty or whitespace-only strings
                    texts.append(ExtractedText(parent_tags=["str"], text=text))
            else:  # You can add more tags as needed
                # Recursively process each element and join its texts with a newline
                parent_tag: str = (
                    f"{index}_{element.name}"  # type: ignore[attr-defined]
                    if soup_element.name == "ul" or soup_element.name == "ol"
                    else element.name  # type: ignore[attr-defined]
                )
                # we are sure that the element here is always a Tag, and will have the .children attribute
                # so, we tell mypy to ignore this error
                sub_texts: list[ExtractedText] = recurse_through_soup(element)  # type: ignore[arg-type]
                for sub_text in sub_texts:
                    sub_text.parent_tags.append(parent_tag)
                if sub_texts:
                    texts.extend(sub_texts)
        return texts

    extracted_texts: list[ExtractedText] = recurse_through_soup(soup)
    for extracted_text in extracted_texts:
        extracted_text.parent_tags = list(reversed(extracted_text.parent_tags))

    return extracted_texts
