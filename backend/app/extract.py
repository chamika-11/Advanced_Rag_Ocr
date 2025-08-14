import re
import spacy
import pytesseract
import cv2

nlp = spacy.load("en_core_web_sm")

def extract_refex(text):
    data = {}
    
    # More precise amount pattern - only matches clear monetary values
    amount_pattern = r'(?:(?:USD|LKR|Rs\.?|₨)\s*[\d,]+(?:\.\d{2})?|\$\s*[\d,]+(?:\.\d{2})?)'
    
    # More specific ID patterns for different types
    nic_pattern = r'\b\d{9}[vVxX]\b|\b\d{12}\b' 
    phone_pattern = r'(?:\+94|0)?(?:7[01245678]\d{7}|11\d{7})'  
    
    # Extract amounts with better filtering
    amounts = re.findall(amount_pattern, text, re.IGNORECASE)
    amounts = [amount.strip() for amount in amounts if amount.strip()]
    
    # Extract IDs
    nic_ids = re.findall(nic_pattern, text)
    
    # Extract phone numbers
    phone_numbers = re.findall(phone_pattern, text)
    
    # Only add to data if we found valid matches
    if amounts:
        data["amounts"] = list(set(amounts)) 
    if nic_ids:
        data["nic_numbers"] = list(set(nic_ids))
    if phone_numbers:
        data["phone_numbers"] = list(set(phone_numbers))

    return data


def extract_with_ner(text):
    doc = nlp(text)
    data = {"names": [], "organizations": [], "locations": []}
    
    # Common false positive patterns to filter out
    false_positive_patterns = [
        r'^[A-Z]{1,3}$',  # Single letters or very short acronyms
        r'^\d+$',  # Pure numbers
        r'^[^a-zA-Z]*$',  # No letters at all
        r'^(Email|Phone|Address|Name|Date)$',  # Common field labels
        r'^\W+$',  # Only special characters
        r'^(Al|RAG|CNN|OOP|MVC|NET|HTML|CSS|SQL)$',  # Tech acronyms that aren't orgs
    ]
    
    # Common tech terms that aren't organizations
    tech_terms = {
        'html', 'css', 'javascript', 'python', 'java', 'react', 'node', 'express',
        'pytorch', 'tensorflow', 'langchain', 'api', 'sql', 'mongodb', 'git',
        'docker', 'kubernetes', 'aws', 'azure', 'gcp', 'ai', 'ml', 'rag', 'llm',
        'cnn', 'rnn', 'nlp', 'ocr', 'mvc', 'oop', 'rest', 'json', 'xml', 'http',
        'https', 'tcp', 'ip', 'dns', 'ssl', 'tls', 'jwt', 'oauth'
    }
    
    # Email pattern to exclude from names/orgs
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    
    for ent in doc.ents:
        entity_text = ent.text.strip()
        entity_lower = entity_text.lower()
        
        # Skip if it matches email pattern
        if re.match(email_pattern, entity_text):
            continue
            
        # Skip if it matches false positive patterns
        is_false_positive = any(re.match(pattern, entity_text, re.IGNORECASE) 
                               for pattern in false_positive_patterns)
        if is_false_positive:
            continue
            
        # Skip tech terms for organizations
        if ent.label_ == "ORG" and entity_lower in tech_terms:
            continue
            
        # Filter based on entity type with additional validation
        if ent.label_ == "PERSON":
            if len(entity_text.split()) >= 2 or (entity_text.istitle() and len(entity_text) > 3):
                data["names"].append(entity_text)
                
        elif ent.label_ == "ORG":
            if (len(entity_text) > 2 and 
                not entity_text.isupper() or 
                any(word in entity_lower for word in ['bank', 'company', 'corp', 'ltd', 'institute', 'university', 'college'])):
                data["organizations"].append(entity_text)
                
        elif ent.label_ in ["GPE", "LOC"]:
            # Only add real-looking locations
            if len(entity_text) > 2 and entity_lower not in tech_terms:
                data["locations"].append(entity_text)
    
    # Remove duplicates and sort
    for key in data:
        data[key] = sorted(list(set(data[key])))
    
    return data


def extract_kv_from_image(image_path, keywords=None):
    if keywords is None:
        keywords = ["name", "account", "date", "loan", "amount", "nic", "id", "number", "address", "phone"]

    image = cv2.imread(image_path)
    
    # Enhanced preprocessing
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Apply denoising
    denoised = cv2.fastNlMeansDenoising(gray)
    
    # Apply threshold
    _, thresh = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    # Custom OCR config
    custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz@.,-/:()'
    
    data = pytesseract.image_to_data(thresh, config=custom_config, output_type=pytesseract.Output.DICT)

    extracted = {}
    
    # Filter and process OCR results
    valid_items = []
    for i in range(len(data['text'])):
        if (int(data['conf'][i]) > 50 and  
            len(data['text'][i].strip()) > 0):
            valid_items.append({
                'text': data['text'][i].strip(),
                'conf': int(data['conf'][i]),
                'left': data['left'][i],
                'top': data['top'][i],
                'index': i
            })
    
    # Look for keyword-value pairs with better spatial analysis
    for i, item in enumerate(valid_items):
        word = item['text'].lower()
        
        for keyword in keywords:
            if keyword in word and len(item['text']) > 1:
                # Look for the next meaningful value
                for j in range(i + 1, min(i + 5, len(valid_items))):
                    next_item = valid_items[j]
                    
                    # Check spatial relationship (same line or next line)
                    same_line = abs(next_item['top'] - item['top']) < 10
                    next_line = 10 <= next_item['top'] - item['top'] <= 40
                    
                    if (same_line and next_item['left'] > item['left']) or next_line:
                        value = next_item['text']
                        # Only add if it looks like a meaningful value
                        if (len(value) > 1 and 
                            not value.lower() in keywords and
                            next_item['conf'] > 60):
                            extracted[keyword] = value
                            break

    return extracted


def extract_additional_patterns(text):
    """Extract additional patterns that might be missed by other methods"""
    additional_data = {}
    
    # Email addresses
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, text, re.IGNORECASE)
    if emails:
        additional_data["emails"] = list(set(emails))
    
    # Dates in various formats
    date_patterns = [
        r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2},?\s+\d{4}\b',
        r'\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b',
        r'\b\d{4}[-/]\d{1,2}[-/]\d{1,2}\b'
    ]
    
    all_dates = []
    for pattern in date_patterns:
        dates = re.findall(pattern, text, re.IGNORECASE)
        all_dates.extend(dates)
    
    if all_dates:
        additional_data["dates"] = list(set(all_dates))
    
    # Years (4 digit numbers that look like years)
    years = re.findall(r'\b(19|20)\d{2}\b', text)
    if years:
        years_full = [f"{match[0]}{match[1]}" if isinstance(match, tuple) else match for match in years]
        additional_data["years"] = list(set(years_full))
    
    return additional_data


def extract_structured_data(text, image_path=None):
    regex_data = extract_refex(text)
    ner_data = extract_with_ner(text)
    additional_data = extract_additional_patterns(text)
    kv_data = {}

    if image_path:
        kv_data = extract_kv_from_image(image_path)

    # Merge all data
    structured = {**regex_data, **ner_data, **additional_data, **kv_data}
    
    # Clean up any remaining false positives
    for key in list(structured.keys()):
        if isinstance(structured[key], list):

            structured[key] = [item for item in structured[key] 
                             if item and len(str(item).strip()) > 1 and str(item).strip() != ',']

            if not structured[key]:
                del structured[key]
    
    return structured