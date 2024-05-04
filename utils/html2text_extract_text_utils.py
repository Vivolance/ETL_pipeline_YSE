import html2text

def html2text_extract_text(input_html: str) -> str:
    """
    Approach 2: Use html2text

    Extracts text from HTML, but preserves the structure of the html document as well
    - Result is unsatisfactory
    """
    h = html2text.HTML2Text()
    h.ignore_links = True
    text = h.handle(input_html)
    return text