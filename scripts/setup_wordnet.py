#!/usr/bin/env python3
"""
Download and setup WordNet data via NLTK

Usage:
    python scripts/setup_wordnet.py
"""
import sys

try:
    import nltk
except ImportError:
    print("ERROR: NLTK not installed", file=sys.stderr)
    sys.exit(1)

def setup_wordnet():
    """Download WordNet data via NLTK"""
    print("Checking for WordNet data...", file=sys.stderr)

    try:
        nltk.data.find('corpora/wordnet')
        print("✓ WordNet already downloaded", file=sys.stderr)
        return True
    except LookupError:
        print("Downloading WordNet...", file=sys.stderr)
        try:
            nltk.download('wordnet', quiet=False)
            nltk.download('omw-1.4', quiet=False)  # Open Multilingual WordNet
            print("✓ WordNet download complete", file=sys.stderr)
            return True
        except Exception as e:
            print(f"ERROR: Failed to download WordNet: {e}", file=sys.stderr)
            return False

if __name__ == '__main__':
    success = setup_wordnet()
    sys.exit(0 if success else 1)
