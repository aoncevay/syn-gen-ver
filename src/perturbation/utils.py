import re
import nltk
from typing import List, Dict, Tuple, Any, Optional

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

def split_into_sentences(text: str) -> List[str]:
    """
    Split text into sentences using NLTK's punkt tokenizer.
    
    Args:
        text: The input text to split
        
    Returns:
        List of sentences
    """
    return nltk.sent_tokenize(text)

def get_sentence_spans(text: str) -> List[Tuple[str, int, int]]:
    """
    Get sentences with their spans in the original text.
    
    Args:
        text: The input text
        
    Returns:
        List of tuples with (sentence, start_index, end_index)
    """
    sentences = split_into_sentences(text)
    spans = []
    start_idx = 0
    
    for sent in sentences:
        # Find the sentence in the original text
        sent_idx = text.find(sent, start_idx)
        if sent_idx != -1:
            spans.append((sent, sent_idx, sent_idx + len(sent)))
            start_idx = sent_idx + len(sent)
    
    return spans

def replace_span_in_text(text: str, start: int, end: int, replacement: str) -> str:
    """
    Replace a span in the text with a replacement string.
    
    Args:
        text: The original text
        start: Start index of the span to replace
        end: End index of the span to replace
        replacement: The replacement string
        
    Returns:
        Modified text with the span replaced
    """
    return text[:start] + replacement + text[end:] 