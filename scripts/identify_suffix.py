#!/usr/bin/env python3
"""
Identify suffix in a given word using longest match heuristic
"""
import json
import sys
from pathlib import Path

# Global cache for suffix database (singleton pattern)
_SUFFIX_DB_CACHE = {}

def load_suffix_database(db_path='data/unified_suffixes.json'):
    """
    Load suffix database with caching (singleton pattern)

    Args:
        db_path: Path to suffix database

    Returns:
        Loaded database dict
    """
    # Resolve path relative to plugin directory
    plugin_dir = Path(__file__).parent.parent
    full_path = plugin_dir / db_path

    # Use string path as cache key
    cache_key = str(full_path)

    if cache_key not in _SUFFIX_DB_CACHE:
        try:
            with open(full_path, 'r') as f:
                _SUFFIX_DB_CACHE[cache_key] = json.load(f)
        except FileNotFoundError:
            _SUFFIX_DB_CACHE[cache_key] = None

    return _SUFFIX_DB_CACHE[cache_key]

def identify_suffix(word, db_path='data/unified_suffixes.json', min_stem_length=2):
    """
    Identify suffix in word using longest matching suffix from database

    Args:
        word: Input word
        db_path: Path to suffix database
        min_stem_length: Minimum stem length to consider (avoid over-segmentation)

    Returns:
        dict with suffix, stem, POS, confidence
    """
    # Preserve original word for output, normalize for matching
    original_word = word
    word_lower = word.lower()

    # Load suffix database (cached after first call)
    db = load_suffix_database(db_path)

    if db is None:
        # Return basic analysis without database
        return {
            'word': original_word,
            'suffix': None,
            'stem': original_word,
            'POS': None,
            'confidence': 0.0,
            'message': 'Suffix database not found - run data acquisition first'
        }

    suffixes = db.get('suffixes', {})

    # Try suffixes from longest to shortest
    suffix_list = sorted(suffixes.keys(), key=len, reverse=True)

    for suffix in suffix_list:
        suffix_str = suffix.lstrip('-')  # Remove leading dash for matching
        if word_lower.endswith(suffix_str) and len(word_lower) > len(suffix_str):
            stem = word_lower[:-len(suffix_str)]
            if len(stem) >= min_stem_length:
                suffix_data = suffixes[suffix]
                return {
                    'word': original_word,
                    'suffix': suffix,
                    'stem': stem,
                    'POS': suffix_data.get('POS'),
                    'base_POS': suffix_data.get('source_POS'),
                    'category': suffix_data.get('category', 'unknown'),
                    'confidence': 0.9 if suffix_data.get('frequency', 0) > 50 else 0.7,
                    'suffix_data': {
                        'meaning': suffix_data.get('meaning'),
                        'examples': suffix_data.get('examples', [])[:3]
                    }
                }

    return {
        'word': original_word,
        'suffix': None,
        'stem': original_word,
        'POS': None,
        'confidence': 0.0,
        'message': 'No suffix identified'
    }

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Identify suffix in word')
    parser.add_argument('--word', required=True, help='Word to analyze')
    parser.add_argument('--db', default='data/unified_suffixes.json', help='Suffix database')
    parser.add_argument('--min-stem', type=int, default=2, help='Minimum stem length')
    args = parser.parse_args()

    result = identify_suffix(args.word, args.db, args.min_stem)
    print(json.dumps(result, indent=2))
