import re

MAX_NARRATION_LEN = 40

# 1. Key Transaction Types (ALWAYS KEEP)
IMPORTANT_TYPES = {
    "MTFR", "NEFT", "RTGS", "UPI", "IMPS", "ATM", "POS", "ECOM", 
    "TRF", "TRANSFER", "CASH", "CHRG", "CHARGES", "BILL", "INB", "MBK"
}

# 2. Noise Words (ALWAYS REMOVE)
NOISE_WORDS = {
    "TO", "BY", "DR", "CR", "WITHDRAWAL", "DEPOSIT", "REF", "NO", "DT", "VAL", "BEING"
}

def limited_narration(raw_text):
    if not raw_text:
        return ""
    
    # --- Step 1: Clean Structure ---
    text = raw_text.strip()
    
    # Remove Date Prefix (e.g., 02-04-2025 or 02/04/25)
    # We remove this because you already have a Date column.
    text = re.sub(r"^\d{2}[-/]\d{2}([-/]\d{2,4})?\s*", "", text)
    
    # Replace separators (slash, hyphen, colon) with spaces for better tokenizing
    text = re.sub(r"[-/:\.]", " ", text)
    
    # Tokenize
    tokens = text.split()
    
    final_tokens = []
    
    for token in tokens:
        upper = token.upper()
        length = len(token)
        
        # --- Step 2: Filter Tokens ---
        
        # A. Always Keep Important Types (mTFR, NEFT...)
        if upper in IMPORTANT_TYPES:
            final_tokens.append(token)
            continue
            
        # B. Skip Known Noise (Dr, Cr, To...)
        if upper in NOISE_WORDS:
            continue
            
        # C. Analyze Content
        is_alpha = token.isalpha()
        is_num = token.isdigit()
        is_alnum = token.isalnum()
        
        # D. Keep Names (Alphabetic Words)
        if is_alpha:
            # Skip single random chars (e.g. "X") unless they look like initials (M, S, A, K)
            if length == 1 and upper not in ['M', 'S', 'A', 'K', 'J']:
                continue
            final_tokens.append(token)
            continue
            
        # E. Filter Numbers & IDs
        # - Skip Phone Numbers / Long Account Numbers (> 6 digits)
        # - Keep Short Numbers (e.g. "Sec 14", "No 1")
        if is_num:
            if length > 6: 
                continue # DROP (Phone numbers, etc.)
            else:
                final_tokens.append(token) # KEEP (Short numbers)
                continue

        # - Handle Mixed IDs (e.g. "JAKAH24096019")
        # - Keep them if they are reasonable length (Ref IDs)
        # - Drop if they are huge strings (> 16 chars)
        if is_alnum and length > 16:
            continue
            
        # F. Fallback: Keep whatever is left (e.g. "A-123")
        final_tokens.append(token)

    # --- Step 3: Reassemble & Truncate ---
    result = " ".join(final_tokens)
    
    # Safety: If we stripped everything, revert to raw text
    if not result:
        result = text.strip()

    # Truncate to limit (smart cut at word boundary)
    if len(result) > MAX_NARRATION_LEN:
        result = result[:MAX_NARRATION_LEN].rsplit(" ", 1)[0]

    return result