from .cpython import cpython_to_markdown
from .google import google_to_markdown, looks_like_google
from .plain import looks_like_plain_text, plain_text_to_markdown
from .rst import looks_like_rst, rst_to_markdown

__version__ = "0.15"


class UnknownFormatError(Exception):
    pass


def convert(docstring: str) -> str:
    if looks_like_rst(docstring):
        return rst_to_markdown(docstring)

    if looks_like_google(docstring):
        return google_to_markdown(docstring)

    if looks_like_plain_text(docstring):
        return plain_text_to_markdown(docstring)

    cpython = cpython_to_markdown(docstring)
    if cpython:
        return cpython

    raise UnknownFormatError()
