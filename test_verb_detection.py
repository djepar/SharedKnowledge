#!/usr/bin/env python3
"""
Test script for the improved French verb detection system
"""

from french_text_processor import FrenchTextProcessor

def test_verb_detection():
    """Test the new spaCy + Lefff verb detection system"""
    
    print("Testing French Verb Detection with spaCy + Lefff")
    print("=" * 60)
    
    # Initialize the processor
    processor = FrenchTextProcessor()
    conjugator = processor.conjugator
    
    # Test words that were previously causing problems
    test_words = [
        # Should NOT be verbs (these were false positives before)
        "première",  # adjective
        "heure",     # noun
        "dire",      # verb (infinitive) - should be TRUE
        "chercher",  # verb (infinitive) - should be TRUE  
        "poser",     # verb (infinitive) - should be TRUE
        
        # Additional test cases
        "mange",     # verb (conjugated) - should be TRUE
        "mangent",   # verb (conjugated) - should be TRUE
        "mangeait",  # verb (conjugated) - should be TRUE
        "maison",    # noun - should be FALSE
        "grand",     # adjective - should be FALSE
        "être",      # verb (infinitive) - should be TRUE
        "est",       # verb (conjugated être) - should be TRUE
        "avoir",     # verb (infinitive) - should be TRUE
        "a",         # verb (conjugated avoir) - should be TRUE
    ]
    
    print("\n1. Individual Word Verb Detection:")
    print("-" * 40)
    for word in test_words:
        is_verb = conjugator.is_verb(word)
        lemma = conjugator.get_verb_lemma(word) if is_verb else "N/A"
        status = "✓ VERB" if is_verb else "✗ NOT VERB"
        print(f"{word:12} → {status:12} (lemma: {lemma})")
    
    # Test with a sample text
    sample_text = """
    Je mange une pomme. Tu manges une orange. 
    Elle va à la première heure de cours.
    Nous cherchons notre livre.
    """
    
    print(f"\n2. Text Analysis:")
    print("-" * 40)
    print(f"Sample text: {sample_text.strip()}")
    
    # Get verb analysis
    verb_analysis = conjugator.analyze_verb_forms(sample_text)
    
    print(f"\nVerbs found by lemma:")
    for lemma, forms in verb_analysis.items():
        print(f"  {lemma}: {', '.join(forms)}")
    
    # Test the find_verbs_in_text method (which uses our improved is_verb)
    verbs_found = processor.find_verbs_in_text(sample_text)
    print(f"\nVerbs found by find_verbs_in_text method:")
    for verb in verbs_found:
        print(f"  {verb}")

if __name__ == "__main__":
    test_verb_detection()