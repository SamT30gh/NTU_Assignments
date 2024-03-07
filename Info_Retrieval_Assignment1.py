import os
import time
import nltk
import string
import re
from collections import defaultdict

from nltk import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

nltk.download('stopwords')
nltk.download('punkt')

def read_files(directory):
    """Reads text files from a directory and returns a list of documents."""
    documents = []
    for filename in os.listdir(directory):
        if filename.endswith(".txt"):
            filepath = os.path.join(directory, filename)
            with open(filepath, 'r', encoding="utf-8") as f:
                documents.append(f.read())
    return documents


def preprocess_text(text):
    """Preprocesses text by tokenizing, removing stopwords, and stemming."""
    term_tokens = word_tokenize(text)

    # Get English stop words
    stop_words = set(stopwords.words('english'))

    # Get punctuation characters
    punctuation = set(string.punctuation)

    # Define a regular expression pattern to match symbols
    symbol_pattern = re.compile(r'[!@#$%^&*()\-_=+\[\]{};:\'",.<>/?\\|~`]')

    # Filter out stop words, punctuation, and numbers from the tokens
    tokens = []
    for word in term_tokens:
        word_lower = word.lower()
        if (word_lower not in stop_words and
                not all(char in punctuation for char in word) and
                not any(char.isdigit() for char in word) and
                word_lower[0].isalpha() and
                not any(char in word_lower for char in 'øüëä')):
            tokens.append(re.sub(symbol_pattern, '', word_lower))

    return tokens

def create_blocks(term_document_matrix, block_size):
    """Creates term blocks based on BSBI or SPIMI approach."""
    start_time = time.time()
    blocks = defaultdict(dict)
    current_block = 0
    for term, doc_freq in sorted(term_document_matrix.items()):
        blocks[current_block][term] = doc_freq
        if len(blocks[current_block]) >= block_size:
            current_block += 1
    end_time = time.time()
    sorting_time = end_time - start_time
    return blocks, sorting_time


def create_term_document_matrix(documents):
    """Creates a term-document matrix with term frequencies."""
    start_time = time.time()
    term_document_matrix = defaultdict(dict)
    for doc_id, document in enumerate(documents):
        for term in preprocess_text(document):
            term_document_matrix[term][doc_id] = term_document_matrix[term].get(doc_id, 0) + 1
    end_time = time.time()
    indexing_time = end_time - start_time
    return term_document_matrix, indexing_time


def merge_blocks(blocks):
    """Merges term blocks into a single sorted list."""
    start_time = time.time()
    merged_list = []
    for block in blocks.values():
        merged_list.extend(block.items())
    merged_list.sort(key=lambda x: x[0])
    end_time = time.time()
    merge_time = end_time - start_time
    return merged_list, merge_time


def write_to_file(data, filename):
    """Writes data to a text file."""
    with open(filename, 'w', encoding="utf-8") as f:
        for term, doc_id in data:
            f.write(f"{term} {doc_id}\n")


def measure_memory(message):
    """Prints the current memory usage with a message."""
    import psutil
    memory_usage = psutil.virtual_memory().used / (1024 * 1024)
    print(f"{message}: {memory_usage:.2f} MB")


def main():
    directory = "C:/Users/samue/PycharmProjects/pythonProject/HillaryEmails"  # Replace with your directory path
    block_size = 1000  # Adjust block size as needed

    # Read documents
    documents = read_files(directory)
    measure_memory("Before Indexing")

    # Indexing
    term_document_matrix, indexing_time = create_term_document_matrix(documents)
    print(f"Indexing Time: {indexing_time:.2f} seconds")

    # Create blocks
    blocks, sorting_time = create_blocks(term_document_matrix, block_size)
    print(f"Sorting Time: {sorting_time:.2f} seconds")
    measure_memory("After Blocking")

    # Merge blocks
    merged_list, merge_time = merge_blocks(blocks)
    print(f"Merge Time: {merge_time:.2f} seconds")

    # Write to file
    write_to_file(merged_list, "output.txt")

    print("Indexing and Merging Complete!")


if __name__ == "__main__":
    main()