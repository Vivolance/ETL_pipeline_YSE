from dataclasses import dataclass
from bs4 import BeautifulSoup, Tag, NavigableString


@dataclass
class ExtractedText:
    parent_tags: list[str]
    text: str

    @property
    def parent_tags_length(self) -> int:
        return len(self.parent_tags)

    @property
    def parent_tags_str(self) -> str:
        return ",".join(reversed(self.parent_tags))


def bs4_recursive_extract_text(html_content: str) -> list[ExtractedText]:
    """
    Approach 3: Use BS4 with recursion

    Gives the feature of the parent HTMl tags a given str belongs to
    """
    soup = BeautifulSoup(html_content, "html.parser")

    # This function will recursively walk through the soup tree
    def recurse_through_soup(
        soup_element: BeautifulSoup | Tag | NavigableString,
    ) -> list[ExtractedText]:
        texts: list[ExtractedText] = []
        for element in soup_element.children:
            if isinstance(
                element, str
            ):  # If the element is a NavigableString, capture it
                text: str = element.strip()
                if text:  # Avoid capturing empty or whitespace-only strings
                    texts.append(ExtractedText(parent_tags=["str"], text=text))
            else:  # You can add more tags as needed
                # Recursively process each element and join its texts with a newline
                sub_texts: list[ExtractedText] = recurse_through_soup(element)
                for sub_text in sub_texts:
                    sub_text.parent_tags.append(element.name)
                if sub_texts:
                    texts.extend(sub_texts)
        return texts

    extracted_texts: list[ExtractedText] = recurse_through_soup(soup)
    # We sort the list of extracted text by
    # their reversed parent tags (cos child is at the front, parent at the back)
    # All the results with the same parent tag prefixes are together by sort order
    # we sort by parent tag length ascending; put the shorter parent tags first; the branching points first
    extracted_texts = sorted(
        extracted_texts,
        key=lambda x: (x.parent_tags_str, x.parent_tags_length),
        reverse=False,
    )
    return extracted_texts


def find_branching_point(
    extracted_texts: list[ExtractedText],
) -> list[tuple[list[str], int]]:
    """
    Finds the branching point in the extracted text sequences.
    """
    branching_points = []
    common_parent_tags = []

    # Find the common parent tags for each extracted text
    for extracted_text in extracted_texts:
        parent_tags = extracted_text.parent_tags
        for i, tag in enumerate(reversed(parent_tags)):
            if i >= len(common_parent_tags) or common_parent_tags[i] != tag:
                # Found a branching point
                branching_points.insert(
                    0, (common_parent_tags[-i:], len(common_parent_tags) - i)
                )
                common_parent_tags = parent_tags
                break
    else:
        # If the loop completes without breaking, the common parent tags are the same for all texts
        branching_points.insert(0, (common_parent_tags, len(common_parent_tags)))

    return branching_points
