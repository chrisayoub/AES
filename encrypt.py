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

RCON = [1, 2, 4, 8, 16, 32, 64, 128, 27, 54]
for r in range(len(RCON)):
    RCON[r] = RCON[r] << 24

L = 4
schedule = []
round_key_num = 0
rounds = 10
ks = 128


# https://stackoverflow.com/questions/1035340/reading-binary-file-and-looping-over-each-byte
def bytes_from_file(filename, chunksize=8192):
    with open(filename, "rb") as f:
        while True:
            chunk = f.read(chunksize)
            if chunk:
                yield from chunk
            else:
                break


def load_keyfile(keyfile):
    global schedule

    val = 0
    count = 0
    for b in bytes_from_file(keyfile):
        val = val << 8 | int(b)

        count += 1
        if count == L:
            schedule.append(val)
            val = 0
            count = 0


def encrypt(keysize, keyfile, inputfile, outputfile):
    global rounds, ks

    out = open(outputfile, "w")
    load_keyfile(keyfile)
    ks = keysize

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
    global round_key_num
    round_key_num = 0

    round_key_encrypt(matrix)
    for i in range(rounds - 1):
        sub_bytes_encrypt(matrix)
        shift_rows_encrypt(matrix)
        mix_cols_encrypt(matrix)
        round_key_encrypt(matrix)
    sub_bytes_encrypt(matrix)
    shift_rows_encrypt(matrix)
    round_key_encrypt(matrix)

    print_matrix(matrix)


def print_matrix(matrix):
    for row in matrix:
        for val in row:
            print(hex(val), end=', ')
        print()
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
        old = [matrix[j][col] for j in range(L)]
        mult = []  # Used for 2 and 3 times
        for val in old:
            mod = val << 1 & 0xff
            if 0x80 & val:
                mod = mod ^ 0x1b
            mult.append(mod)

        # New values
        matrix[0][col] = mult[0] ^ old[3] ^ old[2] ^ mult[1] ^ old[1]
        matrix[1][col] = mult[1] ^ old[0] ^ old[3] ^ mult[2] ^ old[2]
        matrix[2][col] = mult[2] ^ old[1] ^ old[0] ^ mult[3] ^ old[3]
        matrix[3][col] = mult[3] ^ old[2] ^ old[1] ^ mult[0] ^ old[0]


def sub_word(word):
    a0 = (0x000000ff & word)
    a1 = (0x0000ff00 & word) >> 8
    a2 = (0x00ff0000 & word) >> 16
    a3 = (0xff000000 & word) >> 24

    a0 = int(sub_bytes_forward[a0], 16)
    a1 = int(sub_bytes_forward[a1], 16)
    a2 = int(sub_bytes_forward[a2], 16)
    a3 = int(sub_bytes_forward[a3], 16)

    return (a3 << 24) | (a2 << 16) | (a1 << 8) | a0


def rot_word(word):
    a0 = (0x000000ff & word)
    a1 = (0x0000ff00 & word) >> 8
    a2 = (0x00ff0000 & word) >> 16
    a3 = (0xff000000 & word) >> 24

    return (a2 << 24) | (a1 << 16) | (a0 << 8) | a3


def get_new_key():
    global schedule, ks

    i = len(schedule)

    k = 4
    if ks == 256:
        k = 8

    temp = schedule[i - 1]
    if i % k == 0:
        temp = sub_word(rot_word(temp)) ^ RCON[int(i / k) - 1]
    elif k > 6 and i % k == 4:
        temp = sub_word(temp)
    schedule.append(schedule[i - k] ^ temp)


def round_key_encrypt(matrix):
    global round_key_num, schedule

    col = 0
    for row in range(L):
        if round_key_num >= len(schedule):
            get_new_key()
        key = schedule[round_key_num]

        a3 = (0x000000ff & key)
        a2 = (0x0000ff00 & key) >> 8
        a1 = (0x00ff0000 & key) >> 16
        a0 = (0xff000000 & key) >> 24

        matrix[0][col] = matrix[0][col] ^ a0
        matrix[1][col] = matrix[1][col] ^ a1
        matrix[2][col] = matrix[2][col] ^ a2
        matrix[3][col] = matrix[3][col] ^ a3

        col += 1
        round_key_num += 1
