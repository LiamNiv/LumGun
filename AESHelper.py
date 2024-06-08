from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad


class AESHelper:
    """Class made for AES encryption and decryption for both
    the client and server
    """

    def __init__(self, key=None):
        """making an AES-128 key, can either be generated
        using random 16 bytes or a parameter

        Args:
            key (bytes, optional): AES-128 key. Defaults to None.
        """
        if key is None:
            # 16 bytes for AES-128
            self.key = get_random_bytes(16)
        else:
            self.key = key

    def get_key(self):
        """getting the AES key

        Returns:
            bytes: the AES key
        """
        return self.key

    def aes_encrypt(self, plaintext):
        """encrypts using AES

        Args:
            plaintext (string): the string being encrypts

        Returns:
            tuple: the encrypted text (ciphertext, bytes) and the initialization vector (bytes)
        """
        # setting the unique initialization vector
        iv = get_random_bytes(16)

        # make new AES cipher object for encryption
        # using Cipher Block Chaining (CBC)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)

        # pad plaintext to be a multiple of the block size
        padded_plaintext = pad(plaintext.encode(), AES.block_size)

        # encrypt the padded plaintext
        ciphertext = cipher.encrypt(padded_plaintext)

        return ciphertext, iv

    def aes_decrypt(self, ciphertext, iv):
        """decrypts using AES

        Args:
            ciphertext (bytes): the encrypted info
            iv (bytes): initialization vector

        Returns:
            string: the decrypted string
        """
        # make new AES cipher object for decryption
        cipher = AES.new(self.key, AES.MODE_CBC, iv)

        # decrypt ciphertext
        decrypted_padded_data = cipher.decrypt(ciphertext)

        # unpad decrypted data to get the original plaintext
        decrypted_data = unpad(decrypted_padded_data, AES.block_size)

        return decrypted_data.decode()
