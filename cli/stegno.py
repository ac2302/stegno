import cv2
import numpy as np
from sys import argv
from os import path


def write_data(data, image):
    # def write_byte_to_pixel(data, pixel):
    #     lsn = data & 0x0f
    #     msn = data & 0xf0
    #     msn >>= 4
        
    #     new_b, new_g = pixel[:-1]
    #     # setting least significant nibble to 0
    #     new_b = new_b ^ (new_b & 0x0f)
    #     new_g = new_b ^ (new_g & 0x0f)
    #     # setting lsn of blue to lsn
    #     new_b |= lsn
    #     # setting lsn of green to msn
    #     new_g |= msn

    #     pixel[0], pixel[1] = new_b, new_g

    #     print(data.to_bytes(1, 'little'), pixel)

    def write_byte_to_pixel(data, pixel):
            lsn = data & 0x0f
            msn = data & 0xf0
            msn >>= 4

            pixel[0] = (pixel[0] ^ (pixel[0] & 0xf)) | lsn
            pixel[1] = (pixel[1] ^ (pixel[1] & 0xf)) | msn

    size = len(data).to_bytes(4, 'little')
    data = size + data
    rows, columns, _ = image.shape

    current = (0, 0)
    current_index = 0
    is_writing = True
    while is_writing:
        # writing byte of data to pixel
        byte_of_data = data[current_index]
        write_byte_to_pixel(
            byte_of_data, image[current[0]][current[1]])

        # update current
        current_index += 1
        if current_index == len(data):
            break
        current = (current[0], current[1] + 1)
        if current[1] == columns:   # end of row
            current = (current[0] + 1, 0)
            if current[0] == rows:  # end of image
                break

    return image

def read_data(image):
    def get_pixel(index_to_get):
        i = -1
        rows, columns, _ = image.shape
        current = (0, -1)
        while True:
            # updating i and current
            i += 1
            current = (current[0], current[1]+1)
            if current[1] == columns:   # end of row
                current = (current[0]+1, 0)
                if current[0] == rows:  # end of image
                    return 'err'                

            if i == index_to_get:
                return image[current[0]][current[1]]

    def read_from_pixel(pixel):
        b_val, g_val, _ = pixel
        msn = g_val & 0x0f
        lsn = b_val & 0x0f
        return (msn << 4) | lsn

    def get_lenth_of_data(image):
        bs = b''
        for i in range(4):
            bs += int(read_from_pixel(get_pixel(i))).to_bytes(1, 'little')
        
        return int.from_bytes(bs, byteorder='little', signed=False)

    def get_data_from_img(image, length):
        data = bytearray(b'')

        for i in range(4, length+4):
            data.append(read_from_pixel(get_pixel(i)))

        return bytes(data)

    length = get_lenth_of_data(image)
    
    data = get_data_from_img(image, length)

    return data


if argv[1] == 'write':
    input_img_path, output_img_path = argv[2], argv[3]
    # write the data
    input_file = argv[4]
    # input_img = cv2.cvtColor(cv2.imread(input_img, 1), cv2.COLOR_BGR2RGB)
    input_img = cv2.imread(input_img_path, 1)

    with open(input_file, 'rb') as f:
        data = f.read()

    # print(input_img)

    # to_write = []

    # for b in data:
    #     lsn = b & 0x0f
    #     msn = b & 0xf0
    #     msn >>= 4
    #     to_write.append((msn, lsn))

    output_img = write_data(data, input_img)

    # cv2.imshow('output', output_img)
    # cv2.waitKey(0)
    
    cv2.imwrite(output_img_path, output_img)
elif argv[1] == 'read':
    # read the data from file
    input_img_path, output_file_path = argv[2], argv[3]

    input_img = cv2.imread(input_img_path, 1)

    data = read_data(input_img)

    try:
        open(output_file_path, 'x').close()
    except:
        pass

    with open(output_file_path, 'wb') as f:
        f.write(data)
    
