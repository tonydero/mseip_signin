import getpass
from hashlib import sha512
from cryptography.fernet import Fernet
from distutils.util import strtobool

val_incorrect = 1
while val_incorrect:
    input_val = getpass.getpass('What do you want to hash or encode'
                               '(will not show)? ')
    hash_input = strtobool(input('Do you want to hash the input? (\'n\' will '
                                 'use reversible encryption instead) '))
    if hash_input:
        output_val = sha512(bytes(input_val, encoding='ascii')).hexdigest()
    else:
        with open('fernet_key', 'r') as f:
            key_str = f.read()
        c = Fernet(bytes(key_str,encoding='utf-8'))
        output_val = c.encrypt(bytes(input_val,encoding='utf-8'))
        output_val = output_val.decode('utf-8')
        decode_val = c.decrypt(bytes(output_val,encoding='utf-8')).decode(
                     'utf-8')
    print(output_val, 'is the output result')
    show_decoded = strtobool(input('Show the decrypted value? '))
    if show_decoded:
        print(decode_val, 'is what will be decrypted')
    val_incorrect = not strtobool(input('Is this okay? '))
file_out = strtobool(input('Do you want to output this to a file? '))
if file_out:
    file_name = input('What do you want to name the file? ')
    with open(file_name, 'w') as f:
        f.write(output_val)

