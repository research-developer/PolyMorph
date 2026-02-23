"""
JSON output formatter
"""
import json
from typing import Any, Dict, List, Union


def format_json(
    data: Union[Dict, List],
    pretty: bool = True,
    compact: bool = False
) -> str:
    """
    Format data as JSON

    Args:
        data: Data to format (dict or list)
        pretty: Use pretty printing with indentation
        compact: Use compact format (no spaces)

    Returns:
        JSON string
    """
    if compact:
        return json.dumps(data, separators=(',', ':'))
    elif pretty:
        return json.dumps(data, indent=2)
    else:
        return json.dumps(data)
