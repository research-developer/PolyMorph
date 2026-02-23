# Morphological Analysis Infrastructure - Quick Start

## 1-Minute Setup

```bash
cd ~/.claude/plugins/morphological-analysis-infrastructure
./setup.sh
```

## Test It Works

```bash
# Test suffix identification (works immediately with built-in database)
python3 scripts/identify_suffix.py --word happiness

# Test WordNet
python3 scripts/extract_wordnet_features.py --word running

# Test spaCy
python3 scripts/extract_spacy_features.py --word running
```

## Common Use Cases

### "What suffix does this word have?"

```bash
python3 scripts/identify_suffix.py --word unbelievable
```

### "What is the lemma and POS of this word?"

```bash
python3 scripts/extract_wordnet_features.py --word cats
```

### "Analyze this word completely"

```bash
python3 scripts/extract_properties.py --word happiness
```

### "Find all words ending in -tion"

```bash
# First build the trie (one-time operation)
python3 scripts/build_reversed_trie.py \
    --wordlist /usr/share/dict/words \
    --output data/reversed_stems.trie

# Then query
python3 scripts/query_suffix_trie.py \
    --suffix "-tion" \
    --trie data/reversed_stems.trie
```

## Via Claude Code Skills

Once installed, you can use these directly in Claude Code:

```
User: "What is the morphological analysis of 'happiness'?"
Claude: [uses morph-router skill automatically]

User: "Find words ending in '-able'"
Claude: [uses trie-suffix-lookup skill]

User: "What POS tags can 'running' have?"
Claude: [uses property-extractor skill]
```

## Skills Available

- `/morph-router` - Main entry point (auto-routing)
- `/suffix-lexicon` - Suffix database queries
- `/trie-suffix-lookup` - Suffix-to-stem lookups
- `/property-extractor` - Multi-tool property aggregation
- `/spacy-morph` - Statistical analysis
- `/wordnet-morphy` - Lemmatization
- `/data-acquisition` - Download databases

## Data Files

The plugin works with a minimal built-in suffix database (15 common suffixes).

For full functionality, run data acquisition:

```bash
python3 scripts/acquire_data_interactive.py
```

This will:
1. Search for existing data files first (bandwidth-friendly)
2. Prompt before downloading anything
3. Download MorphoLex (~5 MB) and NIH suffix list (<1 MB)
4. Build comprehensive suffix database (100-200 suffixes)

## Troubleshooting

### "Module not found" errors

Install missing packages:
```bash
# spaCy
pip install spacy
python -m spacy download en_core_web_sm

# NLTK
pip install nltk
python -c "import nltk; nltk.download('wordnet')"

# marisa-trie
pip install marisa-trie
```

### "Suffix database not found"

Run setup to create minimal database:
```bash
./setup.sh
```

Or run full data acquisition:
```bash
python3 scripts/acquire_data_interactive.py
```

### "spaCy model not found"

```bash
python -m spacy download en_core_web_sm
```

## Next Steps

1. **Explore the README.md** - Full documentation
2. **Browse skills/** - See all available capabilities
3. **Check scripts/** - Python tools you can use directly
4. **Run data acquisition** - Get complete databases

## Quick Examples

### Example: Suffix identification

```bash
$ python3 scripts/identify_suffix.py --word happiness

{
  "word": "happiness",
  "suffix": "-ness",
  "stem": "happi",
  "POS": "noun",
  "base_POS": ["adjective"],
  "category": "derivational",
  "confidence": 0.9
}
```

### Example: WordNet analysis

```bash
$ python3 scripts/extract_wordnet_features.py --word cats

{
  "word": "cats",
  "POS": "noun",
  "lemma": "cat",
  "lemmas": {
    "noun": "cat"
  },
  "synsets": [
    {
      "name": "cat.n.01",
      "POS": "n",
      "definition": "feline mammal usually having thick soft fur",
      "examples": []
    }
  ]
}
```

### Example: spaCy features

```bash
$ python3 scripts/extract_spacy_features.py --word running --context "They are running"

{
  "word": "running",
  "lemma": "run",
  "POS": "VERB",
  "tag": "VBG",
  "morphological_features": {
    "Aspect": "Prog",
    "Tense": "Pres",
    "VerbForm": "Part"
  },
  "dependency": "ROOT"
}
```

---

**Ready to use!** Try the examples above or use the skills directly in Claude Code conversations.
