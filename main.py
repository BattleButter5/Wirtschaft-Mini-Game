import pygame
import time
import random

pygame.font.init()

# ----------------------------
# Constants & Setup
# ----------------------------
WIDTH, HEIGHT = 1000, 800
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tariff Game")

# Player / Trump / Tariff
PLAYER_WIDTH, PLAYER_HEIGHT = 80, 90
TRUMP_WIDTH, TRUMP_HEIGHT = 70, 90
TARIFF_WIDTH, TARIFF_HEIGHT = 30, 30

PLAYER_VEL = 5
TARIFF_VEL = 4

# Fonts
FONT_TITLE = pygame.font.SysFont("Times New Roman", 40, italic=True)
FONT_TITLE.set_underline(True)
FONT_BUTTONS = pygame.font.SysFont("Times New Roman", 30)

# Images
BG = pygame.transform.scale(pygame.image.load("bg1.png"), (WIDTH, HEIGHT))
TARIFF_IMG = pygame.transform.scale(pygame.image.load("tariff.png"), (TARIFF_WIDTH, TARIFF_HEIGHT))

TRUMP_IDLE = pygame.transform.scale(
    pygame.image.load("trump_1.png").convert_alpha(),
    (TRUMP_WIDTH, TRUMP_HEIGHT)
)

TRUMP_THROW_UP = pygame.transform.scale(
    pygame.image.load("trump_2.png").convert_alpha(),
    (TRUMP_WIDTH, TRUMP_HEIGHT)
)

TRUMP_THROW_DOWN = pygame.transform.scale(
    pygame.image.load("trump_3.png").convert_alpha(),
    (TRUMP_WIDTH, TRUMP_HEIGHT)
)

TRUMP_FRAMES = [
    pygame.transform.scale(
        pygame.image.load(f"trump_{i}.png"),
        (TRUMP_WIDTH, TRUMP_HEIGHT)
    )
    for i in range(1, 4)
]


PLAYER_IDLE = pygame.transform.scale(
    pygame.image.load("player_idle.png"),
    (PLAYER_WIDTH, PLAYER_HEIGHT)
)

PLAYER_WALK_RIGHT = [
    pygame.transform.scale(
        pygame.image.load(f"Player_walking_R_{i}.png"),
        (PLAYER_WIDTH, PLAYER_HEIGHT)
    )
    for i in range(1, 7)
]

PLAYER_WALK_LEFT = [
    pygame.transform.scale(
        pygame.image.load(f"Player_walking_L_{i}.png"),
        (PLAYER_WIDTH, PLAYER_HEIGHT)
    )
    for i in range(1, 7)
]


TARIFF_MASK = pygame.mask.from_surface(TARIFF_IMG)

# Game States
MENU = "menu"
GAME1 = "game1"
GAME2 = "game2"

# Buttons
title_button = pygame.Rect(WIDTH // 2 - 200, 200, 400, 60)
scenario_button1 = pygame.Rect(WIDTH // 2 - 300, 350, 650, 60)
scenario_button2 = pygame.Rect(WIDTH // 2 - 300, 450, 650, 60)


# ----------------------------
# Drawing functions
# ----------------------------
def draw(player, elapsed_time, tariffs, trump, player_img, current_trump_img):
    WIN.blit(BG, (0, 0))
    time_text = FONT_BUTTONS.render(f"Time: {round(elapsed_time)}s", 1, "black")
    WIN.blit(time_text, (850, 10))

    img_rect = player_img.get_rect(midbottom=player.midbottom)
    WIN.blit(player_img, img_rect.topleft)

    WIN.blit(current_trump_img, (trump.x, trump.y))

    for tariff in tariffs:
        WIN.blit(TARIFF_IMG, (tariff.x, tariff.y))

    pygame.display.update()


def draw_menu():
    WIN.blit(BG, (0, 0))
    title = FONT_TITLE.render("Wähle dein Szenario", True, "black")
    WIN.blit(title, (WIDTH//2 - title.get_width()//2, 200))

    pygame.draw.rect(WIN, "red", scenario_button1)
    pygame.draw.rect(WIN, "blue", scenario_button2)

    text1 = FONT_BUTTONS.render("Große Einschränkungen des weltweiten Handels", True, "white")
    text2 = FONT_BUTTONS.render("Weitgehend reibungsloser weltweiter Handel", True, "white")
    WIN.blit(text1, (scenario_button1.x + 20, scenario_button1.y + 15))
    WIN.blit(text2, (scenario_button2.x + 20, scenario_button2.y + 15))

    pygame.display.update()


# ----------------------------
# Shared game loop for scenarios
# ----------------------------
def run_mode(player_speed, tariff_speed, extra_hazards=False):
    player = pygame.Rect(200, HEIGHT - PLAYER_HEIGHT, PLAYER_WIDTH, PLAYER_HEIGHT)
    trump = pygame.Rect(200, 5, TRUMP_WIDTH, TRUMP_HEIGHT)

    player_vel_y = 0
    gravity = 0.5
    jump_strength = -10
    on_ground = True

    # ------------------------
    # Player animation state
    # ------------------------
    current_player_img = PLAYER_IDLE
    walk_index = 0
    walk_timer = 0
    WALK_ANIM_SPEED = 80  # ms per frame
    facing = "right"

    # ------------------------
    # Trump animation state
    # ------------------------
    TRUMP_FRAMES = [
        pygame.transform.scale(pygame.image.load(f"trump_{i}.png"), (TRUMP_WIDTH, TRUMP_HEIGHT))
        for i in range(1, 4)
    ]

    trump_anim_state = "idle"  # "idle" or "throw"
    trump_anim_index = 0
    trump_anim_timer = 0
    TRUMP_ANIM_SPEED = 120  # ms per frame
    current_trump_img = TRUMP_FRAMES[0]

    # ------------------------
    # Precompute all masks
    # ------------------------
    PLAYER_WALK_RIGHT_MASKS = [pygame.mask.from_surface(img) for img in PLAYER_WALK_RIGHT]
    PLAYER_WALK_LEFT_MASKS = [pygame.mask.from_surface(img) for img in PLAYER_WALK_LEFT]
    PLAYER_IDLE_MASK = pygame.mask.from_surface(PLAYER_IDLE)
    current_mask = PLAYER_IDLE_MASK

    tariffs = []
    hit = False

    clock = pygame.time.Clock()
    start_time = time.time()


    TRUMP_VEL = random.choice([-5, 5])
    direction_timer = 0
    tariff_count = 0
    tariff_add_increment = 2000

    while True:
        dt = clock.tick(60)
        elapsed_time = time.time() - start_time
        direction_timer += dt
        tariff_count += dt

        # ------------------------
        # Event Handling
        # ------------------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

        # ------------------------
        # Player Input
        # ------------------------
        keys = pygame.key.get_pressed()
        moving = False

        if keys[pygame.K_LEFT] and player.x - player_speed >= 0:
            player.x -= player_speed
            facing = "left"
            moving = True

        if keys[pygame.K_RIGHT] and player.x + player_speed + player.width <= WIDTH:
            player.x += player_speed
            facing = "right"
            moving = True


        if moving:
            walk_timer += dt
            if walk_timer > WALK_ANIM_SPEED:
                walk_index = (walk_index + 1) % len(PLAYER_WALK_RIGHT)
                walk_timer = 0
            if facing == "right":
                current_player_img = PLAYER_WALK_RIGHT[walk_index]
                current_mask = PLAYER_WALK_RIGHT_MASKS[walk_index]
            else:
                current_player_img = PLAYER_WALK_LEFT[walk_index]
                current_mask = PLAYER_WALK_LEFT_MASKS[walk_index]
        else:
            current_player_img = PLAYER_IDLE
            current_mask = PLAYER_IDLE_MASK
            walk_index = 0

        # Align the mask with the drawn image
        player_img_rect = current_player_img.get_rect(midbottom=player.midbottom)
        #PLAYER_MASK = pygame.mask.from_surface(current_player_img)

        if keys[pygame.K_SPACE] and on_ground:
            player_vel_y = jump_strength
            on_ground = False

        # Gravity
        player_vel_y += gravity
        player.y += player_vel_y
        if player.y + PLAYER_HEIGHT >= HEIGHT:
            player.y = HEIGHT - PLAYER_HEIGHT
            player_vel_y = 0
            on_ground = True


        # ------------------------
        # Trump Movement
        # ------------------------
        if direction_timer > 1000:
            TRUMP_VEL = random.choice([-7, -5, 5, 7])
            direction_timer = 0

        trump.x += TRUMP_VEL
        if trump.x <= 0 or trump.x + TRUMP_WIDTH >= WIDTH:
            TRUMP_VEL *= -1

        if trump_anim_state == "throw":
            trump_anim_timer += dt
            if trump_anim_timer > TRUMP_ANIM_SPEED:
                trump_anim_index += 1
                trump_anim_timer = 0

                if trump_anim_index >= len(TRUMP_FRAMES):
                    trump_anim_state = "idle"
                    trump_anim_index = 0

            current_trump_img = TRUMP_FRAMES[trump_anim_index]
        else:
            current_trump_img = TRUMP_FRAMES[0]

        # ------------------------
        # Trump Throw Animation
        # ------------------------
        trump_anim_timer += dt

        if trump_anim_state == 1 and trump_anim_timer > TRUMP_ANIM_SPEED:
            current_trump_img = TRUMP_THROW_UP
            trump_anim_state = 2
            trump_anim_timer = 0

        elif trump_anim_state == 2 and trump_anim_timer > TRUMP_ANIM_SPEED:
            current_trump_img = TRUMP_THROW_DOWN
            trump_anim_state = 3
            trump_anim_timer = 0

        elif trump_anim_state == 3 and trump_anim_timer > TRUMP_ANIM_SPEED:
            current_trump_img = TRUMP_IDLE
            trump_anim_state = 0
            trump_anim_timer = 0

        # ------------------------
        # Tariff Spawning
        # ------------------------
        if tariff_count > tariff_add_increment:
            # Trigger Trump throw animation
            trump_anim_state = "throw"
            trump_anim_index = 0
            trump_anim_timer = 0

            for _ in range(3):
                tariff_x = random.randint(0, WIDTH - TARIFF_WIDTH)
                tariff_y = TRUMP_HEIGHT
                tariffs.append(pygame.Rect(tariff_x, tariff_y, TARIFF_WIDTH, TARIFF_HEIGHT))

            tariff_count = 0
            tariff_add_increment = max(200, tariff_add_increment - 50)

        # ------------------------
        # Collisions
        # ------------------------
        for tariff in tariffs[:]:
            tariff.y += tariff_speed
            if tariff.y > HEIGHT:
                tariffs.remove(tariff)
                continue

            offset = (tariff.x - player_img_rect.x, tariff.y - player_img_rect.y)
            if current_mask.overlap(TARIFF_MASK, offset):
                hit = True
                break

        if hit:
            lost_text = FONT_BUTTONS.render("You Lost!", 1, "white")
            WIN.blit(lost_text, (WIDTH/2 - lost_text.get_width()/2, HEIGHT/2 - lost_text.get_height()/2))
            pygame.display.update()
            pygame.time.delay(4000)
            return

        # ------------------------
        # Draw Everything
        # ------------------------
        draw(player, elapsed_time, tariffs, trump, current_player_img, current_trump_img)


# ----------------------------
# Individual scenario functions
# ----------------------------
def game_mode1():
    run_mode(player_speed=5, tariff_speed=4, extra_hazards=False)


def game_mode2():
    run_mode(player_speed=4, tariff_speed=6, extra_hazards=True)


# ----------------------------
# Main Menu Loop
# ----------------------------
def main():
    run = True
    game_state = MENU

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if game_state == MENU and event.type == pygame.MOUSEBUTTONDOWN:
                if scenario_button1.collidepoint(event.pos):
                    game_mode1()
                if scenario_button2.collidepoint(event.pos):
                    game_mode2()

        if game_state == MENU:
            draw_menu()
            pygame.time.Clock().tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
