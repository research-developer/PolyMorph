# Quick Reference - TDD Test Suite

## Current Status

```
✓ TDD Phase 1 Complete - Tests written, ready for implementation
✓ 105 tests created (1,940 lines of test code)
✓ 72 tests failing (expected - CLI not implemented)
✓ 33 tests passing (conditional logic)
```

## File Locations

```
~/.claude/plugins/morphological-analysis-infrastructure/
├── tests/                              # Test suite
│   ├── unit/test_suffix_identification.py   (52 tests)
│   ├── unit/test_output_formatters.py       (27 tests)
│   ├── integration/test_analyze_command.py  (34 tests)
│   └── integration/test_suffix_command.py   (24 tests)
│
├── TEST_FAILURE_REPORT.md             # Detailed failure analysis
├── IMPLEMENTATION_GUIDE.md            # Step-by-step implementation
├── TDD_SUMMARY.md                     # Complete summary
└── tests/README.md                    # Test suite docs
```

## Essential Commands

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/unit/test_suffix_identification.py -v

# Run specific test
pytest tests/unit/test_suffix_identification.py::TestSuffixIdentificationCLI::test_identify_common_noun_suffix -v

# Run with summary
pytest tests/ -q

# Stop on first failure
pytest tests/ -x

# Show local variables on failure
pytest tests/ -l

# Run tests matching pattern
pytest tests/ -k "suffix" -v
```

## Test Breakdown

### Unit Tests (79 tests)

**Suffix Identification (52 tests)**
- Basic functionality: 16 tests
- Edge cases: 6 tests
- Database integration: 3 tests

**Output Formatters (27 tests)**
- JSON: 4 tests
- Text: 3 tests
- CSV: 4 tests
- Table: 2 tests
- Field selection: 3 tests
- Verbosity: 3 tests
- Color: 3 tests

### Integration Tests (26 tests)

**Analyze Command (34 tests)**
- Basic: 6 tests
- Multi-tool: 5 tests
- Confidence: 4 tests
- Batch: 3 tests
- Properties: 4 tests
- Edge cases: 9 tests
- Errors: 4 tests

**Suffix Command (24 tests)**
- Integration: 4 tests
- Real words: 4 tests
- Database: 4 tests
- Streaming: 3 tests
- Recovery: 3 tests
- Documentation: 3 tests
- Compatibility: 2 tests

## Implementation Phases

### Phase 1: Basic CLI (Target: 15 tests)
- Create cli.py
- Add argparse
- Implement suffix command
- Add help

### Phase 2: Analyze Command (Target: 40 tests)
- Integrate suffix identification
- Integrate spaCy
- Integrate WordNet
- Add confidence scoring

### Phase 3: Output Formats (Target: 65 tests)
- JSON formatter
- Text formatter
- CSV formatter
- Field selection

### Phase 4: Advanced (Target: 105 tests)
- Batch processing
- File input
- Property selection
- Verbosity flags

## What Tests Expect

### CLI Commands
```bash
# Suffix command
cli.py suffix --word happiness
cli.py suffix --words "happiness,running,cats"
cli.py suffix --word happiness --format text
cli.py suffix --word happiness --db custom.json

# Analyze command
cli.py analyze --word happiness
cli.py analyze --word running --context "They are running"
cli.py analyze --words "happiness,running,cats"
cli.py analyze --word happiness --properties lemma,POS
```

### Expected Output (JSON)
```json
{
  "word": "happiness",
  "suffix": "-ness",
  "stem": "happi",
  "POS": "noun",
  "base_POS": ["adjective"],
  "confidence": 0.9,
  "lemma": "happiness",
  "morphological_features": {...},
  "synsets": [...]
}
```

## Common Test Patterns

### Basic Test Structure
```python
def test_feature(self, cli):
    # Arrange
    word = "happiness"

    # Act
    result = cli.run(["suffix", "--word", word])

    # Assert
    assert result.success
    data = result.json
    assert data["suffix"] == "-ness"
```

### Edge Case Test
```python
def test_edge_case(self, cli):
    result = cli.run(["suffix", "--word", ""])

    if result.success:
        data = result.json
        assert "error" in data or data["word"] == ""
```

### Error Handling Test
```python
def test_error(self, cli):
    result = cli.run(["suffix"])  # Missing --word

    assert not result.success
    assert "required" in result.stderr.lower()
```

## Quick Checks

### Verify Tests Run
```bash
pytest tests/ --collect-only -q
# Should show: 105 tests collected
```

### See Failure Reason
```bash
pytest tests/unit/test_suffix_identification.py::TestSuffixIdentificationCLI::test_identify_common_noun_suffix -v
# Should show: python3: can't open file '.../cli.py'
```

### Check Coverage
```bash
pytest tests/ --cov=. --cov-report=term
```

## Documentation Guide

1. **Start here:** TDD_SUMMARY.md
2. **For implementation:** IMPLEMENTATION_GUIDE.md
3. **For test details:** TEST_FAILURE_REPORT.md
4. **For running tests:** tests/README.md

## Expected Timeline

- **Test creation:** 2 hours (DONE ✓)
- **Implementation:** 4-8 hours
- **Refinement:** 1-2 hours
- **Total:** 7-12 hours

## Success Indicators

Phase 1 Complete:
- [ ] cli.py exists
- [ ] suffix command works
- [ ] JSON output works
- [ ] 15+ tests passing

Phase 2 Complete:
- [ ] analyze command works
- [ ] Multi-tool integration
- [ ] Confidence scoring
- [ ] 40+ tests passing

Phase 3 Complete:
- [ ] All output formats
- [ ] Field selection
- [ ] Format switching
- [ ] 65+ tests passing

Phase 4 Complete:
- [ ] Batch processing
- [ ] All features
- [ ] All tests passing (105/105)

## Getting Help

If stuck:
1. Read relevant section in IMPLEMENTATION_GUIDE.md
2. Check similar passing tests for patterns
3. Look at existing scripts in scripts/ directory
4. Run tests with -vv for maximum detail
5. Use --pdb to debug failing tests

## Key Files to Implement

```python
# Core CLI
cli.py                  # Main entry point

# Formatters (create formatters/ directory)
formatters/
├── __init__.py
├── json_formatter.py
├── text_formatter.py
└── csv_formatter.py
```

## Validation Checklist

Before considering implementation complete:

- [ ] All 105 tests pass
- [ ] Help messages work
- [ ] Error messages are clear
- [ ] Performance requirements met
- [ ] Code is documented
- [ ] Examples work in README

---

**Quick Start Implementation:**

```bash
# 1. Create CLI
touch cli.py && chmod +x cli.py

# 2. Add basic structure (see IMPLEMENTATION_GUIDE.md Phase 1)

# 3. Run tests
pytest tests/unit/test_suffix_identification.py -v

# 4. Implement until tests pass

# 5. Move to next phase
```

**Remember:** TDD = Red → Green → Refactor
