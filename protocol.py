"""
general protocol headers
1: request to log in or sign up (username, password, isTryingToLogIn)
2: player game status (pos_x, posy, angle, isShooting, health)
3: an answer to a request to log in (isValid)
4: player game status (like 2) + enemy's name 
5: this digit simply marks the player requesting his original spawn position from the server, with the player username that killed him
6: handshake - client requesting to get the server's public key, not stripped
7: public key being sent from the server to the client
8: encrypted aes key being sent back to the server
a: request from client for getting the top 3 leaderboard
b: message from server with the top 3 leader board. list len 3 containing tuples with username and kill count
"""


# reads data in a form of a string and uses the other functions
# also strips the protocol header
def read(data):
    try:
        first_letter = data[0]
        data = data[1:]
        if first_letter == '1':
            return read_details(data)
        elif first_letter == '2':
            return read_pos(data)
        elif first_letter == '3':
            return read_ans(data)
        elif first_letter == '4':
            return read_full_pos(data)
        elif first_letter == '5':
            return read_death(data)
        elif first_letter == '6':
            return '6'
        elif first_letter == '7':
            return read_public_key(data)
        elif first_letter == '8':
            return read_encrypted_key(data)
        elif first_letter == 'a':
            return "a"
        elif first_letter == "b":
            return read_leaderboard(data)
        else:
            print('invalid protocol head-number: ' + first_letter)
            return 'Protocol Fail'
    except Exception as e:
        print(f"An error occurred: {e}")
        return 'Protocol Fail'


""" ==== 1 ==== """


def read_details(data):
    """splits data requesting to log in

    Args:
        data (string): all of the parameters split with a ","

    Returns:
        tuple: (string) username, (string) password, (bool) isTryingToLogIg
    """
    try:
        data = data.split(',')
        if data[2] == 'True':
            return str(data[0]), str(data[1]), True
        else:
            return str(data[0]), str(data[1]), False
    except Exception as e:
        print(f"An error occurred: {e}")
        return 'Protocol Fail'


def make_details(data):
    """makes a protocol string from a sign in / up request 

    Args:
        tuple: (string) username, (string) password, (bool) isTryingToLogIg

    Returns:
        data (string): all of the parameters split with a "," + number "1" at the start
    """

    try:
        if data[2]:
            return f"1{str(data[0])},{str(data[1])},True"
        else:
            return f"1{str(data[0])},{str(data[1])},False"
    except Exception as e:
        print(f"An error occurred: {e}")
        return 'Protocol Fail'


""" ==== 2 ==== """

# translates string data of player's game position and status
# parameters: pos_x, pos_y, mouse_pos_x, mouse_pos_y, isShooting, health
# (mouse pos referring to one of their own screen ranging from 0 to screen dimensions)


def read_pos(data):
    """converts string data about the players position to individual variables

    Args:
        data (string): all of the players position attributes divided by ","

    Returns:
        tuple: (int) pos_x, (int) pos_y, (int) mouse_pos_x, (int) mouse_pos_y, (bool) isShooting, (int) health
    """
    try:
        data = data.split(",")
        if data[3] == "True":
            return int(data[0]), int(data[1]), int(float(data[2])), True, int(data[4])
        else:
            return int(data[0]), int(data[1]), int(float(data[2])), False, int(data[4])
    except Exception as e:
        print(f"An error occurred: {e}")
        return 'Protocol Fail'

# makes  data of player's game position and status from string
# parameters: pos_x, pos_y, mouse_pos_x, mouse_pos_y, isShooting, health
# (mouse pos referring to one of their own screen ranging from 0 to screen dimensions)


def make_pos(data):
    """converts data in tuple about the players position to a protocol string

    Args:
        tuple: (int) pos_x, (int) pos_y, (int) mouse_pos_x, (int) mouse_pos_y, (bool) isShooting, (int) health

    Returns:
        data (string): all of the players position attributes divided by "," + a "2" on the start
    """

    try:
        if data[3]:
            return f'2{str(data[0])},{str(data[1])},{str(data[2])},True,{str(data[4])}'
        else:
            return f'2{str(data[0])},{str(data[1])},{str(data[2])},False,{str(data[4])}'
    except Exception as e:
        print(f"An error occurred: {e}")
        return 'Protocol Fail'


""" ==== 3 ==== """

# reading string data indicating log in status


def read_ans(data):
    """reading string data from the server regarding a log in / sign up request

    Args:
        data (string): as string representation of True or False

    Returns:
        bool: the original answer from the server
    """
    try:
        if data == "True":
            return True
        else:
            return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return 'Protocol Fail'

# make string from data indicating log in status


def make_ans(data):
    """making a protocol following string data from the 
    server regarding a log in / sign up request

    Args:
        bool: the original answer from the server

    Returns:
        data (string): as string representation of True or False + a "3" on the start
    """

    try:
        if data:
            return '3True'
        else:
            return '3False'
    except Exception as e:
        print(f"An error occurred: {e}")
        return 'Protocol Fail'


""" ==== 4 ==== """


def read_sub_full_pos(data):
    """converts string data about the players position and username to individual variables

    Args:
        data (string): all of the players position attributes divided by "," + his username

    Returns:
        tuple: (int) pos_x, (int) pos_y, (int) angle,
        (bool) isShooting, (int) health, (string) username
    """
    try:
        data = data.split(",")
        if data[3] == "True":
            return int(data[0]), int(data[1]), int(float(data[2])), True, int(data[4]), data[5]
        else:
            return int(data[0]), int(data[1]), int(float(data[2])), False, int(data[4]), data[5]
    except Exception as e:
        print(f"An error occurred: {e}")
        return 'Protocol Fail'


def make_sub_full_pos(data):
    """converts data in tuple about the players position and username to a protocol string

    Args:
        tuple: (int) pos_x, (int) pos_y, angle, (bool) isShooting, (int) health, (string) username

    Returns:
        data (string): all of the players position attributes and username divided by "," + a "4" on the start
    """
    try:
        if data[3]:
            ret = f"{data[0]},{data[1]},{data[2]},True,{data[4]},{data[5]}"
            return ret
        else:
            ret = f"{data[0]},{data[1]},{data[2]},False,{data[4]},{data[5]}"
            return ret
    except Exception as e:
        print(f"An error occurred: {e}")
        return 'Protocol Fail'


def read_full_pos(data):
    try:
        data = data.split(".")
        full_details_list = []
        for sub_name in data:
            full_details_list.append(read_sub_full_pos(sub_name))
        return full_details_list
    except Exception as e:
        print(f"An error occurred: {e}")
        return 'Protocol Fail'
    

def make_full_pos(data):
    try:
        return f'4{make_sub_full_pos(data[0])}.{make_sub_full_pos(data[1])}.{make_sub_full_pos(data[2])}'
    except Exception as e:
        print(f"An error occurred: {e}")
        return 'Protocol Fail'


""" ==== 5 ==== """

def read_death(data):
    return data

def make_death(data):
    return f'5{data}'


""" ==== 7 ==== """

# reads the public key being sent to the client from string


def read_public_key(data):
    """reads the public key being sent from the server to the client,
    the key includes an e and an n

    Args:
        data (string): both attributes of the key divided by a ','

    Returns:
        tuple: (string) public key, (string) n
    """
    try:
        data = data.split(",")
        return data[0], data[1]
    except Exception as e:
        print(f"An error occurred: {e}")
        return 'Protocol Fail'


def make_public_key(data):
    """makes a string for the public key being set from the 
    server to the client

    Args:
        tuple: (string) public key, (string) n

    Returns:
        data (string): both attributes of the key divided by a ','
    """

    try:
        return f"7{data[0]},{data[1]}"
    except Exception as e:
        print(f"An error occurred: {e}")
        return 'Protocol Fail'


""" ==== 8 ====="""


def read_encrypted_key(data):
    """retrieving the int value from a string representing the encrypted AES key

    Args:
        data (string): the encrypted AES key

    Returns:
        (int): the encrypted AES key
    """
    try:
        return int(data)
    except Exception as e:
        print(f"An error occurred: {e}")
        return 'Protocol Fail'


def make_encrypted_key(data):
    """generating a protocol string representing the encrypted AES key

    Args:
        data (int): encrypted AES key

    Returns:
        string: "8" + string of the encrypted AES key
    """
    try:
        return f"8{data}"
    except Exception as e:
        print(f"An error occurred: {e}")
        return 'Protocol Fail'


" ==== b ==== "

def read_leaderboard(data):
    try:
        data = data.split(".")
        leaderboard_list = []
        for user in data:
            leaderboard_list.append(read_leaderboard_user(user))
        return leaderboard_list
    except Exception as e:
        print(f"An error occurred: {e}")
        return 'Protocol Fail'


def read_leaderboard_user(data):
    try:
        data = data.split(",")
        return data[0], int(data[1])
    except Exception as e:
        print(f"An error occurred: {e}")
        return 'Protocol Fail'


def make_leaderboard(data):
    try:
        return f"b{make_leaderboard_user(data[0])}.{make_leaderboard_user(data[1])}.{make_leaderboard_user(data[2])}"
    except Exception as e:
        print(f"An error occurred: {e}")
        return 'Protocol Fail'

def make_leaderboard_user(data):
    try:
        return f"{data[0]},{str(data[1])}"
    except Exception as e:
        print(f"An error occurred: {e}")
        return 'Protocol Fail'