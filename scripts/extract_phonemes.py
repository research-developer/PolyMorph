#!/usr/bin/env python3
"""
Extract phoneme representations for morphological analysis

Provides phoneme bridges between morphemes using:
- CMUdict for known words (fast)
- Phonemizer for unknown words (fallback)
"""
import json
import sys

# Try CMUdict first (fast, comprehensive)
try:
    import pronouncing
    HAS_PRONOUNCING = True
except ImportError:
    HAS_PRONOUNCING = False

# Phonemizer for unknown words
try:
    from phonemizer import phonemize
    from phonemizer.backend import EspeakBackend
    HAS_PHONEMIZER = True
except ImportError:
    HAS_PHONEMIZER = False

# Global cache to ensure pronouncing dictionary is loaded once
_PRONOUNCING_INITIALIZED = False

def ensure_pronouncing_loaded():
    """
    Ensure pronouncing CMUdict is loaded (singleton pattern)

    First call triggers loading, subsequent calls are instant
    """
    global _PRONOUNCING_INITIALIZED
    if not _PRONOUNCING_INITIALIZED and HAS_PRONOUNCING:
        try:
            # Trigger CMUdict loading
            _ = pronouncing.phones_for_word('test')
            _PRONOUNCING_INITIALIZED = True
        except Exception:
            pass
    return _PRONOUNCING_INITIALIZED


def extract_phonemes(word):
    """
    Extract phoneme representations for a word

    Args:
        word: Word to analyze

    Returns:
        dict with phoneme data (ARPABET and IPA)
    """
    # Ensure pronouncing dictionary is loaded (cached after first call)
    ensure_pronouncing_loaded()

    result = {
        'word': word,
        'source': None,
        'arpabet': None,
        'ipa': None,
    }

    # Try CMUdict first (fast for known words)
    if HAS_PRONOUNCING:
        phones = pronouncing.phones_for_word(word.lower())
        if phones:
            # Take first pronunciation
            result['arpabet'] = phones[0]
            result['source'] = 'cmudict'

            # Convert ARPABET to simplified form
            result['arpabet_clean'] = phones[0].replace('0', '').replace('1', '').replace('2', '')

            return result

    # Fallback to phonemizer for unknown words
    if HAS_PHONEMIZER:
        try:
            # Use espeak backend for IPA
            ipa = phonemize(
                word,
                language='en-us',
                backend='espeak',
                strip=True,
                preserve_punctuation=False,
                with_stress=True
            )

            if ipa:
                result['ipa'] = ipa
                result['source'] = 'espeak'
                return result
        except Exception as e:
            result['error'] = f'Phonemizer failed: {str(e)}'

    # No phoneme data available
    if not HAS_PRONOUNCING and not HAS_PHONEMIZER:
        result['error'] = 'No phoneme libraries available. Install: pip install pronouncing phonemizer'
    elif result['source'] is None:
        result['error'] = 'Word not found in dictionaries'

    return result


def extract_morpheme_phonemes(word, stem=None, suffix=None):
    """
    Extract phonemes for word and its morpheme parts

    Args:
        word: Full word
        stem: Stem (if identified)
        suffix: Suffix (if identified)

    Returns:
        dict with phoneme data for word, stem, and suffix
    """
    result = {
        'word': extract_phonemes(word)
    }

    if stem:
        result['stem'] = extract_phonemes(stem)

    if suffix:
        # Remove leading dash from suffix
        suffix_clean = suffix.lstrip('-')
        if suffix_clean:
            result['suffix'] = extract_phonemes(suffix_clean)

    # Detect phoneme bridge/changes at morpheme boundary
    if stem and suffix and result.get('stem') and result.get('suffix'):
        result['morpheme_bridge'] = detect_phoneme_bridge(
            result['word'],
            result['stem'],
            result['suffix']
        )

    return result


def detect_phoneme_bridge(word_phonemes, stem_phonemes, suffix_phonemes):
    """
    Detect how phonemes bridge between stem and suffix

    Args:
        word_phonemes: Phonemes for full word
        stem_phonemes: Phonemes for stem
        suffix_phonemes: Phonemes for suffix

    Returns:
        dict describing the phoneme bridge
    """
    bridge = {
        'type': 'direct',  # direct, insertion, deletion, modification
        'notes': []
    }

    # Compare ARPABET if available
    word_arpa = word_phonemes.get('arpabet_clean')
    stem_arpa = stem_phonemes.get('arpabet_clean')
    suffix_arpa = suffix_phonemes.get('arpabet_clean')

    if word_arpa and stem_arpa and suffix_arpa:
        expected = stem_arpa + ' ' + suffix_arpa
        if word_arpa != expected.strip():
            # Phoneme change detected
            bridge['type'] = 'modified'
            bridge['expected'] = expected
            bridge['actual'] = word_arpa
            bridge['notes'].append('Phoneme change at morpheme boundary')

    return bridge


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Extract phoneme representations')
    parser.add_argument('--word', required=True, help='Word to analyze')
    parser.add_argument('--stem', help='Stem (if known)')
    parser.add_argument('--suffix', help='Suffix (if known)')
    args = parser.parse_args()

    if args.stem or args.suffix:
        result = extract_morpheme_phonemes(args.word, args.stem, args.suffix)
    else:
        result = extract_phonemes(args.word)

    print(json.dumps(result, indent=2))
