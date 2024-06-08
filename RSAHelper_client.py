from random import randint
from math import gcd


class RSAHelper_client:
    """class meant for RSA encryption in only the client side,
    incapable of generating keys or holding a private key, cant decrypt data
    """

    def __init__(self, public_key):
        self.public_key = (int(public_key[0]), int(public_key[1]))

    def get_public_key(self):
        return self.public_key

    def rsa_encrypt(self, message):
        """in charge of encrypting the AES key, 
        turns the key from a binary to int and then encrypts it using RSA

        Args:
            message (bytes): AES key being encrypted

        Returns:
            int: encrypted AES key
        """
        # separating the public key to e and n
        e, n = self.public_key
        # converting the AES key from bytes to int
        message_as_int = int.from_bytes(message, byteorder='big')
        # encrypting {c = (m^e)(mod n)}
        encrypted_data = pow(message_as_int, e, n)
        return encrypted_data
