# spaCy Morphological Analyzer

**Trigger:** When statistical morphological analysis is needed, POS tagging, or morphological features extraction

**Description:** Leverages spaCy's Morphologizer for statistical morphological analysis. Provides POS tags, morphological features, and can be extended with custom suffix-first components.

## Capabilities

1. **POS Tagging** - Universal Dependencies POS tags
2. **Morphological Features** - Number, Tense, VerbForm, etc.
3. **Lemmatization** - Statistical lemmatizer
4. **Custom Pipeline Integration** - Add suffix-first analysis as preprocessing

## Implementation

### 1. Basic spaCy Analysis

```python
#!/usr/bin/env python3
"""
spaCy morphological analysis

Usage:
    python scripts/spacy_morph_analyze.py --text "The cats are running"
"""
import spacy
import json
import sys

def analyze_text(text, model='en_core_web_sm'):
    """
    Analyze text with spaCy

    Args:
        text: Input text
        model: spaCy model name

    Returns:
        List of token analyses
    """
    try:
        nlp = spacy.load(model)
    except OSError:
        print(f"Model {model} not found. Downloading...", file=sys.stderr)
        spacy.cli.download(model)
        nlp = spacy.load(model)

    doc = nlp(text)

    analyses = []
    for token in doc:
        analysis = {
            'text': token.text,
            'lemma': token.lemma_,
            'POS': token.pos_,
            'tag': token.tag_,
            'morph': str(token.morph),
            'morph_dict': token.morph.to_dict(),
            'dep': token.dep_,
            'shape': token.shape_,
            'is_alpha': token.is_alpha,
            'is_stop': token.is_stop
        }
        analyses.append(analysis)

    return analyses

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='spaCy morphological analysis')
    parser.add_argument('--text', required=True, help='Text to analyze')
    parser.add_argument('--model', default='en_core_web_sm', help='spaCy model')
    args = parser.parse_args()

    results = analyze_text(args.text, args.model)
    print(json.dumps(results, indent=2))
```

### 2. Custom Suffix-First Component

```python
#!/usr/bin/env python3
"""
spaCy custom component for suffix-first POS tagging

This component runs BEFORE spaCy's tagger and provides suffix-based POS hints
"""
import spacy
from spacy.language import Language
from spacy.tokens import Token
import json

# Register custom attribute for suffix-based POS
if not Token.has_extension('suffix_pos'):
    Token.set_extension('suffix_pos', default=None)
if not Token.has_extension('suffix'):
    Token.set_extension('suffix', default=None)

@Language.component('suffix_first_tagger')
def suffix_first_component(doc):
    """
    Custom component that identifies suffixes and sets POS hints

    Runs before tagger in pipeline
    """
    # Load suffix database (in production, cache this)
    try:
        with open('data/unified_suffixes.json', 'r') as f:
            suffix_db = json.load(f)
        suffixes = suffix_db.get('suffixes', {})
    except FileNotFoundError:
        suffixes = {}

    for token in doc:
        # Skip punctuation
        if not token.is_alpha:
            continue

        word = token.text.lower()

        # Try to identify suffix
        suffix_list = sorted(suffixes.keys(), key=len, reverse=True)
        for suffix in suffix_list:
            suffix_str = suffix.lstrip('-')
            if word.endswith(suffix_str) and len(word) > len(suffix_str):
                suffix_data = suffixes[suffix]
                token._.suffix = suffix
                token._.suffix_pos = suffix_data.get('POS')
                break

    return doc

# Usage example
if __name__ == '__main__':
    nlp = spacy.load('en_core_web_sm')

    # Add custom component BEFORE tagger
    if 'suffix_first_tagger' not in nlp.pipe_names:
        nlp.add_pipe('suffix_first_tagger', before='tagger')

    text = "The happiness and sadness of childhood are unforgettable"
    doc = nlp(text)

    for token in doc:
        print(f"{token.text:15} {token.pos_:6} {token._.suffix_pos:10} {token._.suffix}")
```

### 3. Extract Morphological Features

```python
#!/usr/bin/env python3
"""
Extract comprehensive morphological features using spaCy

Usage:
    python scripts/extract_spacy_features.py --word "running"
"""
import spacy
import json

def extract_features(word, context=None, model='en_core_web_sm'):
    """
    Extract morphological features for a word

    Args:
        word: Word to analyze
        context: Optional context sentence
        model: spaCy model

    Returns:
        Feature dict
    """
    nlp = spacy.load(model)

    # If no context, analyze word alone
    if not context:
        context = word

    doc = nlp(context)

    # Find the target word in doc
    target_token = None
    for token in doc:
        if token.text.lower() == word.lower():
            target_token = token
            break

    if not target_token:
        return {'error': f'Word "{word}" not found in context'}

    features = {
        'word': word,
        'lemma': target_token.lemma_,
        'POS': target_token.pos_,
        'tag': target_token.tag_,
        'morphological_features': target_token.morph.to_dict(),
        'dependency': target_token.dep_,
        'is_oov': target_token.is_oov,
        'source': 'spacy'
    }

    return features

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Extract spaCy morphological features')
    parser.add_argument('--word', required=True, help='Word to analyze')
    parser.add_argument('--context', help='Optional context sentence')
    parser.add_argument('--model', default='en_core_web_sm', help='spaCy model')
    args = parser.parse_args()

    result = extract_features(args.word, args.context, args.model)
    print(json.dumps(result, indent=2))
```

## Usage Examples

### Basic Analysis

```bash
python scripts/spacy_morph_analyze.py --text "The children are playing happily"
```

### Word-Level Features

```bash
python scripts/extract_spacy_features.py \
    --word "playing" \
    --context "The children are playing happily"
```

### With Custom Suffix Component

```python
import spacy

nlp = spacy.load('en_core_web_sm')
nlp.add_pipe('suffix_first_tagger', before='tagger')

text = "Happiness is achievable"
doc = nlp(text)

for token in doc:
    print(f"{token.text}: POS={token.pos_}, Suffix-POS={token._.suffix_pos}")
```

## Output Format

```json
{
  "text": "running",
  "lemma": "run",
  "POS": "VERB",
  "tag": "VBG",
  "morph": "Aspect=Prog|Tense=Pres|VerbForm=Part",
  "morph_dict": {
    "Aspect": "Prog",
    "Tense": "Pres",
    "VerbForm": "Part"
  },
  "dep": "ROOT",
  "is_oov": false,
  "source": "spacy"
}
```

## Integration

- Used by **morph-router** for statistical analysis
- Provides baseline POS tags for **property-extractor**
- Can be enhanced with **suffix-first-tagger** component

## Notes

- Requires spaCy model download: `python -m spacy download en_core_web_sm`
- Statistical models may struggle with OOV words (where suffix analysis helps)
- Morphological features follow Universal Dependencies standard

---

**Scripts:** `/Users/preston/.claude/plugins/morphological-analysis-infrastructure/scripts/`
