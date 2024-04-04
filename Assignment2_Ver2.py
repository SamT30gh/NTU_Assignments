import time
import psutil

def boolean_search(query, inverted_index):
    query_words = query.split()
    result_docs = set()
    operator = "AND"  # Default operator
    
    for word in query_words:
        
        if word.upper() == "AND":
            operator = "AND"
        elif word.upper() == "OR":
            operator = "OR"
        elif word.upper() == "NOT":
            operator = "NOT"
        else:
            if word in inverted_index:
                if operator == "AND":
                    if not result_docs:
                        result_docs.update(inverted_index[word])
                    else:
                        result_docs.intersection_update(inverted_index[word])
                elif operator == "OR":
                    result_docs.update(inverted_index[word])
                elif operator == "NOT":
                    if not result_docs:
                        result_docs.update(inverted_index.keys())
                    result_docs.difference_update(inverted_index[word])
    
    return sorted(list(result_docs))

def compression_dictionary_as_a_string(inverted_index):
    start_time = time.time()
    compressed_index = {}
    
    # Concatenate all terms into a single string
    dictionary_string = ""
    for term in sorted(inverted_index.keys()):
        dictionary_string += term
        
    # Concatenate all terms into a single string with pointers
    dictionary_string = ""
    pointers = {}
    pointer = 0
    for term in sorted(inverted_index.keys()):
        pointers[term] = pointer
        dictionary_string += term
        pointer += len(term)
    
    # Store the dictionary string and pointers in the compressed index
    compressed_index['term'] = dictionary_string
    #compressed_index['term pointer'] = pointers
    
    # Store posting lists as they are
    for term, postings in inverted_index.items():
        compressed_index[pointers[term]] = postings
    
    end_time = time.time()
    compression_dictionary_as_a_string_time = end_time - start_time
    
    return compressed_index, compression_dictionary_as_a_string_time

def compression_blocking(inverted_index, block_size):
    start_time = time.time()
    compressed_index = {}
    block_pointers = {}
    term_length_list = []
    current_pointer = 0
    term_number = 0
    compressed_terms = ""

    # Iterate over terms in the inverted index
    for term, postings in inverted_index.items():
        term_length = len(term)
        compressed_terms += str(term_length) + term
        term_number += 1
        
        term_length_list.append(term_length)
        #print(term_length_list)

        # If the current term is the kth term or the last term
        if term_number >= block_size or term == list(inverted_index.keys())[-1]:
            # Store block pointer
            block_pointers[current_pointer] = compressed_terms
    
            # Extract posting lists for the block
            posting_lists = []
            block_start = 0
            term_initial = 0
            while block_start < block_size:
                #term_length = int(compressed_terms[term_initial])
                term_length = term_length_list[block_start]
                if(term_length_list[block_start] >= 10):
                    #print(compressed_terms)
                    term_start = term_initial + 2
                else:
                    term_start = term_initial + 1
                term_end = term_start + term_length
                #print(term_start, term_end)
                posting_lists.append(inverted_index[compressed_terms[term_start:term_end]])
                block_start += 1
                term_initial = term_end
                
                # Break if its last term
                if(term == list(inverted_index.keys())[-1]):
                    break
    
            # Store the posting list for the block
            compressed_index[current_pointer] = posting_lists
    
            # Update current pointer
            current_pointer += len(compressed_terms) # Current pointer points to the end of the current block
    
            # Reset compressed terms for the next block
            compressed_terms = ""
            term_number = 0
            term_length_list = []

    # Add block pointers to the compressed index
    compressed_index['term'] = "".join(block_pointers.values())
    
    # Add block size to the compressed index
    compressed_index['block_size'] = block_size
    
    end_time = time.time()
    compression_blocking_time = end_time - start_time

    return compressed_index, compression_blocking_time

def decompress_dictionary_as_a_string(compressed_term, pointers_postings):
    start_time = time.time()
    decompressed_index = {}
    current_position = 0
    
    keys = list(pointers_postings.keys())  # Convert dictionary keys to a list
    for i, key in enumerate(keys):
        if i < len(keys) - 1:
            next_key = keys[i + 1]
            term = compressed_term[current_position:next_key]
            decompressed_index[term] = pointers_postings[key]
            current_position = next_key
    
    # to handle last index
    last_index = len(compressed_term)
    term = compressed_term[current_position:last_index]
    decompressed_index[term] = pointers_postings[key]
    
    end_time = time.time()
    decompression_dictionary_as_a_string_time = end_time - start_time
      
    return decompressed_index, decompression_dictionary_as_a_string_time

# Function to measure memory
def measure_memory(message):
    """Prints the current memory usage with a message."""
    memory_usage = psutil.virtual_memory().used / (1024 * 1024)
    print(f"{message}: {memory_usage:.2f} MB")
    
# Function to write output to disk
def write_to_file(data, filename):
    """Writes data to a text file."""
    with open(filename, 'w', encoding="utf-8") as f:
        for key,value in data.items():
            f.write(f"{key}: {value}\n")
            

################################# Main Code Starts Here ##################################################

directory = input("Enter the path to the directory containing text files: ")

# Open the file in read mode
with open(directory, 'r') as file:
    # Read all lines from the file
    lines = [line.rstrip('\n') for line in file.readlines() if line.strip()]

# Initialize an empty dictionary
inverted_index = {}

# Iterate through each line and extract key-value pairs
for line in lines:
    # Split each line into key and value parts
    key, value = line.split(" ['")
    key = key.strip('"')  # Remove surrounding double quotes
    # Extract values, remove brackets, split into list, and convert to integers
    value = sorted(map(int, value.replace('[', '').replace(']', '').replace("'", "").split(', ')))
    # Add key-value pair to the dictionary
    inverted_index[key] = value


print("Choose an option:")
print("1. Boolean Search")
print("2. Compression")

choice = input("Enter your choice: ")

if choice == '1':
    query = input("Enter search query (each term separated by space, and use 'AND', 'OR', 'NOT' operators): ")
    result = boolean_search(query, inverted_index)
    print("Posting satisfying the query:", result)
elif choice == '2':
    print("Choose compression method:")
    print("1. Dictionary as a string compression")
    print("2. Blocking compression")
    
    compression_choice = input("Enter your choice: ")
    
    if compression_choice == '1':
        # Dictionary as a String Method - Compression
        compressed_index, compression_dictionary_as_a_string_time = compression_dictionary_as_a_string(inverted_index)
        #print("Compressed Index (Dictionary as a string):", compressed_index)
        print("Dictionary as a string compression completed!")
        measure_memory("Compressed Dictionary as a string Memory Usage:")
        print(f"Compression Time Taken: {compression_dictionary_as_a_string_time:.2f} seconds")
        write_to_file(compressed_index,"dictionary_as_a_string.txt")
        
        # Dictionary as a String Method - Decompression
        exclude_key = 'term'
        other_dicts = {key: value for key, value in compressed_index.items() if key != exclude_key}
        decompressed_index, decompression_dictionary_as_a_string_time = decompress_dictionary_as_a_string(compressed_index['term'], other_dicts)
        #print("Decompressed Inverted Index (Dictionary as a string):", decompressed_index)
        measure_memory("Decompressed Dictionary as a string Memory Usage:")
        print(f"Compression Time Taken: {decompression_dictionary_as_a_string_time:.2f} seconds")
    elif compression_choice == '2':
        # Blocking Method - Compression
        block_size = int(input("Enter block size for blocking compression: "))
        
        compressed_blocking_index, compression_blocking_time = compression_blocking(inverted_index, block_size)
        # Move 'term' & 'block size' to the beginning of the dictionary
        compressed_blocking_index = {'term': compressed_blocking_index.pop('term'), 'block_size': compressed_blocking_index.pop('block_size'), **compressed_blocking_index}
        #print("Compressed Blocking Index (Blocking Method):", compressed_blocking_index)
        print(f"Compression Time Taken: {compression_blocking_time:.2f} seconds")
        measure_memory("Compressed Blocking Memory Usage:")
        write_to_file(compressed_blocking_index,"blocking.txt")
    else:
        print("Invalid compression choice.")
else:
    print("Invalid input.")
        

