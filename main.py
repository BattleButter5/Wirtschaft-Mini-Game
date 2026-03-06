import pygame
import time
import random
import os
import json
import subprocess
#import sys
#import webbrowser

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
TARIFF_WIDTH_1, TARIFF_HEIGHT_1 = 35, 35
TARIFF_WIDTH_2, TARIFF_HEIGHT_2 = 50, 50
TARIFF_WIDTH_3, TARIFF_HEIGHT_3 = 28, 28

PLAYER_VEL = 5
TARIFF_VEL = 4

# Fonts
FONT_TITLE = pygame.font.SysFont("Times New Roman", 50, italic=True)
FONT_TITLE.set_underline(True)
FONT_BUTTONS = pygame.font.SysFont("Times New Roman", 40)

# Images
BG = pygame.transform.scale(pygame.image.load("bg1.png"), (WIDTH, HEIGHT))
BG_2 = pygame.transform.scale(pygame.image.load("BG_6.png"), (WIDTH, HEIGHT))
LIEFERENGPASS_IMG = pygame.image.load("Lieferengpass.png").convert_alpha()
EXPORT_TARGET_IMG = pygame.transform.scale(
    pygame.image.load("Flag.png").convert_alpha(),  # Use your image filename
    (220, 80)
)
HIGHSCORE_FILE = "highscores.json"

# Load tariff sprites
TARIFF_LIGHT_RED = pygame.image.load("tariff_light_red.png").convert_alpha()
TARIFF_DARK_RED = pygame.image.load("tariff_dark_red.png").convert_alpha()
TARIFF_ORANGE = pygame.image.load("tariff_orange.png").convert_alpha()

# Optional: scale them to your standard tariff size
TARIFF_LIGHT_RED = pygame.transform.scale(TARIFF_LIGHT_RED, (TARIFF_WIDTH_1, TARIFF_HEIGHT_1))
TARIFF_DARK_RED = pygame.transform.scale(TARIFF_DARK_RED, (TARIFF_WIDTH_2, TARIFF_HEIGHT_2))
TARIFF_ORANGE = pygame.transform.scale(TARIFF_ORANGE, (TARIFF_WIDTH_3, TARIFF_HEIGHT_3))

# Tariff type info
TARIFF_TYPES = {
    "normal": {
        "img": TARIFF_LIGHT_RED,
        "width": TARIFF_WIDTH_1,
        "height": TARIFF_HEIGHT_1,
        "mask": pygame.mask.from_surface(TARIFF_LIGHT_RED)
    },
    "fast": {
        "img": TARIFF_ORANGE,
        "width": TARIFF_WIDTH_3,
        "height": TARIFF_HEIGHT_3,
        "mask": pygame.mask.from_surface(TARIFF_ORANGE)
    },
    "heavy": {
        "img": TARIFF_DARK_RED,
        "width": TARIFF_WIDTH_2,
        "height": TARIFF_HEIGHT_2,
        "mask": pygame.mask.from_surface(TARIFF_DARK_RED)
    }
}

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

TARIFF_MASK = pygame.mask.from_surface(TARIFF_LIGHT_RED)

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


#------------------------------------------
# PDFS & Fragen
#-----------------------------------------
MODE1_REVIVES = [
    {
        "pdf": "pdf-sample_0.pdf",
        "questions": [
            ("What is a tariff?", ["A tax", "A trade agreement", "A subsidy"], 0),
            ("Who sets tariffs?", ["Government", "Banks", "Companies"], 0),
            ("how old am i?", ["18", "19", "17"], 2),
            ("how old is Tiny?", ["3", "4", "5"], 1)
        ]
    },
    {
        "pdf": "pdf-sample_0.pdf",
        "questions": [
            ("What is a trade war?", ["Mutual tariffs", "Currency union", "Free trade"], 0),
            ("Do trade wars increase prices?", ["Yes", "No", "Never"], 0),
            ("how old am i?", ["18", "19", "17"], 2),
            ("how old is Tiny?", ["3", "4", "5"], 1)
        ]
    }
]

MODE2_REVIVES = [
    {
        "pdf": "pdf-sample_1.pdf",
        "questions": [
            ("What is export?", ["Sell abroad", "Buy abroad", "Tax goods"], 0),
            ("Exports increase GDP?", ["Yes", "No", "Only locally"], 0),
            ("how old am i?", ["18", "19", "17"], 2),
            ("how old is Tiny?", ["3", "4", "5"], 1)
        ]
    },
    {
        "pdf": "pdf-sample_1.pdf",
        "questions": [
            ("What does GDP stand for?", ["Gross Domestic Product", "Global Debt Plan", "General Trade Policy"], 0),
            ("GDP measures?", ["Economic output", "Population", "Inflation only"], 0),
            ("how old am i?", ["18", "19", "17"], 2),
            ("how old is Tiny?", ["3", "4", "5"], 1)
        ]
    }
]

#--------------------------------------
#cutscene text & Bilder
#-------------------------------------

MODE1_CUTSCENE = [
    {
        "text": ["Der internationale Handel steht kurz vor dem Zusammenbruch...",


                 ],
        "images": [
            {
                "path": "cutscene_trade_down.png",
                "size": (350,400),
                "pos": (WIDTH // 2 - 250, HEIGHT // 2 - 200)
            },

        ]
    },
    {
        "text": [ "Trumps Zölle haben einen Zollkrieg ausgelöst!",
                  "Handelsbeziehungen gehen in die Brüche...",
                  "Preise und Bürokratie steigen...",

                 ],
        "images": [
            {
                "path": "cutscene_trump.png",
                "size": (300, 400),
                "pos": (WIDTH // 2 - 250, HEIGHT // 2 - 200)
            },
            {
                "path": "cutscene_scroll.png",
                "size": (200, 200),
                "pos": (WIDTH // 2 + 200, HEIGHT // 2 - 150)
            }
        ]
    },
    {
        "text": [
            "Du bist Teil eines kleinen deutschen Exportunternehmens"
        ],
        "images": [
            {
                "path": "player_idle.png",
                "size": (250, 350),
                "pos": (WIDTH // 2 - 400, HEIGHT // 2 - 150)
            },
            {
                "path": "cutscene_company.png",
                "size": (500, 400),
                "pos": (WIDTH // 2 + 200, HEIGHT // 2 - 150)
            },
            {
                "path": "cutscene_deutschland.png",
                "size": (200, 75),
                "pos": (WIDTH // 2 + 450, HEIGHT // 2 - 150)
            }
        ]
    },
    {
        "text": [
            "Ihr exportiert hauptsächlich in die USA."
        ],
        "images": [
            {
                "path": "player_idle.png",
                "size": (250, 350),
                "pos": (WIDTH // 2 - 400, HEIGHT // 2 - 150)
            },
            {
                "path": "Flag.png",
                "size": (500, 300),
                "pos": (WIDTH // 2 + 200, HEIGHT // 2 - 150)
            }
        ]
    },
    {
        "text": [
            "Die Zölle und der stockende Handel stellen eine große Bedrohung dar...",
            "Weiche ihnen aus um den Bankrott zu vermeiden! "
        ],
        "images": [
            {
                "path": "player_idle.png",
                "size": (250, 350),
                "pos": (WIDTH // 2 - 400, HEIGHT // 2 - 150)
            },
            {
                "path": "tariff_light_red.png",
                "size": (150, 150),
                "pos": (WIDTH // 2  , HEIGHT // 2 - 350)
            },
{
                "path": "cutscene_trade_down.png",
                "size": (350, 200),
                "pos": (WIDTH // 2 + 100, HEIGHT // 2 - 50)
            },
            {
                "path": "cutscene_scroll.png",
                "size": (200, 200),
                "pos": (WIDTH // 2 + 350, HEIGHT // 2 - 350)
            }
        ]
    },
    {
        "text": [
            "Steuerung:",
            "A / D zum Bewegen",
            "LEERTASTE zum Springen",
            "SHIFT zum Ausweichen"
        ],
        "images": [
            {
                "path": "keyboard_colored_1.png",
                "size": (700, 350),
                "pos": (WIDTH // 2 -300 , HEIGHT // 2 -300 )
            }

        ]
    }
]


MODE2_CUTSCENE = [
    {
        "text": ["Der internationale Handel blüht auf!",
                 "Keine Einschränkungen oder Zölle...",
                 "Viele Möglichkeiten für Profit..."

                 ],
        "images": [
            {
                "path": "cutscene_trade_up_1.png",
                "size": (500, 300),
                "pos": (WIDTH // 2 - 600, HEIGHT // 2 - 200)
            },
{
                "path": "BG_2.png",
                "size": (550, 650),
                "pos": (WIDTH // 2 , HEIGHT // 2 - 350)
            },

        ]
    },
    {
        "text": [
            "Du bist Teil eines kleinen deutschen Exportunternehmens"
        ],
        "images": [
            {
                "path": "player_idle.png",
                "size": (250, 350),
                "pos": (WIDTH // 2 - 400, HEIGHT // 2 - 150)
            },
            {
                "path": "cutscene_company.png",
                "size": (500, 400),
                "pos": (WIDTH // 2 + 200, HEIGHT // 2 - 150)
            },
            {
                "path": "cutscene_deutschland.png",
                "size": (200, 75),
                "pos": (WIDTH // 2 + 450, HEIGHT // 2 - 150)
            },
        ],
    },
    {
        "text": [
            "Ihr exportiert hauptsächlich in die USA."
        ],
        "images": [
            {
                "path": "player_idle.png",
                "size": (250, 350),
                "pos": (WIDTH // 2 - 500, HEIGHT // 2 - 150)
            },
            {
                "path": "Flag.png",
                "size": (500, 300),
                "pos": (WIDTH // 2 + 300, HEIGHT // 2 - 150)
            },
            {
                "path": "crate_1.png",
                "size": (100, 100),
                "pos": (WIDTH // 2 , HEIGHT // 2 + 50)
            },
            {
                "path": "crate_2.png",
                "size": (100, 100),
                "pos": (WIDTH // 2 -110, HEIGHT // 2 +50)
            },
            {
                "path": "crate_3.png",
                "size": (100, 100),
                "pos": (WIDTH // 2 -55, HEIGHT // 2 - 60)
            }
        ]
    },

    {
        "text": [
            "Leider hast du einen sehr strengen Chef, der hohe Quartalziele setzt..."
        ],
        "images": [
            {
                "path": "player_idle.png",
                "size": (250, 350),
                "pos": (WIDTH // 2 - 400, HEIGHT // 2 - 150)
            },
            {
                "path": "cutscene_boss_2.png",
                "size": (300, 400),
                "pos": (WIDTH // 2 + 200, HEIGHT // 2 - 150)
            },
        ],
    },
{
        "text": [
            "Exportiere die richtigen Produkte um diese zu erfüllen.",
            "Vermeide Lieferengpässe und erfülle das Ziel in der vorgegebenen Zeit. "
        ],
        "images": [
            {
                "path": "player_idle.png",
                "size": (250, 350),
                "pos": (WIDTH // 2 - 500, HEIGHT // 2 - 150)
            },

            {    "path": "crate_1.png",
                "size": (100, 100),
                "pos": (WIDTH // 2 , HEIGHT // 2 + 50)
            },
            {
                "path": "crate_2.png",
                "size": (100, 100),
                "pos": (WIDTH // 2 -110, HEIGHT // 2 +50)
            },
            {
                "path": "crate_3.png",
                "size": (100, 100),
                "pos": (WIDTH // 2 -55, HEIGHT // 2 - 60)
            },
            {
                "path": "cutscene_ziel.png",
                "size": (550, 100),
                "pos": (WIDTH // 2 +250, HEIGHT // 2 )
            },

        ],
    },
    {
        "text": [
            "Steuerung:",
            "A / D zum Bewegen",
            "SPACE zum Springen",
            "LINKE MAUSTASTE oder F um die Kisten zu exportieren",
            "MAUSRAD oder 1-3 um Kisten zu wechseln"
        ],
        "images": [
            {
                "path": "keyboard_colored.png",
                "size": (700, 350),
                "pos": (WIDTH // 2 - 300, HEIGHT // 2 - 300)
            }

        ]
    }
]

#--------------------------------
#FUNCTIONS
#-------------------------------

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
        WIN.blit(tariff["img"], (tariff["rect"].x, tariff["rect"].y))


def draw_2(player,time_left, tariffs, player_img, quartal, money, quota, target, crates, combo):
    # Decide color based on time left
    if time_left <= 6:
        timer_color = (255, 0, 0)  # red for last 5 seconds
    else:
        timer_color = (255, 255, 255)  # normal white

    if combo >= 3:
        combo_color = (255, 140, 0)
    else:
        combo_color = (255, 255, 255)


    WIN.blit(BG_2, (0, 0))


    target.draw(WIN)

    for crate in crates:
        crate.draw(WIN)

    pygame.draw.rect(WIN, (30, 30, 30), (0, 0, WIDTH, UI_HEIGHT))
    pygame.draw.line(WIN, (80, 80, 80), (0, UI_HEIGHT), (WIDTH, UI_HEIGHT), 2)


    quartal_text = FONT_BUTTONS.render(f"Quartal: {quartal}", True, "white")
    quota_text = FONT_BUTTONS.render("Ziel: $", True, "white")
    time_left_text = FONT_BUTTONS.render(f"Verbleibende Zeit: {max(0, int(time_left))}s", True, timer_color)
    combo_text = FONT_BUTTONS.render(f"Combo: {combo}", True, combo_color)

    WIN.blit(quartal_text, (125, 20))
    WIN.blit(quota_text, (550, 20))
    WIN.blit(time_left_text, (1450, 20))
    WIN.blit(combo_text, (1150, 20))
    draw_quota_bar(money,quota)

    img_rect = player_img.get_rect(midbottom=player.midbottom)
    WIN.blit(player_img, img_rect.topleft)

    for tariff in tariffs:
        WIN.blit(TARIFF_LIGHT_RED, (tariff.x, tariff.y))

    # --- Selection Bar ---
    bar_y = HEIGHT - 55

    for i, img in enumerate(CRATE_IMAGES):
        x_pos = WIDTH // 2 - 120 + i * 120

        border_color = (255, 255, 0) if i == selected_crate else (100, 100, 100)

        pygame.draw.rect(WIN, border_color, (x_pos, bar_y, 50, 50), 3)
        WIN.blit(img, (x_pos + 5, bar_y + 5))




def draw_menu():
    highscores = load_highscores()
    WIN.blit(BG, (0, 0))
    title = FONT_TITLE.render("Wähle dein Szenario", True, "black")
    WIN.blit(title, (WIDTH//2 - title.get_width()//2, 200))

    pygame.draw.rect(WIN, "red", scenario_button1)
    pygame.draw.rect(WIN, "blue", scenario_button2)

    text1 = FONT_BUTTONS.render("Große Einschränkungen des weltweiten Handels", True, "white")
    text2 = FONT_BUTTONS.render("Weitgehend reibungsloser weltweiter Handel", True, "white")
    high_score_text1 = FONT_BUTTONS.render(f"Highscore: {highscores['mode1']}s", True, "black")
    high_score_text2 = FONT_BUTTONS.render(f"Highscore:Q {highscores['mode2']}", True, "black")

    WIN.blit(high_score_text1, (scenario_button1.x + 900, scenario_button1.y + 6 ))
    WIN.blit(high_score_text2, (scenario_button2.x + 900, scenario_button2.y + 6 ))
    WIN.blit(text1, (scenario_button1.x + 15, scenario_button1.y + 8))
    WIN.blit(text2, (scenario_button2.x + 15, scenario_button2.y + 8))

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
    bar_x = WIDTH // 2 - bar_width // 2  -120
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


def show_pdf(chosen_pdf):
    # Get the absolute path
    subprocess.run(["start", chosen_pdf], shell=True)  # Windows



#trivia function -------------------------------------
#------------------------------------------------------

def ask_trivia(questions):
    correct = 0
    font_question = pygame.font.SysFont("Arial", 40)
    font_question.set_underline(True)
    font_options = pygame.font.SysFont("Arial", 34)
    clock = pygame.time.Clock()

    for q_index, (question, options, correct_index) in enumerate(questions):
        answered = False
        selected = -1

        # --- Layout constants ---
        question_y = HEIGHT // 3
        spacing = 80  # pixels between options

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

            # --- Draw question ---
            question_surf = font_question.render(question, True, (255, 255, 255))
            question_x = WIDTH // 2 - question_surf.get_width() // 2
            WIN.blit(question_surf, (question_x, 250))

            # --- Draw options centered ---
            for i, option in enumerate(options):
                option_text = f"{i + 1}. {option}"
                option_surf = font_options.render(option_text, True, (200, 200, 200))
                option_x = WIDTH // 2 - option_surf.get_width() // 2
                option_y = question_y + 50 + i * spacing
                WIN.blit(option_surf, (option_x, option_y))

            # --- Draw progress indicator ---
            progress_text = f"Question {q_index + 1} of {len(questions)}"
            progress_surf = font_options.render(progress_text, True, (255, 255, 0))
            WIN.blit(progress_surf, (1600, 915))

            pygame.display.update()

        # --- Check answer and show feedback ---
        if selected == correct_index:
            correct += 1
            feedback_text = "Correct!"
            feedback_color = (0, 255, 0)
        else:
            feedback_text = f"Wrong! Correct answer: {options[correct_index]}"
            feedback_color = (255, 0, 0)

        # Display feedback for 2 seconds below options
        feedback_surf = font_options.render(feedback_text, True, feedback_color)
        feedback_x = WIDTH // 2 - feedback_surf.get_width() // 2
        feedback_y = question_y + 50 + len(options) * spacing + 20
        WIN.blit(feedback_surf, (feedback_x, feedback_y))
        pygame.display.update()
        pygame.time.delay(2000)

    return correct

#----------------------------------------------
#text

def show_messages_typewriter(messages, color=(255, 0, 0), letter_delay=50):

    font = pygame.font.SysFont("Arial", 28)

    for msg in messages:
        char_index = 0
        start_ticks = pygame.time.get_ticks()
        running = True

        while running:
            dt = pygame.time.Clock().tick(60)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return

            # Calculate how many letters to show based on elapsed time
            now = pygame.time.get_ticks()
            chars_to_show = min(len(msg), (now - start_ticks) // letter_delay)
            displayed_text = msg[:chars_to_show]

            # Draw background & text
            WIN.fill((0, 0, 0))  # Or your BG
            text_surf = font.render(displayed_text, True, color)
            WIN.blit(text_surf, (WIDTH//2 - text_surf.get_width()//2, HEIGHT//2))
            pygame.display.update()

            # Once all letters are shown, wait 1 second and move on
            if chars_to_show == len(msg) and now - start_ticks >= len(msg) * letter_delay + 1000:
                running = False

# ----------------------------
# Death messages per mode
# ----------------------------
def get_death_messages(mode):
    if mode == "mode1":
        return [
            "Du konntest den steigenden Zöllen nicht standhalten!",
            "Bilde dich fort um auf diesem Markt zu bestehen..."
        ]
    elif mode == "mode2":
        return [
            "Der globale Handel hat dich überrollt!",
            "Bilde dich fort um auf diesem Markt zu bestehen..."
        ]
    else:
        return ["Du bist gestorben!", "Versuche es erneut."]


# ----------------------------
# Revive function updated
# ----------------------------
last_pack = None

def revive_player(max_health, revive_packs, mode):
    global last_pack

    # Show mode-specific messages
    messages = get_death_messages(mode)
    show_messages_typewriter(messages, letter_delay=50)

    # Pick a pack different from last one
    available = [p for p in revive_packs if p != last_pack]
    chosen_pack = random.choice(available)
    last_pack = chosen_pack

    show_pdf(chosen_pack["pdf"])

    # Sample 3 random questions
    questions_pool = chosen_pack["questions"]
    num_questions = min(3, len(questions_pool))
    questions_to_ask = random.sample(questions_pool, num_questions)

    correct = ask_trivia(questions_to_ask)

    # Each correct question restores 1/3 of max health
    restored_health = max_health * (correct / 3)
    restored_health =  round(restored_health)

    return restored_health



#game over function -------------------------
#--------------------------------------------
def show_game_over_screen():
    WIN.blit(BG,(0,0))
    WIN.blit(TRUMP_IDLE,(WIDTH//2,100))
    dead_img_rect = PLAYER_DEAD.get_rect(midbottom=(WIDTH//2, HEIGHT//2 + 500))
    WIN.blit(PLAYER_DEAD, dead_img_rect.topleft)

    # Draw game over message
    font = pygame.font.SysFont("Arial", 36)
    msg = "Du wurdest von den steigenden Zöllen überwältigt!"
    text_surf = font.render(msg, True, (255, 0, 0))
    WIN.blit(text_surf, (WIDTH//2 - text_surf.get_width()//2, HEIGHT//2 - 50))

    pygame.display.update()
    pygame.time.delay(3000)  # wait 3 seconds before quitting

# Load highscores or create default if file doesn't exist
def load_highscores():
    if os.path.exists(HIGHSCORE_FILE):
        with open(HIGHSCORE_FILE, "r") as f:
            return json.load(f)
    else:
        # default highscores for mode1 and mode2
        return {"mode1": 0, "mode2": 0}

# Save highscores to file
def save_highscores(highscores):
    with open(HIGHSCORE_FILE, "w") as f:
        json.dump(highscores, f)


#---------------------------------------
#cutscenes
#---------------------------------------

# ----------------------------
# Opening Cutscene System
# ----------------------------

SEEN_CUTSCENES_FILE = "seen_cutscenes.json"


def load_seen_cutscenes():
    if os.path.exists(SEEN_CUTSCENES_FILE):
        with open(SEEN_CUTSCENES_FILE, "r") as f:
            return json.load(f)
    else:
        return {"mode1": False, "mode2": False}


def save_seen_cutscenes(data):
    with open(SEEN_CUTSCENES_FILE, "w") as f:
        json.dump(data, f)


def run_cutscene(slides):

    font = pygame.font.SysFont("Arial", 36)
    small_font = pygame.font.SysFont("Arial", 22)

    clock = pygame.time.Clock()

    # Fade in bars
    for i in range(30):
        WIN.fill((0, 0, 0))
        draw_letterbox(WIN, i / 30)
        pygame.display.update()
        clock.tick(60)

    fade_screen(fade_in=True)

    for slide in slides:

        images = []

        if slide.get("images"):
            for img_data in slide["images"]:
                img = pygame.image.load(img_data["path"]).convert_alpha()
                img = pygame.transform.scale(img, img_data["size"])
                images.append({
                    "surface": img,
                    "pos": img_data["pos"]
                })

        for line in slide["text"]:

            start_time = pygame.time.get_ticks()
            finished = False

            while not finished:
                dt = clock.tick(60)

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        return
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE:
                            finished = True
                        if event.key == pygame.K_ESCAPE:
                            return  # skip entire cutscene

                now = pygame.time.get_ticks()
                chars = min(len(line), (now - start_time) // 25)
                displayed_text = line[:chars]

                WIN.fill((25, 28, 35))

                # Draw image
                for img in images:
                    WIN.blit(img["surface"], img["pos"])

                # Draw text box background
                text_box_rect = pygame.Rect(
                    WIDTH // 6,
                    HEIGHT - 220,
                    WIDTH * 2 // 3,
                    140
                )
                pygame.draw.rect(WIN, (0, 0, 0), text_box_rect)
                pygame.draw.rect(WIN, (200, 200, 200), text_box_rect, 2)

                # Draw text
                text_surface = font.render(displayed_text, True, (255, 255, 255))
                WIN.blit(
                    text_surface,
                    (text_box_rect.centerx - text_surface.get_width() // 2,
                     text_box_rect.centery - text_surface.get_height() // 2 - 20)
                )

                hint = small_font.render("SPACE = next | ESC = skip", True, (160, 160, 160))
                bar_height = HEIGHT // 8
                hint_y = HEIGHT - bar_height - 25

                WIN.blit( hint,(1625 , hint_y))

                # Draw cinematic bars
                draw_letterbox(WIN, 1)

                pygame.display.update()

                if chars == len(line) and now - start_time > len(line) * 25 + 2350:
                    finished = True

        fade_screen(fade_in=False, duration=400)
        fade_screen(fade_in=True, duration=400)

    # Fade out bars smoothly
    for i in reversed(range(30)):
        WIN.fill((0, 0, 0))
        draw_letterbox(WIN, i / 30)
        pygame.display.update()
        clock.tick(60)

    #fade_screen(fade_in=False)

# ----------------------------
# Cinematic Bars
# ----------------------------

def draw_letterbox(surface, progress):

    max_bar_height = HEIGHT // 8
    current_height = int(max_bar_height * progress)

    # True black bars
    top_rect = pygame.Rect(0, 0, WIDTH, current_height)
    bottom_rect = pygame.Rect(0, HEIGHT - current_height, WIDTH, current_height)

    pygame.draw.rect(surface, (0, 0, 0), top_rect)
    pygame.draw.rect(surface, (0, 0, 0), bottom_rect)

    # Subtle cinematic separator lines
    if current_height > 0:
        pygame.draw.line(surface, (40, 40, 40),
                         (0, current_height),
                         (WIDTH, current_height), 2)

        pygame.draw.line(surface, (40, 40, 40),
                         (0, HEIGHT - current_height),
                         (WIDTH, HEIGHT - current_height), 2)


# ----------------------------
# Fade Effect
# ----------------------------

def fade_screen(fade_in=True, duration=600):
    clock = pygame.time.Clock()
    start_time = pygame.time.get_ticks()

    # Compute window area (between the cinematic bars)
    top_bar_height = HEIGHT // 8
    bottom_bar_height = HEIGHT // 8
    window_rect = pygame.Rect(
        0,
        top_bar_height,
        WIDTH,
        HEIGHT - top_bar_height - bottom_bar_height
    )

    # Create fade surface the size of the window area
    fade_surf = pygame.Surface((window_rect.width, window_rect.height))
    fade_surf.fill((0, 0, 0))

    while True:
        dt = clock.tick(60)
        now = pygame.time.get_ticks()
        elapsed = now - start_time
        progress = min(elapsed / duration, 1)

        # Calculate alpha for fade
        if fade_in:
            alpha = 255 - int(255 * progress)
        else:
            alpha = int(255 * progress)

        fade_surf.set_alpha(alpha)

        # Redraw background for the window area (optional: keep content behind if needed)
        # WIN.fill((25, 28, 35))  # Only if you want a background behind fade

        # Draw fade only inside window area
        WIN.blit(fade_surf, (window_rect.x, window_rect.y))

        # Draw cinematic bars on top so they stay solid
        draw_letterbox(WIN, 1)

        pygame.display.update()

        if progress >= 1:
            break

#---------------------------------------
#CLASSES
#---------------------------------------


#----------------------------------------
class MoneyBill(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        original_img = pygame.image.load("money.png").convert_alpha()
        self.image = pygame.transform.scale(original_img, (43, 43))

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
        self.normal_speed = 8
        self.speed = self.normal_speed

    def update(self):
        self.rect.y -= self.speed

    def draw(self, surface):
        surface.blit(self.image, self.rect)


#---------------------
#targets
#----------------------
class ExportTarget:
    def __init__(self, speed):
        # Load PNG instead of creating a red surface
        self.image = EXPORT_TARGET_IMG
        self.rect = self.image.get_rect()
        self.rect.y = 120

        self.base_speed = speed
        self.direction = 1   # 1 = right, -1 = left

        self.last_type = None
        self.repeat_count = 0
        self.max_repeats = 2

        self.new_request()

    def new_request(self):
        available_types = list(range(len(CRATE_IMAGES)))

        if self.repeat_count >= self.max_repeats and self.last_type is not None:
            available_types.remove(self.last_type)

        self.requested_type = random.choice(available_types)

        if self.requested_type == self.last_type:
            self.repeat_count += 1
        else:
            self.repeat_count = 1

        self.last_type = self.requested_type

        self.rect.x = random.randint(0, WIDTH - self.rect.width)

    def update(self):
        self.rect.x += self.base_speed * self.direction

        if self.rect.left <= 0:
            self.rect.left = 0
            self.direction = 1

        elif self.rect.right >= WIDTH:
            self.rect.right = WIDTH
            self.direction = -1

    def draw(self, surface):
        # Draw the PNG
        surface.blit(self.image, self.rect)

        # Draw requested crate icon above it
        crate_img = CRATE_IMAGES[self.requested_type]
        icon_rect = crate_img.get_rect(
            midbottom=(self.rect.centerx, max(self.rect.top - 5, UI_HEIGHT + crate_img.get_height()))
        )
        surface.blit(crate_img, icon_rect)

#--------------------------------------
#Lieferengpass
#-------------------------------------

class BottleneckZone:
    def __init__(self, y_pos):
        self.image = LIEFERENGPASS_IMG
        self.rect = self.image.get_rect(midtop=(WIDTH//2, y_pos))
        self.active = False        # starts invisible
        self.direction = 1         # 1 = right, -1 = left
        self.speed = 2             # horizontal movement speed

    def activate(self):
        self.active = True
        # Optionally randomize starting x
        self.rect.x = random.randint(0, WIDTH - self.rect.width)

    def deactivate(self):
        self.active = False

    def update(self):
        if not self.active:
            return
        # Move horizontally
        self.rect.x += self.speed * self.direction
        # Bounce off edges
        if self.rect.left <= 0:
            self.rect.left = 0
            self.direction = 1
        elif self.rect.right >= WIDTH:
            self.rect.right = WIDTH
            self.direction = -1

    def draw(self, surface):
        if self.active:
            surface.blit(self.image, self.rect)
            # Draw text "Lieferengpass" in red on top
            font = pygame.font.SysFont("Arial", 28, bold=True)
            text_surf = font.render("Lieferengpass", True, (255, 0, 0))
            text_rect = text_surf.get_rect(center=self.rect.center)
            surface.blit(text_surf, text_rect)

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

    # ------------------------
    # Dash System
    # ------------------------
    dash_speed = 20
    dash_duration = 150  # milliseconds
    dash_cooldown = 1500  # milliseconds

    is_dashing = False
    dash_timer = 0
    last_dash_time = 0
    invincible = False

    player_health = 3
    max_health = 3

    dead = False
    first_death = True

    money_bills = pygame.sprite.Group()
    money_timer = 0
    money_interval = random.randint(14000, 20000)

    explosions = []

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
        pygame.transform.scale(pygame.image.load(f"trump_{i}.png").convert_alpha(), (TRUMP_WIDTH, TRUMP_HEIGHT))
        for i in range(1, 4)
    ]
    TRUMP_ANIM_SPEED = 150  # ms per frame
    trump_anim_index = 0
    trump_anim_timer = 0
    is_throwing = False
    trigger_throw = False
    current_trump_img = TRUMP_FRAMES[0]

    # New spawn‑timing variables
    spawn_pending = False
    spawn_ready_time = 0

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
    # Before the loop
    TARIFF_INTERVAL = 1500  # milliseconds
    last_tariff_spawn = 0

    while True:
        dt = clock.tick(60)
        elapsed_time = time.time() - start_time
        now = pygame.time.get_ticks()  # current time in ms
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
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LSHIFT:
                    now = pygame.time.get_ticks()
                    if now - last_dash_time > dash_cooldown:
                        is_dashing = True
                        invincible = True
                        dash_timer = 0
                        last_dash_time = now
            if event.type == pygame.USEREVENT + 1:
                invincible = False  # reset after 200ms

        # ------------------------
        # Player Input
        # ------------------------
        keys = pygame.key.get_pressed()
        moving = False

        current_speed = dash_speed if is_dashing else player_speed

        if keys[pygame.K_a] and player.x - current_speed >= 0:
            player.x -= current_speed
            facing = "left"
            moving = True

        if keys[pygame.K_d] and player.x + current_speed + player.width <= WIDTH:
            player.x += current_speed
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

        player_img_rect = current_player_img.get_rect(midbottom=player.midbottom)

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

        #----------------
        #dash timer
        if is_dashing:
            dash_timer += dt
            if dash_timer >= dash_duration:
                is_dashing = False
                invincible = False

        # ------------------------
        # Trump Movement
        # ------------------------
        if direction_timer > 1000:
            TRUMP_VEL = random.choice([-7, -5, 5, 7])
            direction_timer = 0

        trump.x += TRUMP_VEL
        if trump.x <= 0 or trump.x + TRUMP_WIDTH >= WIDTH:
            TRUMP_VEL *= -1

        # ------------------------
        # Trump Throw Animation Update
        # ------------------------
        if trigger_throw and not is_throwing:
            # Start a new throw animation
            is_throwing = True
            trump_anim_index = 0
            trump_anim_timer = 0
            trigger_throw = False

        if is_throwing:
            trump_anim_timer += dt
            if trump_anim_timer >= TRUMP_ANIM_SPEED:
                trump_anim_index += 1
                trump_anim_timer = 0
                if trump_anim_index >= len(TRUMP_FRAMES):
                    # Animation finished
                    is_throwing = False
                    trump_anim_index = 0  # reset to idle for next time
            # Set current image based on index (0=idle,1=arms up,2=arms down)
            current_trump_img = TRUMP_FRAMES[trump_anim_index]
        else:
            # Not throwing: use idle frame
            current_trump_img = TRUMP_FRAMES[0]

        # ------------------------
        # Tariff Spawning (with throw trigger)
        # ------------------------
        now = pygame.time.get_ticks()
        if now - last_tariff_spawn > TARIFF_INTERVAL:
            last_tariff_spawn = now
            trigger_throw = True  # start animation when spawning

            # Spawn 2–4 normal tariffs
            for _ in range(random.randint(3, 4)):
                tariff_x = random.randint(0, WIDTH - TARIFF_WIDTH_1)
                tariff_y = TRUMP_HEIGHT
                tariffs.append({
                    "rect": pygame.Rect(tariff_x, tariff_y, TARIFF_WIDTH_1, TARIFF_HEIGHT_1),
                    "type": "normal",
                    "shockwave": False,
                    "img": TARIFF_LIGHT_RED,
                    "mask": TARIFF_MASK
                })

            # Spawn 1–2 special tariffs
            for _ in range(random.randint(1, 2)):
                special_type = random.choices(["fast", "heavy"], weights=[50, 50])[0]
                if special_type == "fast":
                    width, height, img, mask = TARIFF_WIDTH_3, TARIFF_HEIGHT_3, TARIFF_ORANGE, pygame.mask.from_surface(
                        TARIFF_ORANGE)
                else:  # heavy
                    width, height, img, mask = TARIFF_WIDTH_2, TARIFF_HEIGHT_2, TARIFF_DARK_RED, pygame.mask.from_surface(
                        TARIFF_DARK_RED)

                tariff_x = random.randint(0, WIDTH - width)
                tariff_y = TRUMP_HEIGHT
                tariffs.append({
                    "rect": pygame.Rect(tariff_x, tariff_y, width, height),
                    "type": special_type,
                    "shockwave": False,
                    "img": img,
                    "mask": mask
                })

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
            rect = tariff["rect"]
            t_type = tariff["type"]

            if t_type == "fast":
                rect.y += tariff_speed * 1.5 * difficulty
            elif t_type == "heavy":
                rect.y += tariff_speed * 0.6 * difficulty
            else:
                rect.y += tariff_speed * difficulty

            if t_type == "heavy" and rect.bottom >= GAME_BOTTOM_1 and not tariff["shockwave"]:
                tariff["shockwave"] = True
                explosions.append({
                    "x": rect.centerx,
                    "y": rect.bottom,
                    "radius": 0,
                    "max_radius": 150,
                    "duration": 300,  # ms
                    "elapsed": 0
                })
                tariffs.remove(tariff)
                continue

            if rect.y > HEIGHT - 60:
                tariffs.remove(tariff)
                continue

            offset = (rect.x - player_img_rect.x, rect.y - player_img_rect.y)
            if not invincible and current_mask.overlap(tariff["mask"], offset):
                player_health -= 1
                tariffs.remove(tariff)
                pygame.time.delay(30)
                if player_health <= 0:
                    dead = True
                break

        # ------------------------
        # Money Pickup Collision
        # ------------------------
        for bill in money_bills:
            if player.colliderect(bill.rect):
                player_health += 1
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

        # Update explosions
        for exp in explosions[:]:
            exp["elapsed"] += dt
            exp["radius"] = exp["max_radius"] * (exp["elapsed"] / exp["duration"])
            alpha = max(0, 255 * (1 - exp["elapsed"] / exp["duration"]))
            surface = pygame.Surface((exp["radius"] * 2, exp["radius"] * 2), pygame.SRCALPHA)
            pygame.draw.circle(surface, (255, 50, 0, int(alpha)), (int(exp["radius"]), int(exp["radius"])),
                               int(exp["radius"]))
            WIN.blit(surface, (exp["x"] - exp["radius"], exp["y"] - exp["radius"]))

            # Shockwave damage
            player_center = player.center
            dx = player_center[0] - exp["x"]
            dy = player_center[1] - exp["y"]
            distance = (dx ** 2 + dy ** 2) ** 0.5
            if distance <= exp["radius"] and not invincible:
                player_health -= 1
                invincible = True
                pygame.time.set_timer(pygame.USEREVENT + 1, 200)

            if exp["elapsed"] >= exp["duration"]:
                explosions.remove(exp)
            if player_health <= 0:
                dead = True

            break

        pygame.display.update()

        if dead:
            if first_death:
                first_death = False
                pause_start = time.time()
                restored_health = revive_player(max_health, MODE1_REVIVES, "mode1")
                pause_duration = time.time() - pause_start
                start_time += pause_duration

                if restored_health > 0:
                    player_health = restored_health
                    dead = False
                    continue
                else:
                    show_game_over_screen()
                    highscores = load_highscores()
                    if elapsed_time > highscores["mode1"]:
                        highscores["mode1"] = round(elapsed_time)
                        save_highscores(highscores)
                    return "menu"

            else:
                show_game_over_screen()
                highscores = load_highscores()
                if elapsed_time > highscores["mode1"]:
                    highscores["mode1"] = round(elapsed_time)
                    save_highscores(highscores)
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

    base_crate_speed = 8
    base_target_speed = 4

    player_vel_y = 0
    gravity = 0.5
    jump_strength = -10
    on_ground = True

    player_health = 3
    max_health = 3

    dash_speed = 20
    dash_duration = 150  # milliseconds
    dash_cooldown = 1500  # milliseconds

    is_dashing = False
    dash_timer = 0
    last_dash_time = 0
    invincible = False

    dead = False
    first_death = True

    combo = 0
    base_reward = 25
    base_multiplier_cap = 2.0  # starting max multiplier

    bottleneck = BottleneckZone(y_pos=HEIGHT // 2)  # adjust Y as you like
    bottleneck_timer = 0
    bottleneck_interval = random.randint(10000, 20000)  # how often it appears
    bottleneck_duration = 8000  # ms
    bottleneck_active_time = 0

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
    target = ExportTarget(base_target_speed)
    shoot_cooldown = 500  # milliseconds
    last_shot = 0
    global selected_crate

    while True:
        dt = clock.tick(60)
        tariff_count += dt
        bottleneck_timer += dt
        elapsed_time = time.time() - quartal_start_time
        time_left = quartal_duration - elapsed_time
        multiplier_cap = base_multiplier_cap + (quartal - 1) * 0.5
        crate_speed = min(base_crate_speed + (quartal - 1) * 0.5, 7)
        target_speed = min(base_target_speed + (quartal - 1) * 0.4, 8)
        target.base_speed = target_speed


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
                selected_crate -= event.y
                selected_crate %= len(CRATE_IMAGES)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    selected_crate = 0
                if event.key == pygame.K_2 and len(CRATE_IMAGES) > 1:
                    selected_crate = 1
                if event.key == pygame.K_3 and len(CRATE_IMAGES) > 2:
                    selected_crate = 2

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LSHIFT:
                    now = pygame.time.get_ticks()
                    if now - last_dash_time > dash_cooldown:
                        is_dashing = True
                        invincible = True
                        dash_timer = 0
                        last_dash_time = now

        # ------------------------
        # Player Input
        # ------------------------
        keys = pygame.key.get_pressed()
        moving = False

        current_speed = dash_speed if is_dashing else player_speed

        if keys[pygame.K_a] and player.x - current_speed >= 0:
            player.x -= current_speed
            facing = "left"
            moving = True

        if keys[pygame.K_d] and player.x + current_speed + player.width <= WIDTH:
            player.x += current_speed
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

        if is_dashing:
            dash_timer += dt
            if dash_timer >= dash_duration:
                is_dashing = False
                invincible = False


        # ------------------------
        # Tariff Spawning
        # ------------------------


        if tariff_count > tariff_interval:
            for _ in range(2):
                tariff_x = random.randint(0, WIDTH - TARIFF_WIDTH_1)
                tariff_y = 100
                tariffs.append(pygame.Rect(tariff_x, tariff_y, TARIFF_WIDTH_1, TARIFF_HEIGHT_1))

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
            if not invincible and current_mask.overlap(TARIFF_MASK, offset):
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
            quota += 50
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
                combo = 0
                crates.remove(crate)

        # Update target
        target.update()


        #crate collision
        for crate in crates[:]:
            if bottleneck.active and crate.rect.colliderect(bottleneck.rect):
                crate.speed = crate.normal_speed * 0.4  # slow it
                crate.rect.x += random.randint(-2, 2)  # wiggle
            else:
                crate.speed = crate.normal_speed  # reset normal speed

            # Then check target collision
            if crate.rect.colliderect(target.rect):
                if crate.type == target.requested_type:
                    combo += 1
                    # apply combo multiplier
                    multiplier = 1 + min(combo * 0.25, multiplier_cap)
                    money += int(base_reward * multiplier)
                    target.new_request()
                else:
                    combo = 0
                    money -= 10  # optional penalty
                crates.remove(crate)

        # Only start appearing in quartal 3+
        if quartal >= 3:
            if not bottleneck.active and bottleneck_timer > bottleneck_interval:
                bottleneck.activate()
                bottleneck_active_time = 0
                bottleneck_timer = 0

            if bottleneck.active:
                bottleneck_active_time += dt
                if bottleneck_active_time > bottleneck_duration:
                    bottleneck.deactivate()
                    bottleneck_timer = 0
                    bottleneck_interval = random.randint(15000, 25000)  # next random spawn

        # ------------------------
        # Draw Everything
        # ------------------------

        draw_2(player,time_left, tariffs, current_player_img, quartal, money, quota,target, crates, combo)
        bottleneck.update()
        bottleneck.draw(WIN)
        draw_health_bar(player, player_health, max_health)
        pygame.display.update()

        if dead:
            if first_death:
                first_death = False
                # Pause game for revival
                restored_health = revive_player(max_health, MODE2_REVIVES,"mode2")

                if restored_health > 0:
                    player_health = restored_health
                    dead = False
                    # RESTART quartal timer so player gets full time after revival
                    quartal_start_time = time.time()
                    continue
                else:
                    show_game_over_screen()
                    highscores = load_highscores()
                    if quartal > highscores["mode2"]:
                        highscores["mode2"] = quartal
                        save_highscores(highscores)
                    return "menu"

            else:
                # SECOND DEATH → permanent game over
                show_game_over_screen()

                highscores = load_highscores()
                if quartal > highscores["mode2"]:
                    highscores["mode2"] = quartal
                    save_highscores(highscores)

                return "menu"

# ----------------------------
# Individual scenario functions
# ----------------------------
def game_mode1():
    run_cutscene(MODE1_CUTSCENE)
    return run_mode_1(player_speed=8, tariff_speed=6)

def game_mode2():
    run_cutscene(MODE2_CUTSCENE)
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