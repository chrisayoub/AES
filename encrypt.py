sub_bytes_forward = \
['63', '7c', '77', '7b', 'f2', '6b', '6f', 'c5', '30', '01', '67', '2b', 'fe', 'd7', 'ab', '76',
 'ca', '82', 'c9', '7d', 'fa', '59', '47', 'f0', 'ad', 'd4', 'a2', 'af', '9c', 'a4', '72', 'c0',
 'b7', 'fd', '93', '26', '36', '3f', 'f7', 'cc', '34', 'a5', 'e5', 'f1', '71', 'd8', '31', '15',
 '04', 'c7', '23', 'c3', '18', '96', '05', '9a', '07', '12', '80', 'e2', 'eb', '27', 'b2', '75',
 '09', '83', '2c', '1a', '1b', '6e', '5a', 'a0', '52', '3b', 'd6', 'b3', '29', 'e3', '2f', '84',
 '53', 'd1', '00', 'ed', '20', 'fc', 'b1', '5b', '6a', 'cb', 'be', '39', '4a', '4c', '58', 'cf',
 'd0', 'ef', 'aa', 'fb', '43', '4d', '33', '85', '45', 'f9', '02', '7f', '50', '3c', '9f', 'a8',
 '51', 'a3', '40', '8f', '92', '9d', '38', 'f5', 'bc', 'b6', 'da', '21', '10', 'ff', 'f3', 'd2',
 'cd', '0c', '13', 'ec', '5f', '97', '44', '17', 'c4', 'a7', '7e', '3d', '64', '5d', '19', '73',
 '60', '81', '4f', 'dc', '22', '2a', '90', '88', '46', 'ee', 'b8', '14', 'de', '5e', '0b', 'db',
 'e0', '32', '3a', '0a', '49', '06', '24', '5c', 'c2', 'd3', 'ac', '62', '91', '95', 'e4', '79',
 'e7', 'c8', '37', '6d', '8d', 'd5', '4e', 'a9', '6c', '56', 'f4', 'ea', '65', '7a', 'ae', '08',
 'ba', '78', '25', '2e', '1c', 'a6', 'b4', 'c6', 'e8', 'dd', '74', '1f', '4b', 'bd', '8b', '8a',
 '70', '3e', 'b5', '66', '48', '03', 'f6', '0e', '61', '35', '57', 'b9', '86', 'c1', '1d', '9e',
 'e1', 'f8', '98', '11', '69', 'd9', '8e', '94', '9b', '1e', '87', 'e9', 'ce', '55', '28', 'df',
 '8c', 'a1', '89', '0d', 'bf', 'e6', '42', '68', '41', '99', '2d', '0f', 'b0', '54', 'bb', '16']


L = 4
schedule = []
rounds = 10

# https://stackoverflow.com/questions/1035340/reading-binary-file-and-looping-over-each-byte
def bytes_from_file(filename, chunksize=8192):
    with open(filename, "rb") as f:
        while True:
            chunk = f.read(chunksize)
            if chunk:
                yield from chunk
            else:
                break


def encrypt(keysize, keyfile, inputfile, outputfile):
    out = open(outputfile, "w")

    if keysize == 128:
        rounds = 10
    elif keysize == 256:
        rounds = 14

    matrix = []
    row = 0
    col = 0

    for b in bytes_from_file(inputfile):
        if row == 0 and col == 0:
            matrix = []
            for i in range(L):
                matrix.append([])
        matrix[row].append(b)

        # Move to next spot
        row += 1
        if row == L:
            row = 0
            col += 1
        if col == L:
            col = 0
            # Can now encrypt block!
            encrypt_block(matrix)
            write_block(matrix, out)

    # One last partial block left?
    if row != 0 and col != 0:
        # Have data left over, pad it!
        pad = L * L - (col * L + row)
        while col < L:
            while row < L:
                matrix[row].append(0)
                row += 1
            row = 0
            col += 1
        matrix[L - 1][L - 1] = pad
        # Now encrypt this last block
        encrypt_block(matrix)
        write_block(matrix, out)


def write_block(matrix, out):
    col = 0
    while col < L:
        row = 0
        while row < L:
            val = matrix[row][col]
            out.write(chr(val))
            row += 1
        col += 1


def encrypt_block(matrix):
    round_key_encrypt(matrix)

    for round in range(rounds - 1):
        sub_bytes_encrypt(matrix)
        shift_rows_encrypt(matrix)
        mix_cols_encrypt(matrix)
        round_key_encrypt(matrix)

    sub_bytes_encrypt(matrix)
    shift_rows_encrypt(matrix)
    round_key_encrypt(matrix)


def print_matrix(matrix):
    for row in matrix:
        print(row)
    print()


def sub_bytes_encrypt(matrix):
    for row in matrix:
        for i in range(L):
            val = row[i]
            row[i] = int(sub_bytes_forward[val], 16)


def shift_rows_encrypt(matrix):
    for row in range(L):
        for shifts in range(row):
            # Do a shift
            temp = matrix[row][0]
            for k in range(L - 1):
                matrix[row][k] = matrix[row][k + 1]
            matrix[row][L - 1] = temp


def mix_cols_encrypt(matrix):
    for col in range(L):
        # Old values
        s0 = matrix[0][col]
        s1 = matrix[1][col]
        s2 = matrix[2][col]
        s3 = matrix[3][col]
        # New values
        matrix[0][col] = mult_2(s0) ^ mult_3(s1) ^ s2 ^ s3
        matrix[1][col] = s0 ^ mult_2(s1) ^ mult_3(s2) ^ s3
        matrix[2][col] = s0 ^ s1 ^ mult_2(s2) ^ mult_3(s3)
        matrix[3][col] = mult_3(s0) ^ s1 ^ s2 ^ mult_2(s3)


def round_key_encrypt(matrix, ):
    N = L / 4


def mult_2(x):
    return (x < 1) ^ 27 # 0x1b


def mult_3(x):
    return mult_2(x) ^ x

