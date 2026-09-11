"""One strict JSON filing, optionally inside one explicit JSON code block."""
import re

from .contracts import require, strict_json


def parsed_json(text):
    text = text.strip()
    if text.startswith('{'):
        return strict_json(text.encode())
    blocks = re.findall(r'(?:^|\n)```json[ \t]*\r?\n(.*?)\r?\n```(?=\s|$)', text, re.DOTALL)
    require(len(blocks) == 1 and text.count('```') == 2, 'exactly one JSON filing required')
    return strict_json(blocks[0].encode())


class CompletedFailure(ValueError):
    """Normal provider completion and quiescence, but an unusable task result."""
