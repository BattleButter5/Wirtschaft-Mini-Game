import pygame
import time
import random
import webbrowser
import os

pygame.font.init()

# ----------------------------
# Constants & Setup
# ----------------------------
WIN = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WIDTH, HEIGHT = WIN.get_size()
pygame.display.set_caption("Tariff Game")

UI_HEIGHT = 100
GAME_HEIGHT = HEIGHT - UI_HEIGHT
GAME_TOP = UI_HEIGHT
GAME_BOTTOM_1 = HEIGHT - 40
GAME_BOTTOM_2 = HEIGHT - 60

# Player / Trump / Tariff
PLAYER_WIDTH, PLAYER_HEIGHT = 100, 120
TRUMP_WIDTH, TRUMP_HEIGHT = 105, 125
TARIFF_WIDTH, TARIFF_HEIGHT = 35, 35

PLAYER_VEL = 5
TARIFF_VEL = 4

# Fonts
FONT_TITLE = pygame.font.SysFont("Times New Roman", 50, italic=True)
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
scenario_button1 = pygame.Rect(WIDTH // 2 - 350, 450, 850, 60)
scenario_button2 = pygame.Rect(WIDTH // 2 - 350, 600, 850, 60)

#crates
CRATE_IMAGES = [
    pygame.transform.scale(pygame.image.load("crate_1.png").convert_alpha(), (40, 40)),
    pygame.transform.scale(pygame.image.load("crate_2.png").convert_alpha(), (40, 40)),
    pygame.transform.scale(pygame.image.load("crate_3.png").convert_alpha(), (40, 40)),
]

# --- Crate System ---

crate_types = [
    {"name": "oil", "color": (30, 30, 30)},
    {"name": "steel", "color": (160, 160, 160)},
    {"name": "food", "color": (50, 200, 50)}
]

selected_crate = 0
requested_crate = 0

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


def draw_2(player,time_left, tariffs, player_img, quartal, money, quota, target, crates):
    # Decide color based on time left
    if time_left <= 6:
        timer_color = (255, 0, 0)  # red for last 5 seconds
    else:
        timer_color = (255, 255, 255)  # normal white


    WIN.blit(BG, (0, 0))


    target.draw(WIN)

    for crate in crates:
        crate.draw(WIN)

    pygame.draw.rect(WIN, (30, 30, 30), (0, 0, WIDTH, UI_HEIGHT))
    pygame.draw.line(WIN, (80, 80, 80), (0, UI_HEIGHT), (WIDTH, UI_HEIGHT), 2)


    quartal_text = FONT_BUTTONS.render(f"Quartal: {quartal}", True, "white")
    quota_text = FONT_BUTTONS.render("Quota: $", True, "white")
    time_left_text = FONT_BUTTONS.render(f"Time Left: {max(0, int(time_left))}", True, timer_color)

    WIN.blit(quartal_text, (250, 20))
    WIN.blit(quota_text, (600, 20))
    WIN.blit(time_left_text, (1650, 20))
    draw_quota_bar(money,quota)

    img_rect = player_img.get_rect(midbottom=player.midbottom)
    WIN.blit(player_img, img_rect.topleft)

    for tariff in tariffs:
        WIN.blit(TARIFF_IMG, (tariff.x, tariff.y))

    # --- Selection Bar ---
    bar_y = HEIGHT - 55

    for i, img in enumerate(CRATE_IMAGES):
        x_pos = WIDTH // 2 - 120 + i * 120

        border_color = (255, 255, 0) if i == selected_crate else (100, 100, 100)

        pygame.draw.rect(WIN, border_color, (x_pos, bar_y, 50, 50), 3)
        WIN.blit(img, (x_pos + 5, bar_y + 5))




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

#-------------------------------
#quota bar
#-------------------------------
def draw_quota_bar(money, quota):
    bar_width = 300
    bar_height = 20
    bar_x = WIDTH // 2 - bar_width // 2  -20
    bar_y = 35

    # Calculate progress ratio
    progress = min(money / quota, 1)  # number between 0 and 1

    # Background (grey)
    bg_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
    pygame.draw.rect(WIN, (50, 50, 50), bg_rect)

    # Foreground (green) — multiply width by progress
    fg_width = int(bar_width * progress)  # <-- must be a number
    fg_rect = pygame.Rect(bar_x, bar_y, fg_width, bar_height)
    pygame.draw.rect(WIN, (50, 200, 50), fg_rect)

    # Optional border
    pygame.draw.rect(WIN, (0,0,0), bg_rect, 2)


def show_pdf(file_path):
    # Get the absolute path
    pdf_path = os.path.abspath("pdf-sample_0.pdf")

    # Open using file:// URL
    webbrowser.open(f"file://{pdf_path}")

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

#-------------------------
#crates
#----------------
class CrateProjectile:
    def __init__(self, x, y, crate_type):
        self.type = crate_type
        self.image = CRATE_IMAGES[crate_type]
        self.rect = self.image.get_rect(midbottom=(x, y))
        self.speed = 8

    def update(self):
        self.rect.y -= self.speed

    def draw(self, surface):
        surface.blit(self.image, self.rect)


#---------------------
#targets
#----------------------
class ExportTarget:
    def __init__(self):
        self.image = pygame.Surface((120, 30))
        self.rect = self.image.get_rect()
        self.rect.y = 120
        self.speed = 4

        self.new_request()

    def new_request(self):
        self.requested_type = random.randint(0, len(CRATE_IMAGES) - 1)
        self.rect.x = random.randint(0, WIDTH - self.rect.width)

    def update(self):
        self.rect.x += self.speed
        if self.rect.left <= 0 or self.rect.right >= WIDTH:
            self.speed *= -1

    def draw(self, surface):
        # Draw base target
        self.image.fill((200, 50, 50))
        surface.blit(self.image, self.rect)

        # Draw requested crate icon above it
        crate_img = CRATE_IMAGES[self.requested_type]
        icon_rect = crate_img.get_rect(midbottom=(self.rect.centerx, max(self.rect.top - 5, UI_HEIGHT + crate_img.get_height())))
        surface.blit(crate_img, icon_rect)
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

        if keys[pygame.K_a] and player.x - player_speed >= 0:
            player.x -= player_speed
            facing = "left"
            moving = True

        if keys[pygame.K_d] and player.x + player_speed + player.width <= WIDTH:
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

        # gravity & floor check
        player_vel_y += gravity
        player.y += player_vel_y

        if player.y + PLAYER_HEIGHT > GAME_BOTTOM_1:
            player.y = GAME_BOTTOM_1 - PLAYER_HEIGHT
            player_vel_y = 0
            on_ground = True

        if player.y < GAME_TOP:
            player.y = GAME_TOP
            player_vel_y = 0

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

    quartal = 1
    quota = 100
    money = 0
    quartal_duration = 30
    quartal_start_time = time.time()

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

    crates = []
    target = ExportTarget()
    shoot_cooldown = 500  # milliseconds
    last_shot = 0
    global selected_crate

    while True:
        dt = clock.tick(60)
        tariff_count += dt
        elapsed_time = time.time() - quartal_start_time
        time_left = quartal_duration - elapsed_time


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
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    now = pygame.time.get_ticks()
                    if now - last_shot > shoot_cooldown:
                        crate = CrateProjectile(player.centerx, player.top,selected_crate)
                        crates.append(crate)
                        last_shot = now
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_f:
                    now = pygame.time.get_ticks()
                    if now - last_shot > shoot_cooldown:
                        crate = CrateProjectile(player.centerx, player.top,selected_crate)
                        crates.append(crate)
                        last_shot = now
            if event.type == pygame.MOUSEWHEEL:
                selected_crate += event.y
                selected_crate %= len(CRATE_IMAGES)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    selected_crate = 0
                if event.key == pygame.K_2 and len(CRATE_IMAGES) > 1:
                    selected_crate = 1
                if event.key == pygame.K_3 and len(CRATE_IMAGES) > 2:
                    selected_crate = 2
        # ------------------------
        # Player Input
        # ------------------------
        keys = pygame.key.get_pressed()
        moving = False

        if keys[pygame.K_a] and player.x - player_speed >= 0:
            player.x -= player_speed
            facing = "left"
            moving = True

        if keys[pygame.K_d] and player.x + player_speed + player.width <= WIDTH:
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

            # gravity & floor check
        player_vel_y += gravity
        player.y += player_vel_y

        if player.y + PLAYER_HEIGHT > GAME_BOTTOM_2:
            player.y = GAME_BOTTOM_2 - PLAYER_HEIGHT
            player_vel_y = 0
            on_ground = True

        if player.y < GAME_TOP:
            player.y = GAME_TOP
            player_vel_y = 0

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

        #  Calculate elapsed time
        quartal_time = time.time() - quartal_start_time

        #   Check if quota reached
        if money >= quota:
            quartal += 1
            quota += 75
            quartal_start_time = time.time()
            money = 0

        #  Check if time expired
        elif time_left <= 0:
            dead = True

        # Update crates
        for crate in crates[:]:
            crate.update()

            # Remove if off-screen
            if crate.rect.bottom < 0:
                crates.remove(crate)

        # Update target
        target.update()


        #crate collision
        for crate in crates[:]:
            if crate.rect.colliderect(target.rect):

                if crate.type == target.requested_type:
                    money += 25
                    target.new_request()
                else:
                    money -= 10  # optional penalty

                crates.remove(crate)
        # ------------------------
        # Draw Everything
        # ------------------------

        draw_2(player,time_left, tariffs, current_player_img, quartal, money, quota,target, crates)
        #target.draw(WIN)

        #for crate in crates:
            #crate.draw(WIN)
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
    return run_mode_2(player_speed=7, tariff_speed=6)

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
