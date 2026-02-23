#!/usr/bin/env python3
"""
Extract morphological features using spaCy

Usage:
    python extract_spacy_features.py --word "running" --context "They are running"
"""
import json
import sys

try:
    import spacy
except ImportError:
    print(json.dumps({'error': 'spaCy not installed'}))
    sys.exit(1)

def extract_spacy_features(word, context=None, model='en_core_web_sm'):
    """
    Extract morphological features for a word using spaCy

    Args:
        word: Word to analyze
        context: Optional context sentence
        model: spaCy model

    Returns:
        Feature dict
    """
    try:
        nlp = spacy.load(model)
    except OSError:
        print(f"Model {model} not found. Please run: python -m spacy download {model}", file=sys.stderr)
        return {'error': f'spaCy model {model} not found'}

    # If no context, analyze word alone
    if not context:
        context = word

    doc = nlp(context)

    # Find the target word in doc
    target_token = None
    for token in doc:
        if token.text.lower() == word.lower():
            target_token = token
            break

    if not target_token:
        return {'error': f'Word "{word}" not found in context'}

    features = {
        'word': word,
        'lemma': target_token.lemma_,
        'POS': target_token.pos_,
        'tag': target_token.tag_,
        'morphological_features': target_token.morph.to_dict(),
        'dependency': target_token.dep_,
        'is_oov': target_token.is_oov,
        'is_alpha': target_token.is_alpha,
        'is_stop': target_token.is_stop,
        'source': 'spacy'
    }

    return features

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Extract spaCy morphological features')
    parser.add_argument('--word', required=True, help='Word to analyze')
    parser.add_argument('--context', help='Optional context sentence')
    parser.add_argument('--model', default='en_core_web_sm', help='spaCy model')
    args = parser.parse_args()

    result = extract_spacy_features(args.word, args.context, args.model)
    print(json.dumps(result, indent=2))
