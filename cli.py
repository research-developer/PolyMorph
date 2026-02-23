#!/usr/bin/env python3
"""
Morphological Analysis CLI

Provides command-line interface for morphological analysis tools including
suffix identification, spaCy integration, and WordNet lookups.

Usage:
    morpho suffix --word <word>
    morpho analyze --word <word>
"""
import sys
import argparse
import json
from pathlib import Path


def aggregate_results(suffix_result, spacy_result, wordnet_result):
    """
    Aggregate results from multiple tools into unified analysis

    Args:
        suffix_result: Result from suffix identification
        spacy_result: Result from spaCy analysis
        wordnet_result: Result from WordNet analysis

    Returns:
        Aggregated result dictionary
    """
    word = suffix_result.get('word')

    # Aggregate lemma (prefer spaCy > WordNet > suffix stem)
    lemma = None
    if spacy_result and not spacy_result.get('error'):
        lemma = spacy_result.get('lemma')
    if not lemma and wordnet_result and not wordnet_result.get('error'):
        lemma = wordnet_result.get('lemma')
    if not lemma:
        lemma = suffix_result.get('stem', word)

    # Aggregate POS
    pos_values = {}
    suffix_pos = suffix_result.get('POS')
    # Handle list POS from suffix (ambiguous suffixes)
    if isinstance(suffix_pos, list):
        suffix_pos = suffix_pos[0] if suffix_pos else None
    if suffix_pos:
        pos_values['suffix'] = suffix_pos

    if spacy_result and not spacy_result.get('error') and spacy_result.get('POS'):
        pos_values['spacy'] = spacy_result['POS'].lower()
    if wordnet_result and not wordnet_result.get('error') and wordnet_result.get('POS'):
        pos_values['wordnet'] = wordnet_result['POS']

    # Determine POS consensus
    # Normalize values for comparison (handle potential lists)
    normalized_pos = {}
    for source, pos_val in pos_values.items():
        if isinstance(pos_val, list):
            normalized_pos[source] = pos_val[0] if pos_val else None
        else:
            normalized_pos[source] = pos_val

    unique_pos = set(v for v in normalized_pos.values() if v)
    if len(unique_pos) == 1:
        # Consensus
        pos = list(unique_pos)[0]
    elif len(unique_pos) > 1:
        # Disagreement - return all with consensus flag
        pos = {**normalized_pos, 'consensus': False}
    else:
        pos = None

    # Calculate confidence
    confidence = suffix_result.get('confidence', 0.5)
    if spacy_result and not spacy_result.get('error'):
        # Boost confidence if spaCy agrees
        if pos_values.get('spacy') == pos_values.get('suffix'):
            confidence = min(confidence + 0.2, 1.0)

    # Build aggregated result
    result = {
        'word': word,
        'lemma': lemma,
        'POS': pos,
        'stem': suffix_result.get('stem'),
        'suffix': suffix_result.get('suffix'),
        'confidence': confidence
    }

    # Add base_POS if available from suffix
    if suffix_result.get('base_POS'):
        result['base_POS'] = suffix_result['base_POS']

    # Add detailed analysis if available
    if suffix_result.get('suffix_data'):
        result['suffix_data'] = suffix_result['suffix_data']

    if spacy_result and not spacy_result.get('error'):
        result['morphological_features'] = spacy_result.get('morphological_features')
        result['tag'] = spacy_result.get('tag')

    if wordnet_result and not wordnet_result.get('error'):
        result['wordnet'] = {
            'lemmas': wordnet_result.get('lemmas', {}),
            'synsets': wordnet_result.get('synsets', [])[:2]
        }
        # Also expose synsets at top level for convenience
        if wordnet_result.get('synsets'):
            result['synsets'] = wordnet_result.get('synsets', [])[:2]

    return result


def filter_fields(data, fields):
    """
    Filter data to include only specified fields

    Args:
        data: Data to filter (dict or list)
        fields: Comma-separated field names or list

    Returns:
        Filtered data
    """
    if isinstance(fields, str):
        field_list = [f.strip() for f in fields.split(',')]
    else:
        field_list = fields

    if isinstance(data, list):
        return [filter_fields(item, field_list) for item in data]
    elif isinstance(data, dict):
        return {k: v for k, v in data.items() if k in field_list}
    else:
        return data


def format_output(data, args):
    """
    Format output according to user preferences

    Args:
        data: Data to format
        args: Command-line arguments

    Returns:
        Formatted string
    """
    from formatters import format_json, format_text, format_csv

    # Apply field filtering if requested
    if hasattr(args, 'fields') and args.fields:
        data = filter_fields(data, args.fields)

    output_format = getattr(args, 'format', 'json')
    pretty = getattr(args, 'pretty', False)
    compact = getattr(args, 'compact', False)

    if output_format == 'json':
        return format_json(data, pretty=pretty, compact=compact)
    elif output_format == 'text':
        return format_text(data)
    elif output_format == 'csv':
        return format_csv(data, headers=True)
    else:
        # Default to JSON
        return format_json(data, pretty=True)


def handle_suffix(args):
    """Handle suffix identification command"""
    try:
        # Import the identify_suffix function
        from scripts.identify_suffix import identify_suffix

        # Call the function with provided arguments
        result = identify_suffix(
            args.word,
            db_path=args.db,
            min_stem_length=args.min_stem
        )

        # Format and output
        output = format_output(result, args)
        print(output)

    except Exception as e:
        # Output error as JSON to stderr
        error_result = {
            'error': str(e),
            'word': args.word
        }
        print(json.dumps(error_result), file=sys.stderr)
        sys.exit(1)


def analyze_single_word(word, context=None):
    """Analyze a single word"""
    from scripts.identify_suffix import identify_suffix
    from scripts.extract_spacy_features import extract_spacy_features
    from scripts.extract_wordnet_features import extract_wordnet_features

    # Run all three analyses
    suffix_result = identify_suffix(word)

    spacy_result = None
    try:
        spacy_result = extract_spacy_features(word, context=context)
    except Exception:
        spacy_result = {'error': 'spaCy analysis failed'}

    wordnet_result = None
    try:
        wordnet_result = extract_wordnet_features(word)
    except Exception:
        wordnet_result = {'error': 'WordNet analysis failed'}

    # Aggregate results
    return aggregate_results(suffix_result, spacy_result, wordnet_result)


def handle_analyze(args):
    """Handle full morphological analysis command"""
    try:
        # Determine if batch mode or single word
        if args.words:
            # Batch mode
            words = [w.strip() for w in args.words.split(',') if w.strip()]
            results = []
            for word in words:
                result = analyze_single_word(word, context=getattr(args, 'context', None))
                results.append(result)
            output = format_output(results, args)
            print(output)
        else:
            # Single word mode
            result = analyze_single_word(args.word, context=getattr(args, 'context', None))
            output = format_output(result, args)
            print(output)

    except Exception as e:
        error_result = {
            'error': str(e),
            'word': getattr(args, 'word', getattr(args, 'words', 'unknown'))
        }
        print(json.dumps(error_result), file=sys.stderr)
        sys.exit(1)


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Morphological analysis tools',
        prog='morpho'
    )

    # Create subcommands
    subparsers = parser.add_subparsers(
        dest='command',
        help='Available commands'
    )

    # Suffix command
    suffix_parser = subparsers.add_parser(
        'suffix',
        help='Identify suffix in word'
    )
    suffix_parser.add_argument(
        '--word',
        required=True,
        help='Word to analyze'
    )
    suffix_parser.add_argument(
        '--db',
        default='data/unified_suffixes.json',
        help='Path to suffix database (default: data/unified_suffixes.json)'
    )
    suffix_parser.add_argument(
        '--min-stem',
        type=int,
        default=2,
        help='Minimum stem length (default: 2)'
    )
    suffix_parser.add_argument(
        '--format',
        choices=['json', 'text', 'csv'],
        default='json',
        help='Output format (default: json)'
    )
    suffix_parser.add_argument(
        '--pretty',
        action='store_true',
        help='Pretty-print JSON output'
    )
    suffix_parser.add_argument(
        '--compact',
        action='store_true',
        help='Compact JSON output (no whitespace)'
    )
    suffix_parser.add_argument(
        '--fields',
        help='Comma-separated field names to include in output'
    )
    suffix_parser.add_argument(
        '--no-color',
        action='store_true',
        help='Disable color output'
    )

    # Analyze command
    analyze_parser = subparsers.add_parser(
        'analyze',
        help='Full morphological analysis (suffix + spaCy + WordNet)'
    )
    word_group = analyze_parser.add_mutually_exclusive_group(required=True)
    word_group.add_argument(
        '--word',
        help='Single word to analyze'
    )
    word_group.add_argument(
        '--words',
        help='Comma-separated list of words to analyze'
    )
    analyze_parser.add_argument(
        '--context',
        help='Optional context sentence for disambiguation'
    )
    analyze_parser.add_argument(
        '--properties',
        help='Comma-separated properties to extract (e.g., lemma,POS,stem)'
    )
    analyze_parser.add_argument(
        '--format',
        choices=['json', 'text', 'csv'],
        default='json',
        help='Output format (default: json)'
    )
    analyze_parser.add_argument(
        '--pretty',
        action='store_true',
        help='Pretty-print JSON output'
    )
    analyze_parser.add_argument(
        '--compact',
        action='store_true',
        help='Compact JSON output (no whitespace)'
    )
    analyze_parser.add_argument(
        '--fields',
        help='Comma-separated field names to include in output'
    )
    analyze_parser.add_argument(
        '--no-color',
        action='store_true',
        help='Disable color output'
    )

    # Parse arguments
    args = parser.parse_args()

    # Dispatch to appropriate handler
    if args.command == 'suffix':
        handle_suffix(args)
    elif args.command == 'analyze':
        handle_analyze(args)
    elif args.command is None:
        parser.print_help()
        sys.exit(1)
    else:
        print(f"Unknown command: {args.command}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
