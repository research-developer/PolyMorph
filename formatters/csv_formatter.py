"""
CSV output formatter
"""
import csv
from io import StringIO
from typing import Dict, List, Union, Any


def format_csv(
    data: Union[Dict, List],
    headers: bool = True
) -> str:
    """
    Format data as CSV

    Args:
        data: Data to format (dict or list)
        headers: Include CSV headers

    Returns:
        CSV string
    """
    # Convert single dict to list
    if isinstance(data, dict):
        data = [data]

    if not data:
        return ""

    # Flatten nested structures for CSV
    flattened_data = [flatten_dict(item) for item in data]

    # Get all possible fieldnames
    fieldnames = set()
    for item in flattened_data:
        fieldnames.update(item.keys())
    fieldnames = sorted(fieldnames)

    # Write CSV
    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=fieldnames)

    if headers:
        writer.writeheader()
    writer.writerows(flattened_data)

    return output.getvalue()


def flatten_dict(d: Dict[str, Any], parent_key: str = '', sep: str = '.') -> Dict[str, str]:
    """
    Flatten nested dictionary for CSV export

    Args:
        d: Dictionary to flatten
        parent_key: Parent key for recursion
        sep: Separator for nested keys

    Returns:
        Flattened dictionary
    """
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k

        if isinstance(v, dict) and not v.get('consensus', True):
            # Special handling for POS disagreement dict
            v = format_pos_for_csv(v)
            items.append((new_key, v))
        elif isinstance(v, dict):
            # Recursively flatten nested dict
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        elif isinstance(v, list):
            # Convert list to comma-separated string
            if v and isinstance(v[0], dict):
                # Skip complex nested structures
                items.append((new_key, f"[{len(v)} items]"))
            else:
                items.append((new_key, ', '.join(str(x) for x in v)))
        else:
            items.append((new_key, str(v) if v is not None else ''))

    return dict(items)


def format_pos_for_csv(pos_dict: Dict) -> str:
    """Format POS disagreement dict for CSV"""
    parts = []
    for source in ['suffix', 'spacy', 'wordnet']:
        if source in pos_dict:
            parts.append(f"{source}:{pos_dict[source]}")
    return '; '.join(parts)
