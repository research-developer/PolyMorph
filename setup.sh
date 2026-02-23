#!/bin/bash
# Setup script for Morphological Analysis Infrastructure Plugin

set -e

PLUGIN_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$PLUGIN_DIR"

echo "=== Morphological Analysis Infrastructure Setup ==="
echo "Plugin directory: $PLUGIN_DIR"
echo

# Create data directory
mkdir -p data

# Check Python packages
echo "Checking Python packages..."
python3 -c "import spacy" 2>/dev/null && echo "✓ spaCy installed" || echo "✗ spaCy not found (will try to continue)"
python3 -c "import nltk" 2>/dev/null && echo "✓ NLTK installed" || echo "✗ NLTK not found"
python3 -c "import marisa_trie" 2>/dev/null && echo "✓ marisa-trie installed" || echo "✗ marisa-trie not found"
echo

# Check spaCy model
echo "Checking spaCy model..."
python3 -c "import spacy; spacy.load('en_core_web_sm')" 2>/dev/null && echo "✓ en_core_web_sm model found" || {
    echo "✗ spaCy model not found"
    read -p "Download en_core_web_sm model? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        python3 -m spacy download en_core_web_sm
    fi
}
echo

# Setup WordNet
echo "Checking WordNet..."
python3 -c "import nltk; nltk.data.find('corpora/wordnet')" 2>/dev/null && echo "✓ WordNet found" || {
    echo "✗ WordNet not found"
    echo "Downloading WordNet..."
    python3 scripts/setup_wordnet.py
}
echo

# Data acquisition
echo "=== Data Acquisition ==="
echo "This will search for existing data files before downloading."
echo "Bandwidth-friendly mode is enabled."
echo

read -p "Run interactive data acquisition? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python3 scripts/acquire_data_interactive.py
else
    echo "Skipping data acquisition. You can run it later with:"
    echo "  python3 scripts/acquire_data_interactive.py"
fi
echo

# Create minimal suffix database if none exists
if [ ! -f "data/unified_suffixes.json" ]; then
    echo "Creating minimal suffix database..."
    python3 -c '
import json

minimal_suffixes = {
    "suffixes": {
        "-ness": {"POS": "noun", "source_POS": ["adjective"], "category": "derivational", "meaning": "state or quality", "examples": ["happiness", "sadness"], "sources": ["builtin"]},
        "-able": {"POS": "adjective", "source_POS": ["verb"], "category": "derivational", "meaning": "capable of", "examples": ["readable", "doable"], "sources": ["builtin"]},
        "-tion": {"POS": "noun", "source_POS": ["verb"], "category": "derivational", "meaning": "act or process", "examples": ["creation", "action"], "sources": ["builtin"]},
        "-ing": {"POS": ["verb", "noun"], "source_POS": ["verb"], "category": "inflectional", "meaning": "present participle or gerund", "examples": ["running", "seeing"], "sources": ["builtin"]},
        "-ed": {"POS": "verb", "source_POS": ["verb"], "category": "inflectional", "meaning": "past tense", "examples": ["walked", "talked"], "sources": ["builtin"]},
        "-s": {"POS": ["noun", "verb"], "source_POS": ["noun", "verb"], "category": "inflectional", "meaning": "plural or 3rd person singular", "examples": ["cats", "runs"], "sources": ["builtin"]},
        "-ly": {"POS": "adverb", "source_POS": ["adjective"], "category": "derivational", "meaning": "in a manner", "examples": ["quickly", "slowly"], "sources": ["builtin"]},
        "-er": {"POS": ["noun", "adjective"], "source_POS": ["verb", "adjective"], "category": "derivational", "meaning": "one who does or comparative", "examples": ["teacher", "bigger"], "sources": ["builtin"]},
        "-est": {"POS": "adjective", "source_POS": ["adjective"], "category": "inflectional", "meaning": "superlative", "examples": ["biggest", "fastest"], "sources": ["builtin"]},
        "-ment": {"POS": "noun", "source_POS": ["verb"], "category": "derivational", "meaning": "result or means", "examples": ["government", "movement"], "sources": ["builtin"]},
        "-ity": {"POS": "noun", "source_POS": ["adjective"], "category": "derivational", "meaning": "state or quality", "examples": ["clarity", "simplicity"], "sources": ["builtin"]},
        "-less": {"POS": "adjective", "source_POS": ["noun"], "category": "derivational", "meaning": "without", "examples": ["hopeless", "careless"], "sources": ["builtin"]},
        "-ful": {"POS": "adjective", "source_POS": ["noun"], "category": "derivational", "meaning": "full of", "examples": ["hopeful", "careful"], "sources": ["builtin"]},
        "-ize": {"POS": "verb", "source_POS": ["adjective", "noun"], "category": "derivational", "meaning": "make or become", "examples": ["modernize", "realize"], "sources": ["builtin"]},
        "-ous": {"POS": "adjective", "source_POS": ["noun"], "category": "derivational", "meaning": "having quality of", "examples": ["dangerous", "famous"], "sources": ["builtin"]}
    },
    "metadata": {
        "total_suffixes": 15,
        "sources": ["builtin"],
        "note": "Minimal suffix database - run data acquisition for full database"
    }
}

with open("data/unified_suffixes.json", "w") as f:
    json.dump(minimal_suffixes, f, indent=2)

print("Created minimal suffix database with 15 common suffixes")
'
fi

echo
echo "=== Setup Complete ==="
echo
echo "Test the plugin with:"
echo "  python3 scripts/identify_suffix.py --word happiness"
echo "  python3 scripts/extract_properties.py --word running"
echo "  python3 scripts/extract_wordnet_features.py --word cats"
echo
echo "For full functionality, run data acquisition:"
echo "  python3 scripts/acquire_data_interactive.py"
echo
