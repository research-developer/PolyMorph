# FST-Based Morphological Analysis

**Trigger:** When bidirectional morphology is needed, complex morphological rules, or FST operations

**Description:** Finite-State Transducer tools for advanced morphological analysis. Supports bidirectional analysis/generation, composition, and inversion.

## FST Tools Supported

### 1. Pynini (OpenFST Python bindings)
- **Strengths:** Python integration, Google-backed, production-ready
- **Use Cases:** Building custom analyzers, composition, weighted FSTs

### 2. HFST (Helsinki Finite-State Toolkit)
- **Strengths:** Lexc grammar files, multilingual, two-level rules
- **Use Cases:** Complex morphologies, pretrained analyzers

### 3. Foma
- **Strengths:** Lightweight, XFST-compatible, simple
- **Use Cases:** Quick prototyping, regex-like rules

## Capabilities

- **Bidirectional Analysis** - Analyze or generate forms
- **Composition** - Combine multiple FSTs
- **Inversion** - Reverse input/output
- **Weighted FSTs** - Probabilistic morphology

## FST Concepts for Morphology

### 1. Basic FST
```
Input: "happiness"
FST: [surface_form] → [lemma + features]
Output: "happy + NOUN + DERIVATIONAL"
```

### 2. Inversion (Generation)
```
Input: "happy + NOUN + DERIVATIONAL"
Inverted FST: [lemma + features] → [surface_form]
Output: "happiness"
```

### 3. Composition (Layered Analysis)
```
Stage 1: Surface → Morphemes
  "happiness" → "happy + ness"

Stage 2: Morphemes → Features
  "happy + ness" → "ADJ + NOUN_SUFFIX"

Stage 3: Features → POS
  "ADJ + NOUN_SUFFIX" → "NOUN"

Composed FST: "happiness" → "NOUN"
```

## Pynini Example

```python
import pynini

# Create suffix FST
suffix_map = {
    "ness": "NOUN_SUFFIX",
    "able": "ADJ_SUFFIX",
    "ize": "VERB_SUFFIX"
}

suffix_fst = pynini.string_map(suffix_map)

# Create stem FST (simplified)
stem_map = {
    "happi": "happy/ADJ",
    "read": "read/VERB"
}

stem_fst = pynini.string_map(stem_map)

# Compose: word analysis FST
analyzer = stem_fst + suffix_fst

# Use it
word = "happiness"
# Split into stem + suffix first
# Then lookup: happi + ness → happy/ADJ + NOUN_SUFFIX → NOUN
```

## Reversed Suffix Matching with FST

```python
# Build reversed FST for suffix-first matching
reversed_words = [word[::-1] for word in lexicon]
reversed_fst = pynini.string_map(reversed_words)

# Query for suffix
suffix_query = "ssen"  # "ness" reversed
matches = reversed_fst.compose(suffix_query)
# Returns all words ending in "ness"
```

## HFST Lexc Grammar

```lexc
! English derivational suffixes

Multichar_Symbols
+Noun +Verb +Adj +Deriv

LEXICON Root
Stems ;

LEXICON Stems
happy:happi AdjStems ;
sad:sad AdjStems ;

LEXICON AdjStems
+Adj # ;
+Adj NounDeriv ;

LEXICON NounDeriv
ness:+Deriv+Noun # ;
```

Compile:
```bash
hfst-lexc english.lexc -o english.hfst
echo "happiness" | hfst-lookup english.hfst
# Output: happiness → happi+Adj+Deriv+Noun
```

## Integration

- **morph-router** can use FST for complex analyses
- **suffix-lexicon** rules can be compiled into FST
- **trie-suffix-lookup** provides alternative to FST for simple cases

## Use Cases

1. **Complex Morphology** - Languages with many affixes
2. **Bidirectional** - Both analysis and generation needed
3. **Composition** - Layered morphological rules
4. **Research** - Experimenting with morphological theories

## Installation

```bash
# Pynini
pip install pynini

# HFST (via conda)
conda install -c conda-forge hfst

# Foma
# Download from: https://fomafst.github.io/
```

## Limitations

- Steeper learning curve than simple lookup
- Requires FST knowledge
- Overkill for simple English morphology
- Better suited for complex languages (Turkish, Finnish, Arabic)

## When to Use FST vs Trie

**Use FST when:**
- Need bidirectional analysis/generation
- Complex morphological rules
- Weighted/probabilistic analysis
- Multilingual support needed

**Use Trie when:**
- Simple suffix lookup
- English or similar languages
- Performance critical
- Simpler implementation

---

**Status:** ⚠ Advanced feature - requires FST libraries
**Installation:** `pip install pynini` or `conda install -c conda-forge hfst`
**Recommended:** Start with trie-based approach, upgrade to FST if needed
