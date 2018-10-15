import getpass
from hashlib import sha512
from distutils.util import strtobool

val_incorrect = 1
while val_incorrect:
    pass_val = getpass.getpass('What do you want to hash (will not show)? ')
    pass_hex = sha512(bytes(pass_val, encoding='ascii')).hexdigest()
    print(pass_hex, 'is the hex hash of your input.')
    val_incorrect = not strtobool(input('Is this okay? '))
file_out = strtobool(input('Do you want to output this to a file? '))
if file_out:
    file_name = input('What do you want to name the file? ')
    with open(file_name, 'w') as f:
        f.write(pass_hex)

