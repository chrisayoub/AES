# AES Encryption + Decryption (128, 256)

Student information:
```
Christopher Ayoub
chrisayoub@utexas.edu
EID cfa348
```

### Usage 

`python3 aes.py --keysize $KEYSIZE --keyfile $KEYFILE --inputfile $INPUTFILE
--outputfile $OUTFILENAME --mode $MODE`

The size of `$KEYFILE` in bits should match the specified `$KEYSIZE`

### How it works

`aes.py` uses `argparse` from the Python standard library to parse
the command line arguments, and then calls either `encrypt.py`
or `decrypt.py` to do the actual work.
+ `read_bytes.py` contains a function to help read a file as bytes
+ `round_key.py` encapsulates the round key schedule generation
+ `sub_bytes.py` encapsulates the arrays used for SubBytes routines

#### Encryption

The code reads in a file a chunk at a time and processes the bits in 
16 byte blocks. Padding is added if there is not enough remaining
bits to fill 16 bytes. As each block is encrypted via the cipher
algorithm, it is then written to the output file. The blocks are 4x4,
where each cell in the block stores a byte.

The cipher algorithm is taken from the AES specification posted to Canvas.
10 rounds of the cipher are used for 128 bit encryption, and 14 rounds are used for 256 bit.

The procedures that make up the cipher algorithm:
+ `sub_bytes`
+ `shift_rows`
+ `mix_cols`
+ `round_key`

Most of the rounds involves each of these steps, 
but there are exceptions for the beginning and at the end. 

##### SubBytes

A simple mapping table is used for each byte in the block, 
The table has been already calculated and stored as a constant.

##### ShiftRows

Row 0 in the block stays the same. Row 1 in the block does 1 circular shift to the left.
Row 2 does 2, and Row 3 does 3. 

##### MixCols

This is essentially a matrix multiplication by a constant matrix 
which has been simplified down to binary multiplication and addition. 
The specification doc goes into detail about how these operations 
should be executed on the bits (which are actually polynomials),
but it all basically simplifies down to mostly XOR bitwise operations.

##### RoundKey

Each column of the block is XOR'd with a value generated from
the key file in a process called generating the *key schedule*.
There will be a constant number of keys generated based on the
key size used, and the code generates these all immediately so
they are available for use.

The keyfile gives us the initial keys in the schedule. Then, we use
various opeartions to generate subsequent keys in the sequence:
+ `sub_word` (Uses the `sub_bytes` lookup table to map the bytes of the key)
+ `rot_word` (Rotates the 32-bit key word)
+ `rcon` (Uses a defined constant for a XOR operation based on current round)

#### Decryption

The procedures that make up the inverse cipher algorithm:
+ `inv_sub_bytes`
+ `inv_shift_rows`
+ `inv_mix_cols`
+ `round_key`

Like in encryption, most of the rounds involves each of these steps, 
but there are exceptions for the beginning and at the end. These
steps are run for a certain number of rounds, based on the keysize.

##### InvSubBytes

SubBytes, but with a different S-Box matrix.

##### InvShiftRows

We simply shift the rows right instead of left circularly.

##### InvMixCols

We do a matrix multiplication by a different set of constants.
The lookup tables posted to Piazza were super useful for this.

##### RoundKey

RoundKey functions the same as in encryption, but we simply choose 
a different index of key from within the generated schedule to apply
to the matrix. This works because it is a XOR operation.