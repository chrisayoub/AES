import argparse


def main():
    parser = argparse.ArgumentParser(description='Encrypt or decrypt with AES')
    parser.add_argument('--keysize', help='Either 128 or 256 bits.', required=True)
    parser.add_argument('--keyfile', help='The path of a keyfile that fits the specified size.', required=True)
    parser.add_argument('--inputfile', help='The file to encrypt or decrypt.', required=True)
    parser.add_argument('--outputfile', help='The path for the desired output file.', required=True)
    parser.add_argument('--mode', help='encrypt or decrypt', required=True)

    args = parser.parse_args()
    keysize = args.keysize
    keyfile = args.keyfile
    inputfile = args.inputfile
    outputfile = args.outputfile
    mode = args.mode




# https://stackoverflow.com/questions/1035340/reading-binary-file-and-looping-over-each-byte
def bytes_from_file(filename, chunksize=8192):
    with open(filename, "rb") as f:
        while True:
            chunk = f.read(chunksize)
            if chunk:
                yield from chunk
            else:
                break


if __name__ == '__main__':
    main()