"""
Word filtering module for chat censorship
"""
import re

# Common English curse words and slurs to filter
FILTERED_WORDS = [
    # Common profanity
    'damn', 'hell', 'crap', 'shit', 'fuck', 'bitch', 'ass', 'asshole',
    'bastard', 'piss', 'pissed', 'cunt', 'cock', 'dick', 'pussy',
    'whore', 'slut', 'fag', 'faggot', 'nigger', 'nigga', 'kike',
    'chink', 'spic', 'wetback', 'retard', 'retarded', 'gay',
    
    # Variations and common misspellings
    'f*ck', 'f**k', 'f***', 'sh*t', 's**t', 'a$$', 'b*tch', 'b**ch',
    'd*mn', 'h*ll', 'cr*p', 'p*ss', 'c*nt', 'c*ck', 'd*ck', 'p*ssy',
    'wh*re', 'sl*t', 'f*g', 'f*ggot', 'n*gger', 'n*gga', 'k*ke',
    'ch*nk', 'sp*c', 'ret*rd', 'g*y',
    
    # Common abbreviations
    'wtf', 'omg', 'lol', 'rofl', 'stfu', 'gtfo', 'fml', 'smh',
    'tbh', 'imo', 'fyi', 'btw', 'idk', 'irl', 'af', 'asf',
    
    # Add more as needed
]

def filter_message(message, enabled=True):
    """
    Filter profanity from a message if censorship is enabled
    
    Args:
        message (str): The message to filter
        enabled (bool): Whether censorship is enabled
        
    Returns:
        str: The filtered message
    """
    if not enabled or not message:
        return message
    
    filtered_message = message
    
    for word in FILTERED_WORDS:
        # Create a case-insensitive regex pattern
        pattern = re.compile(re.escape(word), re.IGNORECASE)
        
        # Replace with asterisks
        asterisks = '*' * len(word)
        filtered_message = pattern.sub(asterisks, filtered_message)
    
    return filtered_message

def get_filtered_words():
    """Get the list of filtered words"""
    return FILTERED_WORDS.copy()

def add_filtered_word(word):
    """Add a word to the filter list"""
    if word.lower() not in [w.lower() for w in FILTERED_WORDS]:
        FILTERED_WORDS.append(word.lower())

def remove_filtered_word(word):
    """Remove a word from the filter list"""
    FILTERED_WORDS[:] = [w for w in FILTERED_WORDS if w.lower() != word.lower()]
