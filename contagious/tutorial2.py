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

#Part2 Step 1: Define Menu Options
menu_options = ["2 players", "3 players", "4 players"]

#Part2 Step 2: Create a Function to Display the Main Menu
def display_menu():
    display.fill(background)
    
    # Display the title and icon
    display.blit(icon, (width / 2.7, height / 22))
    display.blit(icon2, (width / 7, height / 1.5))
    
    title_text = font.render("CONTAGIOUS", True, white)
    display.blit(title_text, (width / 10.7, height / 5))
    
    # Display menu options
    for i, option in enumerate(menu_options):
        text = font.render(option, True, white)
        display.blit(text, (width / 7.7, height / 2.5 + i * 50))
    
    # Display footer
    text4 = font.render("© 2024 | Rusiana", True, white)
    text4 = pygame.transform.scale(text4, (250, 35))
    display.blit(text4, (width / 1.8, height / 1.1))
    
    pygame.display.update()

#Part2 Step 2: Handle the Main Menu
def main_menu():
    display_menu()
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                
                for i, option in enumerate(menu_options):
                    if width / 7.7 < x < width / 7.7 + 200 and height / 2.5 + i * 50 < y < height / 2.5 + (i + 1) * 50:
                        return i + 2  # Return the number of players


#Step 10: Create the Main Game Loop
    #Part2 Step 5: Adjust the Game Loop to Accept Number of Players. Accept the number of players as an argument and update its signature accordingly.
def game_loop(num_players):
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

#Part2 Step 4: Modify the Main Function
def main():
    num_players = main_menu()
    game_loop(num_players)

#PART2 Step 6: Update Entry Point, make sure this is under of main function
if __name__ == "__main__":
    #game_loop()
    main()