# CLI Implementation Guide - From Tests to Code

This guide helps implement the morphological analysis CLI to make all 105 tests pass.

## Quick Start

```bash
# 1. Check current test status
cd ~/.claude/plugins/morphological-analysis-infrastructure
pytest tests/ -q

# 2. Create cli.py
touch cli.py
chmod +x cli.py

# 3. Run tests after each implementation step
pytest tests/unit/test_suffix_identification.py -v
```

## Implementation Roadmap

### Phase 1: Minimal CLI (Target: 15 tests passing)

**Goal:** Get basic `suffix` command working

#### Step 1.1: Create CLI Entry Point
Create `cli.py`:

```python
#!/usr/bin/env python3
"""
Morphological Analysis CLI

Usage:
    morpho suffix --word <word>
    morpho analyze --word <word>
"""
import sys
import argparse
import json
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(
        description='Morphological analysis tools'
    )
    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Suffix command
    suffix_parser = subparsers.add_parser(
        'suffix',
        help='Identify suffix in word'
    )
    suffix_parser.add_argument('--word', required=True, help='Word to analyze')
    suffix_parser.add_argument('--db', default='data/unified_suffixes.json')
    suffix_parser.add_argument('--min-stem', type=int, default=2)

    args = parser.parse_args()

    if args.command == 'suffix':
        handle_suffix(args)
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == '__main__':
    main()
```

**Tests to pass:** `test_identify_common_noun_suffix`, `test_help_message_displayed`

#### Step 1.2: Implement Suffix Command Handler
```python
def handle_suffix(args):
    """Handle suffix command"""
    from scripts.identify_suffix import identify_suffix

    result = identify_suffix(
        args.word,
        db_path=args.db,
        min_stem_length=args.min_stem
    )

    print(json.dumps(result, indent=2))
```

**Tests to pass:** All basic suffix tests (16 tests)

#### Step 1.3: Add Error Handling
```python
def handle_suffix(args):
    """Handle suffix command with error handling"""
    try:
        from scripts.identify_suffix import identify_suffix

        result = identify_suffix(
            args.word,
            db_path=args.db,
            min_stem_length=args.min_stem
        )

        print(json.dumps(result, indent=2))
    except Exception as e:
        print(json.dumps({
            'error': str(e),
            'word': args.word
        }), file=sys.stderr)
        sys.exit(1)
```

**Tests to pass:** Error handling tests

### Phase 2: Analyze Command (Target: 40 tests passing)

#### Step 2.1: Add Analyze Command Parser
```python
# In main()
analyze_parser = subparsers.add_parser(
    'analyze',
    help='Full morphological analysis'
)
analyze_parser.add_argument('--word', required=True)
analyze_parser.add_argument('--context', help='Context sentence')
analyze_parser.add_argument('--properties', help='Comma-separated properties')
```

#### Step 2.2: Implement Multi-Tool Aggregation
```python
def handle_analyze(args):
    """Handle analyze command - aggregate all tools"""
    from scripts.identify_suffix import identify_suffix
    from scripts.extract_spacy_features import extract_spacy_features
    from scripts.extract_wordnet_features import extract_wordnet_features

    word = args.word
    context = args.context or word

    # Gather results from all tools
    suffix_result = identify_suffix(word)
    spacy_result = extract_spacy_features(word, context)
    wordnet_result = extract_wordnet_features(word)

    # Aggregate results
    aggregated = {
        'word': word,
        'lemma': aggregate_lemma(spacy_result, wordnet_result),
        'POS': aggregate_pos(suffix_result, spacy_result, wordnet_result),
        'suffix': suffix_result.get('suffix'),
        'stem': suffix_result.get('stem'),
        'morphological_features': spacy_result.get('morphological_features'),
        'synsets': wordnet_result.get('synsets'),
        'confidence': calculate_confidence(suffix_result, spacy_result, wordnet_result)
    }

    print(json.dumps(aggregated, indent=2))
```

#### Step 2.3: Implement Aggregation Functions
```python
def aggregate_lemma(spacy_result, wordnet_result):
    """Choose best lemma from multiple sources"""
    spacy_lemma = spacy_result.get('lemma')
    wordnet_lemma = wordnet_result.get('lemma')

    # Prefer spaCy if available
    return spacy_lemma or wordnet_lemma

def aggregate_pos(suffix_result, spacy_result, wordnet_result):
    """Aggregate POS from multiple sources"""
    suffix_pos = suffix_result.get('POS')
    spacy_pos = spacy_result.get('POS')
    wordnet_pos = wordnet_result.get('POS')

    # Check for consensus
    if suffix_pos == spacy_pos == wordnet_pos:
        return suffix_pos

    # Show multiple if disagreement
    return {
        'suffix': suffix_pos,
        'spacy': spacy_pos,
        'wordnet': wordnet_pos,
        'consensus': False
    }

def calculate_confidence(suffix_result, spacy_result, wordnet_result):
    """Calculate overall confidence score"""
    suffix_conf = suffix_result.get('confidence', 0.0)
    # spaCy and WordNet typically don't provide confidence
    # Use simple average or weighted score
    return suffix_conf  # Start simple
```

**Tests to pass:** All analyze basic tests (34 tests)

### Phase 3: Output Formatters (Target: 65 tests passing)

#### Step 3.1: Create Formatters Module
```bash
mkdir formatters
touch formatters/__init__.py
touch formatters/json_formatter.py
touch formatters/text_formatter.py
touch formatters/csv_formatter.py
```

#### Step 3.2: Implement JSON Formatter
`formatters/json_formatter.py`:
```python
import json

def format_json(data, pretty=True, compact=False):
    """Format data as JSON"""
    if compact:
        return json.dumps(data, separators=(',', ':'))
    elif pretty:
        return json.dumps(data, indent=2)
    else:
        return json.dumps(data)
```

#### Step 3.3: Implement Text Formatter
`formatters/text_formatter.py`:
```python
def format_text(data):
    """Format data as human-readable text"""
    lines = []
    lines.append(f"Word: {data['word']}")

    if data.get('suffix'):
        lines.append(f"Suffix: {data['suffix']}")
        lines.append(f"Stem: {data['stem']}")

    if data.get('POS'):
        lines.append(f"POS: {data['POS']}")

    if data.get('lemma'):
        lines.append(f"Lemma: {data['lemma']}")

    if data.get('confidence'):
        lines.append(f"Confidence: {data['confidence']:.2f}")

    return '\n'.join(lines)
```

#### Step 3.4: Implement CSV Formatter
`formatters/csv_formatter.py`:
```python
import csv
from io import StringIO

def format_csv(data, headers=True):
    """Format data as CSV"""
    # Handle single dict or list of dicts
    if isinstance(data, dict):
        data = [data]

    output = StringIO()
    if data:
        writer = csv.DictWriter(output, fieldnames=data[0].keys())
        if headers:
            writer.writeheader()
        writer.writerows(data)

    return output.getvalue()
```

#### Step 3.5: Add Format Selection to CLI
```python
# In argument parsers
suffix_parser.add_argument(
    '--format',
    choices=['json', 'text', 'csv'],
    default='json',
    help='Output format'
)
suffix_parser.add_argument('--pretty', action='store_true')
suffix_parser.add_argument('--compact', action='store_true')

# In handle_suffix
def handle_suffix(args):
    from scripts.identify_suffix import identify_suffix
    from formatters import json_formatter, text_formatter, csv_formatter

    result = identify_suffix(args.word, args.db, args.min_stem)

    if args.format == 'json':
        output = json_formatter.format_json(
            result,
            pretty=args.pretty,
            compact=args.compact
        )
    elif args.format == 'text':
        output = text_formatter.format_text(result)
    elif args.format == 'csv':
        output = csv_formatter.format_csv(result)

    print(output)
```

**Tests to pass:** All output formatter tests (27 tests)

### Phase 4: Advanced Features (Target: 105 tests passing)

#### Step 4.1: Batch Processing
```python
# Add --words argument
suffix_parser.add_argument('--words', help='Comma-separated words')

def handle_suffix(args):
    if args.words:
        words = args.words.split(',')
        results = []
        for word in words:
            result = identify_suffix(word.strip(), args.db, args.min_stem)
            results.append(result)

        # Format as list
        if args.format == 'json':
            print(json.dumps(results, indent=2))
        elif args.format == 'csv':
            print(csv_formatter.format_csv(results))
    else:
        # Single word processing
        # ... existing code ...
```

#### Step 4.2: File Input
```python
# Add --file argument
suffix_parser.add_argument('--file', help='File with words (one per line)')

def handle_suffix(args):
    if args.file:
        with open(args.file) as f:
            words = [line.strip() for line in f if line.strip()]

        results = [identify_suffix(w, args.db, args.min_stem) for w in words]
        # Format output
        # ... same as --words ...
```

#### Step 4.3: Field Selection
```python
# Add --fields argument
suffix_parser.add_argument('--fields', help='Comma-separated fields')

def filter_fields(result, fields):
    """Keep only specified fields"""
    if not fields:
        return result

    field_list = [f.strip() for f in fields.split(',')]
    return {k: v for k, v in result.items() if k in field_list}

def handle_suffix(args):
    result = identify_suffix(args.word, args.db, args.min_stem)

    if args.fields:
        result = filter_fields(result, args.fields)

    # Format and print
    # ...
```

#### Step 4.4: Verbosity Flags
```python
# Add verbosity arguments
parser.add_argument('--quiet', '-q', action='store_true')
parser.add_argument('--verbose', '-v', action='store_true')
parser.add_argument('--debug', '-d', action='store_true')

import logging

def setup_logging(args):
    if args.debug:
        level = logging.DEBUG
    elif args.verbose:
        level = logging.INFO
    elif args.quiet:
        level = logging.ERROR
    else:
        level = logging.WARNING

    logging.basicConfig(level=level)

def main():
    args = parser.parse_args()
    setup_logging(args)

    # Rest of main
    # ...
```

#### Step 4.5: Color Output
```python
# Add color arguments
parser.add_argument('--color', action='store_true')
parser.add_argument('--no-color', action='store_true')

import sys

def should_use_color(args):
    if args.no_color:
        return False
    if args.color:
        return True
    # Auto-detect: use color if stdout is a terminal
    return sys.stdout.isatty()

class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'

def colorize(text, color, use_color=True):
    if use_color:
        return f"{color}{text}{Colors.RESET}"
    return text
```

## Testing Strategy

### After Each Implementation Step

```bash
# Run affected tests
pytest tests/unit/test_suffix_identification.py -v

# Run all tests
pytest tests/ -v

# Check progress
pytest tests/ --tb=no -q
```

### Debugging Failed Tests

```bash
# Run single test with full output
pytest tests/unit/test_suffix_identification.py::TestSuffixIdentificationCLI::test_identify_common_noun_suffix -vv -s

# Show local variables on failure
pytest tests/ -l

# Drop into debugger on failure
pytest tests/ --pdb
```

## Common Issues

### Import Errors
**Problem:** `ModuleNotFoundError: No module named 'scripts'`

**Solution:** Add plugin directory to Python path in cli.py:
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
```

### JSON Decode Errors
**Problem:** Tests fail with `json.JSONDecodeError`

**Solution:** Make sure all output goes to stdout, errors to stderr:
```python
# Good
print(json.dumps(result))  # stdout

# Bad (mixes output)
print("Processing...", json.dumps(result))  # Don't mix messages and data
```

### Test Isolation Issues
**Problem:** Tests pass individually but fail when run together

**Solution:** Ensure each test is independent:
- Don't rely on previous test state
- Use fixtures for setup/teardown
- Don't modify global state

## Progress Tracking

Create a checklist as you implement:

```markdown
## Implementation Checklist

### Phase 1: Basic CLI
- [x] Create cli.py
- [x] Add argparse structure
- [x] Implement suffix command
- [x] Add help messages
- [ ] Tests passing: 15/105

### Phase 2: Analyze Command
- [ ] Add analyze command parser
- [ ] Integrate suffix identification
- [ ] Integrate spaCy
- [ ] Integrate WordNet
- [ ] Implement aggregation
- [ ] Add confidence scoring
- [ ] Tests passing: 40/105

### Phase 3: Output Formats
- [ ] Create formatters module
- [ ] Implement JSON formatter
- [ ] Implement text formatter
- [ ] Implement CSV formatter
- [ ] Add format selection
- [ ] Add field filtering
- [ ] Tests passing: 65/105

### Phase 4: Advanced Features
- [ ] Batch processing (--words)
- [ ] File input (--file)
- [ ] Property selection (--properties)
- [ ] Verbosity flags
- [ ] Color output
- [ ] Tests passing: 105/105
```

## Final Verification

Before considering implementation complete:

```bash
# All tests must pass
pytest tests/ -v

# Code coverage should be high
pytest tests/ --cov=. --cov-report=term

# Manual smoke tests
./cli.py suffix --word happiness
./cli.py analyze --word running
./cli.py suffix --words "happiness,running,cats" --format csv
./cli.py analyze --word "running" --context "They are running" --format text

# Help messages work
./cli.py --help
./cli.py suffix --help
./cli.py analyze --help
```

## Next Steps After Implementation

1. **Documentation:** Update README.md with CLI usage examples
2. **Installation:** Add setup.py or install script
3. **Performance:** Profile and optimize slow operations
4. **Features:** Implement lemmatize and extract commands
5. **Distribution:** Package for PyPI or create binary

## Resources

- [Test Suite README](tests/README.md)
- [Test Failure Report](TEST_FAILURE_REPORT.md)
- [Plugin README](README.md)
- [Existing Scripts](scripts/)

## Support

If stuck:
1. Check test output for specific error messages
2. Review similar passing tests for patterns
3. Look at existing scripts for implementation examples
4. Run tests with `-vv` for maximum verbosity
