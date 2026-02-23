# Morphological Analysis Router

**Trigger:** When user requests morphological analysis, suffix parsing, word segmentation, POS tagging, or lemmatization

**Description:** Intelligent router that assesses the nature of morphological queries and routes them to the appropriate specialized tools. Aggregates results from multiple tools and handles disambiguation.

## Core Capabilities

This router can handle queries like:
- "What is the suffix and POS of 'happiness'?"
- "Analyze the morphology of 'unbelievable'"
- "Find all words with suffix '-tion'"
- "What are the possible stems for words ending in '-able'?"
- "Get all morphological properties of 'running'"

## Routing Logic

### Query Type Detection

1. **Suffix-First Analysis** → Route to `trie-suffix-lookup` + `suffix-lexicon`
   - Queries asking for suffix identification
   - Reverse lookup (suffix → stems)
   - Suffix → POS mapping

2. **Full Morphological Analysis** → Route to multiple analyzers in parallel
   - `spacy-morph` for statistical analysis
   - `wordnet-morphy` for lemmatization
   - `freeling-analyzer` for rule-based segmentation (if available)
   - `morfessor-segment` for unsupervised segmentation

3. **FST-Based Analysis** → Route to `fst-morphology`
   - Bidirectional morphology queries
   - Complex morphological generation
   - Language-specific FST operations

4. **Property Extraction** → Route to `property-extractor`
   - Extract specific properties (POS, lemma, features, etc.)
   - Aggregate properties from all available tools

## Usage Examples

```python
# Example 1: Suffix-first analysis
Query: "What suffix does 'happiness' have?"
Router → suffix-lexicon (identifies '-ness')
      → trie-suffix-lookup (finds stems: 'happy', 'sad', etc.)
      → Returns: {suffix: '-ness', POS: 'noun', stem: 'happy', base_POS: 'adjective'}

# Example 2: Full analysis
Query: "Analyze 'unbelievable' morphologically"
Router → spacy-morph (statistical features)
      → wordnet-morphy (lemma)
      → morfessor-segment (unsupervised: un+believe+able)
      → suffix-lexicon (suffix: '-able', POS: 'adjective')
      → Aggregates and returns all properties

# Example 3: Property extraction
Query: "Get POS, lemma, and morphological features for 'running'"
Router → property-extractor
      → Calls: spacy-morph, wordnet-morphy, suffix-lexicon
      → Returns: {
          POS: ['VERB', 'NOUN'],  # ambiguous
          lemma: 'run',
          features: {
            spacy: {Number: 'Sing', VerbForm: 'Ger'},
            suffix: {suffix: '-ing', base_POS: 'verb'}
          }
        }
```

## Implementation

### Step 1: Analyze Query Intent

```python
def analyze_query(query: str) -> QueryType:
    """Determine query type and required tools"""

    # Keywords for suffix-first queries
    suffix_keywords = ['suffix', 'ending', 'ends with', 'words ending in']

    # Keywords for full analysis
    analysis_keywords = ['analyze', 'morphology', 'parse', 'segment']

    # Keywords for property extraction
    property_keywords = ['POS', 'part of speech', 'lemma', 'stem', 'features', 'properties']

    # FST-specific keywords
    fst_keywords = ['generate', 'bidirectional', 'FST', 'transducer']

    # Classify query
    if any(kw in query.lower() for kw in suffix_keywords):
        return QueryType.SUFFIX_FIRST
    elif any(kw in query.lower() for kw in fst_keywords):
        return QueryType.FST
    elif any(kw in query.lower() for kw in property_keywords):
        return QueryType.PROPERTY_EXTRACTION
    else:
        return QueryType.FULL_ANALYSIS
```

### Step 2: Route to Appropriate Tools

```python
def route_query(query_type: QueryType, words: List[str]) -> Dict:
    """Route to appropriate tools based on query type"""

    results = {}

    if query_type == QueryType.SUFFIX_FIRST:
        # Use suffix-first approach
        results['suffix_lexicon'] = call_skill('suffix-lexicon', words)
        results['trie_lookup'] = call_skill('trie-suffix-lookup', words)

    elif query_type == QueryType.FULL_ANALYSIS:
        # Call all available analyzers in parallel
        tools = ['spacy-morph', 'wordnet-morphy', 'morfessor-segment', 'suffix-lexicon']
        for tool in tools:
            try:
                results[tool] = call_skill(tool, words)
            except Exception as e:
                results[tool] = {'error': str(e)}

    elif query_type == QueryType.PROPERTY_EXTRACTION:
        # Use property extractor
        results = call_skill('property-extractor', words)

    elif query_type == QueryType.FST:
        # Use FST-based morphology
        results = call_skill('fst-morphology', words)

    return results
```

### Step 3: Aggregate and Disambiguate Results

```python
def aggregate_results(results: Dict) -> Dict:
    """Aggregate results from multiple tools and handle disambiguation"""

    aggregated = {}

    for word in results.get('words', []):
        word_analysis = {
            'word': word,
            'analyses': {},
            'consensus': {},
            'conflicts': []
        }

        # Collect all analyses
        for tool, tool_results in results.items():
            if tool != 'words' and word in tool_results:
                word_analysis['analyses'][tool] = tool_results[word]

        # Find consensus
        pos_votes = {}
        lemma_votes = {}

        for tool, analysis in word_analysis['analyses'].items():
            if 'POS' in analysis:
                pos = analysis['POS']
                pos_votes[pos] = pos_votes.get(pos, 0) + 1
            if 'lemma' in analysis:
                lemma = analysis['lemma']
                lemma_votes[lemma] = lemma_votes.get(lemma, 0) + 1

        # Consensus = most votes
        if pos_votes:
            word_analysis['consensus']['POS'] = max(pos_votes, key=pos_votes.get)
            if len(pos_votes) > 1:
                word_analysis['conflicts'].append({
                    'property': 'POS',
                    'options': pos_votes
                })

        if lemma_votes:
            word_analysis['consensus']['lemma'] = max(lemma_votes, key=lemma_votes.get)
            if len(lemma_votes) > 1:
                word_analysis['conflicts'].append({
                    'property': 'lemma',
                    'options': lemma_votes
                })

        aggregated[word] = word_analysis

    return aggregated
```

## When to Use This Skill

- User asks about morphological analysis
- User needs suffix-first parsing
- User wants to extract morphological properties
- User needs disambiguation of morphological analyses
- User wants comprehensive analysis from multiple tools

## Tools Invoked

This router may invoke:
- `suffix-lexicon` - Suffix database queries
- `trie-suffix-lookup` - Reversed trie operations
- `fst-morphology` - FST-based analysis
- `spacy-morph` - spaCy statistical analysis
- `freeling-analyzer` - FreeLing rule-based analysis
- `morfessor-segment` - Unsupervised segmentation
- `wordnet-morphy` - WordNet lemmatization
- `property-extractor` - Multi-tool property aggregation

## Output Format

```json
{
  "query_type": "full_analysis",
  "words": ["happiness"],
  "results": {
    "happiness": {
      "analyses": {
        "spacy_morph": {"POS": "NOUN", "Number": "Sing"},
        "wordnet_morphy": {"lemma": "happiness", "POS": "noun"},
        "suffix_lexicon": {"suffix": "-ness", "POS": "noun", "stem": "happy"},
        "morfessor_segment": {"segments": ["happi", "ness"]}
      },
      "consensus": {
        "POS": "noun",
        "lemma": "happiness",
        "stem": "happy",
        "suffix": "-ness"
      },
      "conflicts": []
    }
  }
}
```

## Error Handling

If a tool is unavailable or fails:
1. Log the error
2. Continue with other tools
3. Note missing data in output
4. Provide degraded but useful results

---

**Implementation:** This is a routing skill that delegates to other skills. The actual implementation uses Bash scripts to call Python tools and aggregate results.
