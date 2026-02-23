# Morfessor Morphological Segmentation

**Trigger:** When unsupervised morphological segmentation is needed, or for discovering novel morphemes

**Description:** Uses Morfessor for unsupervised morphological segmentation. Discovers morpheme boundaries without relying on predefined rules or dictionaries.

## Capabilities

- **Unsupervised Segmentation** - Learns morpheme boundaries from data
- **Novel Word Handling** - Works on out-of-vocabulary words
- **Multilingual** - Language-agnostic approach
- **Morpheme Discovery** - Identifies prefixes, roots, and suffixes

## How It Works

Morfessor uses a probabilistic model to segment words into morphemes by:
1. Analyzing letter sequences and their frequencies
2. Finding natural segmentation points
3. Balancing morpheme count vs morpheme length

## Usage

```bash
# Segment a single word (requires Morfessor trained model)
python scripts/morfessor_segment.py --word "unbelievable"

# Output:
# {
#   "word": "unbelievable",
#   "segments": ["un", "believe", "able"],
#   "morphemes": ["un", "believe", "able"],
#   "source": "morfessor"
# }
```

## Installation

```bash
pip install morfessor
```

## Training Custom Model

```python
import morfessor

# Train on word list
io = morfessor.MorfessorIO()
model = morfessor.BaselineModel()

# Load training data
words = ['happiness', 'sadness', 'joyfulness', 'careful', 'careless']
model.load_data(words)

# Train
model.train_batch()

# Segment new words
segments = model.viterbi_segment('unhappiness')
# Returns: ['un', 'happi', 'ness']
```

## Output Format

```json
{
  "word": "unbelievable",
  "segments": ["un", "believe", "able"],
  "morphemes": ["un", "believe", "able"],
  "segmentation_type": "unsupervised",
  "source": "morfessor"
}
```

## Integration

- **property-extractor** uses this for morpheme extraction
- **morph-router** includes Morfessor for segmentation queries
- Complements **suffix-lexicon** by discovering novel patterns

## Limitations

- Unsupervised - may over/under-segment
- Doesn't label morpheme types (prefix vs suffix)
- Requires training data for best results
- May split non-morphological boundaries (e.g., "earnest" → "ear-nest")

## Use Cases

- Analyzing novel/rare words not in dictionary
- Discovering productive morphemes in corpus
- Preprocessing for unsupervised NLP
- Cross-linguistic morphology research

---

**Script:** `scripts/morfessor_segment.py` (requires implementation)
**Status:** ⚠ Requires Morfessor package installation
**Installation:** `pip install morfessor`
