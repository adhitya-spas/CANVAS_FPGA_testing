def text_to_binary(input_file, output_file):
    with open(input_file, 'rb') as infile, open(output_file, 'w') as outfile:
        byte = infile.read(1)
        while byte:
            binary_string = format(ord(byte), '08b')
            outfile.write(binary_string + '\n')
            byte = infile.read(1)

def binary_to_hex(input_file, output_file):
    with open(input_file, 'rb') as infile, open(output_file, 'w') as outfile:
        byte = infile.read(1)
        while byte:
            hex_string = format(ord(byte), '02X')
            outfile.write(hex_string + '\n')
            byte = infile.read(1)

# main
input_path = 'C:/Users/culair/Desktop/CANVAS_test_overnight.txt'
output_path = 'C:/Users/culair/Desktop/output_binary.txt'
output_path2 = 'C:/Users/culair/Desktop/output_hex.txt'
#text_to_binary(input_path, output_path)
binary_to_hex(output_path, output_path2)