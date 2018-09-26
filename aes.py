import argparse
import encrypt as e
import decrypt as d


def main():
    parser = argparse.ArgumentParser(description='Encrypt or decrypt with AES')
    parser.add_argument('--keysize',
                        help='Either 128 or 256 bits.', required=True)
    parser.add_argument('--keyfile',
                        help='The path of a keyfile that fits the keysize.',
                        required=True)
    parser.add_argument('--inputfile',
                        help='The file to encrypt or decrypt.', required=True)
    parser.add_argument('--outputfile',
                        help='The path for the desired output file.',
                        required=True)
    parser.add_argument('--mode',
                        help='encrypt or decrypt', required=True)

    args = parser.parse_args()
    keysize = int(args.keysize)
    keyfile = args.keyfile
    inputfile = args.inputfile
    outputfile = args.outputfile
    mode = args.mode

    if mode == 'encrypt':
        e.encrypt(keysize, keyfile, inputfile, outputfile)
    elif mode == 'decrypt':
        d.decrypt(keysize, keyfile, inputfile, outputfile)


if __name__ == '__main__':
    main()
