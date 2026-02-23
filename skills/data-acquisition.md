# Morphological Data Acquisition

**Trigger:** When downloading or locating morphological databases (MorphoLex, NIH, CELEX, WordNet data)

**Description:** Searches for existing data files, prompts user for location, and downloads morphological databases as needed. Respects bandwidth restrictions by checking for existing data first.

## Data Sources

### 1. MorphoLex (Free, GitHub)
- **URL:** https://github.com/hugomailhot/MorphoLex-en
- **Size:** ~5 MB
- **Content:** 68k English words with morphological segmentation
- **Format:** Excel (.xlsx)

### 2. NIH Lexical Tools Suffix List (Free, Web)
- **URL:** https://lhncbc.nlm.nih.gov/LSG/Projects/lvg/current/docs/designDoc/UDF/derivations/suffixList.html
- **Size:** <1 MB
- **Content:** Derivational suffix rules and examples
- **Format:** HTML (requires scraping)

### 3. WordNet (Free, NLTK)
- **Source:** NLTK data
- **Size:** ~10 MB
- **Content:** Lexical database with lemmatizer
- **Format:** NLTK corpus

### 4. CELEX (Licensed, Not Free)
- **URL:** https://catalog.ldc.upenn.edu/LDC96L14
- **Size:** Variable
- **Content:** Comprehensive morphological database
- **Note:** Requires LDC license

### 5. English Word Lists
- **Source:** `/usr/share/dict/words` or online
- **Size:** 1-5 MB
- **Content:** Basic English vocabulary
- **Format:** Plain text

## Implementation

### Search for Existing Data

```bash
#!/bin/bash
# scripts/search_existing_data.sh
# Search for morphological databases on system

echo "Searching for existing morphological databases..."

# Search common locations
SEARCH_PATHS=(
    "$HOME/Downloads"
    "$HOME/Documents"
    "$HOME/data"
    "$HOME/research"
    "$HOME/nlp"
    "/usr/share/dict"
)

echo "Searching for MorphoLex..."
find "${SEARCH_PATHS[@]}" -type f -iname "*morpholex*" 2>/dev/null | head -5

echo "Searching for CELEX..."
find "${SEARCH_PATHS[@]}" -type d -iname "*celex*" 2>/dev/null | head -5

echo "Searching for word lists..."
find "${SEARCH_PATHS[@]}" -type f -name "words" -o -name "*.txt" 2>/dev/null | grep -i "word\|dict\|english" | head -10

echo "Checking NLTK data..."
python3 -c "import nltk; print('WordNet:', nltk.data.find('corpora/wordnet'))" 2>/dev/null || echo "WordNet not found"
```

### Download MorphoLex

```python
#!/usr/bin/env python3
"""
Download MorphoLex from GitHub

Usage:
    python scripts/download_morpholex.py --output data/
"""
import os
import sys
import requests
from pathlib import Path

def download_morpholex(output_dir):
    """
    Download MorphoLex Excel file from GitHub

    Args:
        output_dir: Directory to save file

    Returns:
        Path to downloaded file
    """
    url = "https://github.com/hugomailhot/MorphoLex-en/raw/master/MorphoLex_en.xlsx"

    output_path = Path(output_dir) / "MorphoLex_en.xlsx"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"Downloading MorphoLex from {url}...", file=sys.stderr)
    print(f"Saving to {output_path}", file=sys.stderr)

    response = requests.get(url, stream=True)
    response.raise_for_status()

    total_size = int(response.headers.get('content-length', 0))
    downloaded = 0

    with open(output_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
                downloaded += len(chunk)
                if total_size > 0:
                    percent = (downloaded / total_size) * 100
                    print(f"\rProgress: {percent:.1f}%", end='', file=sys.stderr)

    print(f"\nDownload complete: {output_path}", file=sys.stderr)
    return str(output_path)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Download MorphoLex database')
    parser.add_argument('--output', default='data/', help='Output directory')
    args = parser.parse_args()

    path = download_morpholex(args.output)
    print(path)
```

### Download NIH Suffix List

```python
#!/usr/bin/env python3
"""
Scrape NIH Lexical Tools suffix list

Usage:
    python scripts/download_nih_suffixes.py --output data/nih_suffixes.json
"""
import requests
from bs4 import BeautifulSoup
import json
import re
import sys

def scrape_nih_suffixes(output_path):
    """
    Scrape NIH suffix list from web page

    Args:
        output_path: Path to save JSON file

    Returns:
        Number of suffixes scraped
    """
    url = "https://lhncbc.nlm.nih.gov/LSG/Projects/lvg/current/docs/designDoc/UDF/derivations/suffixList.html"

    print(f"Fetching NIH suffix list from {url}...", file=sys.stderr)

    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')

    # Find suffix table
    # Table structure: Suffix | Category | Senses | Examples | Lexical Rules
    suffixes = {}

    # Parse table rows (this is a simplified parser - may need adjustment)
    tables = soup.find_all('table')

    for table in tables:
        rows = table.find_all('tr')
        for row in rows[1:]:  # Skip header
            cells = row.find_all('td')
            if len(cells) >= 4:
                suffix = cells[0].get_text(strip=True)
                category = cells[1].get_text(strip=True)
                senses = cells[2].get_text(strip=True)
                examples = cells[3].get_text(strip=True)

                if suffix and not suffix.startswith('Suffix'):
                    # Normalize suffix (ensure starts with -)
                    if not suffix.startswith('-'):
                        suffix = '-' + suffix

                    suffixes[suffix] = {
                        'POS': category.lower() if category else 'unknown',
                        'meaning': senses,
                        'examples': [ex.strip() for ex in examples.split(',') if ex.strip()],
                        'category': 'derivational',
                        'sources': ['NIH']
                    }

    # Save to JSON
    with open(output_path, 'w') as f:
        json.dump({'suffixes': suffixes}, f, indent=2)

    print(f"Scraped {len(suffixes)} suffixes", file=sys.stderr)
    print(f"Saved to {output_path}", file=sys.stderr)

    return len(suffixes)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Download NIH suffix list')
    parser.add_argument('--output', required=True, help='Output JSON file')
    args = parser.parse_args()

    count = scrape_nih_suffixes(args.output)
    print(count)
```

### Setup WordNet (NLTK)

```python
#!/usr/bin/env python3
"""
Download and setup WordNet data via NLTK

Usage:
    python scripts/setup_wordnet.py
"""
import nltk
import sys

def setup_wordnet():
    """Download WordNet data via NLTK"""
    print("Downloading WordNet data...", file=sys.stderr)

    try:
        nltk.data.find('corpora/wordnet')
        print("WordNet already downloaded", file=sys.stderr)
        return True
    except LookupError:
        print("Downloading WordNet...", file=sys.stderr)
        nltk.download('wordnet', quiet=False)
        nltk.download('omw-1.4', quiet=False)  # Open Multilingual WordNet
        print("WordNet download complete", file=sys.stderr)
        return True

if __name__ == '__main__':
    success = setup_wordnet()
    sys.exit(0 if success else 1)
```

### Interactive Data Acquisition

```python
#!/usr/bin/env python3
"""
Interactive data acquisition with user prompts

Usage:
    python scripts/acquire_data_interactive.py
"""
import os
import sys
from pathlib import Path
import subprocess

def prompt_for_existing_data(data_name, extensions):
    """
    Prompt user to provide path to existing data

    Args:
        data_name: Name of data source (e.g., "MorphoLex")
        extensions: List of file extensions to look for

    Returns:
        Path to data or None
    """
    print(f"\n=== {data_name} ===", file=sys.stderr)
    print("Searching for existing files...", file=sys.stderr)

    # Run search script
    result = subprocess.run(
        ['bash', 'scripts/search_existing_data.sh'],
        capture_output=True,
        text=True
    )

    print(result.stdout, file=sys.stderr)

    print(f"\nDo you have {data_name} already? (y/n): ", file=sys.stderr, end='')
    response = input().strip().lower()

    if response == 'y':
        print(f"Enter path to {data_name}: ", file=sys.stderr, end='')
        path = input().strip()
        if os.path.exists(path):
            return path
        else:
            print(f"Path not found: {path}", file=sys.stderr)
            return None
    return None

def acquire_morpholex():
    """Acquire MorphoLex data"""
    existing = prompt_for_existing_data("MorphoLex", ['.xlsx', '.xls'])

    if existing:
        return existing

    print("\nMorphoLex not found. Download now? (y/n): ", file=sys.stderr, end='')
    response = input().strip().lower()

    if response == 'y':
        print("Downloading MorphoLex...", file=sys.stderr)
        result = subprocess.run(
            ['python3', 'scripts/download_morpholex.py', '--output', 'data/'],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            print(f"Download failed: {result.stderr}", file=sys.stderr)
            return None
    return None

def acquire_nih_suffixes():
    """Acquire NIH suffix list"""
    existing = prompt_for_existing_data("NIH Suffix List", ['.json'])

    if existing:
        return existing

    print("\nDownload NIH suffix list? (y/n): ", file=sys.stderr, end='')
    response = input().strip().lower()

    if response == 'y':
        print("Downloading NIH suffix list...", file=sys.stderr)
        result = subprocess.run(
            ['python3', 'scripts/download_nih_suffixes.py', '--output', 'data/nih_suffixes.json'],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return 'data/nih_suffixes.json'
        else:
            print(f"Download failed: {result.stderr}", file=sys.stderr)
            return None
    return None

def acquire_all():
    """Interactive acquisition of all data sources"""
    data_paths = {}

    print("=== Morphological Data Acquisition ===\n", file=sys.stderr)

    # MorphoLex
    morpholex = acquire_morpholex()
    if morpholex:
        data_paths['morpholex'] = morpholex

    # NIH
    nih = acquire_nih_suffixes()
    if nih:
        data_paths['nih'] = nih

    # WordNet
    print("\nSetting up WordNet...", file=sys.stderr)
    subprocess.run(['python3', 'scripts/setup_wordnet.py'])

    # Save configuration
    import json
    config_path = 'data/data_sources.json'
    with open(config_path, 'w') as f:
        json.dump(data_paths, f, indent=2)

    print(f"\nData acquisition complete!", file=sys.stderr)
    print(f"Configuration saved to {config_path}", file=sys.stderr)

    return data_paths

if __name__ == '__main__':
    paths = acquire_all()
    print(json.dumps(paths, indent=2))
```

## Usage

### Quick Start

```bash
# Interactive acquisition (searches first, prompts before downloading)
python scripts/acquire_data_interactive.py
```

### Manual Downloads

```bash
# Download MorphoLex
python scripts/download_morpholex.py --output data/

# Download NIH suffix list
python scripts/download_nih_suffixes.py --output data/nih_suffixes.json

# Setup WordNet
python scripts/setup_wordnet.py
```

### Search Only

```bash
# Just search for existing data
bash scripts/search_existing_data.sh
```

## Output

After acquisition, data is organized as:

```
data/
├── MorphoLex_en.xlsx          # MorphoLex database
├── nih_suffixes.json          # NIH suffix rules
├── morpholex_suffixes.json    # Processed MorphoLex suffixes
├── unified_suffixes.json      # Merged suffix database
├── english_stems.txt          # Stem word list
├── reversed_stems.trie        # Reversed trie index
└── data_sources.json          # Configuration file
```

## Notes

- **Bandwidth-Friendly:** Searches for existing files first
- **Interactive:** Prompts before downloading
- **Configurable:** Saves paths to configuration file
- **Respects Licenses:** Only downloads freely available data

---

**Scripts:** `/Users/preston/.claude/plugins/morphological-analysis-infrastructure/scripts/`
