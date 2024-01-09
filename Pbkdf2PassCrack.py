import hashlib
import base64
import os
import sys
from tqdm import tqdm

"""
Password Cracker for Pbkdf2 SHA hashes.
Specific Software: Apache OFBiz
"""

class PasswordEncryptor:
    def __init__(self, hash_type="SHA", pbkdf2_iterations=10000):
        """
        Initialize the PasswordEncryptor object with a hash type and PBKDF2 iterations.

        :param hash_type: The hash algorithm to use (default is SHA).
        :param pbkdf2_iterations: The number of iterations for PBKDF2 (default is 10000).
        """
        self.hash_type = hash_type
        self.pbkdf2_iterations = pbkdf2_iterations

    def crypt_bytes(self, salt, value):
        """
        Crypt a password using the specified hash type and salt.

        :param salt: The salt used in the encryption.
        :param value: The password value to be encrypted.
        :return: The encrypted password string.
        """
        if not salt:
            salt = base64.urlsafe_b64encode(os.urandom(16)).decode('utf-8')
        hash_obj = hashlib.new(self.hash_type)
        hash_obj.update(salt.encode('utf-8'))
        hash_obj.update(value)
        hashed_bytes = hash_obj.digest()
        result = f"${self.hash_type}${salt}${base64.urlsafe_b64encode(hashed_bytes).decode('utf-8').replace('+', '.')}"
        return result

    def get_crypted_bytes(self, salt, value):
        """
        Get the encrypted bytes for a password.

        :param salt: The salt used in the encryption.
        :param value: The password value to get encrypted bytes for.
        :return: The encrypted bytes as a string.
        """
        try:
            hash_obj = hashlib.new(self.hash_type)
            hash_obj.update(salt.encode('utf-8'))
            hash_obj.update(value)
            hashed_bytes = hash_obj.digest()
            return base64.urlsafe_b64encode(hashed_bytes).decode('utf-8').replace('+', '.')
        except hashlib.NoSuchAlgorithmException as e:
            raise Exception(f"Error while computing hash of type {self.hash_type}: {e}")


def arg_error():
    print("[-] Please provide a HASH and a wordlist path")
    print("[!] hash format: $hash_type$salt$hashed_value")
    print(f"[!] Ex: python3 {sys.argv[0]} '$SHA512$apslifd$uP215aVBpDWFeo5415RzDqRwXQ2I' rockyou.txt")
    sys.exit(1)


# Example usage:
def main(search):
    parts = search.split("$")
    hash_type = parts[1]
    salt = parts[2]
    # Create an instance of the PasswordEncryptor class
    encryptor = PasswordEncryptor(hash_type)

    # Get the number of lines in the wordlist for the loading bar
    total_lines = sum(1 for _ in open(wordlist, 'r', encoding='latin-1'))

    # Iterate through the wordlist with a loading bar and check for a matching password
    with open(wordlist, 'r', encoding='latin-1') as password_list:
        for password in tqdm(password_list, total=total_lines, desc="Processing"):
            value = password.strip()

            # Get the encrypted password
            try:
                hashed_password = encryptor.crypt_bytes(salt, value.encode('utf-8'))
            except Exception as e:
                if "unsupported hash type" in str(e):
                    hash_type = "SHA1"
                    parts[1] = hash_type
                    search = "$".join(parts)
                    encryptor = PasswordEncryptor(hash_type)
                    try:
                        hashed_password = encryptor.crypt_bytes(salt, value.encode('utf-8'))
                    except:
                        print('[-] Invalid HASH')
                        return

            # Compare with the search hash
            if hashed_password == search:
                print(f'[+] Found Password:{value}, hash:{hashed_password}')
                return  # Stop the loop if a match is found
    main(f'{search}=')


if __name__ == "__main__":
    if len(sys.argv) != 3:
        arg_error()
    else:
        try:
            search = sys.argv[1]
            wordlist = sys.argv[2]
            main(search)
        except:
            arg_error()
