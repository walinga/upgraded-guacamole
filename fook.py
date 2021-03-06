from colours import *
import pygame
import sys
import pm
import time

#global variable lol
PIECE_FOLDER = "Pieces/"

marginsize = 30
screenwidth = 1024
screenheight = 640

# Assumes width > height
xcorner = (screenwidth - screenheight) / 2 + marginsize + 200
ycorner = marginsize
boardsize = screenheight - 2 * marginsize
squaresize = boardsize / 8

buttonWidth, buttonHeight = 200, 30
buttonx = 4 * marginsize # everything hardcoded :)
buttony = 450 + marginsize
surpy = buttony + marginsize
fooky = surpy + marginsize

pygame.init()
screen = pygame.display.set_mode((screenwidth, screenheight))
MessageFont = pygame.font.SysFont("comic sans", 50)
ButtonFont = pygame.font.SysFont("comic sans", 30)

#pygame.mixer.music.load("sandstorm.mp3");
#pygame.mixer.music.play();


# helper to obtain file and rank
def fileAndRank(sqr): return sqr%8, 7 - sqr/8

def checkType(event):
    # Check for quit
    if event.type == pygame.QUIT: pygame.quit(); sys.exit();
    if event.type == pygame.MOUSEBUTTONUP:
        mousex, mousey = event.pos
        if buttonx < mousex < buttonx + buttonWidth and buttony < mousey < buttony + buttonHeight:
            # Reset the game if 'new game' selected
            resetState()
        elif buttonx < mousex < buttonx + buttonWidth and surpy < mousey < surpy + buttonHeight:
            generateMeme()
        elif buttonx < mousex < buttonx + buttonWidth and fooky < mousey < fooky + buttonHeight:
            drawStuff()
        else: return False
        return True


# Draws an obnoxious message across the board
def displayMessage(message, xcoord):
    pygame.draw.rect(screen, boardcolour, (xcoord, xcoord, 250, 30), 0)
    message = MessageFont.render(message, 10, green)
    screen.blit(message, (xcoord, xcoord))
    pygame.display.update()
    mainState.END = True


# Load an image and set it to the specified size
def loadAndTransform(image, size):
    loadedImage = pygame.image.load(image)
    return pygame.transform.smoothscale(loadedImage, (size, size))

def drawLogo():
    logo = loadAndTransform("TerribleChess.png", 400)
    screen.blit(logo, (0, 0))


# Draws the board to the screen
def drawBoard():
    k, size = squaresize, boardsize
    pygame.draw.rect(screen, boardcolour, (xcorner, ycorner, size, size), 3)
    colour = generateColour(1)
    for sqr in range(64):
        f, r = fileAndRank(sqr)
        sx = xcorner + f*k + 2 # Add 2 to centre the board
        sy = ycorner + r*k + 2
        if (sqr/8)%2 == sqr%2:
            pygame.draw.rect(screen, generateColour(), (sx, sy, k, k))
        else:
            pygame.draw.rect(screen, colour, (sx, sy, k, k))


# Draws the pieces to the screen
def drawPieces():
    k = squaresize
    for p in pm.allpieces:
        pieceImage = loadAndTransform(PIECE_FOLDER + p.picture, k)
        for sqr in p.piecelist:
            f, r = fileAndRank(sqr)
            screen.blit(pieceImage, (xcorner + f*k, ycorner + r*k))
    pygame.display.update()


# Draws the buttons below the board
def drawButtons():
    def buttonHelper(ycoord, text):
        x, y = buttonx, ycoord
        messagex = x + 75//2 - ((len(text) * 75//11) / 2) # Magic to centre text
        screen.blit(ButtonFont.render(text, 1, blue), (messagex , y+3))
    buttonHelper(buttony, "NEW GAME")
    buttonHelper(surpy, "SURPRISE")
    buttonHelper(fooky, "FUCK ME UP")
    

# Highlights the specified square
def drawHighlight(sqr):
    f, r = fileAndRank(sqr)
    x = xcorner + f * squaresize + 2
    y = ycorner + r * squaresize + 2
    pygame.draw.rect(screen, brown, (x, y, squaresize, squaresize))

# Returns square clicked (as a number) or -1 if mouse was off board
def squareClicked(mousex, mousey):
    x = mousex - xcorner
    y = mousey - ycorner
    k, size = squaresize, boardsize
    if x>0 and x<size and y>0 and y<size:
        fil = x // k
        rank = y // k
        sqr = 8*(7-rank) + fil
        return sqr
    return -1


# Draws a circle for each valid move of the piece on sqr
def drawMoves(sqr):
    for s in pm.PieceMovement(sqr):
        f, r = fileAndRank(s)
        k, size = squaresize, boardsize
        x = (xcorner + k*f + k/2) // 1
        y = (ycorner + k*r + k/2) // 1
        pygame.draw.circle(screen, green, (x, y), k//4, 0)
        pygame.display.update()


# Redraws the board and pieces
def drawStuff(sqr=-1):
    screen.fill(backcolour)
    drawButtons()
    drawBoard()
    drawLogo()
    if sqr != -1: drawHighlight(sqr)
    drawPieces()


# A class used for resetting the game
class GameState:
    def __init__(self):
        self.movenumber = 0
        self.END = False

mainState = GameState()

def resetState():
    global mainState
    mainState = GameState()
    pm.resetboard()
    drawStuff()

def generateMeme():
    global PIECE_FOLDER
    if PIECE_FOLDER == "Memes/": PIECE_FOLDER = "Pieces/"
    else: PIECE_FOLDER = "Memes/"
    drawStuff()

# Switches turn and increases move number
def switchTurn(): mainState.movenumber += 1

# Makes a move for the computer
def DoCompTurn():
    if mainState.END: return
    if mainState.movenumber <= 1:
        pm.MovePiece(52, 36, pm.bp)
        drawStuff(36)
    else:
        pm.MovePiece(59, 31, pm.bq)
        drawStuff(31)
    switchTurn()


# Moves a piece selected by the player
def DoPlayerTurn():
    temp = -1
    while (True):
        for event in pygame.event.get():
            if checkType(event): return
            if event.type == pygame.MOUSEBUTTONUP:
                mousex, mousey = event.pos
                msqr = squareClicked(mousex, mousey)
                if msqr != -1:

                    # Moves a piece if one was selected
                    if temp != -1:
                        for s in pm.PieceMovement(temp):
                            if msqr == s:
                                pm.MovePiece(temp, msqr, pm.wp)
                                drawStuff()
                                switchTurn()
                                return
                        drawStuff()
                        temp = -1

                    # Displays valid moves
                    else:
                        for piece in pm.whitepieces:
                            for sqr in piece.piecelist:
                                if sqr == msqr:
                                    drawMoves(msqr)
                                    temp = msqr
                                             
def main():
    # Initialize things
    pygame.display.set_caption('How TERRIBLE are you?')
    drawStuff()

    # Main game loop:
    while (True):
        for event in pygame.event.get(): checkType(event)

        # Checks for mate
        if not mainState.END:
            mate_status = pm.isMated()
        if mate_status:
            displayMessage(mate_status + "!", screenwidth / 2 - marginsize)

        elif mainState.movenumber % 2 == 0: # White's turn
            DoPlayerTurn()

        else: DoCompTurn()




#imagesList = ["Pieces/WhiteKing.png", "Pieces/WhiteQueen.png", "Pieces/WhiteBishop.png", "Pieces/WhiteKnight.png", 
#"Pieces/WhiteRook.png", "Pieces/WhitePawn.png", "Pieces/BlackKing.png", "Pieces/BlackQueen.png", 
#"Pieces/BlackBishop.png", "Pieces/BlackKnight.png","Pieces/BlackRook.png", "Pieces/BlackPawn.png"]

#pyjsdl.display.setup(run)            
main()
