import pygame
import time
import random
pygame.font.init()

WIDTH, HEIGHT = 1000, 800
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
PLAYER_WIDTH = 60
PLAYER_HEIGHT = 80
TRUMP_WIDTH = 70
TRUMP_HEIGHT = 90

PLAYER_VEL = 5
TARIFF_WIDTH = 30
TARIFF_HEIGHT = 30
TARIFF_VEL = 4

pygame.display.set_caption("Tariff Game")

BG = pygame.transform.scale(pygame.image.load("bg1.png"), (WIDTH, HEIGHT))
FONT_TITLE = pygame.font.SysFont("Times New Roman", 40, italic=True)
FONT_TITLE.set_underline(True)
FONT_BUTTONS = pygame.font.SysFont("Times New Roman", 30)
PLAYER_IMG = pygame.image.load("player.png")
TRUMP_IMG = pygame.image.load("trump.png")
TARIFF_IMG = pygame.image.load("tariff.png")
PLAYER_IMG = pygame.transform.scale(PLAYER_IMG, (PLAYER_WIDTH, PLAYER_HEIGHT))
TRUMP_IMG = pygame.transform.scale(TRUMP_IMG, (TRUMP_WIDTH, TRUMP_HEIGHT))
TARIFF_IMG = pygame.transform.scale(TARIFF_IMG, (TARIFF_WIDTH, TARIFF_HEIGHT))
PLAYER_MASK = pygame.mask.from_surface(PLAYER_IMG)
TARIFF_MASK = pygame.mask.from_surface(TARIFF_IMG)

MENU = "menu"
GAME1 = "game1"
GAME2 = "game2"

title_button = pygame.Rect(WIDTH // 2 - 200, 200, 400,60)
scenario_button1 = pygame.Rect(WIDTH // 2 - 300, 350, 650, 60)
scenario_button2 = pygame.Rect(WIDTH // 2 - 300, 450, 650, 60)

def draw(player, elapsed_time, tariffs, trump):
    WIN.blit(BG, (0, 0))

    time_text = FONT_BUTTONS.render(f"Time: {round(elapsed_time)}s", 1, "white")
    WIN.blit(time_text, (10, 10))

    #pygame.draw.rect(WIN, "red", player)
    WIN.blit(PLAYER_IMG, (player.x, player.y))
    #pygame.draw.rect(WIN, "blue", trump)
    WIN.blit(TRUMP_IMG, (trump.x, trump.y))

    for tariff in tariffs:
        WIN.blit(TARIFF_IMG, (tariff.x, tariff.y))


    pygame.display.update()
def draw_menu():
    WIN.blit(BG, (0, 0))

    title = FONT_TITLE.render("Wähle dein Szenario", True, "black")
    #pygame.draw.rect(WIN, "black",title_button)
    WIN.blit(title, (WIDTH//2 - title.get_width()//2, 200))

    pygame.draw.rect(WIN, "red", scenario_button1)
    pygame.draw.rect(WIN, "blue", scenario_button2)

    text1 = FONT_BUTTONS.render("Große Einschränkungen des weltweiten Handels", True, "white")
    text2 = FONT_BUTTONS .render("Weitgehend reibungsloser weltweiter Handel", True, "white")

    WIN.blit(text1, (scenario_button1.x + 20, scenario_button1.y + 15))
    WIN.blit(text2, (scenario_button2.x + 20, scenario_button2.y + 15))

    pygame.display.update()

def main():
    run = True
    game_state = MENU
    player = pygame.Rect(200, HEIGHT - PLAYER_HEIGHT, PLAYER_WIDTH, PLAYER_HEIGHT)
    trump = pygame.Rect(200, 5, TRUMP_WIDTH, TRUMP_HEIGHT )


    TRUMP_VEL = random.randint(-5, 5)

    player_vel_y = 0  # vertical speed
    gravity = 0.5  # gravity pulling the player down
    jump_strength = -10  # strength of the jump
    on_ground = True

    clock = pygame.time.Clock()
    start_time = time.time()
    elapsed_time = 0
    direction_timer = 0

    tariff_add_increment = 2000
    tariff_count = 0

    tariffs = []
    hit = False

    while run:
        tariff_count += clock.tick(60)
        elapsed_time = time.time() - start_time
        direction_timer += clock.get_time()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

            if game_state == MENU:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if scenario_button1.collidepoint(event.pos):
                        game_state = GAME1
                    if scenario_button2.collidepoint(event.pos):
                        game_state = GAME2

        if game_state == MENU:
            draw_menu()
            continue

        elif game_state == GAME1:
            # run scenario 1 logic
            draw(player, elapsed_time, tariffs, trump)

        elif game_state == GAME2:
            # run scenario 2 logic
            draw(player, elapsed_time, tariffs, trump)

        if direction_timer > 1000:  # every 2 seconds
            TRUMP_VEL = random.choice([-7, -5, 5, 7])
            direction_timer = 0

        trump.x += TRUMP_VEL

        if trump.x <= 0 or trump.x + TRUMP_WIDTH >= WIDTH:
                TRUMP_VEL *= -1



        if tariff_count > tariff_add_increment:
            for _ in range(3):
                tariff_x = random.randint(0, WIDTH - TARIFF_WIDTH)
                tariff_y = TRUMP_HEIGHT
                tariff = pygame.Rect(tariff_x, tariff_y,
                                   TARIFF_WIDTH, TARIFF_HEIGHT)
                tariffs.append(tariff)

            tariff_add_increment = max(200, tariff_add_increment - 50)
            tariff_count = 0



        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player.x - PLAYER_VEL >= 0:
            player.x -= PLAYER_VEL
        if keys[pygame.K_RIGHT] and player.x + PLAYER_VEL + player.width <= WIDTH:
            player.x += PLAYER_VEL
        if keys[pygame.K_SPACE] and on_ground:  # <-- jump
            player_vel_y = jump_strength
            on_ground = False
        player_vel_y += gravity
        player.y += player_vel_y

        # Check for hitting the floor
        if player.y + PLAYER_HEIGHT >= HEIGHT:
            player.y = HEIGHT - PLAYER_HEIGHT
            player_vel_y = 0
            on_ground = True

        for star in tariffs[:]:
            star.y += TARIFF_VEL
            if star.y > HEIGHT:
                tariffs.remove(star)
                continue

            offset = (star.x - player.x, star.y - player.y)


            if PLAYER_MASK.overlap(TARIFF_MASK, offset):
                tariffs.remove(star)
                hit = True
                break

        if hit:
            lost_text = FONT_BUTTONS.render("You Lost!", 1, "white")
            WIN.blit(lost_text, (WIDTH/2 - lost_text.get_width()/2, HEIGHT/2 - lost_text.get_height()/2))
            pygame.display.update()
            pygame.time.delay(4000)
            break


    pygame.quit()


if __name__ == "__main__":
    main()