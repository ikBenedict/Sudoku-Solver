# Sudoku-GUI.py
import pygame
import time
from random import sample
pygame.font.init()


def Gen():
    # randomize rows, columns and numbers (of valid 3 pattern)
    rB = range(3) 
    rows  = [ g*3 + r for g in sample(rB,len(rB)) for r in sample(rB,len(rB)) ] 
    cols  = [ g*3 + c for g in sample(rB,len(rB)) for c in sample(rB,len(rB)) ]
    v=range(1,3*3+1)
    nums=sample(v,len(v))
    # produce board using randomized baseline pattern
    global board
    board = [ [nums[(3*(r%3)+r//3+c)%9] for c in cols] for r in rows ]
    squares=9*9
    empties = squares * 5//10

    for p in sample(range(squares),empties):
        board[p//9][p%9] = 0
    return board


class Space:
    def __init__(self, rows, cols, width, height, win, board):
        self.rows = rows
        self.cols = cols
        self.board=board
        #calls Cell i*j times, so its a i*j array
        self.cubes = [[Cell(self.board[i][j], i, j, width, height) for j in range(cols)] for i in range(rows)]
        self.width = width
        self.height = height
        self.model = None
        self.update_model()
        self.selected = None
        self.win = win

    def update_model(self):
        self.model = [[self.cubes[i][j].value for j in range(self.cols)] for i in range(self.rows)]

    #The verification call (called when ENTER is pressed) 
    def place(self, val):
        row, col = self.selected
        if self.cubes[row][col].value == 0:
            self.cubes[row][col].set(val)
            self.update_model()
            if valid(self.model, val, (row,col)) and self.solve():
                return True
            else:
                self.cubes[row][col].set(0)
                self.cubes[row][col].set_guess(0)
                self.update_model()
                return False

    def sketch(self, val):
        row, col = self.selected
        self.cubes[row][col].set_guess(val)

    #draws the entire puzzle in the beginning
    def draw(self):
        # Draw Gridlines
        gap = self.width / 9
        for i in range(self.rows+1):
            if i % 3 == 0 and i != 0:
                thick = 3
            else:
                thick = 1
            # horizontal line (main windows,colour,coordinates,thickness)
            pygame.draw.line(self.win, (0,0,0), (0, i*gap), (self.width, i*gap), thick)
            # vertical line (main windows,colour,coordinates,thickness)
            pygame.draw.line(self.win, (0, 0, 0), (i * gap, 0), (i * gap, self.height), thick)

        # Entering the numbers in the puzzle (calling the draw function of the 'Cell' class) 
        for i in range(self.rows):
            for j in range(self.cols):
                self.cubes[i][j].draw(self.win)

    def select(self, row, col):
        # Reset all other
        for i in range(self.rows):
            for j in range(self.cols):
                self.cubes[i][j].selected = False
        #select the one which you want
        self.cubes[row][col].selected = True
        self.selected = (row, col)

    def clear(self):
        row, col = self.selected
        if self.cubes[row][col].value == 0:
            self.cubes[row][col].set_guess(0)

    def click(self, pos):
        """
        :param: pos
        :return: (row, col)
        """
        if pos[0] < self.width and pos[1] < self.height:
            gap = self.width / 9
            x = pos[0] // gap
            y = pos[1] // gap
            return (int(y),int(x))
        else:
            return None

    #checking if the puzzle is filled
    def is_finished(self):
        for i in range(self.rows):
            for j in range(self.cols):
                if self.cubes[i][j].value == 0:
                    return False
        return True

    #solution of the puzzle
    def solve(self):
        find = find_empty(self.model)
        if not find:
            return True
        else:
            row, col = find
        for i in range(1, 10):
            if valid(self.model, i, (row, col)):
                self.model[row][col] = i

                if self.solve():
                    return True
                #back tracking step
                self.model[row][col] = 0
        return False


    def solve_gui(self):
        self.update_model()
        #finding an empty cell
        find = find_empty(self.model)
        if not find:
            return True
        else:
            row, col = find
        for i in range(1, 10):
            if valid(self.model, i, (row, col)):
                #going through 1 to 9, entering, drawing the change
                self.model[row][col] = i
                self.cubes[row][col].set(i)
                self.cubes[row][col].draw_change(self.win, True)
                self.update_model()
                pygame.display.update()
                pygame.time.delay(100)
                #proceeding with the entered value
                if self.solve_gui():
                    return True
                #if the previous value is resulting in a unfeasible solution, backtracking
                self.model[row][col] = 0
                self.cubes[row][col].set(0)
                self.update_model()
                self.cubes[row][col].draw_change(self.win, False)
                pygame.display.update()
                pygame.time.delay(100)

        return False

# class to enter/change the contents of a 1*1 Cell
class Cell:
    rows = 9
    cols = 9

    def __init__(self, value, row, col, width, height):
        self.value = value
        self.guess = 0
        #particular row and column
        self.row = row
        self.col = col
        self.width = width
        self.height = height
        self.selected = False

    #value that would be fixed (which is correct for a cell)
    def set(self, val):
        self.value = val

    #guessed value
    def set_guess(self, val):
        self.guess = val

    def draw(self, win):
        fnt = pygame.font.SysFont("comicsans", 40)

        gap = self.width / 9
        x = self.col * gap
        y = self.row * gap
        #storing the guessed entered value
        if self.guess != 0 and self.value == 0: 
            text = fnt.render(str(self.guess), 1, (128,128,128))
            win.blit(text, (x+5, y+5))
        #fixing the word which is as it should be in solved example
        elif not(self.value == 0):
            text = fnt.render(str(self.value), 1, (0, 0, 0))
            win.blit(text, (x + (gap/2 - text.get_width()/2), y + (gap/2 - text.get_height()/2)))
        #just the surrounding border
        if self.selected:
            pygame.draw.rect(win, (0,0,255), (x,y, gap ,gap), 3)

    #the graphics of the solution visualizer
    def draw_change(self, win, g=True):
        fnt = pygame.font.SysFont("comicsans", 40)

        gap = self.width / 9
        x = self.col * gap
        y = self.row * gap

        pygame.draw.rect(win, (255, 255, 255), (x, y, gap, gap), 0)

        text = fnt.render(str(self.value), 1, (0, 0, 0))
        win.blit(text, (x + (gap / 2 - text.get_width() / 2), y + (gap / 2 - text.get_height() / 2)))
        #Cell borders
        if g:
            pygame.draw.rect(win, (0, 255, 0), (x, y, gap, gap), 3)
        else:
            pygame.draw.rect(win, (0, 0, 255), (x, y, gap, gap), 3)

    


def find_empty(bo):
    for i in range(len(bo)):
        for j in range(len(bo[0])):
            if bo[i][j] == 0:
                return (i, j)  # row, col

    return None

#validating if the element entered can belong to the Cell
def valid(bo, num, pos):
    # Check row
    for i in range(len(bo[0])):
        if bo[pos[0]][i] == num and pos[1] != i:
            return False

    # Check column
    for i in range(len(bo)):
        if bo[i][pos[1]] == num and pos[0] != i:
            return False

    # Check box
    box_x = pos[1] // 3
    box_y = pos[0] // 3

    for i in range(box_y*3, box_y*3 + 3):
        for j in range(box_x * 3, box_x*3 + 3):
            if bo[i][j] == num and (i,j) != pos:
                return False

    return True


def redraw_window(win, board, time, strikes):
    win.fill((255,255,255))
    # Draw time
    fnt = pygame.font.SysFont("comicsans", 40)
    text = fnt.render("Time: " + format_time(time), 1, (0,0,0))
    win.blit(text, (540 - 160, 560))
    # Draw Strikes
    text = fnt.render("X " * strikes, 1, (255, 0, 0))
    win.blit(text, (20, 560))
    # Draw Space and board
    board.draw()


def format_time(secs):
    sec = secs%60
    minute = secs//60
    hour = minute//60
    mat = str(hour)+":" + str(minute) + ":" + str(sec)
    return mat


def main():
    #dimensions of the window
    win = pygame.display.set_mode((540,600))
    pygame.display.set_caption("Sudoku")
    board=Gen()
    #populating the window
    BOX = Space(9, 9, 540, 540, win, board)
    key = None
    run = True
    start = time.time()
    strikes = 0
    while run:

        play_time = round(time.time() - start)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    key = 1
                if event.key == pygame.K_2:
                    key = 2
                if event.key == pygame.K_3:
                    key = 3
                if event.key == pygame.K_4:
                    key = 4
                if event.key == pygame.K_5:
                    key = 5
                if event.key == pygame.K_6:
                    key = 6
                if event.key == pygame.K_7:
                    key = 7
                if event.key == pygame.K_8:
                    key = 8
                if event.key == pygame.K_9:
                    key = 9
                if event.key == pygame.K_KP1:
                    key = 1
                if event.key == pygame.K_KP2:
                    key = 2
                if event.key == pygame.K_KP3:
                    key = 3
                if event.key == pygame.K_KP4:
                    key = 4
                if event.key == pygame.K_KP5:
                    key = 5
                if event.key == pygame.K_KP6:
                    key = 6
                if event.key == pygame.K_KP7:
                    key = 7
                if event.key == pygame.K_KP8:
                    key = 8
                if event.key == pygame.K_KP9:
                    key = 9
                if event.key == pygame.K_DELETE:
                    #clears the current element
                    BOX.clear()
                    key = None

                if event.key == pygame.K_SPACE:
                    BOX.solve_gui()

                if event.key == pygame.K_TAB:
                    board=Gen()
                    restart=time.time()
                    BOX = Space(9, 9, 540, 540, win, board)
                    play_time = round(time.time() - restart)
                    start=restart
                    strikes=0

                if event.key == pygame.K_RETURN:
                    i, j = BOX.selected
                    if BOX.cubes[i][j].guess != 0:
                        if BOX.place(BOX.cubes[i][j].guess):
                            print("Success")
                        else:
                            print("Wrong")
                            strikes += 1
                        key = None

                        if BOX.is_finished():
                            print("Game over")

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                clicked = BOX.click(pos)
                if clicked:
                    BOX.select(clicked[0], clicked[1])
                    key = None

        if BOX.selected and key != None:
            BOX.sketch(key)

        redraw_window(win, BOX, play_time, strikes)
        pygame.display.update()


main()
pygame.quit()
