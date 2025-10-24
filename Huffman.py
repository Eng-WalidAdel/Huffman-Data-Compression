import heapq
from collections import defaultdict, namedtuple

import heapq
from collections import defaultdict, namedtuple

class Node:
    def __init__(self, char, freq):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None
    
    def __lt__(self, other):
        return self.freq < other.freq

class InternalNode:
    def __init__(self, left, right):
        self.left = left
        self.right = right
        self.freq = left.freq + right.freq
    
    def __lt__(self, other):
        return self.freq < other.freq

def build_frequency_dict(data):
    frequency = defaultdict(int)
    for symbol in data:
        frequency[symbol] += 1
    return frequency

def build_huffman_tree(frequency):
    heap = [Node(char, freq) for char, freq in frequency.items()]
    heapq.heapify(heap)
    
    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        internal_node = InternalNode(left, right)
        heapq.heappush(heap, internal_node)
    
    return heap[0]

def build_codes(tree, code='', mapping=None):
    if mapping is None:
        mapping = {}
    
    if isinstance(tree, Node):
        mapping[tree.char] = code
    else:
        build_codes(tree.left, code + '0', mapping)
        build_codes(tree.right, code + '1', mapping)
    return mapping

def compress_file(input_path, output_path):
    # Read input file
    with open(input_path, 'rb') as file:
        data = file.read()
    
    # Build Huffman tree and codes
    frequency = build_frequency_dict(data)
    tree = build_huffman_tree(frequency)
    codes = build_codes(tree)
    
    # Compress data
    encoded = ''.join(codes[byte] for byte in data)
    
    # Add padding and convert to bytes
    padding = 8 - (len(encoded) % 8)
    encoded += '0' * padding
    
    # Convert bits to bytes
    compressed = bytearray()
    for i in range(0, len(encoded), 8):
        byte = encoded[i:i+8]
        compressed.append(int(byte, 2))
    
    # Write compressed data
    with open(output_path, 'wb') as file:
        # Write frequency dictionary
        freq_str = str(dict(frequency))
        file.write(len(freq_str).to_bytes(4, 'big'))
        file.write(freq_str.encode())
        file.write(padding.to_bytes(1, 'big'))
        file.write(bytes(compressed))

def decompress_file(input_path, output_path):
    with open(input_path, 'rb') as file:
        # Read frequency dictionary
        freq_size = int.from_bytes(file.read(4), 'big')
        freq_str = file.read(freq_size).decode()
        frequency = eval(freq_str)
        
        # Read padding
        padding = int.from_bytes(file.read(1), 'big')
        
        # Read compressed data
        data = file.read()
        
    # Rebuild Huffman tree
    tree = build_huffman_tree(frequency)
    
    # Convert bytes to bits
    bits = ''.join(format(byte, '08b') for byte in data)
    bits = bits[:-padding] if padding else bits
    
    # Decode data
    decoded = bytearray()
    current = tree
    for bit in bits:
        current = current.left if bit == '0' else current.right
        if isinstance(current, Node):
            decoded.append(current.char)
            current = tree
    
    # Write decompressed data
    with open(output_path, 'wb') as file:
        file.write(decoded)

if __name__ == '__main__':
    # Example usage
    input_file = "example.txt"
    compressed_file = "compressed.bin"
    decompressed_file = "decompressed.txt"

    compress_file(input_file, compressed_file)
    decompress_file(compressed_file, decompressed_file)