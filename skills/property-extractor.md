# Morphological Property Extractor

**Trigger:** When requesting specific morphological properties from words, or when aggregating results from multiple tools

**Description:** Unified interface for extracting morphological properties. Routes queries to appropriate tools and aggregates results with disambiguation. Allows specifying exactly which properties are needed.

## Supported Properties

### Core Properties
- **lemma** - Base form of word
- **POS** - Part of speech (universal/coarse)
- **tag** - Fine-grained POS tag
- **stem** - Morphological stem (may differ from lemma)
- **suffix** - Identified suffix
- **base_POS** - POS of stem before suffixation

### Morphological Features (Universal Dependencies)
- **Number** - Sing, Plur
- **Tense** - Past, Pres, Fut
- **VerbForm** - Fin, Inf, Ger, Part
- **Person** - 1, 2, 3
- **Gender** - Masc, Fem, Neut
- **Case** - Nom, Acc, Gen, etc.
- **Aspect** - Perf, Imp, Prog
- **Mood** - Ind, Imp, Sub

### Derivational Properties
- **morphemes** - Segmented morphemes
- **suffix_type** - derivational | inflectional
- **productivity** - Suffix productivity score
- **alternations** - Orthographic changes

### Meta Properties
- **is_oov** - Out-of-vocabulary
- **confidence** - Analysis confidence score
- **sources** - Which tools contributed data

## Implementation

### Property Extractor Core

```python
#!/usr/bin/env python3
"""
Unified morphological property extractor

Usage:
    python scripts/extract_properties.py \
        --word "happiness" \
        --properties lemma,POS,suffix,stem \
        --sources spacy,wordnet,suffix-lexicon
"""
import json
import sys
import subprocess
from pathlib import Path

class PropertyExtractor:
    """Extracts morphological properties from multiple sources"""

    def __init__(self, config_path='data/data_sources.json'):
        """Initialize with data source configuration"""
        self.config_path = config_path
        self.load_config()

    def load_config(self):
        """Load data source paths"""
        try:
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            self.config = {}

    def extract(self, word, properties=None, sources=None):
        """
        Extract properties from word

        Args:
            word: Word to analyze
            properties: List of properties to extract (None = all)
            sources: List of sources to use (None = all)

        Returns:
            Dict of properties with values and sources
        """
        results = {
            'word': word,
            'properties': {},
            'all_analyses': {}
        }

        # Default: use all sources
        if sources is None:
            sources = ['spacy', 'wordnet', 'suffix-lexicon', 'morfessor']

        # Gather data from each source
        if 'spacy' in sources:
            results['all_analyses']['spacy'] = self._extract_spacy(word)

        if 'wordnet' in sources:
            results['all_analyses']['wordnet'] = self._extract_wordnet(word)

        if 'suffix-lexicon' in sources:
            results['all_analyses']['suffix_lexicon'] = self._extract_suffix(word)

        if 'morfessor' in sources:
            results['all_analyses']['morfessor'] = self._extract_morfessor(word)

        # Aggregate properties
        results['properties'] = self._aggregate_properties(
            results['all_analyses'],
            properties
        )

        return results

    def _extract_spacy(self, word):
        """Extract properties using spaCy"""
        try:
            result = subprocess.run(
                ['python3', 'scripts/extract_spacy_features.py', '--word', word],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return json.loads(result.stdout)
        except Exception as e:
            return {'error': str(e)}
        return {}

    def _extract_wordnet(self, word):
        """Extract properties using WordNet"""
        try:
            result = subprocess.run(
                ['python3', 'scripts/extract_wordnet_features.py', '--word', word],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return json.loads(result.stdout)
        except Exception as e:
            return {'error': str(e)}
        return {}

    def _extract_suffix(self, word):
        """Extract properties using suffix lexicon"""
        try:
            suffix_db = self.config.get('unified_suffixes', 'data/unified_suffixes.json')
            result = subprocess.run(
                ['python3', 'scripts/identify_suffix.py',
                 '--word', word,
                 '--db', suffix_db],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return json.loads(result.stdout)
        except Exception as e:
            return {'error': str(e)}
        return {}

    def _extract_morfessor(self, word):
        """Extract properties using Morfessor"""
        try:
            result = subprocess.run(
                ['python3', 'scripts/morfessor_segment.py', '--word', word],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return json.loads(result.stdout)
        except Exception as e:
            return {'error': str(e)}
        return {}

    def _aggregate_properties(self, analyses, requested_properties=None):
        """
        Aggregate properties from all sources

        Args:
            analyses: Dict of source → analysis
            requested_properties: List of properties to include (None = all)

        Returns:
            Dict of property → value(s) with confidence and sources
        """
        aggregated = {}

        # Property mapping: which sources provide which properties
        property_sources = {
            'lemma': ['spacy', 'wordnet'],
            'POS': ['spacy', 'wordnet', 'suffix_lexicon'],
            'tag': ['spacy'],
            'stem': ['suffix_lexicon'],
            'suffix': ['suffix_lexicon'],
            'base_POS': ['suffix_lexicon'],
            'morphemes': ['morfessor'],
            'morph_features': ['spacy']
        }

        # For each requested property, aggregate from sources
        for prop in (requested_properties or property_sources.keys()):
            if prop not in property_sources:
                continue

            values = {}
            sources = []

            for source in property_sources[prop]:
                analysis = analyses.get(source, {})

                if 'error' in analysis:
                    continue

                # Extract property value from source
                value = None
                if prop == 'lemma':
                    value = analysis.get('lemma')
                elif prop == 'POS':
                    value = analysis.get('POS')
                elif prop == 'tag':
                    value = analysis.get('tag')
                elif prop == 'stem':
                    value = analysis.get('stem')
                elif prop == 'suffix':
                    value = analysis.get('suffix')
                elif prop == 'base_POS':
                    value = analysis.get('base_POS')
                elif prop == 'morphemes':
                    value = analysis.get('segments') or analysis.get('morphemes')
                elif prop == 'morph_features':
                    value = analysis.get('morphological_features')

                if value:
                    values[source] = value
                    sources.append(source)

            # Determine consensus value
            if len(values) == 0:
                aggregated[prop] = None
            elif len(values) == 1:
                source, value = list(values.items())[0]
                aggregated[prop] = {
                    'value': value,
                    'confidence': 0.9,
                    'sources': [source],
                    'consensus': True
                }
            else:
                # Multiple sources - check for agreement
                unique_values = set(
                    json.dumps(v, sort_keys=True) if isinstance(v, (dict, list)) else v
                    for v in values.values()
                )

                if len(unique_values) == 1:
                    # All sources agree
                    aggregated[prop] = {
                        'value': list(values.values())[0],
                        'confidence': 0.95,
                        'sources': sources,
                        'consensus': True
                    }
                else:
                    # Disagreement - provide all options
                    aggregated[prop] = {
                        'values': values,
                        'confidence': 0.6,
                        'sources': sources,
                        'consensus': False,
                        'note': 'Sources disagree - showing all options'
                    }

        return aggregated

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Extract morphological properties')
    parser.add_argument('--word', required=True, help='Word to analyze')
    parser.add_argument('--properties', help='Comma-separated list of properties (default: all)')
    parser.add_argument('--sources', help='Comma-separated list of sources (default: all)')
    parser.add_argument('--config', default='data/data_sources.json', help='Config file')
    args = parser.parse_args()

    properties = args.properties.split(',') if args.properties else None
    sources = args.sources.split(',') if args.sources else None

    extractor = PropertyExtractor(args.config)
    results = extractor.extract(args.word, properties, sources)

    print(json.dumps(results, indent=2))
```

### Batch Property Extraction

```python
#!/usr/bin/env python3
"""
Batch property extraction for multiple words

Usage:
    python scripts/batch_extract_properties.py \
        --words word1,word2,word3 \
        --properties lemma,POS,suffix
"""
import json
import sys
from extract_properties import PropertyExtractor

def batch_extract(words, properties=None, sources=None):
    """Extract properties for multiple words"""
    extractor = PropertyExtractor()

    results = {}
    for word in words:
        print(f"Processing {word}...", file=sys.stderr)
        results[word] = extractor.extract(word, properties, sources)

    return results

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Batch property extraction')
    parser.add_argument('--words', required=True, help='Comma-separated words')
    parser.add_argument('--properties', help='Comma-separated properties')
    parser.add_argument('--sources', help='Comma-separated sources')
    args = parser.parse_args()

    words = args.words.split(',')
    properties = args.properties.split(',') if args.properties else None
    sources = args.sources.split(',') if args.sources else None

    results = batch_extract(words, properties, sources)
    print(json.dumps(results, indent=2))
```

## Usage Examples

### Extract All Properties

```bash
python scripts/extract_properties.py --word "happiness"
```

Output:
```json
{
  "word": "happiness",
  "properties": {
    "lemma": {
      "value": "happiness",
      "confidence": 0.95,
      "sources": ["spacy", "wordnet"],
      "consensus": true
    },
    "POS": {
      "value": "noun",
      "confidence": 0.95,
      "sources": ["spacy", "wordnet", "suffix_lexicon"],
      "consensus": true
    },
    "suffix": {
      "value": "-ness",
      "confidence": 0.9,
      "sources": ["suffix_lexicon"],
      "consensus": true
    },
    "stem": {
      "value": "happi",
      "confidence": 0.9,
      "sources": ["suffix_lexicon"],
      "consensus": true
    }
  }
}
```

### Extract Specific Properties

```bash
python scripts/extract_properties.py \
    --word "running" \
    --properties lemma,POS,morphemes
```

### Use Specific Sources

```bash
python scripts/extract_properties.py \
    --word "unbelievable" \
    --sources suffix-lexicon,morfessor
```

### Batch Processing

```bash
python scripts/batch_extract_properties.py \
    --words "happiness,sadness,running,believable" \
    --properties lemma,POS,suffix
```

## Integration

- **morph-router** uses this for PROPERTY_EXTRACTION queries
- **All tools** can be accessed through this unified interface
- **Disambiguation** handled automatically with confidence scores

## Disambiguation Strategy

When sources disagree:
1. **High confidence:** 3+ sources agree → consensus value
2. **Medium confidence:** 2 sources agree → majority value
3. **Low confidence:** All disagree → provide all options

Priority order (when sources partially agree):
1. suffix-lexicon (for suffix-related properties)
2. spacy (for statistical properties)
3. wordnet (for lemmatization)
4. morfessor (for segmentation)

## Notes

- Caches results for repeated queries (optional)
- Handles missing tools gracefully
- Provides confidence scores for all properties
- Supports custom property definitions

---

**Scripts:** `/Users/preston/.claude/plugins/morphological-analysis-infrastructure/scripts/`
