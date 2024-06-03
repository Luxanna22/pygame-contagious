#STEP 1: import Modules
import pygame
import sys

#2: Initialize Pygame
pygame.init()

#3: Setup The Display
width = 600
height = 600
display = pygame.display.set_mode((width, height))

#Setup the Clock for later
clock = pygame.time.Clock()

#Step 5: Set the Window Title and Icon
pygame.display.set_caption('Contagious')
icon = pygame.image.load("covid_red.png")
icon2 = pygame.image.load("Covid_blue.png")
pygame.display.set_icon(icon)
icon = pygame.transform.scale(icon, (500, 500))
icon2 = pygame.transform.scale(icon2, (200, 200))

#Step 6: Define Colors
background = (50, 50, 50)
border = (208, 211, 212)
red = (231, 76, 60)
white = (244, 246, 247)
violet = (136, 78, 160)
blue = (52, 152, 219)
green = (88, 214, 141)

playerColor = [red, green, violet, blue]

#Step 7: Load our game's Default font
font = pygame.font.SysFont("Times New Roman", 30)

#Step 8: Define Grid Parameters
blocks = 40
d = blocks // 2 - 2
cols = int(width // blocks)
rows = int(height // blocks)

grid = []

#Step 9: Load Player Images
player_images = ["covid_red.png", "covid_green.png", "covid_purple.png", "covid_blue.png"]
player_imgs = [pygame.image.load(img) for img in player_images]
player_imgs = [pygame.transform.scale(img, (27, 27)) for img in player_imgs]


#Step 10: Create the Main Game Loop
def game_loop():
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        display.fill(background)
        pygame.display.update()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    game_loop()
