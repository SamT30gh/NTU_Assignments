import os
import time
import re
import string
from collections import defaultdict
from nltk.corpus import stopwords
from nltk import word_tokenize
from nltk.stem import PorterStemmer
import psutil


# Function to read documents from a directory
def read_documents_from_directory(directory):
    start_time = time.time()
    documents = []
    for filename in os.listdir(directory):
        if filename.endswith(".txt"):
            with open(os.path.join(directory, filename), 'r', encoding='utf-8') as file:
                documents.append((os.path.splitext(filename)[0], os.path.join(directory, filename), file.read()))
    end_time = time.time()
    read_time = end_time - start_time
    return read_time, documents

# Function to preprocess text content
def preprocess_text(text):
    """Preprocesses text by tokenizing, removing stopwords, and stemming."""
    term_tokens = word_tokenize(text)

    # Get English stop words
    stop_words = set(stopwords.words('english'))

    # Get punctuation characters
    punctuation = set(string.punctuation)

    # Define a regular expression pattern to match symbols
    symbol_pattern = re.compile(r'[!@#$%^&*()\-_=+\[\]{};:\'",.<>/?\\|~`]')
    
    # Initialize Porter Stemmer
    porter = PorterStemmer()

    # Filter out stop words, punctuation, and numbers from the tokens
    tokens = []
    for word in term_tokens:
        word_lower = word.lower()
        if (word_lower not in stop_words and 
            not all(char in punctuation for char in word) and 
            not any(char.isdigit() for char in word) and 
            word_lower[0].isalpha() and
            not any(char in word_lower for char in 'øüëä')):
            stemmed_word = porter.stem(word_lower)  # Apply stemming
            tokens.append(re.sub(symbol_pattern, '', stemmed_word))

    return tokens

# Function to create block with tokenizing, indexing and sorting
def create_blocks(documents, block_size):
    """Creates term blocks based on BSBI with indexing and sorting within each block."""
    start_time = time.time()
    blocks = defaultdict(dict)
    current_block = 0
    for doc_name, doc_path, document in documents:
        for term in preprocess_text(document):
            blocks[current_block][term] = blocks[current_block].get(doc_name, []) + [doc_name]
            if len(blocks[current_block]) >= block_size:
                current_block += 1
        # Sort terms within each block
        sorted_block = sorted(blocks[current_block].items())
        blocks[current_block] = dict(sorted_block)

    end_time = time.time()
    create_index_time = end_time - start_time
    return blocks, create_index_time

# Function to merge blocks into 1 single sorted text-document pair
def merge_and_sort_blocks(blocks):
    """Merges term-document pairs from all blocks and sorts them."""
    start_time = time.time()
    merged_dict = defaultdict(list)
    for block in blocks.values():
        for term, doc_ids in block.items():
            merged_dict[term].extend(doc_ids)
    
    # Sort the merged dictionary by terms
    sorted_merged_list = sorted(merged_dict.items(), key=lambda x: x[0])
    
    end_time = time.time()
    merge_sort_time = end_time - start_time
    return sorted_merged_list, merge_sort_time

# Function to measure memory
def measure_memory(message):
    """Prints the current memory usage with a message."""
    memory_usage = psutil.virtual_memory().used / (1024 * 1024)
    print(f"{message}: {memory_usage:.2f} MB")

# Function to write output to disk
def write_to_file(data, filename):
    start_time = time.time()
    """Writes data to a text file."""
    with open(filename, 'w', encoding="utf-8") as f:
        for term, doc_id in data:
            f.write(f"{term} {doc_id}\n")
    end_time = time.time()
    write_time = end_time - start_time
    return write_time

def main():
    start_time = time.time()
    print("\nReading directory files....")
    
    # Read documents from directory input
    read_time, documents = read_documents_from_directory(directory)
    print(f"Read directory files Time: {read_time:.2f} seconds")
    measure_memory("Read directory files Memory Usage")

    print("\nCreating Blocks, Tokenizing & Indexing....")

    # Create blocks with tokenizing, indexing and sorting
    blocks, create_index_time = create_blocks(documents, block_size)
    print(f"Create Blocks & Tokenize & Index Time: {create_index_time:.2f} seconds")
    measure_memory("Create Blocks & Tokenize & Index Memory Usage")

    print("\nMerging Blocks & Sorting....")   
    
    # Merge and sort terms-document pairs
    merged_list, merge_sort_time = merge_and_sort_blocks(blocks)
    print(f"Merge Blocks & Sort Time: {merge_sort_time:.2f} seconds")
    measure_memory("Merge Blocks & Sort Memory Usage")
    
    print("\nWriting to disk....")   

    # Writing terms-document pairs single output into disk
    write_time = write_to_file(merged_list, "output.txt")
    print(f"Done Writing to disk Time: {write_time:.2f} seconds")
    measure_memory("Done writing to disk Memory Usage")
    
    end_time = time.time()
    total_time = end_time - start_time
    
    print(f"\nTotal Time Usage: {total_time:.2f} seconds")
    measure_memory("Total Memory Usage")
    
# Main Code Starts Here
directory = input("Enter the path to the directory containing text files: ")
block_size = int(input("Enter the block size parameter: "))
main()
