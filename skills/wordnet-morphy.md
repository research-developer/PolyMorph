# WordNet Morphological Analyzer

**Trigger:** When lemmatization is needed, or when analyzing inflectional morphology

**Description:** Uses NLTK's WordNet morphy algorithm for lemmatization and POS-aware morphological analysis. Particularly strong for inflectional suffixes.

## Capabilities

- **Lemmatization** - Find base form with POS hint
- **Inflectional Rules** - WordNet's morphological exception lists
- **Synset Analysis** - Word sense disambiguation
- **Multi-POS Lemmatization** - Try all POS categories

## WordNet Morphy Rules

### Noun Inflections
- `-s` → base (cats → cat)
- `-ses` → s (analyses → analysis)
- `-xes` → x (boxes → box)
- `-zes` → z (quizzes → quiz)
- `-ches` → ch (churches → church)
- `-shes` → sh (dishes → dish)
- `-men` → man (women → woman)
- `-ies` → y (cities → city)

### Verb Inflections
- `-s` → base (runs → run)
- `-ies` → y (flies → fly)
- `-es` → e (loves → love)
- `-es` → base (teaches → teach)
- `-ed` → base (walked → walk)
- `-ed` → e (loved → love)
- `-ing` → base (running → run)
- `-ing` → e (loving → love)

### Adjective Inflections
- `-er` → base (bigger → big)
- `-est` → base (biggest → big)

## Usage

```bash
# Basic lemmatization
python scripts/extract_wordnet_features.py --word "running"

# Multiple words
for word in cats running happiest; do
    python scripts/extract_wordnet_features.py --word "$word"
done | jq -s '.'
```

## Output Format

```json
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
      "definition": "feline mammal...",
      "examples": []
    }
  ],
  "source": "wordnet"
}
```

## Integration

- **property-extractor** uses this for lemmatization
- **morph-router** includes WordNet for noun/verb disambiguation
- Complements **suffix-lexicon** for inflectional analysis

## Limitations

- Only handles words in WordNet lexicon
- Derivational suffixes not covered (use suffix-lexicon)
- No frequency information
- English-focused (though OMW provides some multilingual support)

---

**Script:** `scripts/extract_wordnet_features.py`
**Status:** ✓ Fully implemented and tested
