import math
from sys import exit
import pygame
from network import Network
from protocol import *
from AESHelper import AESHelper
from RSAHelper_client import RSAHelper_client
from AES_protocol import *
import my_sha256


class Circle(pygame.sprite.Sprite):
    """The big circle obstacle in the middle of the map

    Args:
        pygame (class): the pygame sprite class
    """

    def __init__(self, pos, group):
        super().__init__(group)
        self.image = pygame.image.load('graphics/Circle.png').convert_alpha()
        self.rect = self.image.get_rect(center=pos)
        self.mask = pygame.mask.from_surface(self.image)


class Slash(pygame.sprite.Sprite):
    """The forward facing slashes obstacles around the map

    Args:
        pygame (class): the pygame sprite class
    """

    def __init__(self, pos, group):
        super().__init__(group)
        self.image = pygame.image.load('graphics/Slash.png').convert_alpha()
        self.rect = self.image.get_rect(center=pos)
        self.mask = pygame.mask.from_surface(self.image)


class Backslash(pygame.sprite.Sprite):
    """The backwards facing slashes obstacles around the map

    Args:
        pygame (class): the pygame sprite class
    """

    def __init__(self, pos, group):
        super().__init__(group)
        self.image = pygame.image.load(
            'graphics/Backslash.png').convert_alpha()
        self.rect = self.image.get_rect(center=pos)
        self.mask = pygame.mask.from_surface(self.image)


class Player(pygame.sprite.Sprite):
    """a player, can move around the map and shoot, 
    either the main player or the enemy

    Args:
        pygame (class): the pygame sprite class
    """

    def __init__(self, pos, isUser, username=''):

        super().__init__()

        self.isUser = isUser

        # decides what skin to give player based on if hes an enemy or not
        if isUser:
            self.original_image = pygame.image.load(
                'graphics/Player.png').convert_alpha()
        else:
            self.original_image = pygame.image.load(
                'graphics/Enemy.png').convert_alpha()

        # setting up basic parameters for the player
        self.image = self.original_image
        self.rect = self.image.get_rect(center=pos)
        self.direction = pygame.math.Vector2()
        self.speed = 2
        self.angle = 0
        self.mask = pygame.mask.from_surface(self.original_image)

        # health bar- gray
        self.health_bar_background = pygame.Surface((30, 4))
        self.health_bar_background.fill((199, 199, 199))
        # actual health variable
        self.health = 30
        self.health_bar_health = pygame.Surface((self.health, 4))
        self.health_bar_health.fill((0, 255, 0))
        self.health_bar_rect = self.health_bar_background.get_rect(
            center=(self.rect.centerx, self.rect.centery - 22))

        # username
        self.username = username
        self.username_font = pygame.font.Font('font/Pixeltype.ttf', 18)
        self.username_surf = self.username_font.render(
            self.username, False, 'Black')
        self.username_rect = self.username_surf.get_rect(
            center=(self.rect.centerx, self.rect.centery - 30))
        
        # tracking the player who shot the player last
        self.last_hit_username = ""

    def set_username(self, username):
        """sets the username to be what is requested

        Args:
            username (string): the new username
        """
        self.username = username

    def face_mouse(self, angle_info):
        """calculates the difference between the players position and the mouse, 
        and applies the rotation needed for the player to face the mouse.

        Args:
            mouse_pos (tuple): containing the mouse x and y position
        """

        # if the angle info given is the mouse position
        player_pos = self.rect.center
        if isinstance(angle_info, tuple):
            # distance between the player and the mouse
            x_dist = angle_info[0] - player_pos[0] + camera_group.offset[0]
            y_dist = -(angle_info[1] - player_pos[1] + camera_group.offset[1])
            # updating the angle of the player, using tan
            self.angle = math.degrees(math.atan2(y_dist, x_dist))
        # if its the angle (for enemy)
        else:
            self.angle = angle_info
        # rotating the image
        self.image = pygame.transform.rotate(
            self.original_image, self.angle - 90)
        self.rect = self.image.get_rect(center=(player_pos[0], player_pos[1]))
        self.mask = pygame.mask.from_surface(self.image)

    def create_bullet(self):
        """shoots a bullet from the player

        Args:
            mouse_pos (tuple): the position of the mouse, pass to the bullet __init__

        Returns:
            Bullet: the bullet being fired
        """
        return Bullet(self.rect.center, self)

    def input(self):
        """is in charge of changing the players direction, 
        which is a 2d vector attribute or the player
        """

        keys = pygame.key.get_pressed()

        if keys[pygame.K_w] and keys[pygame.K_s]:
            self.direction.x = 0
        elif keys[pygame.K_w]:
            self.direction.y = -1
        elif keys[pygame.K_s]:
            self.direction.y = 1
        else:
            self.direction.y = 0

        if keys[pygame.K_d] and keys[pygame.K_a]:
            self.direction.x = 0
        elif keys[pygame.K_d]:
            self.direction.x = 1
        elif keys[pygame.K_a]:
            self.direction.x = -1
        else:
            self.direction.x = 0

    def border_collision(self):
        """in charge making sure the player doesn't exist the fighting arena, 
        by detecting if he is about to head outside and quickly change his position back 
        """
        # half is the player's radius, so the method can detect if the player is
        # touching the border with his outline.
        half = 15
        if self.rect.center[0] < 120 + half:
            self.rect.center = (120 + half, self.rect.center[1])
        if self.rect.center[0] > 880 - half:
            self.rect.center = (880 - half, self.rect.center[1])
        if self.rect.center[1] < 120 + half:
            self.rect.center = (self.rect.center[0], 120 + half)
        if self.rect.center[1] > 380 - half:
            self.rect.center = (self.rect.center[0], 380 - half)

    def obstacle_collision(self):
        """handles the player colliding with the obstacles 
        in the map, simply pushing them the opposite way when they
        try to move into them to simulate a wall
        """
        keys = pygame.key.get_pressed()
        if pygame.sprite.spritecollide(self, camera_group, False, pygame.sprite.collide_mask):
            if keys[pygame.K_w]:
                self.rect.centery += 2
            elif keys[pygame.K_s]:
                self.rect.centery -= 2

            if keys[pygame.K_d]:
                self.rect.centerx -= 2
            elif keys[pygame.K_a]:
                self.rect.centerx += 2

    def bullet_collision(self, bullet_group):
        """checks for collisions of a bullet with a player,
        kills the bullet (third parameter in if) and changes the health

        Args:
            bullet_group (Group): the sprite group containing all of the bullets
        """
        # makes sure the player being hit is only the main one, enemy health is sent
        colliding_bullets = pygame.sprite.spritecollide(self, bullet_group, True, pygame.sprite.collide_mask)
        if colliding_bullets and self.isUser:
            if self.health != 0:
                if self.health == 1:
                    self.last_hit_username = colliding_bullets[0].shooter_username
                self.health -= 1

    def die(self):
        """in charge of sending the info to the server when a player dies
        can only be activated if the main player, not enemy dies, if the enemy dies
        he will trigger this method in his own code and the info will pass through the server
        """

        # sending the sever a message meaning death
        # and receiving the cords to re-spawn
        spawn_pos = read(aes_helper.aes_decrypt(
            *read_cipheriv(n.send(make_cipheriv(aes_helper.aes_encrypt(make_death(self.last_hit_username)))))))

        self.rect.centerx = spawn_pos[0]
        self.rect.centery = spawn_pos[1]
        self.health = spawn_pos[4]

    def update(self, angle_info):
        """updates the player using all of the necessary methods

        Args:
            mouse_pos (tuple): the mouse position
        """



        self.input()
        self.rect.center += self.direction * self.speed
        self.face_mouse(angle_info)
        self.border_collision()
        self.obstacle_collision()
        self.bullet_collision(bullets)

        if self.health == 0 and self.isUser:
            self.die()

        # health bar
        self.health_bar_health = pygame.Surface((self.health, 4))
        self.health_bar_health.fill((0, 255, 0))

        # username
        self.username_surf = self.username_font.render(
            self.username, False, 'Black')
        self.username_rect = self.username_surf.get_rect(
            center=(self.rect.centerx, self.rect.centery - 32))


class Bullet(pygame.sprite.Sprite):
    """class for a single bullet

    Args:
        pygame (class): pygame sprite class
    """

    def __init__(self, pos, player):
        super().__init__()
        # loading the image before its turned to the face the trajectory
        self.original_image = pygame.image.load('graphics/Bullet.png')

        self.rect = self.original_image.get_rect(center=(pos))

        self.angle = player.angle

        self.magnitude = 10

        self.shooter_username = player.username

        # rotates the image
        self.image = pygame.transform.rotate(
            self.original_image, self.angle - 90)

        # positions the bullet right outside the player body, so it doesn't collide with it
        self.rect.center += pygame.Vector2(self.magnitude * math.cos(math.radians(self.angle)),
                                           -self.magnitude * math.sin(math.radians(self.angle))) * 2

        # creates mask
        self.mask = pygame.mask.from_surface(self.image)

    def collision_sprite(self):
        """checks for collision with the edges of the maps or the map's obstacles

        Returns:
            bool: boolean statement for "is the bullet hitting something?"
        """
        if pygame.sprite.spritecollide(self, camera_group, False, pygame.sprite.collide_mask):
            return True
        if self.rect.centerx < 124 or self.rect.centerx > 876 or self.rect.centery < 124 or self.rect.centery > 376:
            return True
        return False

    def update(self):
        """updates the bullet, moving it forward and killing it if it touches anything
        """
        # bullet travel
        self.rect.center += pygame.Vector2(self.magnitude * math.cos(math.radians(self.angle)),
                                           -self.magnitude * math.sin(math.radians(self.angle)))
        # if bullet collides with obstacle it self kills
        if self.collision_sprite():
            self.kill()


class CameraGroup(pygame.sprite.Group):
    """sprite group for all of the obstacles around the map
    ground also in it but not as a sprite
    makes the illusion of the camera following the player
    using a custom blitting function with an offset


    Args:
        pygame (class): the python group class
    """

    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()

        # camera offset
        # serves to keep the player's view on himself
        self.offset = pygame.math.Vector2()
        self.half_w = self.display_surface.get_size()[0] // 2
        self.half_h = self.display_surface.get_size()[1] // 2

        # ground
        self.ground_surf = pygame.image.load(
            'graphics/Background_new.png').convert_alpha()
        self.ground_rect = self.ground_surf.get_rect(topleft=(0, 0))

    def center_target_camera(self, target):
        """in charge of updating the camera offset, 
          in which objects around the map need to be offset by 
          in order to look like they are the ones moving around the player.

        Args:
            target (Player): the main player
        """

        self.offset.x = target.sprite.rect.centerx - self.half_w
        self.offset.y = target.sprite.rect.centery - self.half_h

    def custom_draw(self, player, enemies):
        """
        this method uses the offset in order to create the illusion of
        a camera following the player around, by moving everything around him
        while blitting them into the screen, uses the player as the main "target"
        """

        # calculating the offset (players displacement)
        self.center_target_camera(player)

        # blitting ground
        ground_offset = self.ground_rect.topleft - self.offset
        self.display_surface.blit(self.ground_surf, ground_offset)

        # blitting all of the bullets in the bullets group
        for sprite in bullets.sprites():
            bullet_offset_pos = sprite.rect.topleft - self.offset
            self.display_surface.blit(sprite.image, bullet_offset_pos)

        # blitting player
        player_offset = player.sprite.rect.topleft - self.offset
        self.display_surface.blit(player.sprite.image, player_offset)

        
        for enemy in enemies:
            # blitting enemy
            enemy_offset = enemy.sprite.rect.topleft - self.offset
            self.display_surface.blit(enemy.sprite.image, enemy_offset)


        # blitting all of the obstacles on the map
        for sprite in self.sprites():
            offset_pos = sprite.rect.topleft - self.offset
            self.display_surface.blit(sprite.image, offset_pos)


        # blitting player health
        player_center_offset = player.sprite.rect.center - self.offset
        self.display_surface.blit(player.sprite.health_bar_background,
                                  (player_center_offset[0] - 15, player_center_offset[1] - 22))
        self.display_surface.blit(player.sprite.health_bar_health,
                                  (player_center_offset[0] - 15, player_center_offset[1] - 22))

        # blitting player username
        self.display_surface.blit(player.sprite.username_surf, (
            player_center_offset[0] - player.sprite.username_rect.w//2, player_center_offset[1] - 32))


        for enemy in enemies:
            # blitting enemy health
            enemy_center_offset = enemy.sprite.rect.center - self.offset
            self.display_surface.blit(enemy.sprite.health_bar_background,
                                    (enemy_center_offset[0] - 15, enemy_center_offset[1] - 22))
            self.display_surface.blit(enemy.sprite.health_bar_health,
                                    (enemy_center_offset[0] - 15, enemy_center_offset[1] - 22))
            
            # blitting enemy username
            self.display_surface.blit(enemy.sprite.username_surf, (
            enemy_center_offset[0] - enemy.sprite.username_rect.w//2, enemy_center_offset[1] - 32))






class Button(pygame.sprite.Sprite):
    """button class for the homepage "sign up / in" buttons
    doesn't handle actually being pressed, changes color if
    mouse is hovering over it

    Args:
        pygame (class): the pygame sprite class
    """

    def __init__(self, x, y, width, height, text, button_color_passive=(0, 0, 0), button_color_active=(40, 40, 40), text_color=(255, 255, 255), text_size=25):
        super().__init__()
        # setting up the square
        self.button_rect = pygame.rect.Rect(0, 0, width, height)
        self.button_rect.center = (x, y)

        # colors for rect

        self.color_passive = button_color_passive
        self.color_active = button_color_active
        self.color = color_passive

        # setting up the text
        button_text_font = pygame.font.Font('font/Pixeltype.ttf', text_size)
        self.button_text_surf = button_text_font.render(
            text, False, text_color)
        self.button_text_rect = self.button_text_surf.get_rect(
            center=self.button_rect.center)

    def update(self):
        """if the mouse is on top of the button, it changes the current color attribute
        """
        if self.button_rect.collidepoint(pygame.mouse.get_pos()):
            self.color = self.color_active
        else:
            self.color = self.color_passive

    def draw(self):
        """drawing the button on screen using its current color
        """
        pygame.draw.rect(screen, self.color, self.button_rect)
        screen.blit(self.button_text_surf, self.button_text_rect)


# object with methods including basic communication with the server
n = Network()


pygame.init()
screen = pygame.display.set_mode((300, 300))  # screen size
pygame.display.set_caption('LumGun')  # give window title
clock = pygame.time.Clock()  # setting clock

# bool for game activeness
game_active = False

# initializing sprites in camera group
camera_group = CameraGroup()
b1 = Backslash((320, 320), camera_group)
b2 = Backslash((680, 180), camera_group)
s1 = Slash((600, 300), camera_group)
s2 = Slash((400, 200), camera_group)
c1 = Circle((500, 250), camera_group)

random_pos = read(n.getPos())

# initializing player
player = pygame.sprite.GroupSingle()
player.add(Player((random_pos[0], random_pos[1]), True))
click = False



# initializing enemy
enemy_1 = pygame.sprite.GroupSingle()
enemy_1.add(Player((random_pos[0], random_pos[1]), False))

enemy_2 = pygame.sprite.GroupSingle()
enemy_2.add(Player((random_pos[0], random_pos[1]), False))

enemy_3 = pygame.sprite.GroupSingle()
enemy_3.add(Player((random_pos[0], random_pos[1]), False))

enemies = [enemy_1, enemy_2, enemy_3]

# initializing bullet group
bullets = pygame.sprite.Group()


""" ==== menu screen ==== """




# static elements - text
# fonts
pixel_font_small = pygame.font.Font('font/Pixeltype.ttf', 25)
pixel_font_mid = pygame.font.Font('font/Pixeltype.ttf', 35)
pixel_font_big = pygame.font.Font('font/Pixeltype.ttf', 60)

# big "LumGun" title
menu_text_top_surf = pixel_font_big.render("- LumGun -", False, 'Black')
menu_text_top_rect = menu_text_top_surf.get_rect(center=(150, 50))

# static elements - player pic
menu_player_surf = pygame.image.load('graphics/Player.png').convert_alpha()
menu_player_surf = pygame.transform.scale2x(menu_player_surf)
menu_player_rect = menu_player_surf.get_rect(center=(150, 200))


""" username """

username_box_height = 100

# the "username" text that shows up if text box is passive and empty
username_placeholder_surf = pixel_font_mid.render(
    "username", False, (40, 40, 40))
username_placeholder_rect = username_placeholder_surf.get_rect(
    center=(150, username_box_height))

# var that stores the username
username = ''

# the visible border around the username text box
username_border_rect = pygame.Rect(0, 0, 120, 28)
username_border_rect.center = (150, username_box_height)

# colors for the username text box border depending on activity
color_active = pygame.Color(240, 240, 240)
color_passive = pygame.Color(207, 207, 207)
username_border_rect_color = color_passive

# bool for activeness of username text box
username_box_active = False


""" password """

password_box_height = 130

# the "password" text that shows up if text box is passive and empty
password_placeholder_surf = pixel_font_mid.render(
    "password", False, (40, 40, 40))
password_placeholder_rect = password_placeholder_surf.get_rect(
    center=(150, password_box_height))

# var that stores the username
password = ''
censored_password = ''

# the visible border around the username text box
password_border_rect = pygame.Rect(0, 0, 120, 28)
password_border_rect.center = (150, password_box_height)

# colors for the password text box border depending on activity
password_border_rect_color = color_passive

# bool for activeness of username text box
password_box_active = False


""" error message """

error_height = 155

msg = ""
show_error = False

# time from the start of program until error msg needs to be presented
start_time = pygame.time.get_ticks()

# tim from the start of program until current time (when msg is up)
current_time = pygame.time.get_ticks()

# the time the msg is presented, when it gets too big, the msg hides
delta_time = start_time - current_time


""" buttons """


sign_in_button = pygame.sprite.GroupSingle()
sign_in_button.add(Button(200, 260, 70, 20, 'sign in'))

sign_up_button = pygame.sprite.GroupSingle()
sign_up_button.add(Button(100, 260, 70, 20, 'sign up'))


""" RSA HANDSHAKE """

print('=== client ===')
# contains methods to communicate using aes
aes_helper = AESHelper()

# sending request for the public key
print('1. sending \'6\' to get public key')
public_key = read(n.send_before('6'))

print('4. got the public key: ' + make_public_key(public_key)[1:])
# making encryptor using the public key
rsa_helper_client = RSAHelper_client(public_key)

print('5. AES key: ' + str(aes_helper.get_key()))

# making an encrypted aes key
encrypted_aes_key = rsa_helper_client.rsa_encrypt(aes_helper.get_key())
print('6. made encrypted AES key, sending it: ' + str(encrypted_aes_key))

# sending the encrypted aes key
n.send_no_answer(make_encrypted_key(str(encrypted_aes_key)))


# game loop
while True:
    if (game_active):
        """ ==== game is active ==== """

        # bool var for shooting
        click = False

        # for loop for checking for input to shut program or to shoot
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                bullets.add(player.sprite.create_bullet())
                click = True
            else:
                click = False

        # sending and receiving info from/to enemy
        # cant send if the player is dead
        if player.sprite.health != 0:
            enemy_pos = read(aes_helper.aes_decrypt(*read_cipheriv(n.send(make_cipheriv(aes_helper.aes_encrypt(make_pos((player.sprite.rect.centerx, player.sprite.rect.centery,
                                                                                                                         player.sprite.angle,
                                                                                                                         click, player.sprite.health))))))))


        for enemy, enemy_pos in zip(enemies, enemy_pos):


            # updating enemy's position and health
            enemy.sprite.rect.centerx = enemy_pos[0]
            enemy.sprite.rect.centery = enemy_pos[1]
            enemy.sprite.health = enemy_pos[4]

            # if information is delivered about an enemy's name, save it
            if len(enemy_pos) > 5:
                enemy.sprite.username = enemy_pos[5]

            # check whether to add bullets depending on shooting status of enemy
            if enemy_pos[3]:
                bullets.add(enemy.sprite.create_bullet())

            enemy.update(enemy_pos[2])

        # general color to fill the screen
        screen.fill('#F7D9B4')

        # updates
        bullets.update()
        camera_group.update()
        player.update(pygame.mouse.get_pos())


        camera_group.custom_draw(player, enemies)
    else:
        """ ==== game is NOT active ==== """

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            # if there is a click it decides which textbox is active
            if event.type == pygame.MOUSEBUTTONDOWN:
                # changes the state of text boxes
                username_box_active = username_border_rect.collidepoint(
                    event.pos)
                password_box_active = password_border_rect.collidepoint(
                    event.pos)

                # if the sign in button was clicked
                if sign_in_button.sprite.button_rect.collidepoint(event.pos):
                    # than it would send the details to the server and check for validity
                    if read(aes_helper.aes_decrypt(*read_cipheriv(n.send(make_cipheriv(aes_helper.aes_encrypt(make_details((username, my_sha256.hash_string(password), True)))))))):
                        # changes game state to on because details got approved
                        game_active = True
                        enemy_pos = read(aes_helper.aes_decrypt(*read_cipheriv(n.send(make_cipheriv(aes_helper.aes_encrypt(make_pos((player.sprite.rect.centerx, player.sprite.rect.centery,
                                                                                                                                     player.sprite.angle,
                                                                                                                                     click, player.sprite.health))))))))
                        player.sprite.username = username
                    # if the details are not good
                    else:
                        msg = 'Details don\'t match with any users'
                        show_error = True
                        start_time = pygame.time.get_ticks()
                # if the sign up button was clicked
                if sign_up_button.sprite.button_rect.collidepoint(event.pos):

                    # checking for min username and password length, locally
                    if len(username) <= 1:
                        msg = 'Username must be at least 2 letters'
                        show_error = True
                        start_time = pygame.time.get_ticks()
                    elif len(password) <= 5:
                        msg = 'Password must be at least 6 letters'
                        show_error = True
                        start_time = pygame.time.get_ticks()
                    # checking for servers response
                    # if the sign up request is positive
                    elif read(aes_helper.aes_decrypt(*read_cipheriv(n.send(make_cipheriv(aes_helper.aes_encrypt(make_details((username, my_sha256.hash_string(password), False)))))))):
                        # changes game state to on because details got approved
                        game_active = True
                        enemy_pos = read(aes_helper.aes_decrypt(*read_cipheriv(n.send(make_cipheriv(aes_helper.aes_encrypt(make_pos((player.sprite.rect.centerx, player.sprite.rect.centery,
                                                                                                                                     player.sprite.angle,
                                                                                                                                     click, player.sprite.health))))))))
                        player.sprite.username = username
                    # sign up request is negative
                    else:
                        # change the msg
                        msg = 'Username already taken'
                        # starting the 3000 millisecond timer to show msg
                        show_error = True
                        start_time = pygame.time.get_ticks()

            if event.type == pygame.KEYDOWN:
                # makes sure enter doesn't count
                if event.key != pygame.K_RETURN:

                    if username_box_active:
                        # if the backspace is pressed
                        if event.key == pygame.K_BACKSPACE:
                            # than the last char in username is deleted
                            username = username[0:-1]
                        # limits username length to 12
                        elif len(username) <= 12:
                            allowed_characters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_"
                            # check if the character is in the allowed set
                            if event.unicode in allowed_characters:
                                username += event.unicode
                    elif password_box_active:
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

        # static menu elements
        screen.fill('#b4ede1')
        screen.blit(menu_text_top_surf, menu_text_top_rect)
        screen.blit(menu_player_surf, menu_player_rect)

        """ username textbox """

        # changes the color of the username text box outline based on active status
        if username_box_active:
            username_border_rect_color = color_active
        else:
            username_border_rect_color = color_passive

        # draw the username border rect
        pygame.draw.rect(screen, username_border_rect_color,
                         username_border_rect, 2)

        # the surface on which the username is written on
        username_surf = pixel_font_mid.render(username, False, 'Black')
        # the invisible rect around that username
        username_rect = username_surf.get_rect(
            center=(150, username_box_height))

        # changes the width of the username text box outline based on text length
        username_border_rect.w = max(username_rect.w + 8, 120)

        # makes sure the username border rect is in the center
        username_border_rect.center = (150, username_box_height)

        # decides whether "username" text placeholder shows or actual username
        if len(username) > 0 or username_box_active:
            screen.blit(username_surf, username_rect)
        else:
            screen.blit(username_placeholder_surf, username_placeholder_rect)

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
        password_surf = pixel_font_mid.render(
            censored_password, False, 'Black')
        # the invisible rect around that password
        password_rect = password_surf.get_rect(
            center=(150, password_box_height))

        # changes the width of the password text box outline based on text length
        password_border_rect.w = max(password_rect.w + 8, 120)

        # makes sure the password border rect is in the center
        password_border_rect.center = (150, password_box_height)

        # decides whether "password" text placeholder shows or actual password
        if len(password) > 0 or password_box_active:
            screen.blit(password_surf, password_rect)
        else:
            screen.blit(password_placeholder_surf, password_placeholder_rect)

        """ error msg """

        if show_error:
            error_surf = pixel_font_small.render(msg, False, 'Red')
            error_rect = error_surf.get_rect(center=(150, error_height))
            current_time = pygame.time.get_ticks()
            delta_time = current_time - start_time

            # makes sure the error displays for only 3000 milliseconds
            if delta_time < 3000:
                screen.blit(error_surf, error_rect)
            else:
                show_error = False
                msg = ''

        """ buttons """

        sign_in_button.sprite.update()
        sign_in_button.sprite.draw()

        sign_up_button.sprite.update()
        sign_up_button.sprite.draw()

    # draw all our elements
    # update everything
    pygame.display.update()
    clock.tick(60)  # 60 tick per second
