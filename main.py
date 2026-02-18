import pygame
import time
import random
import webbrowser

pygame.font.init()

# ----------------------------
# Constants & Setup
# ----------------------------
WIN = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WIDTH, HEIGHT = WIN.get_size()
pygame.display.set_caption("Tariff Game")

UI_HEIGHT = 100
GAME_HEIGHT = HEIGHT - UI_HEIGHT

# Player / Trump / Tariff
PLAYER_WIDTH, PLAYER_HEIGHT = 100, 120
TRUMP_WIDTH, TRUMP_HEIGHT = 105, 125
TARIFF_WIDTH, TARIFF_HEIGHT = 35, 35

PLAYER_VEL = 5
TARIFF_VEL = 4

# Fonts
FONT_TITLE = pygame.font.SysFont("Times New Roman", 40, italic=True)
FONT_TITLE.set_underline(True)
FONT_BUTTONS = pygame.font.SysFont("Times New Roman", 40)

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

PLAYER_DEAD = pygame.transform.scale(
    pygame.image.load("player_dead.png"),
    (PLAYER_WIDTH, PLAYER_HEIGHT)
)

TARIFF_MASK = pygame.mask.from_surface(TARIFF_IMG)

# Game States
MENU = "menu"
GAME1 = "game1"
GAME2 = "game2"

# Buttons
title_button = pygame.Rect(WIDTH // 2 - 200, 200, 400, 60)
scenario_button1 = pygame.Rect(WIDTH // 2 - 300, 350, 650, 60)
scenario_button2 = pygame.Rect(WIDTH // 2 - 300, 450, 650, 60)
scenario_button1_img = pygame.image.load("button_pink.png").convert_alpha()
scenario_button2_img = pygame.image.load("button_blue1.png").convert_alpha()


# ----------------------------
# Drawing functions
# ----------------------------
def draw_1(player, elapsed_time, tariffs, trump, player_img, current_trump_img):
    WIN.blit(BG, (0, 0))
    time_text = FONT_BUTTONS.render(f"Zeit: {round(elapsed_time)}s", 1, "black")
    WIN.blit(time_text, (1700, 10))

    img_rect = player_img.get_rect(midbottom=player.midbottom)
    WIN.blit(player_img, img_rect.topleft)

    WIN.blit(current_trump_img, (trump.x, trump.y))

    for tariff in tariffs:
        WIN.blit(TARIFF_IMG, (tariff.x, tariff.y))


def draw_2(player, elapsed_time, tariffs, player_img, money, month, quota):
    WIN.blit(BG, (0, 0))
    pygame.draw.rect(WIN, (30, 30, 30), (0, 0, WIDTH, UI_HEIGHT))
    pygame.draw.line(WIN, (80, 80, 80), (0, UI_HEIGHT), (WIDTH, UI_HEIGHT), 2)

    money_text = FONT_BUTTONS.render(f"Money: ${money}", True, "white")
    month_text = FONT_BUTTONS.render(f"Month: {month}", True, "white")
    quota_text = FONT_BUTTONS.render(f"Quota: ${quota}", True, "white")
    time_text = FONT_BUTTONS.render(f"Time: {int(elapsed_time)}s", True, "white")

    WIN.blit(money_text, (20, 20))
    WIN.blit(month_text, (250, 20))
    WIN.blit(quota_text, (450, 20))
    WIN.blit(time_text, (650, 20))

    img_rect = player_img.get_rect(midbottom=player.midbottom)
    WIN.blit(player_img, img_rect.topleft)

    for tariff in tariffs:
        WIN.blit(TARIFF_IMG, (tariff.x, tariff.y))




def draw_menu():
    WIN.blit(BG, (0, 0))
    title = FONT_TITLE.render("Wähle dein Szenario", True, "black")
    WIN.blit(title, (WIDTH//2 - title.get_width()//2, 200))

    pygame.draw.rect(WIN, "red", scenario_button1)
    pygame.draw.rect(WIN, "blue", scenario_button2)

    button_1 = pygame.transform.scale(scenario_button1_img,(1000,100))
    WIN.blit(button_1, (WIDTH // 2 - 300, 350, 650, 60))
    button_2 = pygame.transform.scale(scenario_button2_img, (1000, 100))
    WIN.blit(button_2, (WIDTH // 2 - 300, 450, 650, 60))

    text1 = FONT_BUTTONS.render("Große Einschränkungen des weltweiten Handels", True, "white")
    text2 = FONT_BUTTONS.render("Weitgehend reibungsloser weltweiter Handel", True, "white")
    WIN.blit(text1, (scenario_button1.x + 20, scenario_button1.y + 15))
    WIN.blit(text2, (scenario_button2.x + 20, scenario_button2.y + 15))

    pygame.display.update()

def draw_health_bar(player_rect, health, max_health):
    bar_width = 40
    bar_height = 6
    offset_y = 10  # distance above the player's head

    health_ratio = health / max_health

    # Position above player
    bar_x = player_rect.centerx - bar_width // 2
    bar_y = player_rect.top - offset_y

    # Background (red)
    bg_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
    pygame.draw.rect(WIN, (180, 0, 0), bg_rect)

    # Health (green)
    fg_rect = pygame.Rect(
        bar_x,
        bar_y,
        int(bar_width * health_ratio),
        bar_height
    )
    pygame.draw.rect(WIN, (0, 200, 0), fg_rect)

    # Optional border (looks clean)
    pygame.draw.rect(WIN, (0, 0, 0), bg_rect, 1)


def show_pdf(file_path):
    webbrowser.open(file_path)

#trivia function -------------------------------------
#------------------------------------------------------

def ask_trivia(questions):
    """
    questions: list of tuples:
    (question_string, [option1, option2, option3], correct_index)
    Returns number of correct answers
    """

    correct = 0
    font = pygame.font.SysFont("Arial", 28)
    clock = pygame.time.Clock()

    for question, options, correct_index in questions:
        answered = False
        selected = -1

        while not answered:
            clock.tick(60)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return 0

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        selected = 0
                        answered = True
                    elif event.key == pygame.K_2:
                        selected = 1
                        answered = True
                    elif event.key == pygame.K_3:
                        selected = 2
                        answered = True

            WIN.fill((40, 40, 40))

            # Draw question
            question_surf = font.render(question, True, (255, 255, 255))
            WIN.blit(question_surf, (WIDTH // 2 - question_surf.get_width() // 2, HEIGHT // 2 - 100))

            # Draw options
            for i, option in enumerate(options):
                option_text = f"{i+1}. {option}"
                option_surf = font.render(option_text, True, (200, 200, 200))
                WIN.blit(option_surf, (WIDTH // 2 - option_surf.get_width() // 2, HEIGHT // 2 - 40 + i * 40))

            pygame.display.update()

        # Check answer
        if selected == correct_index:
            correct += 1

        pygame.time.delay(500)  # small pause before next question

    return correct

#revive function -------------------------------------
#-----------------------------------------------------
def revive_player(max_health):
    # Step 1: Show message
    font = pygame.font.SysFont("Arial", 28)
    WIN.fill((0,0,0))
    msg = "You were overwhelmed by rising tariffs! Read this article to survive!"
    text_surf = font.render(msg, True, (255,255,255))
    WIN.blit(text_surf, (WIDTH//2 - text_surf.get_width()//2, HEIGHT//2))
    pygame.display.update()
    pygame.time.delay(2000)

    # Step 2: Open PDF
    show_pdf("pdf-sample_0.pdf")

    # Step 3: Ask trivia
    questions = [
        ("What is a tariff?", ["A tax", "A trade agreement", "A subsidy"], 0),
        ("Who sets tariffs?", ["Private companies", "Government", "Banks"], 1),
        ("Do tariffs increase import prices?", ["Yes", "No", "Only in Europe"], 0)
    ]
    correct = ask_trivia(questions)

    # Step 4: Restore health
    restored_health = max_health * (correct / len(questions))

    # Return restored health or 0 if player failed
    if restored_health > 0:
        return int(restored_health)
    else:
        return 0


#game over function -------------------------
#--------------------------------------------
def show_game_over_screen():
    WIN.blit(BG,(0,0))
    WIN.blit(TRUMP_IDLE,(WIDTH//2,100))
    dead_img_rect = PLAYER_DEAD.get_rect(midbottom=(WIDTH//2, HEIGHT//2 + 400))
    WIN.blit(PLAYER_DEAD, dead_img_rect.topleft)

    # Draw game over message
    font = pygame.font.SysFont("Arial", 36)
    msg = "Du konntest den steigenden Zöllen nicht standhalten!"
    text_surf = font.render(msg, True, (255, 0, 0))
    WIN.blit(text_surf, (WIDTH//2 - text_surf.get_width()//2, HEIGHT//2 - 50))

    pygame.display.update()
    pygame.time.delay(3000)  # wait 3 seconds before quitting

#----------------------------------------
class MoneyBill(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        original_img = pygame.image.load("money.png").convert_alpha()
        self.image = pygame.transform.scale(original_img, (35, 35))

        self.rect = self.image.get_rect()

        self.rect.x = random.randint(0, WIDTH - self.rect.width)
        self.rect.y = -50

        self.speed = 180

    def update(self, dt):
        self.rect.y += self.speed * dt / 1000

        # remove if off-screen
        if self.rect.top > HEIGHT:
            self.kill()

# ----------------------------
# Shared game loop for scenarios
# ----------------------------
def run_mode_1(player_speed, tariff_speed):
    player = pygame.Rect(200, HEIGHT - PLAYER_HEIGHT, PLAYER_WIDTH, PLAYER_HEIGHT)
    trump = pygame.Rect(200, 5, TRUMP_WIDTH, TRUMP_HEIGHT)

    player_vel_y = 0
    gravity = 0.5
    jump_strength = -12
    on_ground = True

    player_health = 3
    max_health = 3

    dead = False
    first_death = True

    money_bills = pygame.sprite.Group()
    money_timer = 0
    money_interval = random.randint(14000, 20000)

    # ------------------------
    # Player animation state
    # ------------------------
    current_player_img = PLAYER_IDLE
    walk_index = 0
    walk_timer = 0
    walk_anim_speed = 80  # ms per frame
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
        difficulty = min(1 + elapsed_time / 30, 3)

        money_timer += dt

        # ------------------------
        # Event Handling
        # ------------------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
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
            if walk_timer > walk_anim_speed:
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

            for _ in range(random.randint(3,4)):
                tariff_x = random.randint(0, WIDTH - TARIFF_WIDTH)
                tariff_y = TRUMP_HEIGHT
                tariffs.append(pygame.Rect(tariff_x, tariff_y, TARIFF_WIDTH, TARIFF_HEIGHT))

            tariff_count = 0
            tariff_add_increment = max(375, tariff_add_increment - 80)

        #-----------------------------
        #---money----------
        if money_timer >= money_interval:
            bill = MoneyBill()
            money_bills.add(bill)

            money_timer = 0
            money_interval = random.randint(10000, 15000)

        # ------------------------
        # Collisions
        # ------------------------
        for tariff in tariffs[:]:
            tariff.y += tariff_speed * difficulty
            if tariff.y > HEIGHT:
                tariffs.remove(tariff)
                continue

            offset = (tariff.x - player_img_rect.x, tariff.y - player_img_rect.y)
            if current_mask.overlap(TARIFF_MASK, offset):
                player_health -= 1
                tariffs.remove(tariff)

                # small invulnerability delay (prevents double-hits)
                pygame.time.delay(30)



                if player_health <= 0:
                    dead = True

                break
                # ------------------------
                # Money Pickup Collision
                # ------------------------
            for bill in money_bills:
                if player.colliderect(bill.rect):
                    player_health += 1  # restore 1 health
                    if player_health > max_health:
                        player_health = max_health
                    bill.kill()

        # ------------------------
        # Draw Everything
        # ------------------------
        draw_1(player, elapsed_time, tariffs, trump, current_player_img, current_trump_img)
        draw_health_bar(player, player_health, max_health)
        money_bills.update(dt)
        money_bills.draw(WIN)
        pygame.display.update()

        if dead:
            if first_death:
                first_death = False

                pause_start = time.time()
                restored_health = revive_player(max_health)
                pause_duration = time.time() - pause_start
                start_time += pause_duration  # pause game timer

                if restored_health > 0:
                    player_health = restored_health
                    dead = False
                    continue
                else:
                    # permanent game over → back to menu
                    show_game_over_screen()
                    return "menu"

            else:
                # SECOND DEATH → permanent game over
                show_game_over_screen()
                return "menu"

#------------------------------------------------
#------------------------------------------------
# run_mode_2
#------------------------------------------------
#------------------------------------------------
def run_mode_2(player_speed, tariff_speed):
    player = pygame.Rect(200, HEIGHT - PLAYER_HEIGHT, PLAYER_WIDTH, PLAYER_HEIGHT)

    clock = pygame.time.Clock()
    start_time = time.time()

    month = 1
    quota = 100
    money = 0
    month_duration = 30
    month_start_time = time.time()

    player_vel_y = 0
    gravity = 0.5
    jump_strength = -10
    on_ground = True

    player_health = 3
    max_health = 3

    dead = False
    first_death = True

    # ------------------------
    # Player animation state
    # ------------------------
    current_player_img = PLAYER_IDLE
    walk_index = 0
    walk_timer = 0
    walk_anim_speed = 80  # ms per frame
    facing = "right"


    PLAYER_WALK_RIGHT_MASKS = [pygame.mask.from_surface(img) for img in PLAYER_WALK_RIGHT]
    PLAYER_WALK_LEFT_MASKS = [pygame.mask.from_surface(img) for img in PLAYER_WALK_LEFT]
    PLAYER_IDLE_MASK = pygame.mask.from_surface(PLAYER_IDLE)
    current_mask = PLAYER_IDLE_MASK

    tariffs = []
    hit = False



    tariff_count = 0
    tariff_interval = random.randint(10000, 15000)


    while True:
        dt = clock.tick(60)
        elapsed_time = time.time() - start_time
        tariff_count += dt
        month_time = time.time() - month_start_time


        # ------------------------
        # Event Handling
        # ------------------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
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
            if walk_timer > walk_anim_speed:
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
        # Tariff Spawning
        # ------------------------


        if tariff_count > tariff_interval:
            for _ in range(2):
                tariff_x = random.randint(0, WIDTH - TARIFF_WIDTH)
                tariff_y = 100
                tariffs.append(pygame.Rect(tariff_x, tariff_y, TARIFF_WIDTH, TARIFF_HEIGHT))

            tariff_count = 0


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
                player_health -= 1
                tariffs.remove(tariff)


                pygame.time.delay(30)



                if player_health <= 0:
                    dead = True

                break


        #quota
        if month_time >= month_duration:
            if money >= quota > 0:
                # Player passed the month
                month += 1
                quota += 75  # increase difficulty
                month_start_time = time.time()
            else:
                dead = True

        # ------------------------
        # Draw Everything
        # ------------------------
        draw_2(player, elapsed_time, tariffs, current_player_img, money, month, quota)
        draw_health_bar(player, player_health, max_health)
        pygame.display.update()

        if dead:
            if first_death:
                first_death = False

                pause_start = time.time()
                restored_health = revive_player(max_health)
                pause_duration = time.time() - pause_start
                start_time += pause_duration  # pause game timer

                if restored_health > 0:
                    player_health = restored_health
                    dead = False
                    continue
                else:
                    # permanent game over → back to menu
                    show_game_over_screen()
                    return "menu"

            else:
                # SECOND DEATH → permanent game over
                show_game_over_screen()
                return "menu"

# ----------------------------
# Individual scenario functions
# ----------------------------
def game_mode1():
    return run_mode_1(player_speed=8, tariff_speed=6)

def game_mode2():
    return run_mode_2(player_speed=8, tariff_speed=6)

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

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    return

            if game_state == MENU and event.type == pygame.MOUSEBUTTONDOWN:
                if scenario_button1.collidepoint(event.pos):
                    result = game_mode1()
                    if result == "menu":
                        game_state = MENU
                if scenario_button2.collidepoint(event.pos):
                    result = game_mode2()
                    if result == "menu":
                        game_state = MENU
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if game_state != MENU:
                        game_state = MENU  # back to menu
                    else:
                        run = False

        if game_state == MENU:
            draw_menu()
            pygame.time.Clock().tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
