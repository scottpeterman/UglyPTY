import os
from cryptography.fernet import Fernet

# Check if the file exists
if os.path.isfile('crypto.key'):
    # Ask the user for confirmation
    confirm = input(
        'The file "crypto.key" already exists, do you want to overwrite it? This will invalidate your currently encrypted passwords. (y/n): ')

    # Check the user's response
    if confirm.lower() != 'y':
        print('Operation cancelled.')
        exit()

# Generate a key
key = Fernet.generate_key()

# Save the key to the file
with open('crypto.key', 'wb') as file:
    file.write(key)

print('Key saved to "crypto.key".')

