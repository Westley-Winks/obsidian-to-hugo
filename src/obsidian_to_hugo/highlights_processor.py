import re

def remove_highlights(text: str) -> str:
    """
    Remove all highlights imported from Kindle
    """
    highlights_regex = r"(## Highlights)"
    text_without_highlights = re.split(highlights_regex, text)[0]
    return text_without_highlights