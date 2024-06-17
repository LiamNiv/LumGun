import socket
from _thread import *
from protocol import *
from database_manager import *
from RSAHelper import RSAHelper
from AESHelper import AESHelper
from AES_protocol import *
import pygame
import my_sha256


""" 
==============================================
==============================================

ADMIN PASSWORD

==============================================
==============================================
 """


pygame.init()

screen = pygame.display.set_mode((600, 300))  # screen size
pygame.display.set_caption('LumGun - Server')  # give window title
clock = pygame.time.Clock()  # setting clock

give_access = False
pixel_font_small = pygame.font.Font('font/Pixeltype.ttf', 25)
pixel_font_mid = pygame.font.Font('font/Pixeltype.ttf', 35)
pixel_font_giant = pygame.font.Font('font/Pixeltype.ttf', 80)

# top text
menu_text_top_surf = pixel_font_giant.render(
    "Enter Admin Password", False, 'Black')
menu_text_top_rect = menu_text_top_surf.get_rect(center=(300, 100))

# "click ENTER to activate"
menu_text_bottom_surf = pixel_font_mid.render(
    "Click ENTER to Activate", False, 'Black')
menu_text_bottom_rect = menu_text_bottom_surf.get_rect(center=(300, 270))

""" password """

password_box_height = 150

color_active = pygame.Color(240, 240, 240)
color_passive = pygame.Color(207, 207, 207)

# the "password" text that shows up if text box is passive and empty
password_placeholder_surf = pixel_font_mid.render(
    "password", False, (40, 40, 40))
password_placeholder_rect = password_placeholder_surf.get_rect(
    center=(300, password_box_height))

# var that stores the username
password = ''
censored_password = ''

# the visible border around the username text box
password_border_rect = pygame.Rect(0, 0, 120, 28)
password_border_rect.center = (300, password_box_height)

# colors for the password text box border depending on activity
password_border_rect_color = color_passive

# bool for activeness of username text box
password_box_active = False


""" error message """

error_height = 180

msg = ""
show_error = False

# time from the start of program until error msg needs to be presented
start_time = pygame.time.get_ticks()

# tim from the start of program until current time (when msg is up)
current_time = pygame.time.get_ticks()

# the time the msg is presented, when it gets too big, the msg hides
delta_time = start_time - current_time

while not give_access:
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        # if there is a click it decides if password textbox is active
        if event.type == pygame.MOUSEBUTTONDOWN:
            password_box_active = password_border_rect.collidepoint(event.pos)

        if event.type == pygame.KEYDOWN:
            # if the enter key is not pressed
            if event.key != pygame.K_RETURN:
                if password_box_active:
                    # if the backspace is pressed
                    if event.key == pygame.K_BACKSPACE:
                        # than the last char in password is deleted
                        password = password[0:-1]
                        censored_password = censored_password[0:-1]
                    # limits username length to 18
                    elif len(password) <= 18:
                        allowed_characters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_"
                        # check if the character is in the allowed set
                        if event.unicode in allowed_characters:
                            password += event.unicode
                            censored_password = '*' * len(password)
            else:
                if my_sha256.hash_string(password) == "8e0bdd994d9c0b4a093fa172c049788cfdcdea8a0133bad4abc511ac6189fc48":
                    give_access = True
                else:
                    # change the msg
                    msg = 'Incorrect Password'
                    # starting the 3000 millisecond timer to show msg
                    show_error = True
                    start_time = pygame.time.get_ticks()

    # static elements
    screen.fill('#b4ede1')
    screen.blit(menu_text_top_surf, menu_text_top_rect)
    screen.blit(menu_text_bottom_surf, menu_text_bottom_rect)

    """ password textbox"""

    # changes the color of the password text box outline based on active status
    if password_box_active:
        password_border_rect_color = color_active
    else:
        password_border_rect_color = color_passive

    # draw the password border rect
    pygame.draw.rect(screen, password_border_rect_color,
                     password_border_rect, 2)

    # the surface on which the password is written on
    password_surf = pixel_font_mid.render(censored_password, False, 'Black')
    # the invisible rect around that password
    password_rect = password_surf.get_rect(center=(300, password_box_height))

    # changes the width of the password text box outline based on text length
    password_border_rect.w = max(password_rect.w + 8, 120)

    # makes sure the password border rect is in the center
    password_border_rect.center = (300, password_box_height)

    # decides whether "password" text placeholder shows or actual password
    if len(password) > 0 or password_box_active:
        screen.blit(password_surf, password_rect)
    else:
        screen.blit(password_placeholder_surf, password_placeholder_rect)

    """ error msg """

    # if the error msg is supposed to show
    if show_error:
        error_surf = pixel_font_small.render(msg, False, 'Red')
        error_rect = error_surf.get_rect(center=(300, error_height))
        current_time = pygame.time.get_ticks()
        delta_time = current_time - start_time

        # makes sure the error displays for only 3000 milliseconds
        if delta_time < 3000:
            screen.blit(error_surf, error_rect)
        else:
            show_error = False
            msg = ''

    # draw all our elements
    # update everything
    pygame.display.update()
    clock.tick(60)  # 60 tick per second
pygame.display.quit()


""" 
==============================================
==============================================

Server working - functioning as server

==============================================
==============================================
"""

accept_all_connections_ip = "0.0.0.0"
port = 5555

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


def other(p):
    """returns the value of the other player

    Args:
        p (int): 0 or 1, the number of a player

    Returns:
        int: 0 or 1, whatever p isn't
    """
    if p == 0:
        return 1
    else:
        return 0


try:
    s.bind((accept_all_connections_ip, port))
except socket.error as e:
    str(e)

s.listen(2)
print("Waiting for a connection, Server Started")

rsa_helper = RSAHelper()

players_online = 0
# list for the original spawn positions
spawn_pos = [(200, 250, 200, 200, False, 30), (800, 250, 200, 300, False, 30)]
# list for storing the current player positions
pos = [spawn_pos[0], spawn_pos[1]]
# list for storing the player's usernames
player_usernames = ['', '']
# list for tracking how many shots a player shot, 
# have to use it in case two messages are received
# for the same player in a row
bullets_shot = [0, 0]

# tracking the connections
connections = [None, None]

# saving the AES encryption object per player
aes_lst = [None, None]


def threaded_client(conn, player):

    # sending non sensitive spawn pos cords
    conn.sendall(str.encode(make_pos(spawn_pos[player])))

    """ RSA HANDSHAKE """

    print(f'==== Handshake player {[player + 1]} ===')

    # receiving request for public key
    data = read(conn.recv(120).decode())

    if data == '6':
        print('2. received request for public key')
        # sending the public key
        print('3. sending public key: ' +
              make_public_key(rsa_helper.get_public_key())[1:])
        conn.sendall(str.encode(make_public_key(rsa_helper.get_public_key())))

        # receiving the encrypted aes key
        encrypted_aes_key = read(conn.recv(1000).decode())
        print('7. received encrypted AES key: ' + str(encrypted_aes_key))

        # decrypting the encrypted aes key
        aes_key = rsa_helper.rsa_decrypt(encrypted_aes_key)

        print("8. decrypted AES key: " + str(aes_key))

    # adding to the aes object the one transferred
    aes_lst[player] = AESHelper(aes_key)

    # adding the connection
    connections[player] = conn

    # variable that turns to True if there is a lost connection in the home screen,
    # tells to skip the while True loop for the game in order to shut down the connection
    skip_game_loop = False

    """ SIGN IN / SIGN UP """
    while True:
        data = conn.recv(120)

        # if the there if no data, disconnect the client
        if not data:
            print(f"player {player + 1}: No data received")
            skip_game_loop = True
            break

        print("==== Menu ====")
        print(f"Received from player {player + 1} [encrypted]: ", data)

        data = read(aes_lst[player].aes_decrypt(*read_cipheriv(data)))

        # if the data received doesn't follow protocol, than disconnect him
        if data == 'Protocol Fail':
            print(
                f"player {player + 1}: Decrypted data doesn't follow protocol")
            skip_game_loop = True
            break

        print(f"Received from player {player + 1}: ", data)

        # if the request is for signing in
        if data[2]:
            # if log in was valid
            if isValid(data[0], data[1]):
                # send True back
                conn.sendall(make_cipheriv(
                    aes_lst[player].aes_encrypt(make_ans(True))))
                # go to game loop
                print(f"Sending to player {player + 1}: True")
                break
            # if log in wan NOT valid
            else:
                # send False
                conn.sendall(make_cipheriv(
                    aes_lst[player].aes_encrypt(make_ans(False))))
                # redo the loop
                print(f"Sending to player {player + 1}: False")
                continue
        # if the request is to sign up
        else:
            # if signing up was successful
            if signUp(data[0], data[1]):
                conn.sendall(make_cipheriv(
                    aes_lst[player].aes_encrypt(make_ans(True))))
                # go to game loop
                print(f"Sending to player {player + 1}: True")
                break
            else:
                conn.sendall(make_cipheriv(
                    aes_lst[player].aes_encrypt(make_ans(False))))
                # redo the loop
                print(f"Sending to player {player + 1}: False")
                continue

    # if there wasn't a problem with the login process
    if not skip_game_loop:
        # save the connected name
        player_usernames[player] = data[0]

    """ GAME """

    reply = ""
    while True:
        try:

            # if data wasn't received during sign in
            if skip_game_loop:
                # leave game ppl
                break

            data = conn.recv(120)

            # if there's no data being received
            if not data:
                # print corespondent message
                print(f"player {player + 1}: No data received")
                # exit the game loop
                break

            print("==== Game ====")
            print(f"Received from player {player + 1} [encrypted]: ", data)

            data = read(aes_lst[player].aes_decrypt(*read_cipheriv(data)))

            # if the data received doesn't follow protocol
            if data == 'Protocol Fail':
                # print corespondent message
                print(
                    f"player {player + 1}: Decrypted data doesn't follow protocol")
                # leave game loop
                break

            # if the player reports about his own death
            if data == '5':
                # changes his stored pos to his spawn pos
                pos[player] = spawn_pos[player]
                # adds a kill to the other player
                addKill(player_usernames[other(player)])
                # sends the dead player his spawn position
                conn.sendall(make_cipheriv(
                    aes_lst[player].aes_encrypt(make_pos((pos[player])))))
                continue
            # if its not a death the server will continue like normal
            else:
                # storing the players position into the pos list
                pos[player] = data

            # if a player shot a shot, add one to his shots meant for transfer
            if data[4]:
                bullets_shot[player] += 1

            # setting the reply to be the other players position
            # initializing variable for "should the other player be shooting?"
            other_player_shooting = False

            # updating the isShooting variable for the other player
            if bullets_shot[other(player)] > 0:
                other_player_shooting = True
                bullets_shot[other(player)] -= 1

            # sending a response with all of the detail, inserting the shooting bool in the middle
            reply = (*pos[other(player)][0:4],
                     other_player_shooting, pos[other(player)][5])

            # server prints information
            print(f"Received from player {player + 1}: ", data)
            print(f"Sending to player {player + 1}: ", reply)

            # sending information back to the client:
            # position and name, using protocol 4
            conn.sendall(make_cipheriv(aes_lst[player].aes_encrypt(
                make_name((*reply, player_usernames[other(player)])))))
        except error as e:
            print(e)

    # the server lost connection with the user

    print(f"player {player + 1}: Lost connection")
    # resetting position to spawn position
    pos[player] = spawn_pos[player]
    # resetting the username
    player_usernames[player] = ''
    # resetting the count of the player
    bullets_shot[player] = 0
    # clearing connection
    connections[player] = None
    aes_lst[player] = None
    conn.close()


while True:
    # accepting connections
    conn, addr = s.accept()
    print("Connected to:", addr)

    # finding player slots
    player_slot = -1
    for i in range(2):
        if connections[i] is None:
            player_slot = i
            break

    # if both the slots are filled
    if player_slot == -1:
        # print msg
        print("Server full, cannot handle more connections.")
        # close the new connection
        conn.close()
        continue

    start_new_thread(threaded_client, (conn, player_slot))

    players_online = players_online + 1
