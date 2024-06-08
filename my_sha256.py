import hashlib


def hash_string(input_string):
    """hashing function using sha256 but on strings

    Args:
        input_string (string): the data being encrypted

    Returns:
        string: hashed string
    """
    # making hash object
    hash_object = hashlib.sha256()

    # feeding the string into the object as bytes
    hash_object.update(input_string.encode())

    # digest the data as hexadecimal string of the hash
    # return it
    return hash_object.hexdigest()
