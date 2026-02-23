"""
Plain text output formatter
"""
from typing import Dict, List, Union, Any


def format_text(data: Union[Dict, List]) -> str:
    """
    Format data as human-readable plain text

    Args:
        data: Data to format (dict or list)

    Returns:
        Plain text string
    """
    if isinstance(data, list):
        # Format list of results
        parts = []
        for i, item in enumerate(data):
            if i > 0:
                parts.append("\n" + "-" * 40 + "\n")
            parts.append(format_single_result(item))
        return "\n".join(parts)
    else:
        return format_single_result(data)


def format_single_result(data: Dict[str, Any]) -> str:
    """Format a single analysis result"""
    lines = []

    # Word
    if 'word' in data:
        lines.append(f"Word: {data['word']}")

    # Lemma
    if 'lemma' in data and data['lemma']:
        lines.append(f"Lemma: {data['lemma']}")

    # POS
    if 'POS' in data and data['POS']:
        pos_str = format_pos(data['POS'])
        lines.append(f"POS: {pos_str}")

    # Stem
    if 'stem' in data and data['stem']:
        lines.append(f"Stem: {data['stem']}")

    # Suffix
    if 'suffix' in data and data['suffix']:
        lines.append(f"Suffix: {data['suffix']}")

    # Base POS
    if 'base_POS' in data and data['base_POS']:
        base_pos = data['base_POS']
        if isinstance(base_pos, list):
            base_pos = ', '.join(base_pos)
        lines.append(f"Base POS: {base_pos}")

    # Confidence
    if 'confidence' in data and data['confidence'] is not None:
        lines.append(f"Confidence: {data['confidence']:.2f}")

    # Tag
    if 'tag' in data and data['tag']:
        lines.append(f"Tag: {data['tag']}")

    # Morphological features
    if 'morphological_features' in data and data['morphological_features']:
        features = data['morphological_features']
        if isinstance(features, dict):
            feat_str = ', '.join(f"{k}={v}" for k, v in features.items())
            lines.append(f"Morphological Features: {feat_str}")

    # Phonemes
    if 'phonemes' in data and data['phonemes']:
        phonemes = data['phonemes']
        if 'word' in phonemes and phonemes['word'].get('arpabet'):
            lines.append(f"Phonemes (ARPABET): {phonemes['word']['arpabet']}")
        if 'word' in phonemes and phonemes['word'].get('ipa'):
            lines.append(f"Phonemes (IPA): {phonemes['word']['ipa']}")

        # Show stem and suffix phonemes if available
        if 'stem' in phonemes and phonemes['stem'].get('arpabet'):
            lines.append(f"  Stem phonemes: {phonemes['stem']['arpabet']}")
        if 'suffix' in phonemes and phonemes['suffix'].get('arpabet'):
            lines.append(f"  Suffix phonemes: {phonemes['suffix']['arpabet']}")

    return '\n'.join(lines)


def format_pos(pos) -> str:
    """Format POS value (handles dict with consensus flag)"""
    if isinstance(pos, dict):
        if pos.get('consensus') is False:
            # Show disagreement
            parts = []
            for source in ['suffix', 'spacy', 'wordnet']:
                if source in pos:
                    parts.append(f"{source}:{pos[source]}")
            return f"[{', '.join(parts)}] (no consensus)"
        else:
            # Extract value from dict
            for key in ['suffix', 'spacy', 'wordnet']:
                if key in pos:
                    return str(pos[key])
    return str(pos)
