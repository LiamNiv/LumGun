import sympy
from random import randint
from math import gcd

# Class for RSA encryption made by the server


class RSAHelper:
    """class for all RSA encryption needs, can generate keys,
    encrypt and decrypt
    """

    def __init__(self):
        """goes through the process of creating keys
        """
        while True:
            # generate p - large prime
            p = sympy.nextprime(randint(2**1018, 2**1023))

            # generate q - large prime
            q = sympy.nextprime(randint(2**1018, 2**1023))

            # regenerate q if needed
            while q == p:
                q = sympy.nextprime(randint(2**1018, 2**1023))

            # constant component of public/private keys
            n = p * q

            # helps create e, public key
            phi = (p - 1) * (q - 1)

            # very common co-prime to phi
            e = 65537

            # if e is co-prime with phi, exit the loop, we have what we need
            # if its not co-prime, q and p will be regenerated
            if gcd(e, phi) == 1:
                break

        # d = (1/e)(mod phi)
        d = pow(e, -1, phi)

        self.public_key = (e, n)
        self.private_key = (d, n)

    def get_public_key(self):
        return self.public_key

    def rsa_decrypt(self, encrypted_message):
        """decrypts the encrypted AES key

        Args:
            encrypted_message (int): encrypted AES key

        Returns:
            bytes: AES key
        """
        # splitting the private key to d and n
        d, n = self.private_key
        # decrypting {m = (c^d)(mod n)}
        decrypted_int = pow(encrypted_message, d, n)
        # returning msg to bytes
        # adding 7 and floor dividing by 8 the bit length to calculate the length of the decrypted msg
        decrypted_message = decrypted_int.to_bytes(
            (decrypted_int.bit_length() + 7) // 8, byteorder='big')
        return decrypted_message

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
        # converting the AES key to int
        message_as_int = int.from_bytes(message, byteorder='big')
        # encrypting {c = (m^e)(mod n)}
        encrypted_data = pow(message_as_int, e, n)
        return encrypted_data
