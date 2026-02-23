"""
Integration tests for the main 'analyze' command

Tests full morphological analysis pipeline integrating:
- Suffix identification
- Lemmatization (WordNet)
- POS tagging (spaCy)
- Morphological features
- Property aggregation

Following TDD - these tests MUST fail initially.
"""
import pytest
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from helpers.cli_runner import CLIRunner


class TestAnalyzeCommandBasic:
    """Basic functionality tests for analyze command"""

    @pytest.fixture
    def cli(self):
        return CLIRunner()

    def test_analyze_command_exists(self, cli):
        """Test that analyze command is available"""
        result = cli.run(["analyze", "--help"])

        # Should show help without error
        assert result.exit_code == 0
        assert "analyze" in result.stdout.lower()

    def test_analyze_simple_noun(self, cli):
        """Test analyzing simple noun 'happiness'"""
        result = cli.run(["analyze", "--word", "happiness"])

        assert result.success, f"Command failed: {result.stderr}"
        data = result.json

        # Should include multiple analysis components
        assert data["word"] == "happiness"
        assert "suffix" in data
        assert "POS" in data
        assert "lemma" in data
        assert "stem" in data

    def test_analyze_simple_verb(self, cli):
        """Test analyzing simple verb 'running'"""
        result = cli.run(["analyze", "--word", "running"])

        assert result.success
        data = result.json

        assert data["word"] == "running"
        assert data["lemma"] == "run"
        assert "suffix" in data
        # POS might be ambiguous (verb/noun)
        assert "POS" in data

    def test_analyze_simple_adjective(self, cli):
        """Test analyzing adjective 'beautiful'"""
        result = cli.run(["analyze", "--word", "beautiful"])

        assert result.success
        data = result.json

        assert data["word"] == "beautiful"
        assert "POS" in data
        # Should identify -ful suffix
        assert data.get("suffix") == "-ful"

    def test_analyze_no_word_argument_fails(self, cli):
        """Test that analyze requires --word argument"""
        result = cli.run(["analyze"])

        # Should fail with error message
        assert not result.success
        assert "word" in result.stderr.lower() or "required" in result.stderr.lower()

    def test_analyze_with_context(self, cli):
        """Test analyzing word with context sentence"""
        result = cli.run([
            "analyze",
            "--word", "running",
            "--context", "They are running in the park"
        ])

        assert result.success
        data = result.json

        # Context should help disambiguate POS
        assert data["lemma"] == "run"
        # In this context, "running" is a verb
        assert "verb" in str(data.get("POS", "")).lower()


class TestAnalyzeCommandMultiTool:
    """Test multi-tool integration in analyze command"""

    @pytest.fixture
    def cli(self):
        return CLIRunner()

    def test_analyze_includes_spacy_features(self, cli):
        """Test that analysis includes spaCy morphological features"""
        result = cli.run(["analyze", "--word", "running"])

        assert result.success
        data = result.json

        # Should include spaCy-specific features
        assert "morphological_features" in data or "features" in data or "morph" in data

    def test_analyze_includes_wordnet_synsets(self, cli):
        """Test that analysis includes WordNet synset information"""
        result = cli.run(["analyze", "--word", "happiness"])

        assert result.success
        data = result.json

        # Should include WordNet synset data
        assert "synsets" in data or "senses" in data or "definitions" in data

    def test_analyze_includes_suffix_metadata(self, cli):
        """Test that analysis includes suffix database metadata"""
        result = cli.run(["analyze", "--word", "happiness"])

        assert result.success
        data = result.json

        # Should include suffix-related data
        assert "suffix" in data
        assert "base_POS" in data or "source_POS" in data

    def test_analyze_aggregates_pos_from_multiple_sources(self, cli):
        """Test that POS is aggregated from multiple tools"""
        result = cli.run(["analyze", "--word", "running"])

        assert result.success
        data = result.json

        # Should show POS from different sources or indicate consensus
        assert "POS" in data
        # May have structure showing different tool results
        pos_data = data["POS"]
        # Could be simple string or complex object with sources
        assert pos_data is not None

    def test_analyze_handles_tool_disagreement(self, cli):
        """Test handling when tools disagree on analysis"""
        # "running" can be verb or noun - tools might disagree
        result = cli.run(["analyze", "--word", "running"])

        assert result.success
        data = result.json

        # Should indicate when there's disagreement
        # Either show all options or indicate uncertainty
        assert "POS" in data
        # Check for ambiguity indicators
        has_ambiguity = (
            "ambiguous" in str(data).lower() or
            "consensus" in str(data).lower() or
            isinstance(data.get("POS"), list) or
            isinstance(data.get("POS"), dict)
        )
        # Ambiguous words should show this somehow
        assert has_ambiguity


class TestAnalyzeCommandConfidence:
    """Test confidence scoring in analyze command"""

    @pytest.fixture
    def cli(self):
        return CLIRunner()

    def test_analyze_includes_overall_confidence(self, cli):
        """Test that analysis includes overall confidence score"""
        result = cli.run(["analyze", "--word", "happiness"])

        assert result.success
        data = result.json

        assert "confidence" in data
        assert 0.0 <= data["confidence"] <= 1.0

    def test_analyze_high_confidence_common_word(self, cli):
        """Test high confidence for common, unambiguous word"""
        result = cli.run(["analyze", "--word", "happiness"])

        assert result.success
        data = result.json

        # Common word with clear suffix should have high confidence
        assert data["confidence"] >= 0.7

    def test_analyze_low_confidence_ambiguous_word(self, cli):
        """Test lower confidence for ambiguous word"""
        result = cli.run(["analyze", "--word", "running"])

        assert result.success
        data = result.json

        # Ambiguous word might have lower confidence
        # Or confidence per interpretation
        assert "confidence" in data

    def test_analyze_per_property_confidence(self, cli):
        """Test confidence scores for individual properties"""
        result = cli.run(["analyze", "--word", "happiness"])

        assert result.success
        data = result.json

        # May have confidence per property
        # e.g., suffix confidence, POS confidence, lemma confidence
        # At minimum, should have overall confidence
        assert "confidence" in data or any(
            "confidence" in str(v) for v in data.values()
        )


class TestAnalyzeCommandBatchMode:
    """Test batch processing in analyze command"""

    @pytest.fixture
    def cli(self):
        return CLIRunner()

    def test_analyze_multiple_words(self, cli):
        """Test analyzing multiple words at once"""
        result = cli.run([
            "analyze",
            "--words", "happiness,running,cats"
        ])

        assert result.success
        data = result.json

        # Should return list or dict of results
        assert isinstance(data, (list, dict))

        # Should have results for all words
        if isinstance(data, list):
            assert len(data) == 3
            words = [item["word"] for item in data]
        else:
            words = list(data.keys())

        assert "happiness" in words
        assert "running" in words
        assert "cats" in words

    def test_analyze_from_file(self, cli, tmp_path):
        """Test analyzing words from input file"""
        # Create temp file with words
        word_file = tmp_path / "words.txt"
        word_file.write_text("happiness\nrunning\ncats\n")

        result = cli.run([
            "analyze",
            "--file", str(word_file)
        ])

        if result.success:
            data = result.json
            # Should process all words from file
            assert isinstance(data, (list, dict))

    def test_analyze_batch_performance(self, cli):
        """Test that batch mode is efficient"""
        import time

        # Process 10 words
        words = ["happiness", "running", "cats", "beautiful", "quickly",
                 "government", "player", "singing", "teacher", "brightness"]

        start = time.time()
        result = cli.run([
            "analyze",
            "--words", ",".join(words)
        ])
        elapsed = time.time() - start

        if result.success:
            # Should complete in reasonable time (< 5 seconds for 10 words)
            assert elapsed < 5.0


class TestAnalyzeCommandPropertySelection:
    """Test selecting specific properties to analyze"""

    @pytest.fixture
    def cli(self):
        return CLIRunner()

    def test_analyze_only_lemma(self, cli):
        """Test requesting only lemmatization"""
        result = cli.run([
            "analyze",
            "--word", "running",
            "--properties", "lemma"
        ])

        if result.success:
            data = result.json
            assert "lemma" in data
            # Other properties may or may not be included

    def test_analyze_only_suffix(self, cli):
        """Test requesting only suffix analysis"""
        result = cli.run([
            "analyze",
            "--word", "happiness",
            "--properties", "suffix,stem"
        ])

        if result.success:
            data = result.json
            assert "suffix" in data
            assert "stem" in data

    def test_analyze_only_pos(self, cli):
        """Test requesting only POS tagging"""
        result = cli.run([
            "analyze",
            "--word", "running",
            "--properties", "POS"
        ])

        if result.success:
            data = result.json
            assert "POS" in data

    def test_analyze_all_properties(self, cli):
        """Test requesting all available properties"""
        result = cli.run([
            "analyze",
            "--word", "happiness",
            "--properties", "all"
        ])

        assert result.success
        data = result.json

        # Should include comprehensive analysis
        assert "lemma" in data
        assert "POS" in data
        assert "suffix" in data
        assert "stem" in data


class TestAnalyzeCommandEdgeCases:
    """Test edge cases for analyze command"""

    @pytest.fixture
    def cli(self):
        return CLIRunner()

    def test_analyze_oov_word(self, cli):
        """Test analyzing out-of-vocabulary word"""
        result = cli.run(["analyze", "--word", "flurpiness"])

        assert result.success
        data = result.json

        # Should still attempt analysis
        assert data["word"] == "flurpiness"
        # May identify suffix even for made-up word
        assert "suffix" in data

    def test_analyze_single_letter(self, cli):
        """Test analyzing single letter"""
        result = cli.run(["analyze", "--word", "a"])

        assert result.success
        data = result.json

        # Should handle gracefully
        assert data["word"] == "a"

    def test_analyze_very_long_word(self, cli):
        """Test analyzing very long word"""
        long_word = "antidisestablishmentarianism"
        result = cli.run(["analyze", "--word", long_word])

        assert result.success
        data = result.json

        assert data["word"] == long_word
        # Should identify suffix
        assert "suffix" in data

    def test_analyze_word_with_hyphen(self, cli):
        """Test analyzing hyphenated word"""
        result = cli.run(["analyze", "--word", "well-being"])

        assert result.success
        data = result.json

        assert "well-being" in data["word"]

    def test_analyze_word_with_apostrophe(self, cli):
        """Test analyzing word with apostrophe"""
        result = cli.run(["analyze", "--word", "don't"])

        assert result.success
        data = result.json

        # Should handle contractions
        assert data["word"] == "don't"

    def test_analyze_numeric_input(self, cli):
        """Test handling numeric input"""
        result = cli.run(["analyze", "--word", "12345"])

        assert result.success
        data = result.json

        # Should handle gracefully (no suffix for numbers)
        assert data["suffix"] is None

    def test_analyze_mixed_case(self, cli):
        """Test analyzing mixed case word"""
        result = cli.run(["analyze", "--word", "HaPpInEsS"])

        assert result.success
        data = result.json

        # Should normalize case
        assert "suffix" in data
        assert data["suffix"] == "-ness"

    def test_analyze_unicode_word(self, cli):
        """Test analyzing word with unicode characters"""
        result = cli.run(["analyze", "--word", "café"])

        # Should either handle unicode or fail gracefully
        if result.success:
            data = result.json
            assert "café" in data["word"]


class TestAnalyzeCommandErrorHandling:
    """Test error handling in analyze command"""

    @pytest.fixture
    def cli(self):
        return CLIRunner()

    def test_analyze_invalid_property_name(self, cli):
        """Test error on invalid property name"""
        result = cli.run([
            "analyze",
            "--word", "happiness",
            "--properties", "invalid_property"
        ])

        # Should fail or warn
        if not result.success:
            assert len(result.stderr) > 0

    def test_analyze_malformed_words_argument(self, cli):
        """Test error on malformed --words argument"""
        result = cli.run([
            "analyze",
            "--words", ""  # Empty
        ])

        # Should fail gracefully
        assert not result.success or result.json.get("error")

    def test_analyze_conflicting_arguments(self, cli):
        """Test error on conflicting arguments"""
        result = cli.run([
            "analyze",
            "--word", "happiness",
            "--words", "running,cats"  # Both --word and --words
        ])

        # Should either choose one or show error
        if not result.success:
            assert "conflict" in result.stderr.lower() or len(result.stderr) > 0

    def test_analyze_missing_required_tools(self, cli):
        """Test behavior when required tools aren't available"""
        # This would test graceful degradation
        # Hard to test without actually breaking the environment
        # Placeholder for now
        pass
