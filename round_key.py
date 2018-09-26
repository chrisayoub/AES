import read_bytes as rb
import sub_bytes as sb


class Round:

    RCON = [1, 2, 4, 8, 16, 32, 64, 128, 27, 54]
    for r in range(len(RCON)):
        RCON[r] = RCON[r] << 24

    L = 4
    schedule = []
    round_key_num = 0
    ks = 128

    def __init__(self, keyfile, keysize):
        self.schedule = []
        self.load_keyfile(keyfile)
        self.ks = keysize
        self.round_key_num = 0

    def load_keyfile(self, keyfile):
        val = 0
        count = 0
        for b in rb.bytes_from_file(keyfile):
            val = val << 8 | int(b)

            count += 1
            if count == self.L:
                self.schedule.append(val)
                val = 0
                count = 0

    def sub_word(self, word):
        a0 = (0x000000ff & word)
        a1 = (0x0000ff00 & word) >> 8
        a2 = (0x00ff0000 & word) >> 16
        a3 = (0xff000000 & word) >> 24

        a0 = sb.sub_bytes_enc(a0)
        a1 = sb.sub_bytes_enc(a1)
        a2 = sb.sub_bytes_enc(a2)
        a3 = sb.sub_bytes_enc(a3)

        return (a3 << 24) | (a2 << 16) | (a1 << 8) | a0

    def rot_word(self, word):
        a0 = (0x000000ff & word)
        a1 = (0x0000ff00 & word) >> 8
        a2 = (0x00ff0000 & word) >> 16
        a3 = (0xff000000 & word) >> 24

        return (a2 << 24) | (a1 << 16) | (a0 << 8) | a3

    def get_new_key(self):
        i = len(self.schedule)

        k = 4
        if self.ks == 256:
            k = 8

        temp = self.schedule[i - 1]
        if i % k == 0:
            temp = self.sub_word(self.rot_word(temp)) ^ self.RCON[int(i / k) - 1]
        elif k > 6 and i % k == 4:
            temp = self.sub_word(temp)
        self.schedule.append(self.schedule[i - k] ^ temp)

    def round_key_encrypt(self, matrix):
        col = 0
        for row in range(self.L):
            if self.round_key_num >= len(self.schedule):
                self.get_new_key()
            key = self.schedule[self.round_key_num]

            a3 = (0x000000ff & key)
            a2 = (0x0000ff00 & key) >> 8
            a1 = (0x00ff0000 & key) >> 16
            a0 = (0xff000000 & key) >> 24

            matrix[0][col] = matrix[0][col] ^ a0
            matrix[1][col] = matrix[1][col] ^ a1
            matrix[2][col] = matrix[2][col] ^ a2
            matrix[3][col] = matrix[3][col] ^ a3

            col += 1
            self.round_key_num += 1

    def reset(self):
        self.round_key_num = 0
