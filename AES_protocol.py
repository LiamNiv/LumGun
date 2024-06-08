"""
this file is contains the functions that enable sending out
encrypted AES ciphertext along with the iv

when sending information from or to the server, not related to the handshake
these functions are used. the ciphertext that is connected to the iv is 
send as bytes to the server/client, when then its separated for decryption use
"""


def make_cipheriv(data):
    """forms the sent combination of both the ciphertext and the iv

    Args:
        data (tuple): ciphertext, iv

    Returns:
        bytes: iv attached to the end of the ciphertext
    """
    return data[0] + data[1]


def read_cipheriv(data):
    """splits the received combination of the ciphertext and the iv

    Args:
        data (bytes): long string of bytes with the ciphertext and the iv at the end

    Returns:
        tuple: containing the ciphertext and the iv, this tuple will be unpacked for decryption
    """
    # ciphertext being first until the last 16 bytes
    ciphertext = data[:-16]
    # iv being the last 16 bytes
    iv = data[-16:]
    return ciphertext, iv
