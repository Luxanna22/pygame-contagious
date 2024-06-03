import pygame
import sys
from math import *

# Initialization of Pygame
pygame.init()

width = 600
height = 600
display = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()

pygame.display.set_caption('Contagious')
icon = pygame.image.load("covid_red.png")
icon2 = pygame.image.load("Covid_blue.png")
pygame.display.set_icon(icon)
icon = pygame.transform.scale(icon, (500,500))
icon2 = pygame.transform.scale(icon2, (200,200))

# Colors
background = (50, 50, 50)
border = (208, 211, 212)
red = (231, 76, 60)
white = (244, 246, 247)
violet = (136, 78, 160)
blue = (52, 152, 219) 
green = (88, 214, 141)

playerColor = [red, green, violet, blue]

font = pygame.font.SysFont("Times New Roman", 30)

blocks = 40

d = blocks // 2 - 2

cols = int(width // blocks)
rows = int(height // blocks)

grid = []

# Load PNG images for each player
player_images = ["covid_red.png", "covid_green.png", "covid_purple.png", "covid_blue.png"]
player_imgs = [pygame.image.load(img) for img in player_images]
player_imgs = [pygame.transform.scale(img, (27, 27)) for img in player_imgs]

# Main menu options
menu_options = ["2 players", "3 players", "4 players"]

# Function to display the main menu
def display_menu():
    display.fill(background)
    #bg
    display.blit(icon, (width / 2.7, height / 22))
    #icon2
    display.blit(icon2, (width / 7, height / 1.5))
    
    #title
    title_text = font.render("CONTAGIOUS", True, white)
    display.blit(title_text, (width / 10.7, height / 5))

    # Display menu options
    for i, option in enumerate(menu_options):
        text = font.render(option, True, white)
        display.blit(text, (width / 7.7, height / 2.5 + i * 50))
        
    #my name
    text4 = font.render("© 2024 | Rusiana", True, white)
    text4 = pygame.transform.scale(text4, (250,35))
    #bottom-right
    display.blit(text4, (width / 1.8, height / 1.1))
    pygame.display.update()

# Function to handle the main menu
def main_menu():
    display_menu()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                # Check which menu option was clicked
                for i, _ in enumerate(menu_options):
                    if width / 7.7 < x < width / 7.7 + 200 and height / 2.5 + i * 50 < y < height / 2.5 + (i + 1) * 50:
                        return i + 2  # Return the number of players (2, 3, or 4)

# Start the game loop
def game_loop(num_players):
    global numOfPlayers, activePlayers
    numOfPlayers = num_players
    initializeGrid()
    loop = True

    turns = 0
    
    currentPlayer = 0

    rotation_angle = 0  # Initial rotation angle

    rotation_speed = 3  # Adjust the rotation speed here

    activePlayers = list(range(numOfPlayers))  # Initialize list of active players

    while loop:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                close()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    close()
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                i = int(x // blocks)
                j = int(y // blocks)
                if grid[i][j].color == players[activePlayers[currentPlayer]] or grid[i][j].color == border:
                    turns += 1
                    addAtom(i, j, players[activePlayers[currentPlayer]])
                    currentPlayer += 1
                    if currentPlayer >= len(activePlayers):
                        currentPlayer = 0
                if turns >= numOfPlayers:
                    activePlayers = isPlayerInGame()
                    if currentPlayer >= len(activePlayers):
                        currentPlayer = 0

        display.fill(background)
        # Increment rotation angle for animation
        rotation_angle += rotation_speed
        if rotation_angle >= 360:
            rotation_angle %= 360
        
        if activePlayers:
            drawGrid(activePlayers[currentPlayer])
            showPresentGrid(rotation_angle)
        
        pygame.display.update()

        res = checkWon()
        if res < 9999:
            gameOver(res)
            
        clock.tick(20)

# Quit or Close the Game Window
def close():
    pygame.quit()
    sys.exit()

# Class for Each Spot in Grid
class Spot():
    def __init__(self):
        self.color = border
        self.neighbors = []
        self.noAtoms = 0
        self.limit = 4  # Define the limit for each cell

    def addNeighbors(self, i, j):
        if i > 0:
            self.neighbors.append(grid[i - 1][j])
        if i < rows - 1:
            self.neighbors.append(grid[i + 1][j])
        if j < cols - 1:
            self.neighbors.append(grid[i][j + 1])
        if j > 0:
            self.neighbors.append(grid[i][j - 1])

# Initializing the Grid with "Empty or 0"
def initializeGrid():
    global grid, score, players
    score = []
    for i in range(numOfPlayers):
        score.append(0)

    players = []
    for i in range(numOfPlayers):
        players.append(playerColor[i])

    grid = [[]for _ in range(cols)]
    for i in range(cols):
        for j in range(rows):
            newObj = Spot()
            grid[i].append(newObj)
    for i in range(cols):
        for j in range(rows):
            grid[i][j].addNeighbors(i, j)

# Draw the Grid in Pygame Window
def drawGrid(currentIndex):
    r = 0
    c = 0
    for i in range(width // blocks):
        r += blocks
        c += blocks
        pygame.draw.line(display, players[currentIndex], (c, 0), (c, height))
        pygame.draw.line(display, players[currentIndex], (0, r), (width, r))

# Draw the Present Situation of Grid
def showPresentGrid(rotation_angle=0):
    r = -blocks
    c = -blocks
    padding = 2
    for i in range(cols):
        r += blocks
        c = -blocks 
        for j in range(rows):
            c += blocks
            if grid[i][j].noAtoms == 0:
                grid[i][j].color = border
            elif grid[i][j].noAtoms == 1:
                rotated_img = pygame.transform.rotate(player_imgs[players.index(grid[i][j].color)], rotation_angle)
                display.blit(rotated_img, (r + padding, c + padding))
            elif grid[i][j].noAtoms == 2:
                rotated_img = pygame.transform.rotate(player_imgs[players.index(grid[i][j].color)], (rotation_angle))
                display.blit(rotated_img, (r + padding, c + padding))
                # Adjust position for the second image
                display.blit(rotated_img, (r + padding + 9, c + padding))

            elif grid[i][j].noAtoms == 3:
                angle = rotation_angle
                x = r + (d / 2) * cos(radians(angle)) + blocks / 4
                y = c + (d / 2) * sin(radians(angle)) + blocks / 4
                display.blit(player_imgs[players.index(grid[i][j].color)], (x, y))
                x = r + (d / 2) * cos(radians(angle + 90)) + blocks / 4
                y = c + (d / 2) * sin(radians(angle + 90)) + padding
                display.blit(player_imgs[players.index(grid[i][j].color)], (x, y))
                x = r + (d / 2) * cos(radians(angle - 90)) + blocks / 4
                y = c + (d / 2) * sin(radians(angle - 90)) + padding
                display.blit(player_imgs[players.index(grid[i][j].color)], (x, y))

    pygame.display.update()

# Increase the Atom when Clicked
def addAtom(i, j, color):
    cell = grid[i][j]
    if cell.noAtoms < cell.limit:  # Check if the cell has reached its limit
        cell.noAtoms += 1
        cell.color = color
        if cell.noAtoms >= len(cell.neighbors):
            overFlow(cell, color)

# Split the Disease when it Increases the "LIMIT"
def overFlow(cell, color):
    cell.noAtoms = 0
    try:
        for neighbor in cell.neighbors:
            if neighbor.noAtoms < neighbor.limit:  # Check if the neighbor has reached its limit
                neighbor.noAtoms += 1
                neighbor.color = color
                if neighbor.noAtoms >= len(neighbor.neighbors):
                    overFlow(neighbor, color)
    except RecursionError:
        # Recursion error occurred, triggering game over with the player who caused the error winning
        gameOver(players.index(color))

# Checking if Any Player has WON!
def isPlayerInGame():
    global score, players
    playerScore = [0] * numOfPlayers
    for i in range(cols):
        for j in range(rows):
            for k in range(numOfPlayers):
                if grid[i][j].color == players[k]:
                    playerScore[k] += grid[i][j].noAtoms
    score = playerScore[:]
    
    activePlayers = [i for i in range(numOfPlayers) if score[i] > 0]
    return activePlayers

# GAME OVER
def gameOver(playerIndex):
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                close()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    close()
                if event.key == pygame.K_SPACE: #For RESTARTING
                     game_loop(numOfPlayers)
                if event.key == pygame.K_ESCAPE: #BACK TO MAIN MENU
                    main_menu()
                    for i, _ in enumerate(menu_options):
                        x, y = pygame.mouse.get_pos()  
                        if width / 7.7 < x < width / 7.7 + 200 and height / 2.5 + i * 50 < y < height / 2.5 + (i + 1) * 50:
                            global numPlayer 
                            numPlayer = i + 2 #
                    game_loop(numPlayer)
                    return  # Exit the gameOver function after resetting

        player_color = playerColor[playerIndex]
        wonText = font.render("Player %s Won!" % ("RED" if player_color == red else
                                                "GREEN" if player_color == green else
                                                "PURPLE" if player_color == violet else
                                                "BLUE"), True, player_color)
        restartText = font.render("'SPACEBAR' to restart!", True, white, green)
        menuText = font.render("'ESC' to main menu.", True, white, green)
        
        display.blit(wonText, (width / 3, height / 3))
        display.blit(restartText, (width / 3.5, height / 2))
        display.blit(menuText, (width / 3.2, height / 1.7))
        
        pygame.display.update()
        clock.tick(60)

# Function to check if any player has won
def checkWon():
    num = 0
    for i in range(numOfPlayers):
        if score[i] == 0:
            num += 1
    if num == numOfPlayers - 1:
        for i in range(numOfPlayers):
            if score[i]:
                return i
    return 9999

# Main function
def main():
    num_players = main_menu()
    game_loop(num_players)

# Entry point of the program
if __name__ == "__main__":
    main()
