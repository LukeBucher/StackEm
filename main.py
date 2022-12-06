import RPi.GPIO as GPIO
import board
import neopixel
import time
from itertools import chain

RED = (255, 0, 0)
BLACK = (0, 0, 0)


class Game_Object:
    def __init__(self, length):  # Objects are created in the play area at the top of the screen
        self.MOVE_STATES = ("LEFT", "RIGHT")
        self.Move_State = self.MOVE_STATES[1]
        self.length = length
        self.x_pos = 0
        self.y_pos = 0
        self.is_active = True  # Playable user piece
        self.is_falling = False  # User has dropped the object
        self.last_fall_frame = 0
        self.last_move_frame = 0


class Stacker_Game:
    def __init__(self):
        self.pixels = neopixel.NeoPixel(board.D18, 300,brightness=.5,auto_write=False)
        self.MAX_X = 5
        self.MAX_Y = 15
        self.FRAME_TIMING = 15  # 30 frames must pass before the lock releases on input
        self.FALL_RATE = 10  # Every 10 frames we can move 1 y level
        self.MOVE_RATE = 35  # Bigger is Easier Adjusted every 2 y level
        self.STATES = ("INTRO", "START",
                       "END")  # Game state will move from INTRO to START on input, From Start to END on Game completion

        self.Current_State = self.STATES[0]  # All Games objects will start at the intro screen
        self.Board_State = [[None for i in range(15)] for j in range(5)]  # An empty board that does not contain any game objects start of game
        self.current_frame = 0  # total count of number of frames for this game iteration
        self.last_input = 0  # Frame number where button was last counted without a lock present
        self.is_input = False
        self.active_game_object = None
        self.difficulty = 3
        self.max_fall = 14

    def input_listen(self):  # Listen for button pushes
        x = 0
        while x < 25:
            input_state = GPIO.input(23)
            if input_state == False:
                print("Input Pushed")
                return True
            x += 1
            time.sleep(.02)
        return False

    def board_update(self):  # Update the current game state of the internal board
        def below_check():
            cur_y, cur_x = self.active_game_object.y_pos, self.active_game_object.x_pos
            if cur_y + 1 == self.MAX_Y:  # We made it to the bottom of the board
                return False
            for tiles in range(self.active_game_object.length):
                if self.Board_State[cur_x][cur_y + 1] is not None:
                    return False
                cur_x += 1
            return True

        def piece_fall():  # Move the piece at the current fall rate
            cur_y, cur_x = self.active_game_object.y_pos, self.active_game_object.x_pos
            for tiles in range(self.active_game_object.length):
                self.Board_State[cur_x][cur_y] = None
                self.Board_State[cur_x][cur_y + 1] = self.active_game_object
                cur_x += 1
            self.active_game_object.y_pos += 1
            self.active_game_object.last_fall_frame = self.current_frame

        def piece_removal():  # Remove parts of the game piece that are not supported by pieces underneath
            cur_y, cur_x = self.active_game_object.y_pos, self.active_game_object.x_pos
            if cur_y == 14:
                return
            for tiles in range(self.active_game_object.length):
                if self.Board_State[cur_x + tiles][cur_y + 1] == None:
                    self.Board_State[cur_x][cur_y] = None
                    self.active_game_object.length -= 1
                    self.difficulty -= 1

        def piece_move():
            cur_y, cur_x = self.active_game_object.y_pos, self.active_game_object.x_pos
            if self.active_game_object.Move_State == "RIGHT":  # Left most pixel needs to move Right
                self.Board_State[cur_x][cur_y] = None  # Left most Tile is moved
                self.Board_State[cur_x + self.active_game_object.length][cur_y] = self.active_game_object
                self.active_game_object.x_pos += 1
            else:
                self.Board_State[cur_x + self.active_game_object.length - 1][cur_y] = None  # Left most Tile is moved
                self.Board_State[cur_x - 1][cur_y] = self.active_game_object
                self.active_game_object.x_pos -= 1

            if self.active_game_object.x_pos + self.active_game_object.length == self.MAX_X:  # Compare if Object needs to move left or right
                self.active_game_object.Move_State = self.active_game_object.MOVE_STATES[0]
            elif self.active_game_object.x_pos == 0:
                self.active_game_object.Move_State = self.active_game_object.MOVE_STATES[1]
            self.active_game_object.last_move_frame = self.current_frame

        def end_game():
            self.Current_State = self.STATES[2]  # End Game to break loop

        if self.difficulty == 0:  # Player has Lost All blocks
            end_game()

        if self.active_game_object is None:  # If there is no current playable object generate one in the playable area
            self.active_game_object = Game_Object(self.difficulty)
            for length in range(self.active_game_object.length):
                self.Board_State[length][0] = self.active_game_object  # Update the location of the new game object


        if self.is_input and self.active_game_object.is_falling is False:  # User input has been pressed
            self.active_game_object.is_falling = True
            if below_check():  # If there is no piece below
                piece_fall()
            else:  # If the Stack is at the top of the Game area end the game
                end_game()

        else:  # When there is no user input we need to check the current active piece and either continue a fall or move
            if self.active_game_object.is_falling:
                if below_check() and self.active_game_object.y_pos < self.max_fall:
                    if self.current_frame - self.active_game_object.last_fall_frame > self.FALL_RATE:
                        piece_fall()
                else:
                    if self.active_game_object.y_pos != self.max_fall:
                        piece_removal()  # Validate piece is in a valid location
                    self.active_game_object.is_falling = False  # Game object is no longer falling
                    self.active_game_object.is_active = False  # Will generate new object on next loop
                    self.active_game_object = None
                    self.max_fall -= 1
            else:
                if self.current_frame - self.active_game_object.last_move_frame > self.MOVE_RATE:
                    piece_move()

    def draw_board(self):  # Push board state to the physical LEDs
        # Convert tiles to pixels
        output = [(0, 0, 0)] * 300
        for x in range(self.MAX_X):
            for y in range(self.MAX_Y):
                pixel = [[x * 2, y * 2], [x * 2, (y * 2) + 1], [(x * 2) + 1, y * 2], [(x * 2) + 1, (y * 2) + 1]]
                cur_values = [0] * 4
                for i in range(4):
                    cur_values[i] = pixel[i][0] * 30
                    if pixel[i][0] % 2 != 0:
                        cur_values[i] += 31 - pixel[i][1]
                    else:
                        cur_values[i] += pixel[i][1]
                    cur_values[i] = 299 - cur_values[i]
                for item in cur_values:
                    if self.Board_State[x][y] is not None:
                        output[item] = RED
                    else:
                        output[item] = BLACK

        for i in range(len(self.pixels)):
            self.pixels[i] = output[i]
        self.pixels.show()

    def game_loop(self):  # Handles all high elevated logic for the game
        # 3 easiest - 1 hardest
        print("game start")
        while self.Current_State != "END":  # Run until game completion
            print(self.current_frame)
            if self.current_frame - self.last_input > self.FRAME_TIMING and self.active_game_object.is_falling is not True:  # If the lockout has been removed
                self.is_input = self.input_listen()
                if self.is_input:
                    self.last_input = self.current_frame  # Update input to start lock out again
            else:
                self.is_input = False
            self.board_update()  # Move gameplay loop
            self.draw_board()  # Update LEDs if needed
            time.sleep(1/self.FRAME_TIMING)  # we need to pause execution so that we run at 30 iterations each step. .03 Is 30 Milliseconds for 30FPS
            self.current_frame += 1



def main():
    print("start")
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    game = Stacker_Game()
    game.game_loop()
    return print("Success")




main()
