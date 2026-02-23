# Suffix Lexicon Manager

**Trigger:** When querying suffix→POS mappings, loading suffix databases, or identifying suffixes in words

**Description:** Manages and queries suffix lexicons from MorphoLex, NIH Lexical Tools, and custom databases. Provides suffix→POS mappings, productivity statistics, and suffix identification.

## Data Sources

1. **MorphoLex** - 68k English words with derivational morphology
   - Suffix family size and frequency
   - Empirical productivity data
   - GitHub: `hugomailhot/MorphoLex-en`

2. **NIH Lexical Tools** - Comprehensive derivational suffix list
   - ~100-200 derivational suffixes
   - Suffix→POS category mappings
   - Transformation rules

3. **WordNet Morphy** - Inflectional suffix rules
   - NOUN: -s, -ses, -xes, -zes, -ches, -shes, -men, -ies
   - VERB: -s, -ies, -es, -es, -ed, -ed, -ing, -ing
   - ADJ: -er, -est
   - ADV: (minimal)

## Core Functions

### 1. Load Suffix Databases

```bash
# Load from MorphoLex
python scripts/load_morpholex.py --output data/morpholex_suffixes.json

# Load from NIH Lexical Tools
python scripts/scrape_nih_suffixes.py --output data/nih_suffixes.json

# Merge databases
python scripts/merge_suffix_dbs.py \
  --input data/morpholex_suffixes.json data/nih_suffixes.json \
  --output data/unified_suffixes.json
```

### 2. Query Suffix Properties

```python
# Get suffix properties
python scripts/query_suffix.py --suffix "-ness"
# Returns:
# {
#   "suffix": "-ness",
#   "POS": "noun",
#   "source_POS": ["adjective"],
#   "productivity": 0.85,
#   "frequency": 450,
#   "examples": ["happiness", "sadness", "kindness"],
#   "alternations": ["-ity"],
#   "sources": ["MorphoLex", "NIH"]
# }
```

### 3. Identify Suffix in Word

```python
# Identify longest matching suffix
python scripts/identify_suffix.py --word "unbelievable"
# Returns:
# {
#   "word": "unbelievable",
#   "suffix": "-able",
#   "stem": "unbelieve",  # or "unbeliev" with -e deletion rule
#   "POS": "adjective",
#   "base_POS": "verb",
#   "confidence": 0.95
# }
```

### 4. Reverse Lookup (Suffix → Words)

```python
# Find all words with suffix (requires word list)
python scripts/suffix_reverse_lookup.py --suffix "-tion" --wordlist data/english_words.txt
# Returns list of words ending in -tion
```

## Suffix Database Schema

```json
{
  "suffixes": {
    "-ness": {
      "POS": "noun",
      "source_POS": ["adjective"],
      "category": "derivational",
      "meaning": "state, quality, or condition",
      "productivity": 0.85,
      "frequency": 450,
      "alternations": ["-ity"],
      "orthographic_rules": [
        {"pattern": "y$", "replacement": "i", "example": "happy → happiness"}
      ],
      "examples": ["happiness", "sadness", "kindness", "darkness"],
      "sources": ["MorphoLex", "NIH"]
    },
    "-able": {
      "POS": "adjective",
      "source_POS": ["verb", "noun"],
      "category": "derivational",
      "meaning": "capable of, able to, can do",
      "productivity": 0.90,
      "frequency": 380,
      "alternations": ["-ible"],
      "orthographic_rules": [
        {"pattern": "e$", "replacement": "", "example": "believe → believable"}
      ],
      "examples": ["believable", "readable", "doable"],
      "sources": ["MorphoLex", "NIH"]
    },
    "-s": {
      "POS": ["noun", "verb"],
      "source_POS": ["noun", "verb"],
      "category": "inflectional",
      "meaning": "plural (noun) or 3rd person singular (verb)",
      "productivity": 1.0,
      "frequency": 50000,
      "alternations": ["-es"],
      "orthographic_rules": [
        {"pattern": "y$", "replacement": "ies", "example": "city → cities"},
        {"pattern": "(s|x|z|ch|sh)$", "replacement": "es", "example": "box → boxes"}
      ],
      "examples": ["cats", "dogs", "runs", "eats"],
      "sources": ["WordNet"]
    }
  },
  "metadata": {
    "total_suffixes": 147,
    "derivational": 120,
    "inflectional": 27,
    "sources": ["MorphoLex", "NIH", "WordNet"],
    "updated": "2026-02-22"
  }
}
```

## Implementation Scripts

### Load MorphoLex (`scripts/load_morpholex.py`)

```python
#!/usr/bin/env python3
"""
Load suffix data from MorphoLex database
"""
import pandas as pd
import json
import sys
from collections import defaultdict

def load_morpholex(morpholex_path):
    """Load MorphoLex Excel file and extract suffix data"""
    df = pd.read_excel(morpholex_path)

    # Group by suffix
    suffix_data = defaultdict(lambda: {
        'POS': set(),
        'source_POS': set(),
        'examples': [],
        'frequency': 0,
        'family_size': 0
    })

    for _, row in df.iterrows():
        if pd.notna(row.get('MorphoLexSegm')):
            # Parse morphological segmentation
            segm = row['MorphoLexSegm']
            if '.' in segm:  # Has suffix
                parts = segm.split('.')
                if len(parts) >= 2:
                    suffix = parts[-1]
                    if suffix.startswith('-'):
                        pos = row.get('POS', 'unknown')
                        word = row.get('Word', '')

                        suffix_data[suffix]['POS'].add(pos)
                        suffix_data[suffix]['examples'].append(word)
                        suffix_data[suffix]['frequency'] += 1

    # Convert sets to lists for JSON serialization
    result = {}
    for suffix, data in suffix_data.items():
        result[suffix] = {
            'POS': list(data['POS'])[0] if len(data['POS']) == 1 else list(data['POS']),
            'source_POS': list(data['source_POS']),
            'category': 'derivational',
            'frequency': data['frequency'],
            'examples': data['examples'][:10],  # Top 10 examples
            'sources': ['MorphoLex']
        }

    return result

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Load MorphoLex suffix data')
    parser.add_argument('--input', required=True, help='Path to MorphoLex Excel file')
    parser.add_argument('--output', required=True, help='Output JSON file')
    args = parser.parse_args()

    suffixes = load_morpholex(args.input)
    with open(args.output, 'w') as f:
        json.dump(suffixes, f, indent=2)
    print(f"Loaded {len(suffixes)} suffixes from MorphoLex")
```

### Query Suffix (`scripts/query_suffix.py`)

```python
#!/usr/bin/env python3
"""
Query suffix properties from unified suffix database
"""
import json
import sys

def query_suffix(suffix, db_path='data/unified_suffixes.json'):
    """Query suffix properties"""
    with open(db_path, 'r') as f:
        db = json.load(f)

    # Normalize suffix (ensure it starts with -)
    if not suffix.startswith('-'):
        suffix = '-' + suffix

    suffix_data = db.get('suffixes', {}).get(suffix)

    if suffix_data:
        return suffix_data
    else:
        return {'error': f'Suffix {suffix} not found in database'}

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Query suffix properties')
    parser.add_argument('--suffix', required=True, help='Suffix to query (e.g., -ness)')
    parser.add_argument('--db', default='data/unified_suffixes.json', help='Suffix database path')
    args = parser.parse_args()

    result = query_suffix(args.suffix, args.db)
    print(json.dumps(result, indent=2))
```

### Identify Suffix in Word (`scripts/identify_suffix.py`)

```python
#!/usr/bin/env python3
"""
Identify suffix in a given word using longest match heuristic
"""
import json
import sys

def identify_suffix(word, db_path='data/unified_suffixes.json', min_stem_length=3):
    """
    Identify suffix in word using longest matching suffix from database

    Args:
        word: Input word
        db_path: Path to suffix database
        min_stem_length: Minimum stem length to consider (avoid over-segmentation)

    Returns:
        dict with suffix, stem, POS, confidence
    """
    with open(db_path, 'r') as f:
        db = json.load(f)

    suffixes = db.get('suffixes', {})

    # Try suffixes from longest to shortest
    suffix_list = sorted(suffixes.keys(), key=len, reverse=True)

    for suffix in suffix_list:
        suffix_str = suffix.lstrip('-')  # Remove leading dash for matching
        if word.endswith(suffix_str):
            stem = word[:-len(suffix_str)]
            if len(stem) >= min_stem_length:
                suffix_data = suffixes[suffix]
                return {
                    'word': word,
                    'suffix': suffix,
                    'stem': stem,
                    'POS': suffix_data.get('POS'),
                    'base_POS': suffix_data.get('source_POS'),
                    'confidence': 0.9 if suffix_data.get('frequency', 0) > 50 else 0.7,
                    'suffix_data': suffix_data
                }

    return {
        'word': word,
        'suffix': None,
        'stem': word,
        'POS': None,
        'confidence': 0.0,
        'message': 'No suffix identified'
    }

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Identify suffix in word')
    parser.add_argument('--word', required=True, help='Word to analyze')
    parser.add_argument('--db', default='data/unified_suffixes.json', help='Suffix database')
    parser.add_argument('--min-stem', type=int, default=3, help='Minimum stem length')
    args = parser.parse_args()

    result = identify_suffix(args.word, args.db, args.min_stem)
    print(json.dumps(result, indent=2))
```

## Usage Examples

### Example 1: Query suffix properties
```bash
python scripts/query_suffix.py --suffix "-ness"
```

### Example 2: Identify suffix in word
```bash
python scripts/identify_suffix.py --word "happiness"
```

### Example 3: Batch processing
```bash
# Process multiple words
cat wordlist.txt | while read word; do
  python scripts/identify_suffix.py --word "$word"
done > results.jsonl
```

## Integration with Other Skills

- **trie-suffix-lookup**: Uses suffix identification to query reversed trie
- **property-extractor**: Provides suffix-based POS hints
- **morph-router**: Primary source for suffix-first analysis

## Notes

- Handles orthographic alternations (y→i, e-deletion, etc.)
- Distinguishes derivational vs inflectional suffixes
- Provides productivity metrics for disambiguation
- Supports multiple POS assignments for ambiguous suffixes (-ing, -er)

---

**Location:** `/Users/preston/.claude/plugins/morphological-analysis-infrastructure/scripts/`
