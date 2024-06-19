import json


def isValid(username, password):
    """checks the validity of a username a password 

    Args:
        username (string): inputted username
        password (string): inputted password

    Returns:
        bool: boolean for "are these details saved in the database?"
    """
    with open("database.json") as f:
        data = json.load(f)
        user_list = data["users"]
        for user in user_list:
            if user["username"] == username and user["password"] == password:
                return True
        return False


def isUnique(username):
    """checks if a username is already in the database to check if
    it would be unique for a player trying to sign up

    Args:
        username (string): the username being checked

    Returns:
        bool: boolean for "will this username be unique?"
    """
    with open("database.json") as f:
        data = json.load(f)
        user_list = data["users"]
        for user in user_list:
            if user["username"] == username:
                return False
        return True


def addUser(username, password):
    """adding a new user to the database with 0 kills

    Args:
        username (string): username of the new player
        password (string): password of the new player
    """
    # reading the file
    with open('database.json') as f:
        data = json.load(f)
        # current list of dicts
        current_users = data["users"]
        # defining new dict for the new player
        new_user = {"username": username, "password": password, "kills": 0}
        # adding the new player to the list of dicts
        current_users.append(new_user)

    # writing the updated list back into the json file
    with open('database.json', "w") as f:
        json.dump(data, f, indent=4)


def signUp(username, password):
    """full function for the sign up process, check if a user 
    is unique, if its unique it adds it to the database. if
    its not unique than it doesn't

    Args:
        username (string): username 
        password (string): password

    Returns:
        bool: boolean for "was the process successful?"
    """
    if isUnique(username):
        addUser(username, password)
        return True
    return False


def addKill(username):
    """adds a kill for the specified player

    Args:
        username (string): username of player that has got another kill

    Returns:
        bool: return whether the addition was successful
    """
    did_work = False
    with open("database.json") as f:
        data = json.load(f)
        user_list = data["users"]
        for user in user_list:
            if user["username"] == username:
                user["kills"] = user["kills"] + 1
                did_work = True

    # writing the updated list back into the json file
    with open('database.json', "w") as f:
        json.dump(data, f, indent=4)

    return did_work


def getKills(username):
    """gets the amount of kills a player has

    Args:
        username (string): the username of the player

    Returns:
        int: the number of kills
    """
    with open("database.json") as f:
        data = json.load(f)
        user_list = data["users"]
        for user in user_list:
            if user["username"] == username:
                return user["kills"]


def getLeaderboard():
    """returns the top 3 users along with their kills

    Returns:
        list: list of 3 tuples, each tuple containing username and kill count
    """
    with open("database.json") as f:
        data = json.load(f)
        user_dict_list = data["users"]
        user_kills_tup_list = []
        for user in user_dict_list:
            user_kills_tup_list.append((user["username"], user["kills"]))
        sorted_list = sorted(user_kills_tup_list, key=lambda x: x[1], reverse=True)
        return sorted_list[:3]

