#!/usr/bin/env python3
"""
French Text Processing Script

This script provides tools for processing French texts and accessing dictionaries.
It includes functionality for:
- Loading and processing French books from the static/books/french/ directory
- Accessing French dictionaries via multiple sources
- Text analysis and word lookup
"""

import os
import re
import json
import requests
from pathlib import Path
from typing import Dict, List, Optional, Union
import unicodedata

try:
    from verbecc import Conjugator
    VERBECC_AVAILABLE = True
except ImportError:
    VERBECC_AVAILABLE = False
    print("Warning: verbecc not available. Verb conjugation features will be limited.")

try:
    import spacy
    from spacy_lefff import LefffLemmatizer, POSTagger
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    print("Warning: spaCy or spacy-lefff not available. Advanced French morphological analysis will be limited.")

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    print("Warning: pandas not available. Gender analysis will use fallback methods.")


class FrenchConjugator:
    """Handle French verb conjugation and detection using spaCy + Lefff and verbecc."""
    
    def __init__(self):
        if VERBECC_AVAILABLE:
            self.conjugator = Conjugator(lang='fr')
        else:
            self.conjugator = None
            
        # Initialize spaCy for French morphological analysis
        self.nlp = None
        if SPACY_AVAILABLE:
            try:
                self.nlp = spacy.load("fr_dep_news_trf")
                print("spaCy initialized successfully for French morphological analysis")
            except Exception as e:
                print(f"Warning: Failed to initialize spaCy: {e}")
                self.nlp = None
    
    def conjugate_verb(self, verb: str, mood: str = None, tense: str = None) -> Dict:
        """
        Conjugate a French verb.
        
        Args:
            verb: The infinitive form of the verb
            mood: Specific mood (e.g., 'indicatif', 'subjonctif')
            tense: Specific tense (e.g., 'présent', 'passé composé')
        
        Returns:
            Dictionary with conjugation results
        """
        if not self.conjugator:
            return {"error": "Conjugator not available"}
        
        try:
            result = self.conjugator.conjugate(verb)
            
            if mood and tense:
                # Extract specific mood and tense if requested
                conjugations = result.get(mood, {}).get(tense, {})
                return {
                    "verb": verb,
                    "mood": mood,
                    "tense": tense,
                    "conjugations": conjugations
                }
            
            return {
                "verb": verb,
                "full_conjugation": result
            }
            
        except Exception as e:
            return {"error": f"Failed to conjugate '{verb}': {e}"}
    
    def get_verb_info(self, verb: str) -> Dict:
        """
        Get detailed information about a French verb.
        
        Args:
            verb: The infinitive form of the verb
            
        Returns:
            Dictionary with verb information and common conjugations
        """
        if not self.conjugator:
            return {"error": "Conjugator not available"}
        
        try:
            result = self.conjugator.conjugate(verb)
            
            # Extract common tenses
            present = result.get('indicatif', {}).get('présent', {})
            imperfect = result.get('indicatif', {}).get('imparfait', {})
            future = result.get('indicatif', {}).get('futur', {})
            
            return {
                "verb": verb,
                "present": present,
                "imperfect": imperfect,
                "future": future,
                "available_moods": list(result.keys()) if result else []
            }
            
        except Exception as e:
            return {"error": f"Failed to get info for '{verb}': {e}"}
    
    def is_verb(self, word: str) -> bool:
        """
        Check if a word is a French verb (infinitive or conjugated) using spaCy + Lefff.
        
        Args:
            word: Word to check
            
        Returns:
            True if word is a French verb (infinitive or conjugated form)
        """
        if not self.nlp:
            # Fallback to basic heuristic if spaCy not available
            if self.conjugator:
                try:
                    result = self.conjugator.conjugate(word.lower())
                    return result and isinstance(result, dict) and len(result) > 0
                except Exception:
                    pass
            verb_endings = ['er', 'ir', 're', 'oir']
            return any(word.lower().endswith(ending) for ending in verb_endings)
        
        try:
            # Use spaCy + Lefff for accurate morphological analysis
            doc = self.nlp(word.lower())
            
            for token in doc:
                # Check if POS tag indicates it's a verb
                # French verb POS tags: VERB (finite verbs), AUX (auxiliary verbs)
                if token.pos_ in ['VERB', 'AUX']:
                    return True
                    
                # Also check detailed POS tags for verb forms
                # VER:* tags indicate various verb forms in French
                if token.tag_ and token.tag_.startswith('VER'):
                    return True
                    
            return False
            
        except Exception as e:
            # Fallback if spaCy processing fails
            if self.conjugator:
                try:
                    result = self.conjugator.conjugate(word.lower())
                    return result and isinstance(result, dict) and len(result) > 0
                except Exception:
                    pass
            return False
            
    def get_verb_lemma(self, word: str) -> Optional[str]:
        """
        Get the lemma (infinitive form) of a French verb.
        
        Args:
            word: Word to analyze (can be conjugated form)
            
        Returns:
            Lemma/infinitive form if it's a verb, None otherwise
        """
        if not self.nlp:
            return None
            
        try:
            doc = self.nlp(word.lower())
            
            for token in doc:
                if token.pos_ in ['VERB', 'AUX'] or (token.tag_ and token.tag_.startswith('VER')):
                    return token.lemma_
                    
            return None
            
        except Exception:
            return None
            
    def analyze_verb_forms(self, text: str) -> Dict[str, List[str]]:
        """
        Analyze text to find all verb forms and their lemmas.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with verb forms categorized by lemma
        """
        if not self.nlp:
            return {}
            
        try:
            doc = self.nlp(text)
            verb_analysis = {}
            
            for token in doc:
                if token.pos_ in ['VERB', 'AUX'] or (token.tag_ and token.tag_.startswith('VER')):
                    lemma = token.lemma_
                    form = token.text.lower()
                    
                    if lemma not in verb_analysis:
                        verb_analysis[lemma] = []
                    
                    if form not in verb_analysis[lemma]:
                        verb_analysis[lemma].append(form)
                        
            return verb_analysis
            
        except Exception:
            return {}


class FrenchGenderAnalyzer:
    """Handle French grammatical gender analysis."""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.gender_data_path = self.base_dir / "data" / "gender" / "french_nouns_gender.tsv"
        self.gender_dict = {}
        self.load_gender_data()
    
    def load_gender_data(self):
        """Load French noun gender data from TSV file."""
        if not self.gender_data_path.exists():
            print(f"Warning: Gender data file not found at {self.gender_data_path}")
            return
        
        try:
            if PANDAS_AVAILABLE:
                df = pd.read_csv(self.gender_data_path, sep='\t')
                # Create dictionary mapping noun to gender
                for _, row in df.iterrows():
                    noun = row['noun'].lower()
                    gender = row['gender']
                    count = row['count']
                    
                    # If noun already exists, keep the one with higher count
                    if noun not in self.gender_dict or count > self.gender_dict[noun]['count']:
                        self.gender_dict[noun] = {'gender': gender, 'count': count}
            else:
                # Fallback method without pandas
                with open(self.gender_data_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()[1:]  # Skip header
                    for line in lines:
                        parts = line.strip().split('\t')
                        if len(parts) >= 3:
                            noun = parts[0].lower()
                            gender = parts[1]
                            count = int(parts[2])
                            
                            if noun not in self.gender_dict or count > self.gender_dict[noun]['count']:
                                self.gender_dict[noun] = {'gender': gender, 'count': count}
            
            print(f"Loaded {len(self.gender_dict)} French nouns with gender information")
            
        except Exception as e:
            print(f"Error loading gender data: {e}")
    
    def get_word_gender(self, word: str) -> Optional[str]:
        """
        Get the grammatical gender of a French word.
        
        Args:
            word: French word to analyze
            
        Returns:
            'm' for masculine, 'f' for feminine, None if unknown
        """
        word_lower = word.lower()
        
        # Check exact match in dictionary
        if word_lower in self.gender_dict:
            return self.gender_dict[word_lower]['gender']
        
        # Fallback to rule-based gender prediction (common patterns)
        return self.predict_gender_by_ending(word_lower)
    
    def predict_gender_by_ending(self, word: str) -> Optional[str]:
        """
        Predict gender based on word endings (rule-based approach).
        
        Args:
            word: French word in lowercase
            
        Returns:
            'm' for masculine, 'f' for feminine, None if uncertain
        """
        # Common feminine endings
        feminine_endings = [
            'tion', 'sion', 'ance', 'ence', 'ette', 'elle', 'esse', 'ise', 'ure', 'té', 'tié',
            'ie', 'ée', 'euse', 'trice', 'ade', 'ude', 'age'  # Note: 'age' has exceptions
        ]
        
        # Common masculine endings
        masculine_endings = [
            'ment', 'isme', 'oir', 'eau', 'eu', 'ou', 'er', 'al', 'el', 'il', 'ol', 'ul',
            'ant', 'ent', 'in', 'on', 'un'
        ]
        
        # Check feminine endings first (usually more reliable)
        for ending in feminine_endings:
            if word.endswith(ending):
                # Exception: some -age words are feminine (like 'page', 'image', 'plage')
                if ending == 'age' and word in ['page', 'image', 'plage', 'cage', 'rage', 'nage']:
                    return 'f'
                elif ending == 'age':
                    return 'm'  # Most -age words are masculine
                else:
                    return 'f'
        
        # Check masculine endings
        for ending in masculine_endings:
            if word.endswith(ending):
                return 'm'
        
        return None  # Unable to predict
    
    def analyze_text_gender(self, words: List[str]) -> Dict:
        """
        Analyze the gender distribution of words in a text.
        
        Args:
            words: List of French words to analyze
            
        Returns:
            Dictionary with gender analysis results
        """
        gender_counts = {'m': 0, 'f': 0, 'unknown': 0}
        gendered_words = {'m': [], 'f': [], 'unknown': []}
        
        for word in words:
            gender = self.get_word_gender(word)
            
            if gender == 'm':
                gender_counts['m'] += 1
                if word not in gendered_words['m']:
                    gendered_words['m'].append(word)
            elif gender == 'f':
                gender_counts['f'] += 1
                if word not in gendered_words['f']:
                    gendered_words['f'].append(word)
            else:
                gender_counts['unknown'] += 1
                if word not in gendered_words['unknown']:
                    gendered_words['unknown'].append(word)
        
        total_gendered = gender_counts['m'] + gender_counts['f']
        
        return {
            'counts': gender_counts,
            'words': gendered_words,
            'percentages': {
                'masculine': round((gender_counts['m'] / len(words)) * 100, 2) if words else 0,
                'feminine': round((gender_counts['f'] / len(words)) * 100, 2) if words else 0,
                'unknown': round((gender_counts['unknown'] / len(words)) * 100, 2) if words else 0
            },
            'gender_ratio': {
                'masculine': round((gender_counts['m'] / total_gendered) * 100, 2) if total_gendered else 0,
                'feminine': round((gender_counts['f'] / total_gendered) * 100, 2) if total_gendered else 0
            }
        }


class FrenchDictionary:
    """Handle French dictionary lookups from multiple sources."""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.books_dir = self.base_dir / "static" / "books" / "french"
        
    def lookup_word_api(self, word: str) -> Optional[Dict]:
        """
        Look up a French word using the Free Dictionary API.
        Falls back to French synonyms API if available.
        """
        # Clean the word
        word = word.lower().strip()
        
        try:
            # Try Free Dictionary API (limited French support)
            url = f"https://api.dictionaryapi.dev/api/v2/entries/fr/{word}"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                return response.json()
            
        except requests.RequestException as e:
            print(f"API lookup failed for '{word}': {e}")
            
        try:
            # Try French synonyms API
            url = f"https://synonymes-api.now.sh/{word}"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                synonyms_data = response.json()
                return {
                    "word": word,
                    "synonyms": synonyms_data,
                    "source": "synonymes-api"
                }
                
        except requests.RequestException as e:
            print(f"Synonyms API lookup failed for '{word}': {e}")
            
        return None
    
    def download_freedict_dictionary(self) -> bool:
        """
        Download French-English dictionary from FreeDict.
        Returns True if successful, False otherwise.
        """
        dict_dir = self.base_dir / "dictionaries"
        dict_dir.mkdir(exist_ok=True)
        
        try:
            # Download French-English dictionary
            url = "https://download.freedict.org/dictionaries/fra-eng/fra-eng.stardict.tar.xz"
            dict_file = dict_dir / "fra-eng.stardict.tar.xz"
            
            print(f"Downloading French-English dictionary to {dict_file}...")
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                with open(dict_file, 'wb') as f:
                    f.write(response.content)
                print("Dictionary downloaded successfully!")
                return True
            else:
                print(f"Failed to download dictionary: {response.status_code}")
                return False
                
        except requests.RequestException as e:
            print(f"Error downloading dictionary: {e}")
            return False


class FrenchTextProcessor:
    """Process French texts and perform various analysis tasks."""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.books_dir = self.base_dir / "static" / "books" / "french"
        self.dictionary = FrenchDictionary()
        self.conjugator = FrenchConjugator()
        self.gender_analyzer = FrenchGenderAnalyzer()
        
    def list_available_books(self) -> List[str]:
        """List all available French books."""
        if not self.books_dir.exists():
            return []
        
        books = []
        for file_path in self.books_dir.glob("*.txt"):
            books.append(file_path.stem)
        
        return sorted(books)
    
    def load_book(self, book_name: str) -> Optional[str]:
        """
        Load a French book by name.
        
        Args:
            book_name: Name of the book file (with or without .txt extension)
        
        Returns:
            Book content as string, or None if not found
        """
        if not book_name.endswith('.txt'):
            book_name += '.txt'
            
        book_path = self.books_dir / book_name
        
        if not book_path.exists():
            print(f"Book not found: {book_path}")
            return None
            
        try:
            with open(book_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return content
        except Exception as e:
            print(f"Error reading book {book_name}: {e}")
            return None
    
    def clean_gutenberg_text(self, text: str) -> str:
        """
        Remove Project Gutenberg headers and footers from text.
        
        Args:
            text: Raw text from Project Gutenberg
            
        Returns:
            Cleaned text with just the book content
        """
        # Find the start of actual content (after *** START OF...)
        start_match = re.search(r'\*\*\* START OF.*?\*\*\*', text, re.DOTALL | re.IGNORECASE)
        if start_match:
            text = text[start_match.end():]
        
        # Find the end of actual content (before *** END OF...)
        end_match = re.search(r'\*\*\* END OF.*?\*\*\*', text, re.DOTALL | re.IGNORECASE)
        if end_match:
            text = text[:end_match.start()]
        
        # Remove any remaining Project Gutenberg metadata
        text = re.sub(r'Project Gutenberg.*?(?=\n\n|\n[A-Z])', '', text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'Language:.*?\n', '', text, flags=re.IGNORECASE)
        text = re.sub(r'Release date:.*?\n', '', text, flags=re.IGNORECASE)
        text = re.sub(r'Credits:.*?\n', '', text, flags=re.IGNORECASE)
        text = re.sub(r'Author:.*?\n', '', text, flags=re.IGNORECASE)
        text = re.sub(r'Title:.*?\n', '', text, flags=re.IGNORECASE)
        
        return text.strip()
    
    def extract_words(self, text: str, min_length: int = 3) -> List[str]:
        """
        Extract words from French text.
        
        Args:
            text: Input text
            min_length: Minimum word length to include
            
        Returns:
            List of unique words
        """
        # Clean Project Gutenberg formatting
        text = self.clean_gutenberg_text(text)
        
        # Extract words (French characters including accents)
        words = re.findall(r'\b[a-zA-ZàâäéèêëïîôöùûüÿçÀÂÄÉÈÊËÏÎÔÖÙÛÜŸÇ]+\b', text)
        
        # Filter by length and convert to lowercase
        words = [word.lower() for word in words if len(word) >= min_length]
        
        # Remove duplicates while preserving order
        unique_words = list(dict.fromkeys(words))
        
        return unique_words
    
    def count_sentences(self, text: str) -> int:
        """
        Count the number of sentences in French text.
        
        Args:
            text: Input text
            
        Returns:
            Number of sentences
        """
        # Clean the text first
        text = self.clean_gutenberg_text(text)
        
        # French sentence endings
        sentence_endings = r'[.!?]+'
        
        # Split by sentence endings
        sentences = re.split(sentence_endings, text)
        
        # Filter out empty sentences and very short ones (likely fragments)
        valid_sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 10]
        
        return len(valid_sentences)
    
    def extract_sentences(self, text: str, max_sentences: int = 10) -> List[str]:
        """
        Extract individual sentences from French text.
        
        Args:
            text: Input text
            max_sentences: Maximum number of sentences to return
            
        Returns:
            List of sentences
        """
        # Clean the text first
        text = self.clean_gutenberg_text(text)
        
        # French sentence endings
        sentence_endings = r'([.!?]+)'
        
        # Split by sentence endings but keep the delimiters
        parts = re.split(sentence_endings, text)
        
        sentences = []
        for i in range(0, len(parts) - 1, 2):
            sentence = parts[i].strip()
            if i + 1 < len(parts):
                sentence += parts[i + 1]
            
            # Filter out very short sentences and clean up
            if len(sentence.strip()) > 20:
                sentence = re.sub(r'\s+', ' ', sentence.strip())
                sentences.append(sentence)
                
                if len(sentences) >= max_sentences:
                    break
        
        return sentences
    
    def find_verbs_in_text(self, text: str, max_verbs: int = 20) -> List[str]:
        """
        Find potential French verbs in text.
        
        Args:
            text: Input text
            max_verbs: Maximum number of verbs to return
            
        Returns:
            List of potential verbs (infinitive forms)
        """
        words = self.extract_words(text)
        verbs = []
        
        for word in words:
            if self.conjugator.is_verb(word) and word not in verbs:
                verbs.append(word)
                if len(verbs) >= max_verbs:
                    break
        
        return verbs
    
    def get_word_frequency(self, text: str, top_n: int = 50) -> Dict[str, int]:
        """
        Get word frequency analysis of the text.
        
        Args:
            text: Input text
            top_n: Number of most frequent words to return
            
        Returns:
            Dictionary with word frequencies
        """
        # Clean the text first
        text = self.clean_gutenberg_text(text)
        
        # Extract all words (including duplicates for counting)
        words = re.findall(r'\b[a-zA-ZàâäéèêëïîôöùûüÿçÀÂÄÉÈÊËÏÎÔÖÙÛÜŸÇ]+\b', text)
        words = [word.lower() for word in words if len(word) >= 3]
        
        # Count frequencies
        frequency = {}
        for word in words:
            frequency[word] = frequency.get(word, 0) + 1
        
        # Sort by frequency and return top N
        sorted_words = sorted(frequency.items(), key=lambda x: x[1], reverse=True)
        
        return dict(sorted_words[:top_n])
    
    def analyze_book(self, book_name: str) -> Dict:
        """
        Perform comprehensive analysis of a French book.
        
        Args:
            book_name: Name of the book to analyze
            
        Returns:
            Analysis results dictionary
        """
        content = self.load_book(book_name)
        if not content:
            return {"error": f"Could not load book: {book_name}"}
        
        words = self.extract_words(content)
        frequency = self.get_word_frequency(content)
        
        # Basic statistics
        total_chars = len(content)
        total_words = len(content.split())
        unique_words = len(words)
        
        # Sentence analysis
        sentence_count = self.count_sentences(content)
        sample_sentences = self.extract_sentences(content, 5)
        
        # Verb analysis
        verbs_found = self.find_verbs_in_text(content, 10)
        
        # Gender analysis
        gender_analysis = self.gender_analyzer.analyze_text_gender(words)
        
        # Average word length
        if words:
            avg_word_length = sum(len(word) for word in words) / len(words)
        else:
            avg_word_length = 0
        
        # Average sentence length
        if sentence_count > 0:
            avg_sentence_length = total_words / sentence_count
        else:
            avg_sentence_length = 0
        
        return {
            "book": book_name,
            "statistics": {
                "total_characters": total_chars,
                "total_words": total_words,
                "unique_words": unique_words,
                "sentence_count": sentence_count,
                "average_word_length": round(avg_word_length, 2),
                "average_sentence_length": round(avg_sentence_length, 2)
            },
            "top_words": frequency,
            "sample_words": words[:20],
            "sample_sentences": sample_sentences,
            "verbs_found": verbs_found,
            "gender_analysis": gender_analysis
        }
    
    def lookup_words(self, words: List[str]) -> Dict[str, Dict]:
        """
        Look up multiple words in the dictionary.
        
        Args:
            words: List of words to look up
            
        Returns:
            Dictionary with lookup results
        """
        results = {}
        
        for word in words:
            print(f"Looking up: {word}")
            result = self.dictionary.lookup_word_api(word)
            results[word] = result
            
        return results


def main():
    """Main function to demonstrate the French text processor."""
    processor = FrenchTextProcessor()
    
    print("French Text Processor")
    print("=" * 50)
    
    # List available books
    books = processor.list_available_books()
    print(f"\nAvailable books ({len(books)}):")
    for i, book in enumerate(books, 1):
        print(f"  {i}. {book}")
    
    if not books:
        print("No books found in static/books/french/")
        return
    
    # Analyze first book as example
    book_name = books[0]
    print(f"\nAnalyzing: {book_name}")
    print("-" * 30)
    
    analysis = processor.analyze_book(book_name)
    
    if "error" in analysis:
        print(f"Error: {analysis['error']}")
        return
    
    # Display statistics
    stats = analysis["statistics"]
    print(f"Total characters: {stats['total_characters']:,}")
    print(f"Total words: {stats['total_words']:,}")
    print(f"Unique words: {stats['unique_words']:,}")
    print(f"Total sentences: {stats['sentence_count']:,}")
    print(f"Average word length: {stats['average_word_length']}")
    print(f"Average sentence length: {stats['average_sentence_length']} words")
    
    # Display top words
    print(f"\nTop 10 most frequent words:")
    for word, count in list(analysis["top_words"].items())[:10]:
        print(f"  {word}: {count}")
    
    # Display sample sentences
    print(f"\nSample sentences:")
    for i, sentence in enumerate(analysis["sample_sentences"][:3], 1):
        print(f"  {i}. {sentence[:100]}{'...' if len(sentence) > 100 else ''}")
    
    # Display found verbs
    print(f"\nVerbs found in text:")
    verbs = analysis["verbs_found"][:5]
    for verb in verbs:
        print(f"  {verb}")
    
    # Gender analysis
    gender_data = analysis["gender_analysis"]
    print(f"\nGrammatical Gender Analysis:")
    print(f"  Masculine words: {gender_data['counts']['m']} ({gender_data['percentages']['masculine']}%)")
    print(f"  Feminine words: {gender_data['counts']['f']} ({gender_data['percentages']['feminine']}%)")
    print(f"  Unknown gender: {gender_data['counts']['unknown']} ({gender_data['percentages']['unknown']}%)")
    
    if gender_data['counts']['m'] + gender_data['counts']['f'] > 0:
        print(f"\nGender ratio (gendered words only):")
        print(f"  Masculine: {gender_data['gender_ratio']['masculine']}%")
        print(f"  Feminine: {gender_data['gender_ratio']['feminine']}%")
    
    # Sample gendered words
    print(f"\nSample masculine words:")
    masculine_words = gender_data['words']['m'][:8]
    for word in masculine_words:
        print(f"  {word} (m)")
    
    print(f"\nSample feminine words:")
    feminine_words = gender_data['words']['f'][:8]
    for word in feminine_words:
        print(f"  {word} (f)")
    
    # Verb conjugation example
    if verbs and VERBECC_AVAILABLE:
        print(f"\nVerb conjugation example - '{verbs[0]}':")
        conjugation = processor.conjugator.get_verb_info(verbs[0])
        if "error" not in conjugation:
            present = conjugation.get("present", {})
            if present:
                for person, form in list(present.items())[:3]:
                    print(f"  {person}: {form}")
        else:
            print(f"  {conjugation['error']}")
    
    # Dictionary lookup example
    print(f"\nDictionary lookup example (first 2 words):")
    sample_words = analysis["sample_words"][:2]
    lookups = processor.lookup_words(sample_words)
    
    for word, result in lookups.items():
        if result:
            print(f"  {word}: Found")
        else:
            print(f"  {word}: Not found")


if __name__ == "__main__":
    main()
