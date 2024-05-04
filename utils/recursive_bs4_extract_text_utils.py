from dataclasses import dataclass
from bs4 import BeautifulSoup, Tag, NavigableString

@dataclass
class ExtractedText:
    parent_tags: list[str]
    text: str


def bs4_recursive_extract_text(html_content: str) -> list[ExtractedText]:
    """
    Approach 3: Use BS4 with recursion

    Gives the feature of the parent HTMl tags a given str belongs to
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    # This function will recursively walk through the soup tree
    def recurse_through_soup(soup_element: BeautifulSoup | Tag | NavigableString) -> list[ExtractedText]:
        texts: list[ExtractedText] = []
        for element in soup_element.children:
            if isinstance(element, str):  # If the element is a NavigableString, capture it
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
    return extracted_texts