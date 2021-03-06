"""
Shoot Trump in this demo program created with
Python and the Arcade library.

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.asteroid_smasher
"""

import random
import math
import arcade
import os
from typing import cast

#define scaling
STARTING_ASTEROID_COUNT = 3
SCALE = 0.5
SCALE_VOTE = 0.2
SCALE_ITEM = 0.1
SCALE_LIVES = 1.0
ITEM_COUNT = 30
OFFSCREEN_SPACE = 0
SCREEN_WIDTH = 1380
SCREEN_HEIGHT = 800
SCREEN_TITLE = "Trump Smasher - created by Pythoneers"
LEFT_LIMIT = -OFFSCREEN_SPACE
RIGHT_LIMIT = SCREEN_WIDTH + OFFSCREEN_SPACE
BOTTOM_LIMIT = -OFFSCREEN_SPACE
TOP_LIMIT = SCREEN_HEIGHT + OFFSCREEN_SPACE


#Instruction view
class InstructionView(arcade.View):
    """ View to show instructions """

    def __init__(self):
        """ This is run once when we switch to this view """
        super().__init__()
        self.texture = arcade.load_texture("Images/Intro.png")

        # Reset the viewport, necessary if we have a scrolling game and we need
        # to reset the viewport back to the start so we can see what we draw.
        arcade.set_viewport(0, SCREEN_WIDTH - 1, 0, SCREEN_HEIGHT - 1)

    def on_draw(self):
        """ Draw this view """
        arcade.start_render()
        self.texture.draw_sized(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2,
                                SCREEN_WIDTH, SCREEN_HEIGHT)

    def on_key_press(self, symbol, modifiers):
        """ If the user presses ENTER, start the game. """
        if symbol == arcade.key.ENTER:
            game_view = GameView()
            game_view.start_new_game()
            self.window.show_view(game_view)


#for collecting items
class Item(arcade.Sprite):
    """ This class represents the items on our screen. """

    def reset_pos(self):
        # Reset the item to a random spot above the screen
        self.center_y = random.randrange(SCREEN_HEIGHT + 20,
                                         SCREEN_HEIGHT + 100)
        self.center_x = random.randrange(SCREEN_WIDTH)

    def update(self):
        # Move the item
        self.center_y -= 1

        # See if the item has fallen off the bottom of the screen.
        # If so, reset it.
        if self.top < 0:
            self.reset_pos()

class TurningSprite(arcade.Sprite):
    """ Sprite that sets its angle to the direction it is traveling in. """
    def update(self):
        """ Move the sprite """
        super().update()
        self.angle = math.degrees(math.atan2(self.change_y, self.change_x))


class ShipSprite(arcade.Sprite):
    """
    Sprite that represents our space ship.

    Derives from arcade.Sprite.
    """
    def __init__(self, filename, scale):
        """ Set up the space ship. """

        # Call the parent Sprite constructor
        super().__init__(filename, scale)

        # Info on where we are going.
        # Angle comes in automatically from the parent class.
        self.thrust = 0
        self.speed = 0
        self.max_speed = 5
        self.drag = 0.0
        self.respawning = 0

        # Mark that we are respawning.
        self.respawn()


    def respawn(self):
        """
        Called when we die and need to make a new ship.
        'respawning' is an invulnerability timer.
        """
        # If we are in the middle of respawning, this is non-zero.
        self.respawning = 1
        self.center_x = SCREEN_WIDTH / 2
        self.center_y = SCREEN_HEIGHT / 2
        self.angle = 0

    def update(self):
        """
        Update our position and other particulars.
        """
        if self.respawning:
            self.respawning += 1
            self.alpha = self.respawning
            if self.respawning > 250:
                self.respawning = 0
                self.alpha = 255
        if self.speed > 0:
            self.speed -= self.drag
            if self.speed < 0:
                self.speed = 0

        if self.speed < 0:
            self.speed += self.drag
            if self.speed > 0:
                self.speed = 0

        self.speed += self.thrust
        if self.speed > self.max_speed:
            self.speed = self.max_speed
        if self.speed < -self.max_speed:
            self.speed = -self.max_speed

        self.change_x = -math.sin(math.radians(self.angle)) * self.speed
        self.change_y = math.cos(math.radians(self.angle)) * self.speed

        self.center_x += self.change_x
        self.center_y += self.change_y

        # If the ship goes off-screen, move it to the other side of the window
        if self.right < 0:
            self.left = SCREEN_WIDTH

        if self.left > SCREEN_WIDTH:
            self.right = 0

        if self.bottom < 0:
            self.top = SCREEN_HEIGHT

        if self.top > SCREEN_HEIGHT:
            self.bottom = 0

        """ Call the parent class. """
        super().update()


class AsteroidSprite(arcade.Sprite):
    """ Sprite that represents an asteroid. """

    def __init__(self, image_file_name, scale):
        super().__init__(image_file_name, scale=scale)
        self.size = 0

    def update(self):
        """ Move the asteroid around. """
        super().update()
        if self.center_x < LEFT_LIMIT:
            self.center_x = RIGHT_LIMIT
        if self.center_x > RIGHT_LIMIT:
            self.center_x = LEFT_LIMIT
        if self.center_y > TOP_LIMIT:
            self.center_y = BOTTOM_LIMIT
        if self.center_y < BOTTOM_LIMIT:
            self.center_y = TOP_LIMIT


#change MyGame Window to View for the Introduction View
class GameView(arcade.View):
    """ Our custom Window Class"""

    def __init__(self):
        """ Initializer """
        # Call the parent class initializer
        super().__init__()

        self.frame_count = 0
        self.game_over = False

        # Sprite lists
        self.player_sprite_list = arcade.SpriteList()
        self.asteroid_list = arcade.SpriteList()
        self.bullet_list = arcade.SpriteList()
        self.ship_life_list = arcade.SpriteList()
        self.item_list = arcade.SpriteList()
#        self.level_list = arcade.SpriteList()

        # Set up the player
        self.score = 0
        self.player_sprite = None
        self.lives = 3
        self.level = 1

        self.item_list = None

        # Sounds
        Background_Music = arcade.load_sound("Sound/Trump.mp3")
        arcade.play_sound(Background_Music, 0.05)

        self.laser_sound = arcade.load_sound(":resources:sounds/hurt5.wav")
        self.laser2_sound= arcade.load_sound(":resources:sounds/fall1.wav")
        self.hit_sound1 = arcade.load_sound(":resources:sounds/explosion1.wav")
        self.hit_sound2 = arcade.load_sound(":resources:sounds/explosion2.wav")
        self.hit_sound3 = arcade.load_sound(":resources:sounds/hit1.wav")
        self.hit_sound4 = arcade.load_sound(":resources:sounds/hit2.wav")

        #change Mouse Invisible /JD for the Introduction View
        #self.set_mouse_visible(False)
        self.window.set_mouse_visible(False)

        #Background
        self.background = None
        arcade.set_background_color(arcade.color.LIGHT_BLUE)

    def start_new_game(self):
        """ Set up the game and initialize the variables. """

        self.frame_count = 0
        self.game_over = False

        # Sprite lists
        self.player_sprite_list = arcade.SpriteList()
        self.asteroid_list = arcade.SpriteList()
        self.bullet_list = arcade.SpriteList()
        self.ship_life_list = arcade.SpriteList()
        self.item_list = arcade.SpriteList()
#        self.level_list = arcade.SpriteList()

        # Set up the player
        self.score = 0
        self.player_sprite = ShipSprite(":resources:images/space_shooter/playerShip2_orange.png", SCALE)
        self.player_sprite_list.append(self.player_sprite)
        self.lives = 3

        # icons that represent the player livesand are positioned:
        #x-axis is equal to cursor position and width of the sprite
        #y-Axis is equal to life height
        #+= Adds the value of a numeric expression to the value of a numeric variable or property and assigns the result to the variable or property
        cur_pos = 8
        for i in range(self.lives):
            life = arcade.Sprite(":resources:images/space_shooter/playerLife1_orange.png", SCALE_LIVES)
            life.center_x = cur_pos + life.width
            life.center_y = life.height
            cur_pos += life.width
            self.ship_life_list.append(life)

        # Create the items
        for i in range(ITEM_COUNT):

            # Create the item instance
            item = Item("Images/Flag.png", SCALE_ITEM)

            # Position the item
            item.center_x = random.randrange(SCREEN_WIDTH)
            item.center_y = random.randrange(SCREEN_HEIGHT)

            # Add the item to the lists
            self.item_list.append(item)


        # Make the asteroids
        image_list = ("Images/Trump_sprite.png",
                      "Images/Trump_sprite.png",
                      "Images/Trump_sprite.png",
                      "Images/Trump_sprite.png")

        for i in range(STARTING_ASTEROID_COUNT):
            image_no = random.randrange(4)
            enemy_sprite = AsteroidSprite(image_list[image_no], SCALE)
            enemy_sprite.guid = "Asteroid"

            enemy_sprite.center_y = random.randrange(BOTTOM_LIMIT, TOP_LIMIT)
            enemy_sprite.center_x = random.randrange(LEFT_LIMIT, RIGHT_LIMIT)

            enemy_sprite.change_x = random.random() * 2 - 1
            enemy_sprite.change_y = random.random() * 2 - 1

            enemy_sprite.change_angle = (random.random() - 0.5) * 2
            enemy_sprite.size = 4
            self.asteroid_list.append(enemy_sprite)

    def on_draw(self):
        """
        Render the screen.
        """

        # This command has to happen before we start drawing
        arcade.start_render()

        # Draw the background texture
        #arcade.draw_lrwh_rectangle_textured(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, self.background)


        # Draw all the sprites.
        self.asteroid_list.draw()
        self.ship_life_list.draw()
        self.bullet_list.draw()
        self.player_sprite_list.draw()
        self.item_list.draw()
#        self.level_list.draw()


        # Put the text on the screen. #coordinates of the score/ASteroids/Level and the Color
        output = f"Score: {self.score}"
        arcade.draw_text(output, 10, 110, arcade.color.BLACK, 13)

        output = f"Asteroid Count: {len(self.asteroid_list)}"
        arcade.draw_text(output, 10, 80, arcade.color.BLACK, 13)

        output = f"Level: {self.level}"
        arcade.draw_text(output, 10, 50, arcade.color.BLACK, 13)

    # Weapon 1
    def on_key_press(self, symbol, modifiers):
        """ Called whenever a key is pressed. """
        # keyboard controls
        if not self.player_sprite.respawning and symbol == arcade.key.A:
            # look
            bullet_sprite = TurningSprite(":resources:images/space_shooter/laserBlue01.png", SCALE)
            # speed
            bullet_speed = 50
            # in which direction the bullet flies
            bullet_sprite.change_y = \
                math.cos(math.radians(self.player_sprite.angle)) * bullet_speed
            bullet_sprite.change_x = \
                -math.sin(math.radians(self.player_sprite.angle)) \
                * bullet_speed
            # where the bullet starts
            bullet_sprite.center_x = self.player_sprite.center_x
            bullet_sprite.center_y = self.player_sprite.center_y
            bullet_sprite.update()
            # add bulltet to bullet_list
            self.bullet_list.append(bullet_sprite)
            # sound
            arcade.play_sound(self.laser_sound, 0.03)

        # Weapon 2
        # keyboard controls
        if not self.player_sprite.respawning and symbol == arcade.key.D:
            # look
            bullet_sprite = TurningSprite("Images/vote.png", SCALE_VOTE)
            # speed
            bullet_speed = 3
            # in which direction the bullet flies
            bullet_sprite.change_y = \
                math.cos(math.radians(self.player_sprite.angle)) * -bullet_speed
            bullet_sprite.change_x = \
                -math.sin(math.radians(self.player_sprite.angle)) \
                * -bullet_speed
            # where the bullet starts
            bullet_sprite.center_x = self.player_sprite.center_x
            bullet_sprite.center_y = self.player_sprite.center_y
            bullet_sprite.update()
            # add bulltet to bullet_list
            self.bullet_list.append(bullet_sprite)
            # sound
            arcade.play_sound(self.laser2_sound, 0.02)

        if symbol == arcade.key.LEFT:
            self.player_sprite.change_angle = 3
        elif symbol == arcade.key.RIGHT:
            self.player_sprite.change_angle = -3
        elif symbol == arcade.key.UP:
            self.player_sprite.thrust = 0.15
        elif symbol == arcade.key.DOWN:
            self.player_sprite.thrust = -.2
        elif symbol == arcade.key.P:
                # pass self, the current view, to preserve this view's state
            pause = PauseView(self)
            self.window.show_view(pause)

    def on_key_release(self, symbol, modifiers):
        """ Called whenever a key is released. """
        if symbol == arcade.key.LEFT:
            self.player_sprite.change_angle = 0
        elif symbol == arcade.key.RIGHT:
            self.player_sprite.change_angle = 0
        elif symbol == arcade.key.UP:
            self.player_sprite.thrust = 0
        elif symbol == arcade.key.DOWN:
            self.player_sprite.thrust = 0

#One Point for the destruction of each Asteroid
    def split_asteroid(self, asteroid: AsteroidSprite):
        """ Split an asteroid into chunks. """
        x = asteroid.center_x
        y = asteroid.center_y
        self.score += 1

        if asteroid.size == 4:
            for i in range(3):
                image_no = random.randrange(2)
                image_list = ["Images/twitter.png",
                              "Images/twitter.png"]

                enemy_sprite = AsteroidSprite(image_list[image_no],
                                              SCALE * 1.5)

                enemy_sprite.center_y = y
                enemy_sprite.center_x = x

                enemy_sprite.change_x = random.random() * 2.5 - 1.25
                enemy_sprite.change_y = random.random() * 2.5 - 1.25

                enemy_sprite.change_angle = (random.random() - 0.5) * 2
                enemy_sprite.size = 3

                self.asteroid_list.append(enemy_sprite)

        elif asteroid.size == 3:
            for i in range(3):
                image_no = random.randrange(2)
                image_list = ["Images/twitter.png",
                              "Images/twitter.png"]

                enemy_sprite = AsteroidSprite(image_list[image_no],
                                              SCALE * 1.5)

                enemy_sprite.center_y = y
                enemy_sprite.center_x = x

                enemy_sprite.change_x = random.random() * 3 - 1.5
                enemy_sprite.change_y = random.random() * 3 - 1.5

                enemy_sprite.change_angle = (random.random() - 0.5) * 2
                enemy_sprite.size = 2

                self.asteroid_list.append(enemy_sprite)
                self.hit_sound2.play(0.01)

        elif asteroid.size == 2:
            for i in range(3):
                image_no = random.randrange(2)
                image_list = ["Images/fake.png",
                              "Images/fake.png"]

                enemy_sprite = AsteroidSprite(image_list[image_no],
                                              SCALE * 1.5)

                enemy_sprite.center_y = y
                enemy_sprite.center_x = x

                enemy_sprite.change_x = random.random() * 3.5 - 1.75
                enemy_sprite.change_y = random.random() * 3.5 - 1.75

                enemy_sprite.change_angle = (random.random() - 0.5) * 2
                enemy_sprite.size = 1

                self.asteroid_list.append(enemy_sprite)
                self.hit_sound3.play(0.01)

        elif asteroid.size == 1:
            pass

    def on_update(self, x):
        """ Move everything """

        # for collecting items
        self.item_list.update()
    #    self.level_list.update()

        # Generate a list of all sprites that collided with the player.
        hit_list = arcade.check_for_collision_with_list(self.player_sprite, self.item_list)

        # Loop through each colliding sprite, remove it, and add to the score.
        for item in hit_list:
            item.remove_from_sprite_lists()
            self.score += 1

        # Create levels
        if self.score == 10:
            self.level = 2
        if self.score == 30:
            self.level = 3

        # Show the Winner View
        if self.level == 3:
            view = WinnerView()
            self.window.show_view(view)


        self.frame_count += 1

        if not self.game_over:
            self.asteroid_list.update()
            self.bullet_list.update()
            self.player_sprite_list.update()

            for bullet in self.bullet_list:
                asteroids = arcade.check_for_collision_with_list(bullet, self.asteroid_list)

                for asteroid in asteroids:
                    self.split_asteroid(cast(AsteroidSprite, asteroid))  # expected AsteroidSprite, got Sprite instead
                    asteroid.remove_from_sprite_lists()
                    bullet.remove_from_sprite_lists()

                # Remove bullet if it goes off-screen
                size = max(bullet.width, bullet.height)
                if bullet.center_x < 0 - size:
                    bullet.remove_from_sprite_lists()
                if bullet.center_x > SCREEN_WIDTH + size:
                    bullet.remove_from_sprite_lists()
                if bullet.center_y < 0 - size:
                    bullet.remove_from_sprite_lists()
                if bullet.center_y > SCREEN_HEIGHT + size:
                    bullet.remove_from_sprite_lists()

            if not self.player_sprite.respawning:
                asteroids = arcade.check_for_collision_with_list(self.player_sprite, self.asteroid_list)
                if len(asteroids) > 0:
                    if self.lives > 0:
                        self.lives -= 1
                        self.player_sprite.respawn()
                        self.split_asteroid(cast(AsteroidSprite, asteroids[0]))
                        asteroids[0].remove_from_sprite_lists()
                        self.ship_life_list.pop().remove_from_sprite_lists()
                        print("Du Lappen hast einen Unfall gebaut!")
                    else:
                        self.game_over = True
                        print("Du Lappen hast zu viele Unfälle gebaut... Game Over")

            #for Game Over View
            if self.game_over:
                view = GameOverView()
                self.window.show_view(view)


class PauseView(arcade.View):
    def __init__(self, game_view): #initialize new Objekt
        super().__init__() #Superclass (class on "top level")
        self.game_view = game_view #Define View

    def on_show(self):
        arcade.set_background_color(arcade.color.LIGHT_BLUE) #Show the background

    def on_draw(self):
        arcade.start_render() #start rendering

        # Draw player, for effect, on pause screen.
        # The previous View (GameView) was passed in
        # and saved in self.game_view.
        player_sprite = self.game_view.player_sprite #define sprites
        player_sprite.draw() #draw sprites

        # draw an filter over him
        arcade.draw_lrtb_rectangle_filled(left=player_sprite.left,
                                          right=player_sprite.right,
                                          top=player_sprite.top,
                                          bottom=player_sprite.bottom,
                                          color=arcade.color.LIGHT_BLUE + (200,))

        arcade.draw_text("PAUSED", SCREEN_WIDTH/2, SCREEN_HEIGHT/2+50,
                         arcade.color.BLACK, font_size=50, anchor_x="center") #Text in Pause View

        # Show tip to return or reset
        arcade.draw_text("Press Esc. to return",
                         SCREEN_WIDTH/2,
                         SCREEN_HEIGHT/2,
                         arcade.color.BLACK,
                         font_size=20,
                         anchor_x="center")
        """arcade.draw_text("Press Enter to reset",
                         SCREEN_WIDTH/2,
                         SCREEN_HEIGHT/2-30,
                         arcade.color.BLACK,
                         font_size=20,
                         anchor_x="center")"""

    def on_key_press(self, key, _modifiers):
        if key == arcade.key.ESCAPE:   # resume game
            self.window.show_view(self.game_view)
        """elif key == arcade.key.ENTER:  # reset game
            MyGame = GameView()
            self.window.show_view(game_view)"""

#Game Over View
class GameOverView(arcade.View):
    """ View to show when game is over """

    def __init__(self):
        """ This is run once when we switch to this view """
        super().__init__()
        self.texture = arcade.load_texture("Images/GameOverTrump.png")

        # Reset the viewport, necessary if we have a scrolling game and we need
        # to reset the viewport back to the start so we can see what we draw.
        arcade.set_viewport(0, SCREEN_WIDTH - 1, 0, SCREEN_HEIGHT - 1)

    def on_draw(self):
        """ Draw this view """
        arcade.start_render()
        self.texture.draw_sized(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2,
                                SCREEN_WIDTH, SCREEN_HEIGHT)

    def on_key_press(self, symbol, modifiers):
        """ If the user presses ENTER, start the game. """
        if symbol == arcade.key.ENTER:
            game_view = GameView()
            game_view.start_new_game()
            self.window.show_view(game_view)

#Winner View
class WinnerView(arcade.View):
    """ View to show when game is over """

    def __init__(self):
        """ This is run once when we switch to this view """
        super().__init__()
        self.texture = arcade.load_texture("Images/Winner.png")

        # Reset the viewport, necessary if we have a scrolling game and we need
        # to reset the viewport back to the start so we can see what we draw.
        arcade.set_viewport(0, SCREEN_WIDTH - 1, 0, SCREEN_HEIGHT - 1)

    def on_draw(self):
        """ Draw this view """
        arcade.start_render()
        self.texture.draw_sized(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2,
                                SCREEN_WIDTH, SCREEN_HEIGHT)

    def on_key_press(self, symbol, modifiers):
        """ If the user presses ENTER, start the game. """
        if symbol == arcade.key.ENTER:
            game_view = GameView()
            game_view.start_new_game()
            self.window.show_view(game_view)


def main():
    """ Main method """
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, fullscreen= True)
    start_view = InstructionView()
    window.show_view(start_view)
    arcade.run()

if __name__ == "__main__":
    main()
