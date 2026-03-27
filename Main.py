
import pygame
import math
import button

pygame.init()

Clock = pygame.time.Clock()
FPS = 60

SCREEN_WIDTH = 1500
SCREEN_HEIGHT = 600


SCROLL_SPEED = 4 #minimum scroll speed
MAX_SCROLL_SPEED = 12 #maximum scroll speed
current_scroll_speed = 4 #starting speed

on_ground = True
Y_Gravity = 0.5 #how fast character falls
Y_Velocity = 0
X_Position = 200
Y_Position = 400

HILL_AMPLITUDE = 90 #height of hills
HILL_FREQUENCY = 0.008 #frequency of hills
HILL_BASELINE = 420 #vertical position of hills
World_offset = 0 #tracks total scroll distance

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Menu')

#load all images
start_img = pygame.image.load('start_btn.png').convert_alpha()
exit_img = pygame.image.load('exit_btn.png').convert_alpha()
bg = pygame.image.load("bg_img (2).png").convert()
bg_2 = pygame.image.load("Night_bg.png").convert()
Main_bg = pygame.image.load("Main_Menu.png").convert_alpha()
Home = pygame.image.load("Home_Button.png").convert()

background = pygame.transform.smoothscale(bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
background_2 = pygame.transform.smoothscale(bg_2, (SCREEN_WIDTH, SCREEN_HEIGHT))
menu_background = pygame.transform.smoothscale(Main_bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
Trojan_img = pygame.transform.scale(pygame.image.load("Trojan_img.png"), (80, 80))
restart_img = pygame.image.load('Restart_img.png').convert_alpha()

#buttons - first two numbers are x and y position on screen
start_button = button.Button(600, 50, start_img, 1.0)
start_button2 = button.Button(600, 250, start_img, 1.0)
exit_button = button.Button(615, 450, exit_img, 1.0)
restart_button = button.Button(250, 0, restart_img, 0.5)
Home_button = button.Button(20,20, Home, 0.2)


bg_width = background.get_width()
scroll = 0
tiles = math.ceil(SCREEN_WIDTH / bg_width) + 1

bg_width_2 = background_2.get_width()
scroll = 0
tiles = math.ceil(SCREEN_WIDTH / bg_width_2) + 1

score = 0
run = True
game_active = False
game_over = False
level_1 = False
level_2 = False

#makes the hills varied so it doesnt feel repetative
def get_hill_y(x, offset):
    wave1 = HILL_AMPLITUDE * math.sin(HILL_FREQUENCY * (x + offset))
    wave2 = (HILL_AMPLITUDE * 0.4) * math.sin((HILL_FREQUENCY * 2.3) * (x + offset))
    return HILL_BASELINE + wave1 + wave2

#draws the green hills
def draw_hills(surface, offset):
    hill_points = [(int(x), int(get_hill_y(x, offset))) for x in range(0, SCREEN_WIDTH + 1, 5)]
    pygame.draw.polygon(surface, (34, 139, 34), [(0, SCREEN_HEIGHT)] + hill_points + [(SCREEN_WIDTH, SCREEN_HEIGHT)])
    for i in range(len(hill_points) - 1):
        pygame.draw.line(surface, (50, 180, 50), hill_points[i], hill_points[i + 1], 3)

def draw_hills_2(surface, offset):
    hill_points = [(int(x), int(get_hill_y(x, offset))) for x in range(0, SCREEN_WIDTH + 1, 5)]
    pygame.draw.polygon(surface, (30, 100, 200), [(0, SCREEN_HEIGHT)] + hill_points + [(SCREEN_WIDTH, SCREEN_HEIGHT)])
    for i in range(len(hill_points) - 1):
        pygame.draw.line(surface, (50, 150, 255), hill_points[i], hill_points[i + 1], 3)

#restets all variables to starting values
def reset_game():
    global current_scroll_speed, Y_Velocity, Y_Position, on_ground, game_over, World_offset, scroll, score
    current_scroll_speed = 4
    Y_Velocity = 0
    Y_Position = 400
    on_ground = True
    game_over = False
    World_offset = 0
    scroll = 0
    score = 0
    level_1 = False
    level_2 = False

while run:

    Clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
    #draw background
    screen.fill((255, 165, 0))
    

    #main menu
    if not game_active:
        if start_button.draw(screen):
            level_1 = True
            game_active = True
            reset_game()
        if start_button2.draw(screen):
            level_2 = True
            game_active = True
            reset_game()
        if exit_button.draw(screen):
            run = False
        if level_1 == True or level_2 == True:
            pygame.display.set_caption("Trojan Advance")
        else:
            pygame.display.set_caption('Menu')


    #main game loop runs when start button or restart button is pressed
    if game_active and level_1 and not game_over:

        #draw scrolling background
        for i in range(tiles):
            screen.blit(background, (i * bg_width + scroll, 0))
        scroll -= current_scroll_speed
        if abs(scroll) > bg_width:
            scroll = 0

        keys = pygame.key.get_pressed()

        #increment score every frame to get score
        if current_scroll_speed > 1:
            score += 1


        # speed controls - increase 0.2 for faster acceleration
        if on_ground and keys[pygame.K_SPACE]:
            current_scroll_speed += 0.2
            current_scroll_speed = min(current_scroll_speed, MAX_SCROLL_SPEED)
        
        #gradually speeds up on its own - increase 0.01 for faster auto speedup
        elif on_ground:
            current_scroll_speed -= 0.1
            current_scroll_speed = max(current_scroll_speed, 0)

        # slope affects speed on ground - uphill slows down, downhill speeds up
        slope_now = get_hill_y(X_Position, World_offset) - get_hill_y(X_Position + 20, World_offset)
        if on_ground:
            if slope_now < 0:
                current_scroll_speed += 0.06 #increase 0.05 for more speed going downhill
                current_scroll_speed = min(current_scroll_speed, MAX_SCROLL_SPEED)
            elif slope_now > 2:
                current_scroll_speed -= 0.06 #increase 0.03 for more speed loss going up
                current_scroll_speed = max(current_scroll_speed, SCROLL_SPEED)

        #scrolls and drawws hills
        World_offset += current_scroll_speed
        draw_hills(screen, World_offset)

        if on_ground:
            Y_Position = get_hill_y(X_Position, World_offset) - Trojan_img.get_height() // 2

            # check both ahead AND behind to confirm its a real peak not a small bump
            #increase slope_ahead to make launch less frequent
            #increase current_scroll_speed to require more speed to launch
            slope_ahead = get_hill_y(X_Position, World_offset) - get_hill_y(X_Position + 50, World_offset)
            slope_behind = get_hill_y(X_Position - 30, World_offset) - get_hill_y(X_Position, World_offset)

            if slope_ahead > 20 and slope_behind > 5 and current_scroll_speed > 8:
                on_ground = False
                Y_Velocity = -(current_scroll_speed * 1.5) #increase 1.5 to launch higher of peaks

        #hold space to dive down
        else:
            if keys[pygame.K_SPACE]:
                Y_Velocity += Y_Gravity * 4
            else:
                Y_Velocity += Y_Gravity
            Y_Position += Y_Velocity

            #checks if landed back on hills
            surface_y = get_hill_y(X_Position, World_offset) - Trojan_img.get_height() // 2
            if Y_Position >= surface_y:
                Y_Position = surface_y

                # if Y_Velocity >= 15:
                #     game_over = True

                #death system
                landing_slope = get_hill_y(X_Position, World_offset) - get_hill_y(X_Position + 20, World_offset)
                if landing_slope < -30: #decrease -20 to make death easier
                    game_over = True

                if Y_Velocity > 20 and landing_slope > 20:
                    game_over = True

                
                Y_Velocity = 0
                on_ground = True

                #bad landing slows down speed
                landing_slope = get_hill_y(X_Position, World_offset) - get_hill_y(X_Position + 20, World_offset)
                if landing_slope < -25:
                    current_scroll_speed = max(current_scroll_speed * 0.1, SCROLL_SPEED) #increase 0.4 to slow down more on bad landing
                            
        #draw trojan horse                  
        screen.blit(Trojan_img, Trojan_img.get_rect(center=(X_Position, int(Y_Position))))

        font = pygame.font.SysFont('Arial', 40)
        score_text = font.render(f'score: {score // 60}', True, (255,255,255))
        screen.blit(score_text, (20, 20))




    if level_2 == True and not game_over:


        HILL_AMPLITUDE = 80 #height of hills
        HILL_FREQUENCY = 0.01 #frequency of hills
        HILL_BASELINE = 420 #vertical position of hills

        for i in range(tiles):
            screen.blit(background_2, (i * bg_width_2 + scroll, 0))
        scroll -= current_scroll_speed
        if abs(scroll) > bg_width_2:
            scroll = 0

        keys = pygame.key.get_pressed()

        #increment score every frame to get score
        
        if current_scroll_speed > 1:
            score += 1

        # speed controls - increase 0.2 for faster acceleration
        if on_ground and keys[pygame.K_SPACE]:
            current_scroll_speed += 0.2
            current_scroll_speed = min(current_scroll_speed, MAX_SCROLL_SPEED)
        
        #gradually speeds up on its own - increase 0.01 for faster auto speedup
        elif on_ground:
            current_scroll_speed -= 0.1
            current_scroll_speed = max(current_scroll_speed, 0)

        # slope affects speed on ground - uphill slows down, downhill speeds up
        slope_now = get_hill_y(X_Position, World_offset) - get_hill_y(X_Position + 20, World_offset)
        if on_ground:
            if slope_now < 0:
                current_scroll_speed += 0.06 #increase 0.05 for more speed going downhill
                current_scroll_speed = min(current_scroll_speed, MAX_SCROLL_SPEED)
            elif slope_now > 2:
                current_scroll_speed -= 0.06 #increase 0.03 for more speed loss going up
                current_scroll_speed = max(current_scroll_speed, SCROLL_SPEED)

        #scrolls and drawws hills
        World_offset += current_scroll_speed
        draw_hills_2(screen, World_offset)

        if on_ground:
            Y_Position = get_hill_y(X_Position, World_offset) - Trojan_img.get_height() // 2

            # check both ahead AND behind to confirm its a real peak not a small bump
            #increase slope_ahead to make launch less frequent
            #increase current_scroll_speed to require more speed to launch
            slope_ahead = get_hill_y(X_Position, World_offset) - get_hill_y(X_Position + 50, World_offset)
            slope_behind = get_hill_y(X_Position - 30, World_offset) - get_hill_y(X_Position, World_offset)

            if slope_ahead > 20 and slope_behind > 5 and current_scroll_speed > 8:
                on_ground = False
                Y_Velocity = -(current_scroll_speed * 1.5) #increase 1.5 to launch higher of peaks

        #hold space to dive down
        else:
            if keys[pygame.K_SPACE]:
                Y_Velocity += Y_Gravity * 4
            else:
                Y_Velocity += Y_Gravity
            Y_Position += Y_Velocity

            #checks if landed back on hills
            surface_y = get_hill_y(X_Position, World_offset) - Trojan_img.get_height() // 2
            if Y_Position >= surface_y:
                Y_Position = surface_y

                # if Y_Velocity >= 15:
                #     game_over = True

                #death system
                landing_slope = get_hill_y(X_Position, World_offset) - get_hill_y(X_Position + 20, World_offset)
                if landing_slope < -30: #decrease -20 to make death easier
                    game_over = True

                if Y_Velocity > 20 and landing_slope > 20:
                    game_over = True
                
                
                
                Y_Velocity = 0
                on_ground = True

                # #bad landing slows down speed
                # landing_slope = get_hill_y(X_Position, World_offset) - get_hill_y(X_Position + 20, World_offset)
                # if landing_slope < -12:
                #     current_scroll_speed = max(current_scroll_speed * 0.15, SCROLL_SPEED) #increase 0.4 to slow down more on bad landing
                            
        #draw trojan horse                  
        screen.blit(Trojan_img, Trojan_img.get_rect(center=(X_Position, int(Y_Position))))

        font = pygame.font.SysFont('Arial', 40)
        score_text = font.render(f'score: {score // 60}', True, (255,255,255))
        screen.blit(score_text, (20, 20))



        screen.blit(Trojan_img, Trojan_img.get_rect(center=(X_Position, int(Y_Position))))


              #game over screen
    if game_over:
        
        current_scroll_speed = 0

        if level_2:
                screen.fill((30,100,200))
                if Home_button.draw(screen):
                    game_active = False
                    level_1 = False
                    level_2 = False
                    reset_game()
        else:
            screen.fill((34,139,34))
            if Home_button.draw(screen):
                game_active = False
                level_1 = False
                level_2 = False
                reset_game()


        #shows final score
        font = pygame.font.SysFont('Arial', 50)
        score_text =  font.render(f'Score: {score // 60}', True, (255, 255, 255))
        screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 180))

        #resets game once pressed
        if restart_button.draw(screen):
             reset_game()
  


    pygame.display.update()

pygame.quit()
