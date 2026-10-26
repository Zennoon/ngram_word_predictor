import re

### Preprocessing functions


def normalize_similar_characters(text):
    print(
        "Normalizing phonetically similar characters in the Amharic Langauge (ሐ -> ሀ, ኀ -> ሀ, ሠ -> ሰ, ፀ -> ጸ)..."
    )
    replacement_map = {
        "ሐሑሒሓሔሕሖ": "ሀሁሂሃሄህሆ",
        "ኀኁኂኃኄኅኆ": "ሀሁሂሃሄህሆ",
        "ሠሡሢሣሤሥሦሧ": "ሰሱሲሳሴስሶሷ",
        "ፀፁፂፃፄፅፆ": "ጸጹጺጻጼጽጾ",
    }
    for chars, replacements in replacement_map.items():
        for i in range(len(chars)):
            text = text.replace(chars[i], replacements[i])
    return text

def remove_common_stopwords(text):
    print("Removing common stopwords...")
    stopwords = ["ነው", "አይደለም", "ነበር", "ነበረ", "አልነበረም", "ሆነ", "አልሆነም", "ይሆናል", "አይሆንም"]
    for word in stopwords:
        text = re.sub(rf"\s+{word}\s*", "")
    return text

def remove_extra_whitespace(text):
    print("Removing any extra whitespace between words...")
    return re.sub(r"\s+", " ", text)


def remove_punctuation(text):
    print("Removing punctuation to decrease noise...")
    punctuations = ["፣", "፤", "(", ")", "፦", "፡"]
    for punc in punctuations:
        text = text.replace(punc, "")
    return text


def add_delimiter_tags(text):
    print("Adding sentence delimiter tags (<s></s>)...")
    text = "<s> " + text
    sentence_delimiters = ["፡፡", "።", "!", "?"]
    for delimiter in sentence_delimiters:
        text = text.replace(delimiter, " </s> <s> ")

    text = " ".join(text.split())

    if text.endswith("<s>"):
        text = text[:-3].strip()
    if not text.endswith("</s>"):
        text += " </s>"

    return text

def remove_sentence_delimiters(text):
    print("Adding sentence delimiter tags (<s></s>)...")
    text = "<s> " + text
    sentence_delimiters = ["፡፡", "።", "!", "?"]
    for delimiter in sentence_delimiters:
        text = text.replace(delimiter, f" {delimiter} </s> <s> ")
    
    text = " ".join(text.split())
    
    if text.endswith("<s>"):
        text = text[:-3].strip()

    return text


def preprocess_corpus(corpus_content: str, remove_stopwords: bool = False, remove_sentence_delims: bool = False):
    print("Initialzing corpus preprocessing...")
    print("Trimming any extra whitespace...")
    corpus_content = corpus_content.strip()
    corpus_content = normalize_similar_characters(corpus_content)
    if remove_sentence_delims:
        corpus_content = remove_sentence_delimiters(corpus_content)
    else:
        corpus_content = add_delimiter_tags(corpus_content)
    corpus_content = remove_extra_whitespace(corpus_content)
    corpus_content = remove_punctuation(corpus_content)
    if remove_stopwords:
        corpus_content = remove_common_stopwords(corpus_content)
    return corpus_content
