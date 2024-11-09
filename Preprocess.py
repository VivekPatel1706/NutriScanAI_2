import re
import numpy as np
import cv2

# Step 1: Image Preprocessing
def img_preprocess(img):
    img = np.array(img)
    gray_img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    alpha = 1.5  # Contrast control
    beta = 20    # Brightness control
    adjusted_img = cv2.convertScaleAbs(gray_img, alpha=alpha, beta=beta)
    return adjusted_img

# Step 2: Clean and Standardize Text
def clean_text(text):
    text = text.lower()
    unwanted_words = ['ingredients', 'proprietary', 'food', 'indian', 'snacks', 'savouries', 'allergen', 'advice', 'nutritional']
    for word in unwanted_words:
        text = re.sub(r'\b' + word + r'\b', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\b\w{1}\b', '', text)  # Remove single-character words
    text = re.sub(r'[^a-zA-Z0-9\s\(\)%]', '', text)  # Remove unwanted characters
    return text.strip()

# Step 3: Pattern Matching and Token Splitting
def split_token(token):
    # Match pattern where letters are followed by numbers or vice-versa, capturing each group
    match = re.findall(r'[A-Za-z]+|\d+', token)
    return match if match else [token]

# Step 4: Filter and Clean Tokens
def filter_tokens(tokens):
    filtered_tokens = []
    for token in tokens:
        token = re.sub(r'^\((.*)\)$', r'\1', token)  # Remove wrapping parentheses
        token = re.sub(r'[()]', '', token)  # Remove remaining parentheses

        if re.match(r'^[\W_]+$', token):  # Skip tokens with only non-alphanumeric symbols
            continue

        if token:  # Ensure token is not empty
            filtered_tokens.append(token)
    
    return filtered_tokens

# Step 5: n-Token Generation
def n_tokenize(tokens, max_n=3):
    n_tokenized_list = []
    for i in range(len(tokens)):
        for n in range(1, max_n + 1):
            if i + n <= len(tokens):
                n_token = ' '.join(tokens[i:i+n])  # Join tokens with space
                n_tokenized_list.append(n_token)
    return n_tokenized_list

# Main function combining all steps
def text_preprocess(extracted_text, max_n=3):
    final_text = clean_text(extracted_text)
    tokens = final_text.split()
    
    # Apply pattern matching and splitting
    split_tokens = []
    for token in tokens:
        split_tokens.extend(split_token(token))

    # Apply token filtering
    filtered_tokens = filter_tokens(split_tokens)

    # Generate n-grams from cleaned tokens
    ngram_tokens = n_tokenize(filtered_tokens, max_n=max_n)

    # Final cleanup: remove spaces from n-grams and lowercase
    final_tokens = [token.replace(' ', '').lower() for token in ngram_tokens]
    return final_tokens
