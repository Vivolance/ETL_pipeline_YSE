from dataclasses import dataclass
import re

from src.models.text_classification_enum import TextClassification

DATE_PATTERN: re.Pattern = re.compile(
    r"\b(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s\d{1,2},\s\d{4}\b"
)
LI_PATTERN: re.Pattern = re.compile(r"[0-9]+_li")
URL_PATTERN: re.Pattern = re.compile(
    r"\b(?:www\.)?[\w-]+\.(?:[\w-]+\.)?[a-zA-Z]{2,6}\b"
)


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
