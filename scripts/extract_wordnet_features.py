#!/usr/bin/env python3
"""
Extract morphological features using NLTK WordNet

Usage:
    python extract_wordnet_features.py --word "running"
"""
import json
import sys

try:
    import nltk
    from nltk.corpus import wordnet as wn
except ImportError:
    print(json.dumps({'error': 'NLTK not installed'}))
    sys.exit(1)

# Global cache to ensure WordNet is loaded once (singleton pattern)
_WORDNET_INITIALIZED = False

def ensure_wordnet_loaded():
    """
    Ensure WordNet is loaded (singleton pattern)

    First call triggers loading, subsequent calls are instant
    """
    global _WORDNET_INITIALIZED
    if not _WORDNET_INITIALIZED:
        # Trigger WordNet loading by making a dummy query
        try:
            _ = wn.synsets('test')
            _WORDNET_INITIALIZED = True
        except Exception:
            pass
    return _WORDNET_INITIALIZED

def extract_wordnet_features(word):
    """
    Extract features using WordNet morphy and synsets

    Args:
        word: Word to analyze

    Returns:
        Feature dict
    """
    # Ensure WordNet is loaded (cached after first call)
    ensure_wordnet_loaded()

    results = {
        'word': word,
        'source': 'wordnet',
        'lemmas': {},
        'synsets': []
    }

    # Try lemmatization for each POS
    pos_tags = [
        (wn.NOUN, 'noun'),
        (wn.VERB, 'verb'),
        (wn.ADJ, 'adjective'),
        (wn.ADV, 'adverb')
    ]

    for wn_pos, pos_name in pos_tags:
        lemma = wn.morphy(word, wn_pos)
        if lemma:
            results['lemmas'][pos_name] = lemma

    # Get synsets (word senses)
    synsets = wn.synsets(word)
    for synset in synsets[:3]:  # Top 3 senses
        results['synsets'].append({
            'name': synset.name(),
            'POS': synset.pos(),
            'definition': synset.definition(),
            'examples': synset.examples()[:2]
        })

    # Determine most likely POS and lemma
    if results['lemmas']:
        # Prefer noun, then verb, then adj, then adv
        for pos in ['noun', 'verb', 'adjective', 'adverb']:
            if pos in results['lemmas']:
                results['POS'] = pos
                results['lemma'] = results['lemmas'][pos]
                break
    elif results['synsets']:
        # Use first synset POS
        first_pos = results['synsets'][0]['POS']
        pos_map = {'n': 'noun', 'v': 'verb', 'a': 'adjective', 's': 'adjective', 'r': 'adverb'}
        results['POS'] = pos_map.get(first_pos, 'unknown')
        results['lemma'] = word  # WordNet didn't change it
    else:
        results['POS'] = None
        results['lemma'] = word

    return results

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Extract WordNet features')
    parser.add_argument('--word', required=True, help='Word to analyze')
    args = parser.parse_args()

    try:
        # Check if WordNet is downloaded
        wn.synsets('test')
    except LookupError:
        print("Downloading WordNet data...", file=sys.stderr)
        nltk.download('wordnet', quiet=True)
        nltk.download('omw-1.4', quiet=True)

    result = extract_wordnet_features(args.word)
    print(json.dumps(result, indent=2))
