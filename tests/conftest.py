"""
Shared pytest configuration and fixtures for morphological analysis tests

This file is automatically loaded by pytest and provides shared fixtures
across all test modules.
"""
import pytest
import json
from pathlib import Path
import tempfile
import shutil


@pytest.fixture(scope="session")
def plugin_dir():
    """Return path to plugin directory"""
    return Path(__file__).parent.parent


@pytest.fixture(scope="session")
def cli_path(plugin_dir):
    """Return path to CLI executable"""
    return plugin_dir / "cli.py"


@pytest.fixture(scope="session")
def scripts_dir(plugin_dir):
    """Return path to scripts directory"""
    return plugin_dir / "scripts"


@pytest.fixture(scope="session")
def data_dir(plugin_dir):
    """Return path to data directory"""
    return plugin_dir / "data"


@pytest.fixture(scope="session")
def suffix_database(data_dir):
    """Return path to suffix database"""
    db_path = data_dir / "unified_suffixes.json"
    if db_path.exists():
        return db_path
    return None


@pytest.fixture
def temp_dir():
    """Provide temporary directory for test files"""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    # Cleanup after test
    shutil.rmtree(temp_path)


@pytest.fixture
def sample_suffix_database(temp_dir):
    """Create a minimal sample suffix database for testing"""
    db = {
        "suffixes": {
            "-ness": {
                "POS": "noun",
                "source_POS": ["adjective"],
                "category": "derivational",
                "meaning": "state or quality of",
                "examples": ["happiness", "sadness", "brightness"],
                "frequency": 100
            },
            "-ing": {
                "POS": ["verb", "noun"],
                "source_POS": ["verb"],
                "category": "inflectional",
                "meaning": "present participle or gerund",
                "examples": ["running", "singing", "playing"],
                "frequency": 150
            },
            "-ful": {
                "POS": "adjective",
                "source_POS": ["noun"],
                "category": "derivational",
                "meaning": "full of",
                "examples": ["beautiful", "peaceful", "joyful"],
                "frequency": 80
            },
            "-er": {
                "POS": "noun",
                "source_POS": ["verb"],
                "category": "derivational",
                "meaning": "one who does",
                "examples": ["teacher", "player", "singer"],
                "frequency": 120
            },
            "-ly": {
                "POS": "adverb",
                "source_POS": ["adjective"],
                "category": "derivational",
                "meaning": "in a manner",
                "examples": ["quickly", "slowly", "happily"],
                "frequency": 90
            }
        },
        "metadata": {
            "version": "1.0.0",
            "source": "test",
            "count": 5
        }
    }

    db_path = temp_dir / "test_suffixes.json"
    db_path.write_text(json.dumps(db, indent=2))
    return db_path


@pytest.fixture
def sample_word_list(temp_dir):
    """Create a sample word list file for testing"""
    words = [
        "happiness",
        "running",
        "beautiful",
        "teacher",
        "quickly",
        "government",
        "player",
        "singing",
        "peaceful",
        "brightness"
    ]

    word_file = temp_dir / "words.txt"
    word_file.write_text("\n".join(words))
    return word_file


@pytest.fixture
def sample_context_sentences():
    """Provide sample sentences for context-based testing"""
    return {
        "running": [
            "They are running in the park",  # verb
            "Running is good exercise",      # noun (gerund)
            "I saw a running stream"         # adjective
        ],
        "lead": [
            "Please lead the way",           # verb (present)
            "This pipe is made of lead",     # noun (metal)
            "The lead actor was brilliant"   # adjective
        ],
        "close": [
            "Please close the door",         # verb
            "They live close to school",     # adverb
            "We had a close call"            # adjective
        ]
    }


@pytest.fixture(autouse=True)
def reset_environment():
    """Reset environment before each test"""
    # This fixture runs automatically before each test
    # Can be used to reset state, clear caches, etc.
    yield
    # Cleanup after test if needed


def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )
    config.addinivalue_line(
        "markers", "requires_database: marks tests that require suffix database"
    )
    config.addinivalue_line(
        "markers", "requires_spacy: marks tests that require spaCy"
    )
    config.addinivalue_line(
        "markers", "requires_wordnet: marks tests that require WordNet"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers automatically"""
    for item in items:
        # Auto-mark integration tests
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)

        # Auto-mark unit tests
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)

        # Mark tests that use CLI as potentially slow
        if "cli.run" in str(item.function):
            item.add_marker(pytest.mark.slow)
