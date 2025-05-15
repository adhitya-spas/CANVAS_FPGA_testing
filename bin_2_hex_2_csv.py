import csv

def binary_to_hex(input_file, apid, output_file):
    
    # open file
    with open(input_file, 'rb') as infile:
        binary_data = infile.read()

    hex_data = []

    # loop through the binary data in chunks of 1 byte 
    for i in range(0, len(binary_data), 1):
        # get byte
        hex_byte = format(binary_data[i], '02X')
        
        # position data to start with apid
        if i % 16 == 0: 
            hex_line = [format(apid[0], '02X'), format(apid[1], '02X'), format(apid[2], '02X'), format(apid[3], '02X')]
        hex_line.append(hex_byte)

        if len(hex_line) == 17: 
            hex_data.append(hex_line)
            hex_line = [format(apid[0], '02X'), format(apid[1], '02X'), format(apid[2], '02X'), format(apid[3], '02X')]

    if len(hex_line) > 4:
        hex_data.append(hex_line)

    # save
    with open(output_file, 'w', newline='') as outfile:
        writer = csv.writer(outfile)
        writer.writerows(hex_data)

    print(f"CSV file saved as {output_file}")

# main
input_file = 'C:/Users/culair/Desktop/CANVAS_test_overnight2.txt'
output_file = 'C:/Users/culair/Desktop/CSV_output_data2.csv'
apid = [0x1A, 0xCF, 0xFC, 0x1D]  

binary_to_hex(input_file, apid, output_file)
