

import pygame
import math
import button

pygame.init()

Clock = pygame.time.Clock()
FPS = 60

SCREEN_WIDTH = 1500
SCREEN_HEIGHT = 600
SCROLL_SPEED = 4
MAX_SCROLL_SPEED = 12
current_scroll_speed = 4

on_ground = True
Y_Gravity = 0.5
Y_Velocity = 0
X_Position = 200
Y_Position = 400

HILL_AMPLITUDE = 90
HILL_FREQUENCY = 0.008
HILL_BASELINE = 420
World_offset = 0

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Menu')

start_img = pygame.image.load('start_btn.png').convert_alpha()
exit_img = pygame.image.load('exit_btn.png').convert_alpha()
bg = pygame.image.load("bg_img (2).png").convert()
background = pygame.transform.smoothscale(bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
Trojan_img = pygame.transform.scale(pygame.image.load("Trojan_img.png"), (80, 80))

start_button = button.Button(650, 100, start_img, 1.0)
exit_button = button.Button(650, 300, exit_img, 1.0)

bg_width = background.get_width()
scroll = 0
tiles = math.ceil(SCREEN_WIDTH / bg_width) + 1
run = True
game_active = False

def get_hill_y(x, offset):
    wave1 = HILL_AMPLITUDE * math.sin(HILL_FREQUENCY * (x + offset))
    wave2 = (HILL_AMPLITUDE * 0.4) * math.sin((HILL_FREQUENCY * 2.3) * (x + offset))
    return HILL_BASELINE + wave1 + wave2

def draw_hills(surface, offset):
    hill_points = [(int(x), int(get_hill_y(x, offset))) for x in range(0, SCREEN_WIDTH + 1, 5)]
    pygame.draw.polygon(surface, (34, 139, 34), [(0, SCREEN_HEIGHT)] + hill_points + [(SCREEN_WIDTH, SCREEN_HEIGHT)])
    for i in range(len(hill_points) - 1):
        pygame.draw.line(surface, (50, 180, 50), hill_points[i], hill_points[i + 1], 3)

while run:

    Clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    for i in range(tiles):
        screen.blit(background, (i * bg_width + scroll, 0))
    scroll -= current_scroll_speed
    if abs(scroll) > bg_width:
        scroll = 0

    if not game_active:
        if start_button.draw(screen):
            game_active = True
        if exit_button.draw(screen):
            run = False
    elif game_active:
        pygame.display.set_caption("Trojan Advance")

    if game_active:

        keys = pygame.key.get_pressed()

        # speed controls
        if on_ground and keys[pygame.K_SPACE]:
            current_scroll_speed += 0.2
            current_scroll_speed = min(current_scroll_speed, MAX_SCROLL_SPEED)
        elif on_ground:
            current_scroll_speed += 0.01
            current_scroll_speed = min(current_scroll_speed, MAX_SCROLL_SPEED)

        # slope affects speed on ground
        slope_now = get_hill_y(X_Position, World_offset) - get_hill_y(X_Position + 20, World_offset)
        if on_ground:
            if slope_now < 0:
                current_scroll_speed += 0.05
                current_scroll_speed = min(current_scroll_speed, MAX_SCROLL_SPEED)
            elif slope_now > 2:
                current_scroll_speed -= 0.03
                current_scroll_speed = max(current_scroll_speed, SCROLL_SPEED)

        World_offset += current_scroll_speed
        draw_hills(screen, World_offset)

        if on_ground:
            Y_Position = get_hill_y(X_Position, World_offset) - Trojan_img.get_height() // 2

            # check both ahead AND behind to confirm its a real peak not a small bump
            slope_ahead = get_hill_y(X_Position, World_offset) - get_hill_y(X_Position + 50, World_offset)
            slope_behind = get_hill_y(X_Position - 30, World_offset) - get_hill_y(X_Position, World_offset)

            if slope_ahead > 20 and slope_behind > 5 and current_scroll_speed > 8:
                on_ground = False
                Y_Velocity = -(current_scroll_speed * 1.5)

        else:
            if keys[pygame.K_SPACE]:
                Y_Velocity += Y_Gravity * 4
            else:
                Y_Velocity += Y_Gravity
            Y_Position += Y_Velocity

            surface_y = get_hill_y(X_Position, World_offset) - Trojan_img.get_height() // 2
            if Y_Position >= surface_y:
                Y_Position = surface_y
                Y_Velocity = 0
                on_ground = True

                landing_slope = get_hill_y(X_Position, World_offset) - get_hill_y(X_Position + 20, World_offset)
                if landing_slope < -100:
                    current_scroll_speed = max(current_scroll_speed * 0.4, SCROLL_SPEED)

        screen.blit(Trojan_img, Trojan_img.get_rect(center=(X_Position, int(Y_Position))))

    pygame.display.update()

pygame.quit()