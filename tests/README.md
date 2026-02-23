# Morphological Analysis CLI - Test Suite

Comprehensive test suite following Test-Driven Development (TDD) methodology.

## Test Structure

```
tests/
├── README.md                           # This file
├── conftest.py                         # Shared pytest fixtures
├── helpers/
│   ├── __init__.py
│   └── cli_runner.py                   # CLI test utilities
├── unit/
│   ├── __init__.py
│   ├── test_suffix_identification.py   # 52 tests for suffix command
│   └── test_output_formatters.py       # 27 tests for output formatting
└── integration/
    ├── __init__.py
    ├── test_analyze_command.py         # 34 tests for analyze command
    └── test_suffix_command.py          # 24 tests for suffix command
```

## Test Statistics

- **Total Tests:** 105
- **Unit Tests:** 79
- **Integration Tests:** 26
- **Current Status:** 72 failing (expected - CLI not implemented yet)

## Running Tests

### All Tests
```bash
pytest tests/ -v
```

### By Category
```bash
# Unit tests only
pytest tests/unit/ -v

# Integration tests only
pytest tests/integration/ -v

# Suffix tests only
pytest tests/ -k "suffix" -v

# Analyze tests only
pytest tests/ -k "analyze" -v

# Output format tests only
pytest tests/ -k "format" -v
```

### By Speed
```bash
# Skip slow tests
pytest tests/ -m "not slow" -v

# Only slow tests
pytest tests/ -m "slow" -v
```

### Development Workflow
```bash
# Stop on first failure (useful during implementation)
pytest tests/ -x

# Show local variables on failure
pytest tests/ -l

# Show print statements
pytest tests/ -s

# Quiet mode (less verbose)
pytest tests/ -q

# Very verbose (show all test details)
pytest tests/ -vv
```

### Coverage
```bash
# Generate coverage report
pytest tests/ --cov=. --cov-report=html --cov-report=term

# Open coverage report
open htmlcov/index.html
```

### Parallel Execution
```bash
# Run tests in parallel (requires pytest-xdist)
pytest tests/ -n auto
```

## Test Organization

### Unit Tests

**test_suffix_identification.py** (52 tests)
- Basic suffix identification (16 tests)
- Edge cases (6 tests)
- Database integration (3 tests)
- Tests CLI wrapper around `scripts/identify_suffix.py`

**test_output_formatters.py** (27 tests)
- JSON formatting (4 tests)
- Plain text formatting (3 tests)
- CSV formatting (4 tests)
- Table formatting (2 tests)
- Field selection (3 tests)
- Quiet/verbose modes (3 tests)
- Colorization (3 tests)
- Error handling (2 tests)

### Integration Tests

**test_analyze_command.py** (34 tests)
- Basic functionality (6 tests)
- Multi-tool integration (5 tests)
- Confidence scoring (4 tests)
- Batch processing (3 tests)
- Property selection (4 tests)
- Edge cases (9 tests)
- Error handling (4 tests)

**test_suffix_command.py** (24 tests)
- Integration with database (4 tests)
- Real-world words (4 tests)
- Database handling (4 tests)
- Stream processing (3 tests)
- Error recovery (3 tests)
- Documentation (3 tests)
- Compatibility (2 tests)

## Test Fixtures

Available in `conftest.py`:

- **plugin_dir** - Path to plugin root
- **cli_path** - Path to CLI executable
- **scripts_dir** - Path to scripts directory
- **data_dir** - Path to data directory
- **suffix_database** - Path to suffix database
- **temp_dir** - Temporary directory (auto-cleanup)
- **sample_suffix_database** - Minimal test database
- **sample_word_list** - Sample words for testing
- **sample_context_sentences** - Context sentences for ambiguous words

### Example Usage
```python
def test_example(cli_path, temp_dir):
    # cli_path points to cli.py
    # temp_dir is a clean temporary directory
    result = subprocess.run([str(cli_path), "suffix", "--word", "test"])
    assert result.returncode == 0
```

## Test Helpers

### CLIRunner

Located in `tests/helpers/cli_runner.py`, provides utilities for testing CLI:

```python
from helpers.cli_runner import CLIRunner

def test_suffix_command():
    cli = CLIRunner()

    # Run command
    result = cli.run(["suffix", "--word", "happiness"])

    # Check success
    assert result.success

    # Parse JSON output
    data = result.json
    assert data["suffix"] == "-ness"

    # Or run and parse in one step
    data = cli.run_json(["suffix", "--word", "happiness"])
```

## Writing New Tests

### Test Template
```python
import pytest
from helpers.cli_runner import CLIRunner

class TestNewFeature:
    """Test description"""

    @pytest.fixture
    def cli(self):
        return CLIRunner()

    def test_basic_functionality(self, cli):
        """Test that basic feature works"""
        # Arrange
        word = "happiness"

        # Act
        result = cli.run(["command", "--word", word])

        # Assert
        assert result.success
        data = result.json
        assert data["field"] == "expected_value"
```

### Best Practices

1. **Use descriptive test names** - Name should describe what is being tested
2. **Follow AAA pattern** - Arrange, Act, Assert
3. **One assertion per test** - Or related assertions for same behavior
4. **Test edge cases** - Empty strings, very long inputs, special characters
5. **Test error handling** - Invalid inputs should fail gracefully
6. **Use fixtures** - Avoid duplicating setup code
7. **Mark slow tests** - Use `@pytest.mark.slow` for tests > 1 second

### Adding Markers
```python
@pytest.mark.slow
def test_performance():
    # Slow test
    pass

@pytest.mark.requires_database
def test_with_database():
    # Needs database
    pass
```

## Test Development Workflow

### TDD Cycle

1. **Write failing test** - Test should fail because feature doesn't exist
2. **Run test** - Confirm it fails for the right reason
3. **Implement feature** - Write minimal code to make test pass
4. **Run test** - Confirm it passes
5. **Refactor** - Improve code while keeping tests green
6. **Repeat** - Move to next test

### Example Session
```bash
# 1. Write test in test_suffix_identification.py
# 2. Run test to see it fail
pytest tests/unit/test_suffix_identification.py::TestSuffixIdentificationCLI::test_new_feature -v

# 3. Implement feature in cli.py
# 4. Run test again
pytest tests/unit/test_suffix_identification.py::TestSuffixIdentificationCLI::test_new_feature -v

# 5. If passing, run all related tests
pytest tests/unit/test_suffix_identification.py -v

# 6. If all passing, run full suite
pytest tests/ -v
```

## Expected Test Progression

### Phase 1: Basic CLI (Target: 15 tests passing)
- CLI entry point exists
- Basic argument parsing
- `suffix` command works
- JSON output works

### Phase 2: Analyze Command (Target: 40 tests passing)
- `analyze` command implemented
- Multi-tool integration
- Basic confidence scoring

### Phase 3: Output Formats (Target: 65 tests passing)
- Text formatter
- CSV formatter
- Field selection
- Format switching

### Phase 4: Advanced Features (Target: 105 tests passing)
- Batch processing
- Context support
- Property selection
- All formatters complete

## Troubleshooting

### Tests Not Found
```bash
# Make sure you're in the plugin directory
cd ~/.claude/plugins/morphological-analysis-infrastructure

# Run from plugin root
pytest tests/
```

### Import Errors
```bash
# Install test dependencies
pip install -r requirements-test.txt
```

### Fixture Not Found
Check that `conftest.py` is present and properly formatted.

### CLI Not Found (Expected Initially)
This is expected! Tests fail because CLI doesn't exist yet.

Error:
```
python3: can't open file '.../cli.py': [Errno 2] No such file or directory
```

This is correct TDD behavior - tests fail until you implement the code.

## Continuous Integration

### GitHub Actions Example
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - run: pip install -r requirements.txt
      - run: pip install -r requirements-test.txt
      - run: pytest tests/ -v --cov=. --cov-report=xml
      - uses: codecov/codecov-action@v2
```

## Resources

- [pytest documentation](https://docs.pytest.org/)
- [TDD best practices](https://martinfowler.com/bliki/TestDrivenDevelopment.html)
- [Plugin README](../README.md)
- [Test Failure Report](../TEST_FAILURE_REPORT.md)

## Contributing

When adding new functionality:

1. Write tests first (TDD)
2. Run tests to confirm they fail
3. Implement feature
4. Run tests to confirm they pass
5. Update this README if needed

## Status

**Current Phase:** TDD Phase 1 - Tests Written, CLI Not Implemented
**Next Step:** Implement `cli.py` to make first tests pass

See [TEST_FAILURE_REPORT.md](../TEST_FAILURE_REPORT.md) for detailed failure analysis.
