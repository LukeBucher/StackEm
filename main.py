from gpiozero import Button
import board
import neopixel
import time
import random
import sys
from itertools import chain


BLACK = (0, 0, 0)
button = Button(2,bounce_time = .5)


class Game_Object:
    def __init__(self, length,current_frame):  # Objects are created in the play area at the top of the screen
        self.MOVE_STATES = ("LEFT", "RIGHT")
        self.Move_State = self.MOVE_STATES[1]
        self.length = length
        self.x_pos = 0
        self.y_pos = 0
        self.is_active = True  # Playable user piece
        self.is_falling = False  # User has dropped the object
        self.last_fall_frame = 0
        self.last_move_frame = current_frame


class Stacker_Game:
    def __init__(self):
        self.CURRENT_COLOR = (0, 255, 0)
        self.pixels = neopixel.NeoPixel(board.D18, 300, brightness=.5, auto_write=False)
        self.MAX_X = 5
        self.MAX_Y = 15
        self.FRAME_TIMING = 35  # 30 frames must pass before the lock releases on input
        self.FALL_RATE = 1  # Every 10 frames we can move 1 y level
        self.MOVE_RATE = 6  # Bigger is Easier Adjusted every 2 y level
        self.STATES = ("INTRO", "START",
                       "END")  # Game state will move from INTRO to START on input, From Start to END on Game completion

        self.Current_State = self.STATES[0]  # All Games objects will start at the intro screen
        self.Board_State = [[None for i in range(15)] for j in
                            range(5)]  # An empty board that does not contain any game objects start of game
        self.current_frame = 0  # total count of number of frames for this game iteration
        self.last_input = 0  # Frame number where button was last counted without a lock present
        self.is_input = False
        self.active_game_object = None
        self.difficulty = 3
        self.max_fall = 14


    def losePrint(self):
        for item in range(len(self.pixels)):
            self.pixels[item] = BLACK
        self.pixels.show()
        self.CURRENT_COLOR = (255, 0, 0)

        self.pixels[1] = self.CURRENT_COLOR
        self.pixels[4] = self.CURRENT_COLOR
        self.pixels[7] = self.CURRENT_COLOR

        self.pixels[52] = self.CURRENT_COLOR
        self.pixels[53] = self.CURRENT_COLOR
        self.pixels[54] = self.CURRENT_COLOR
        self.pixels[55] = self.CURRENT_COLOR
        self.pixels[56] = self.CURRENT_COLOR
        self.pixels[57] = self.CURRENT_COLOR
        self.pixels[58] = self.CURRENT_COLOR

        self.pixels[61] = self.CURRENT_COLOR
        self.pixels[64] = self.CURRENT_COLOR
        self.pixels[65] = self.CURRENT_COLOR
        self.pixels[66] = self.CURRENT_COLOR
        self.pixels[67] = self.CURRENT_COLOR

        self.pixels[112] = self.CURRENT_COLOR
        self.pixels[115] = self.CURRENT_COLOR
        self.pixels[116] = self.CURRENT_COLOR
        self.pixels[117] = self.CURRENT_COLOR
        self.pixels[118] = self.CURRENT_COLOR

        self.pixels[122] = self.CURRENT_COLOR
        self.pixels[123] = self.CURRENT_COLOR
        self.pixels[124] = self.CURRENT_COLOR
        self.pixels[125] = self.CURRENT_COLOR
        self.pixels[126] = self.CURRENT_COLOR
        self.pixels[127] = self.CURRENT_COLOR

        self.pixels[172] = self.CURRENT_COLOR
        self.pixels[177] = self.CURRENT_COLOR

        self.pixels[182] = self.CURRENT_COLOR
        self.pixels[183] = self.CURRENT_COLOR
        self.pixels[184] = self.CURRENT_COLOR
        self.pixels[185] = self.CURRENT_COLOR
        self.pixels[186] = self.CURRENT_COLOR
        self.pixels[187] = self.CURRENT_COLOR

        self.pixels[232] = self.CURRENT_COLOR
        self.pixels[247] = self.CURRENT_COLOR

        self.pixels[292] = self.CURRENT_COLOR
        self.pixels[293] = self.CURRENT_COLOR
        self.pixels[294] = self.CURRENT_COLOR
        self.pixels[295] = self.CURRENT_COLOR
        self.pixels[296] = self.CURRENT_COLOR
        self.pixels[297] = self.CURRENT_COLOR
        self.pixels[298] = self.CURRENT_COLOR

        self.pixels.show()
        

    def winPrint(self):
        for item in range(len(self.pixels)):
            self.pixels[item] = BLACK
        self.pixels.show()
        self.CURRENT_COLOR = (0, 255, 0)

        self.pixels[1] = self.CURRENT_COLOR
        self.pixels[2] = self.CURRENT_COLOR
        self.pixels[3] = self.CURRENT_COLOR
        self.pixels[4] = self.CURRENT_COLOR
        self.pixels[5] = self.CURRENT_COLOR
        self.pixels[6] = self.CURRENT_COLOR
        self.pixels[7] = self.CURRENT_COLOR
        self.pixels[8] = self.CURRENT_COLOR
        self.pixels[9] = self.CURRENT_COLOR

        self.pixels[54] = self.CURRENT_COLOR

        self.pixels[61] = self.CURRENT_COLOR
        self.pixels[62] = self.CURRENT_COLOR
        self.pixels[63] = self.CURRENT_COLOR
        self.pixels[64] = self.CURRENT_COLOR
        self.pixels[65] = self.CURRENT_COLOR
        self.pixels[66] = self.CURRENT_COLOR
        self.pixels[67] = self.CURRENT_COLOR
        self.pixels[68] = self.CURRENT_COLOR
        self.pixels[69] = self.CURRENT_COLOR

        self.pixels[121] = self.CURRENT_COLOR
        self.pixels[122] = self.CURRENT_COLOR
        self.pixels[123] = self.CURRENT_COLOR
        self.pixels[124] = self.CURRENT_COLOR
        self.pixels[125] = self.CURRENT_COLOR
        self.pixels[126] = self.CURRENT_COLOR
        self.pixels[127] = self.CURRENT_COLOR
        self.pixels[128] = self.CURRENT_COLOR
        self.pixels[129] = self.CURRENT_COLOR

        self.pixels[181] = self.CURRENT_COLOR
        self.pixels[182] = self.CURRENT_COLOR
        self.pixels[183] = self.CURRENT_COLOR
        self.pixels[184] = self.CURRENT_COLOR
        self.pixels[185] = self.CURRENT_COLOR
        self.pixels[186] = self.CURRENT_COLOR
        self.pixels[187] = self.CURRENT_COLOR
        self.pixels[188] = self.CURRENT_COLOR
        self.pixels[189] = self.CURRENT_COLOR

        self.pixels[231] = self.CURRENT_COLOR
        self.pixels[232] = self.CURRENT_COLOR
        self.pixels[233] = self.CURRENT_COLOR

        self.pixels[241] = self.CURRENT_COLOR
        self.pixels[242] = self.CURRENT_COLOR
        self.pixels[243] = self.CURRENT_COLOR
        self.pixels[244] = self.CURRENT_COLOR
        self.pixels[245] = self.CURRENT_COLOR
        self.pixels[246] = self.CURRENT_COLOR
        self.pixels[247] = self.CURRENT_COLOR
        self.pixels[248] = self.CURRENT_COLOR
        self.pixels[249] = self.CURRENT_COLOR

        self.pixels.show()


    def below_check(self):
        cur_y, cur_x = self.active_game_object.y_pos, self.active_game_object.x_pos
        if cur_y + 1 == self.MAX_Y:  # We made it to the bottom of the board
            return False
        for tiles in range(self.active_game_object.length):
            if self.Board_State[cur_x][cur_y + 1] is not None:
                return False
            cur_x += 1
        return True

    def piece_fall(self):  # Move the piece at the current fall rate
        cur_y, cur_x = self.active_game_object.y_pos, self.active_game_object.x_pos
        for tiles in range(self.active_game_object.length):
            self.Board_State[cur_x][cur_y] = None
            self.Board_State[cur_x][cur_y + 1] = self.active_game_object
            cur_x += 1
        self.active_game_object.y_pos += 1
        self.active_game_object.last_fall_frame = self.current_frame

    def end_game(self):
        self.Current_State = self.STATES[2]  # End Game to break loop
        self.active_game_object = None

    def input_listen(self):  # Listen for button pushes
        self.active_game_object.is_falling = True
        if self.below_check():  # If there is no piece below
            self.piece_fall()
        else:  # If the Stack is at the top of the Game area end the game
            self.end_game()
        if self.max_fall % 4 == 1:
            self.MOVE_RATE -= 1


    def board_update(self):  # Update the current game state of the internal board
        def piece_removal():  # Remove parts of the game piece that are not supported by pieces underneath
            cur_y, cur_x = self.active_game_object.y_pos, self.active_game_object.x_pos
            if cur_y == 14:
                return
            for tiles in range(self.active_game_object.length):
                if self.Board_State[cur_x + tiles][cur_y + 1] == None:
                    self.Board_State[cur_x + tiles][cur_y] = None
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

        if self.difficulty == 0:  # Player has Lost All blocks
            self.end_game()
        if self.max_fall == 1:
            self.end_game()

        if self.active_game_object is None:  # If there is no current playable object generate one in the playable area
            if self.difficulty > 0 and self.max_fall > 1:
                self.active_game_object = Game_Object(self.difficulty,self.current_frame)
                for length in range(self.active_game_object.length):
                    self.Board_State[length][0] = self.active_game_object  # Update the location of the new game object
        else:  # When there is no user input we need to check the current active piece and either continue a fall or move
            if self.active_game_object.is_falling:
                if self.below_check() and self.active_game_object.y_pos < self.max_fall:
                    if self.current_frame - self.active_game_object.last_fall_frame > self.FALL_RATE:
                        self.piece_fall()
                else:
                    if self.active_game_object.y_pos is self.max_fall:
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
                        cur_values[i] += 29 - pixel[i][1]
                    else:
                        cur_values[i] += pixel[i][1]
                    cur_values[i] = 299 - cur_values[i]
                for item in cur_values:
                    if self.Board_State[x][y] is not None:
                        output[item] = self.CURRENT_COLOR
                    else:
                        output[item] = BLACK

        for i in range(len(self.pixels)):
            self.pixels[i] = output[i]
        self.pixels.show()

    def game_loop(self):  # Handles all high elevated logic for the game
        # 3 easiest - 1 hardest
        button.when_released = self.input_listen

        print("game start")
        game_state = 2
        while self.Current_State != "END":  # Run until game completion
            self.board_update()  # Move gameplay loop
            self.draw_board()  # Update LEDs if needed
            time.sleep(
                1 / self.FRAME_TIMING)  # we need to pause execution so that we run at 30 iterations each step. .03 Is 30 Milliseconds for 30FPS
            self.current_frame += 1
            self.is_input = False
            if 11 > self.max_fall > 7 and game_state == 2:
                self.CURRENT_COLOR = (0,0,255)
                game_state = 1
                if self.difficulty > 2:
                    self.difficulty = 2
            elif self.max_fall < 7 and game_state == 1:
                self.CURRENT_COLOR = (255, 0, 0)
                self.difficulty = 1
                game_state = 0


        if self.Current_State == "END":
            if self.max_fall == 1:
                print("WIN")
                self.winPrint()

            else:
                print("LOSE")
                self.losePrint()
            time.sleep(5)

def main():
    print("start")
    while True:
        game = Stacker_Game()
        game.game_loop()

main()

    
