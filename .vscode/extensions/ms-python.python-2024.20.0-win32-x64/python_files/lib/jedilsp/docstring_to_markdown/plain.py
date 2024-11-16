from re import fullmatch
from ._utils import escape_markdown


def looks_like_plain_text(value: str) -> bool:
    """Check if given string has plain text following English syntax without need for escaping.

    Accepts:
    - words without numbers
    - full stop, bangs and question marks at the end of a word if followed by a space or end of string
    - commas, colons and semicolons if after a word and followed by a space
    - dashes between words (like in `e-mail`)
    - double and single quotes if proceeded with a space and followed by a word, or if proceeded by a word and followed by a space (or end of string); single quotes are also allowed in between two words
    - parentheses if opening preceded by space and closing followed by space or end

    Does not accept:
    - square brackets (used in markdown a lot)
    """
    if '_' in value:
        return False
    return fullmatch(r"((\w[\.!\?\)'\"](\s|$))|(\w[,:;]\s)|(\w[-']\w)|(\w\s['\"\(])|\w|\s)+", value) is not None


def plain_text_to_markdown(text: str) -> str:
    return escape_markdown(text)

__all__ = ['looks_like_plain_text', 'plain_text_to_markdown']
