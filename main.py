import time


class Game_Object:
    def __init__(self, length): #Objects are created in the play area at the top of the screen
        self.MOVE_STATES = ("LEFT", "RIGHT")
        self.Move_State = self.MOVE_STATES[1]
        self.length = length
        self.x_pos = 0
        self.y_pos = 0
        self.is_active = True #Playable user piece
        self.is_falling = False #User has dropped the object
        self.last_fall_frame = 0
        self.last_move_frame = 0

class Stacker_Game:
    def __init__(self, x, y):
        self.MAX_X = x
        self.MAX_Y = y
        self.FRAME_TIMING = 30 # 30 frames must pass before the lock releases on input
        self.FALL_RATE = 10  # Every 10 frames we can move 1 y level
        self.MOVE_RATE = 35 # Bigger is Easier Adjusted every 2 y level
        self.STATES = ("INTRO", "START",
                       "END")  # Game state will move from INTRO to START on input, From Start to END on Game completion

        self.Current_State = self.STATES[0] #All Games objects will start at the intro screen
        self.Board_State = [None] * x[None] * y  # An empty board that does not contain any game objects start of game
        self.current_frame = 0  # total count of number of frames for this game iteration
        self.last_input = 0 # Frame number where button was last counted without a lock present
        self.is_input = False
        self.active_game_object = None
        self.difficulty = 3

    def input_listen(self):  # Listen for button pushes
        return False

    def board_update(self, is_input):  # Update the current game state of the internal board
        def below_check():
            cur_y, cur_x = self.active_game_object.y_pos, self.active_game_object.x_pos
            if cur_y + 1 == self.MAX_Y: #We made it to the bottom of the board
                return False
            for tiles in range(self.active_game_object.length):
                if self.Board_State[cur_x][cur_y + 1] is not None:
                    return False
                cur_x += 1
            return True

        def piece_fall(): #Move the piece at the current fall rate
            cur_y, cur_x = self.active_game_object.y_pos, self.active_game_object.x_pos
            for tiles in range(self.active_game_object.length):
                self.Board_State[cur_x][cur_y] = None
                self.Board_State[cur_x][cur_y + 1] = self.active_game_object
                cur_x += 1
            self.active_game_object.last_fall_frame = self.current_frame

        def piece_move():
            cur_y, cur_x = self.active_game_object.y_pos, self.active_game_object.x_pos
            if self.active_game_object.Move_State is "RIGHT": #Left most pixel needs to move Right
                self.Board_State[cur_x][cur_y] = None #Left most Tile is moved
                self.Board_State[cur_x + length][cur_y] = self.active_game_object
                self.active_game_object.x_pos += 1
            else:
                self.Board_State[cur_x + length - 1][cur_y] = None #Left most Tile is moved
                self.Board_State[cur_x - 1][cur_y] = self.active_game_object
                self.active_game_object.x_pos += 1

            if self.active_game_object.x_pos + self.active_game_object.length == self.MAX_X: #Compare if Object needs to move left or right
                self.active_game_object.Move_State = self.active_game_object.MOVE_STATES[0]
            elif self.active_game_object.x_pos == 0:
                self.active_game_object.Move_State = self.active_game_object.MOVE_STATES[1]

        def end_game():
            pass


        if self.active_game_object is None: # If there is no current playable object generate one in the playable area
            self.active_game_object = Game_Object(self.difficulty)
            for length in range(self.active_game_object.length):
                start_pos = self.active_game_object.x_pos
                self.Board_State[start_pos][0] = self.active_game_object #Update the location of the new game object
                start_pos += 1

        if is_input and self.active_game_object.is_falling is False: #User input has been pressed
            self.active_game_object.is_falling = True
            if below_check(): #If there is no piece below
                piece_fall()
            else: #If the Stack is at the top of the Game area end the game
                end_game()

        else: #When there is no user input we need to check the current active piece and either continue a fall or move
            if self.active_game_object.is_falling:
                if below_check():
                    if self.current_frame - self.active_game_object.last_fall_frame > self.FALL_RATE:
                        piece_fall()
                else:
                    self.active_game_object.is_falling = False
            else:
                piece_move()




    def draw_board(self):  # Push board state to the physical LEDs
        pass

    def game_loop(self):  # Handles all high elevated logic for the game
         #3 easiest - 1 hardest
        while self.Current_State != "END": #Run until game completion
            if self.current_frame - self.last_input > self.FRAME_TIMING: #If the lockout has been removed
                self.is_input = self.input_listen()
                self.last_input = self.current_frame #Update input to start lock out again
            self.board_update(self.is_input) #Move gameplay loop
            self.draw_board() #Update LEDS if needed
            time.sleep(1/self.FRAME_TIMING)   # we need to pause execution so that we run at 30 iterations each step. .03 Is 30 Milliseconds for 30FPS
            self.current_frame += 1
