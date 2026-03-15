import pygame
import time
import random
import os
import json
import sys

pygame.font.init()

# ----------------------------
# Helper to find resources (for PyInstaller)
# ----------------------------
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def get_writable_path(filename):
    if getattr(sys, 'frozen', False):
        # Running as bundled exe – use the folder containing the exe
        base_path = os.path.dirname(sys.executable)
    else:
        # Running in development – use the current working directory
        base_path = os.path.abspath(".")
    return os.path.join(base_path, filename)
# ----------------------------
# Constants & Setup
# ----------------------------
WIN = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WIDTH, HEIGHT = WIN.get_size()
# After WIDTH, HEIGHT = WIN.get_size()
BASE_WIDTH, BASE_HEIGHT = 1920, 1080
SCALE_X = WIDTH / BASE_WIDTH
SCALE_Y = HEIGHT / BASE_HEIGHT
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

# Fonts – using SysFont for simplicity (system fonts may vary)
# For better portability, include .ttf files and use pygame.font.Font(resource_path("font.ttf"), size)
FONT_TITLE = pygame.font.SysFont("Times New Roman", 50, italic=True)
FONT_TITLE.set_underline(True)
FONT_BUTTONS = pygame.font.SysFont("Times New Roman", 40)

# Images – load with resource_path
BG = pygame.transform.scale(pygame.image.load(resource_path("bg1.png")), (WIDTH, HEIGHT))
BG_2 = pygame.transform.scale(pygame.image.load(resource_path("BG_6.png")), (WIDTH, HEIGHT))
LIEFERENGPASS_IMG = pygame.image.load(resource_path("Lieferengpass.png")).convert_alpha()
EXPORT_TARGET_IMG = pygame.transform.scale(
    pygame.image.load(resource_path("Flag.png")).convert_alpha(),
    (220, 80)
)
HIGHSCORE_FILE = get_writable_path("highscores.json")   # will be created in the same folder as the exe

# Load tariff sprites
TARIFF_LIGHT_RED = pygame.image.load(resource_path("tariff_light_red.png")).convert_alpha()
TARIFF_DARK_RED = pygame.image.load(resource_path("tariff_dark_red.png")).convert_alpha()
TARIFF_ORANGE = pygame.image.load(resource_path("tariff_orange.png")).convert_alpha()

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
    pygame.image.load(resource_path("trump_1.png")).convert_alpha(),
    (TRUMP_WIDTH, TRUMP_HEIGHT)
)

TRUMP_THROW_UP = pygame.transform.scale(
    pygame.image.load(resource_path("trump_2.png")).convert_alpha(),
    (TRUMP_WIDTH, TRUMP_HEIGHT)
)

TRUMP_THROW_DOWN = pygame.transform.scale(
    pygame.image.load(resource_path("trump_3.png")).convert_alpha(),
    (TRUMP_WIDTH, TRUMP_HEIGHT)
)

TRUMP_FRAMES = [
    pygame.transform.scale(
        pygame.image.load(resource_path(f"trump_{i}.png")),
        (TRUMP_WIDTH, TRUMP_HEIGHT)
    )
    for i in range(1, 4)
]

PLAYER_IDLE = pygame.transform.scale(
    pygame.image.load(resource_path("player_idle.png")),
    (PLAYER_WIDTH, PLAYER_HEIGHT)
)

PLAYER_WALK_RIGHT = [
    pygame.transform.scale(
        pygame.image.load(resource_path(f"Player_walking_R_{i}.png")),
        (PLAYER_WIDTH, PLAYER_HEIGHT)
    )
    for i in range(1, 7)
]

PLAYER_WALK_LEFT = [
    pygame.transform.scale(
        pygame.image.load(resource_path(f"Player_walking_L_{i}.png")),
        (PLAYER_WIDTH, PLAYER_HEIGHT)
    )
    for i in range(1, 7)
]

PLAYER_DEAD = pygame.transform.scale(
    pygame.image.load(resource_path("player_dead.png")),
    (PLAYER_WIDTH, PLAYER_HEIGHT)
)

TARIFF_MASK = pygame.mask.from_surface(TARIFF_LIGHT_RED)

# Game States
MENU = "menu"
GAME1 = "game1"
GAME2 = "game2"

# Buttons
title_button = pygame.Rect(WIDTH // 2 - 200, 200, 400, 60)
scenario_button1 = pygame.Rect(WIDTH // 2 - 400, HEIGHT // 2 - 100, 850, 60)
scenario_button2 = pygame.Rect(WIDTH // 2 - 400, HEIGHT // 2 +50, 850, 60)

# crates
CRATE_IMAGES = [
    pygame.transform.scale(pygame.image.load(resource_path("crate_1.png")).convert_alpha(), (40, 40)),
    pygame.transform.scale(pygame.image.load(resource_path("crate_2.png")).convert_alpha(), (40, 40)),
    pygame.transform.scale(pygame.image.load(resource_path("crate_3.png")).convert_alpha(), (40, 40)),
]

# --- Crate System ---
crate_types = [
    {"name": "oil", "color": (30, 30, 30)},
    {"name": "steel", "color": (160, 160, 160)},
    {"name": "food", "color": (50, 200, 50)}
]

selected_crate = 0
requested_crate = 0

# ------------------------------------------
# PDFS & Fragen (paths are relative, will be resolved with resource_path later)
# ------------------------------------------
MODE1_REVIVES = [
    {
        "title": "title1",
        "pdf": "pdf-sample_0.pdf",
        "questions": [
            ("What is a tariff?", ["A tax", "A trade agreement", "A subsidy"], 0),
            ("Who sets tariffs?", ["Government", "Banks", "Companies"], 0),
            ("how old am i?", ["18", "19", "17"], 2),
            ("how old is Tiny?", ["3", "4", "5"], 1)
        ]
    },
    {
        "title": "title2",
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
        "title": "title1",
        "pdf": "pdf-sample_1.pdf",
        "questions": [
            ("What is export?", ["Sell abroad", "Buy abroad", "Tax goods"], 0),
            ("Exports increase GDP?", ["Yes", "No", "Only locally"], 0),
            ("how old am i?", ["18", "19", "17"], 2),
            ("how old is Tiny?", ["3", "4", "5"], 1)
        ]
    },
    {
        "title": "title2",
        "pdf": "pdf-sample_1.pdf",
        "questions": [
            ("What does GDP stand for?", ["Gross Domestic Product", "Global Debt Plan", "General Trade Policy"], 0),
            ("GDP measures?", ["Economic output", "Population", "Inflation only"], 0),
            ("how old am i?", ["18", "19", "17"], 2),
            ("how old is Tiny?", ["3", "4", "5"], 1)
        ]
    }
]

# --------------------------------------
# cutscene text & Bilder (paths will be resolved when used)
# --------------------------------------
MODE1_CUTSCENE = [
    {
        "text": ["Der internationale Handel steht kurz vor dem Zusammenbruch..."],
        "images": [
            {
                "path": "cutscene_trade_down.png",
                "size": (500,400),
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
        "text": ["Du bist Teil eines kleinen deutschen Exportunternehmens"],
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
        "text": ["Ihr exportiert hauptsächlich in die USA."],
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
                "size": (500, 600),
                "pos": (WIDTH // 2 , HEIGHT // 2 - 350)
            },
        ]
    },
    {
        "text": ["Du bist Teil eines kleinen deutschen Exportunternehmens"],
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
        "text": ["Ihr exportiert hauptsächlich in die USA."],
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
        "text": ["Leider hast du einen sehr strengen Chef, der hohe Quartalziele setzt..."],
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

# ----------------------------------------
# FUNCTIONS
# ----------------------------------------

# Drawing functions (unchanged except where they access global assets)
def draw_1(player, elapsed_time, tariffs, trump, player_img, current_trump_img):
    WIN.blit(BG, (0, 0))
    time_text = FONT_BUTTONS.render(f"Zeit: {round(elapsed_time)}s", 1, "black")
    WIN.blit(time_text, (1700, 10))

    img_rect = player_img.get_rect(midbottom=player.midbottom)
    WIN.blit(player_img, img_rect.topleft)

    WIN.blit(current_trump_img, (trump.x, trump.y))

    for tariff in tariffs:
        WIN.blit(tariff["img"], (tariff["rect"].x, tariff["rect"].y))

def draw_2(player, time_left, tariffs, player_img, quartal, money, quota, target, crates, combo):
    # Timer color
    if time_left <= 6:
        timer_color = (255, 0, 0)
    else:
        timer_color = (255, 255, 255)

    # Combo color
    if combo >= 3:
        combo_color = (255, 140, 0)
    else:
        combo_color = (255, 255, 255)

    WIN.blit(BG_2, (0, 0))
    target.draw(WIN)
    for crate in crates:
        crate.draw(WIN)

    # UI background bar
    pygame.draw.rect(WIN, (30, 30, 30), (0, 0, WIDTH, UI_HEIGHT))
    pygame.draw.line(WIN, (80, 80, 80), (0, UI_HEIGHT), (WIDTH, UI_HEIGHT), 2)

    # Scaled positions for texts
    quartal_x = int(125 * SCALE_X)
    quartal_y = int(20 * SCALE_Y)
    quota_x = int(550 * SCALE_X)
    quota_y = int(20 * SCALE_Y)
    combo_x = int(1150 * SCALE_X)
    combo_y = int(20 * SCALE_Y)
    time_x = int(1450 * SCALE_X)
    time_y = int(20 * SCALE_Y)

    quartal_text = FONT_BUTTONS.render(f"Quartal: {quartal}", True, "white")
    quota_text = FONT_BUTTONS.render("Ziel: $", True, "white")
    time_left_text = FONT_BUTTONS.render(f"Verbleibende Zeit: {max(0, int(time_left))}s", True, timer_color)
    combo_text = FONT_BUTTONS.render(f"Combo: {combo}", True, combo_color)

    WIN.blit(quartal_text, (quartal_x, quartal_y))
    WIN.blit(quota_text, (quota_x, quota_y))
    WIN.blit(time_left_text, (time_x, time_y))
    WIN.blit(combo_text, (combo_x, combo_y))

    draw_quota_bar(money, quota)

    # Player
    img_rect = player_img.get_rect(midbottom=player.midbottom)
    WIN.blit(player_img, img_rect.topleft)

    # Tariffs (positions already handled in game logic, so just blit)
    for tariff in tariffs:
        WIN.blit(TARIFF_LIGHT_RED, (tariff.x, tariff.y))

    # --- Selection Bar (perfectly centered) ---
    bar_y = HEIGHT - int(55 * SCALE_Y)  # distance from bottom
    slot_size = int(50 * SCALE_X)  # outer slot size (including border)
    slot_spacing = int(120 * SCALE_X)  # space between slot centers
    start_x = WIDTH // 2 - (len(CRATE_IMAGES) * slot_spacing) // 2

    for i, img in enumerate(CRATE_IMAGES):
        x_pos = start_x + i * slot_spacing
        slot_rect = pygame.Rect(x_pos, bar_y, slot_size, slot_size)

        # Draw slot border (3px thick)
        border_color = (255, 255, 0) if i == selected_crate else (100, 100, 100)
        pygame.draw.rect(WIN, border_color, slot_rect, 3)

        # Inner area: remove border thickness (3px on each side)
        inner_rect = slot_rect.inflate(-6, -6)  # because 3px left + 3px right = 6px total reduction

        # Scale crate image to fit nicely inside inner area (90% of inner size leaves a margin)
        target_size = int(inner_rect.width * 0.8), int(inner_rect.height * 0.8)
        img_scaled = pygame.transform.scale(img, target_size)

        # Center the scaled image in the inner rectangle
        img_rect = img_scaled.get_rect(center=inner_rect.center)
        WIN.blit(img_scaled, img_rect)


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

    WIN.blit(high_score_text1, (scenario_button1.x + 900, scenario_button1.y + 6))
    WIN.blit(high_score_text2, (scenario_button2.x + 900, scenario_button2.y + 6))
    WIN.blit(text1, (scenario_button1.x + 15, scenario_button1.y + 8))
    WIN.blit(text2, (scenario_button2.x + 15, scenario_button2.y + 8))

    pygame.display.update()

def draw_health_bar(player_rect, health, max_health):
    bar_width = 40
    bar_height = 6
    offset_y = 10
    health_ratio = health / max_health
    bar_x = player_rect.centerx - bar_width // 2
    bar_y = player_rect.top - offset_y
    bg_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
    pygame.draw.rect(WIN, (180, 0, 0), bg_rect)
    fg_rect = pygame.Rect(bar_x, bar_y, int(bar_width * health_ratio), bar_height)
    pygame.draw.rect(WIN, (0, 200, 0), fg_rect)
    pygame.draw.rect(WIN, (0, 0, 0), bg_rect, 1)

def draw_quota_bar(money, quota):
    bar_width = int(300 * SCALE_X)
    bar_height = int(20 * SCALE_Y)
    bar_x = WIDTH // 2 - bar_width // 2 - int(120 * SCALE_X)
    bar_y = int(35 * SCALE_Y)

    progress = min(money / quota, 1)

    bg_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
    pygame.draw.rect(WIN, (50, 50, 50), bg_rect)

    fg_width = int(bar_width * progress)
    fg_rect = pygame.Rect(bar_x, bar_y, fg_width, bar_height)
    pygame.draw.rect(WIN, (50, 200, 50), fg_rect)

    pygame.draw.rect(WIN, (0,0,0), bg_rect, 2)

def show_pdf(chosen_pdf):
    """Open PDF with default viewer – uses resource_path to locate the file."""
    full_path = resource_path(chosen_pdf)
    os.startfile(full_path)   # Windows only – for cross‑platform use webbrowser.open()

def ask_trivia(questions):
    correct = 0
    font_question = pygame.font.SysFont("Arial", 40)
    font_question.set_underline(True)
    font_options = pygame.font.SysFont("Arial", 34)
    clock = pygame.time.Clock()

    for q_index, (question, options, correct_index) in enumerate(questions):
        answered = False
        selected = -1
        question_y = HEIGHT // 3
        spacing = 80

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
            question_surf = font_question.render(question, True, (255, 255, 255))
            question_x = WIDTH // 2 - question_surf.get_width() // 2
            WIN.blit(question_surf, (question_x, 250))
            for i, option in enumerate(options):
                option_text = f"{i + 1}. {option}"
                option_surf = font_options.render(option_text, True, (200, 200, 200))
                option_x = WIDTH // 2 - option_surf.get_width() // 2
                option_y = question_y + 50 + i * spacing
                WIN.blit(option_surf, (option_x, option_y))
            progress_text = f"Question {q_index + 1} of {len(questions)}"
            progress_surf = font_options.render(progress_text, True, (255, 255, 0))
            WIN.blit(progress_surf, (1600, 915))
            pygame.display.update()

        if selected == correct_index:
            correct += 1
            feedback_text = "Correct!"
            feedback_color = (0, 255, 0)
        else:
            feedback_text = f"Wrong! Correct answer: {options[correct_index]}"
            feedback_color = (255, 0, 0)

        feedback_surf = font_options.render(feedback_text, True, feedback_color)
        feedback_x = WIDTH // 2 - feedback_surf.get_width() // 2
        feedback_y = question_y + 50 + len(options) * spacing + 20
        WIN.blit(feedback_surf, (feedback_x, feedback_y))
        pygame.display.update()
        pygame.time.delay(2000)

    return correct

def show_messages_typewriter(messages, color=(255, 0, 0), letter_delay=50):
    font = pygame.font.SysFont("Arial", 28)
    for msg in messages:
        start_ticks = pygame.time.get_ticks()
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
            now = pygame.time.get_ticks()
            chars_to_show = min(len(msg), (now - start_ticks) // letter_delay)
            displayed_text = msg[:chars_to_show]
            WIN.fill((0, 0, 0))
            text_surf = font.render(displayed_text, True, color)
            WIN.blit(text_surf, (WIDTH//2 - text_surf.get_width()//2, HEIGHT//2))
            pygame.display.update()
            if chars_to_show == len(msg) and now - start_ticks >= len(msg) * letter_delay + 1000:
                running = False

def get_death_messages(mode):
    if mode == "mode1":
        return [
            "Du konntest den steigenden Zöllen nicht standhalten!",
            "Bilde dich fort um auf diesem Markt zu bestehen..."
        ]
    elif mode == "mode2":
        return [
            "Du konntest die Quartal-Ziele nicht erfüllen!",
            "Bilde dich fort um auf diesem Markt zu bestehen..."
        ]
    else:
        return ["Du bist gestorben!", "Versuche es erneut."]

def get_game_over_message(mode):
    messages = {
        "mode1": "Du wurdest von den steigenden Zöllen überwältigt!",
        "mode2": "Du konntest die Quartal-Ziele nicht erfüllen!"
    }
    return messages.get(mode, "Du bist gestorben!")

last_pack = None

def choose_article(revive_packs):
    font_title = pygame.font.SysFont("Arial", 42)
    font_option = pygame.font.SysFont("Arial", 34)
    clock = pygame.time.Clock()

    selected_pack = None

    while selected_pack is None:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None

            if event.type == pygame.KEYDOWN:
                if pygame.K_1 <= event.key <= pygame.K_9:
                    index = event.key - pygame.K_1
                    if index < len(revive_packs):
                        selected_pack = revive_packs[index]

        WIN.fill((40,40,40))

        title = font_title.render("Wähle den Text, den du lesen möchtest:", True, (255,255,255))
        WIN.blit(title, (WIDTH//2 - title.get_width()//2, 200))

        for i, pack in enumerate(revive_packs):
            option_text = f"{i+1}. {pack['title']}"
            surf = font_option.render(option_text, True, (200,200,200))
            WIN.blit(surf, (WIDTH//2 - surf.get_width()//2, 320 + i*60))

        hint = font_option.render("Drücke die jeweilige Zahl zum Auswählen", True, (255,255,0))
        WIN.blit(hint, (WIDTH//2 - hint.get_width()//2, HEIGHT - 200))

        pygame.display.update()

    return selected_pack

def revive_player(max_health, revive_packs, mode):
    global last_pack

    messages = get_death_messages(mode)
    show_messages_typewriter(messages, letter_delay=50)

    chosen_pack = choose_article(revive_packs)
    last_pack = chosen_pack
    show_pdf(chosen_pack["pdf"])

    questions_pool = chosen_pack["questions"]
    num_questions = min(3, len(questions_pool))
    questions_to_ask = random.sample(questions_pool, num_questions)

    correct = ask_trivia(questions_to_ask)

    restored_health = max_health * (correct / 3)
    restored_health = round(restored_health)

    return restored_health

def show_game_over_screen(mode):
    WIN.blit(BG, (0,0))
    WIN.blit(TRUMP_IDLE, (WIDTH//2,100))
    dead_img_rect = PLAYER_DEAD.get_rect(midbottom=(WIDTH//2, GAME_BOTTOM_2))
    WIN.blit(PLAYER_DEAD, dead_img_rect.topleft)

    msg = get_game_over_message(mode)
    font = pygame.font.SysFont("Arial", 36)
    text_surf = font.render(msg, True, (255, 0, 0))
    WIN.blit(text_surf, (WIDTH//2 - text_surf.get_width()//2, HEIGHT//2 - 50))

    pygame.display.update()
    pygame.time.delay(3000)

def load_highscores():
    if os.path.exists(HIGHSCORE_FILE):
        with open(HIGHSCORE_FILE, "r") as f:
            return json.load(f)
    else:
        return {"mode1": 0, "mode2": 0}

def save_highscores(highscores):
    with open(HIGHSCORE_FILE, "w") as f:
        json.dump(highscores, f)

SEEN_CUTSCENES_FILE = get_writable_path("seen_cutscenes.json")

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

    # Reference resolution (your design target)
    BASE_WIDTH, BASE_HEIGHT = 1920, 1080
    scale_x = WIDTH / BASE_WIDTH
    scale_y = HEIGHT / BASE_HEIGHT

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
                img = pygame.image.load(resource_path(img_data["path"])).convert_alpha()
                orig_size = img_data["size"]
                new_size = (int(orig_size[0] * scale_x), int(orig_size[1] * scale_y))
                img = pygame.transform.scale(img, new_size)
                pos = img_data["pos"]  # already computed for current screen
                images.append({"surface": img, "pos": pos})

        # Text box dimensions (constant)
        bar_height = HEIGHT // 8
        text_box_height = 120
        text_box_width = WIDTH * 2 // 3
        text_box_x = WIDTH // 6

        # Fixed y: bottom of text box aligns with top of bottom bar
        text_box_y = (HEIGHT - bar_height) - text_box_height +5
        text_box_rect = pygame.Rect(text_box_x, text_box_y, text_box_width, text_box_height)

        for line in slide["text"]:
            start_time = pygame.time.get_ticks()
            finished = False
            while not finished:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        return
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE:
                            finished = True
                        if event.key == pygame.K_ESCAPE:
                            return
                now = pygame.time.get_ticks()
                chars = min(len(line), (now - start_time) // 25)
                displayed_text = line[:chars]

                WIN.fill((25, 28, 35))
                for img in images:
                    WIN.blit(img["surface"], img["pos"])

                # Draw text box
                pygame.draw.rect(WIN, (0, 0, 0), text_box_rect)
                pygame.draw.rect(WIN, (200, 200, 200), text_box_rect, 2)

                text_surface = font.render(displayed_text, True, (255, 255, 255))
                WIN.blit(
                    text_surface,
                    (text_box_rect.centerx - text_surface.get_width() // 2,
                     text_box_rect.centery - text_surface.get_height() // 2 - 20)
                )

                # Hint text (right‑aligned, above bottom bar)
                hint_surf = small_font.render("SPACE = next | ESC = skip", True, (160, 160, 160))
                hint_x = WIDTH - hint_surf.get_width() - 30
                hint_y = HEIGHT - bar_height - 30
                WIN.blit(hint_surf, (hint_x, hint_y))

                draw_letterbox(WIN, 1)
                pygame.display.update()

                if chars == len(line) and now - start_time > len(line) * 25 + 2350:
                    finished = True

        fade_screen(fade_in=False, duration=400)
        fade_screen(fade_in=True, duration=400)

    for i in reversed(range(30)):
        WIN.fill((0, 0, 0))
        draw_letterbox(WIN, i / 30)
        pygame.display.update()
        clock.tick(60)

def draw_letterbox(surface, progress):
    max_bar_height = HEIGHT // 8
    current_height = int(max_bar_height * progress)
    top_rect = pygame.Rect(0, 0, WIDTH, current_height)
    bottom_rect = pygame.Rect(0, HEIGHT - current_height, WIDTH, current_height)
    pygame.draw.rect(surface, (0, 0, 0), top_rect)
    pygame.draw.rect(surface, (0, 0, 0), bottom_rect)
    if current_height > 0:
        pygame.draw.line(surface, (40, 40, 40), (0, current_height), (WIDTH, current_height), 2)
        pygame.draw.line(surface, (40, 40, 40), (0, HEIGHT - current_height), (WIDTH, HEIGHT - current_height), 2)

def fade_screen(fade_in=True, duration=600):
    start_time = pygame.time.get_ticks()
    top_bar_height = HEIGHT // 8
    bottom_bar_height = HEIGHT // 8
    window_rect = pygame.Rect(0, top_bar_height, WIDTH, HEIGHT - top_bar_height - bottom_bar_height)
    fade_surf = pygame.Surface((window_rect.width, window_rect.height))
    fade_surf.fill((0, 0, 0))

    while True:
        now = pygame.time.get_ticks()
        elapsed = now - start_time
        progress = min(elapsed / duration, 1)
        if fade_in:
            alpha = 255 - int(255 * progress)
        else:
            alpha = int(255 * progress)
        fade_surf.set_alpha(alpha)
        WIN.blit(fade_surf, (window_rect.x, window_rect.y))
        draw_letterbox(WIN, 1)
        pygame.display.update()
        if progress >= 1:
            break

# ---------------------------------------
# CLASSES
# ---------------------------------------
class MoneyBill(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        original_img = pygame.image.load(resource_path("money.png")).convert_alpha()
        self.image = pygame.transform.scale(original_img, (43, 43))
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, WIDTH - self.rect.width)
        self.rect.y = -50
        self.speed = 180

    def update(self, dt):
        self.rect.y += self.speed * dt / 1000
        if self.rect.top > HEIGHT:
            self.kill()

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

class ExportTarget:
    def __init__(self, speed):
        self.image = EXPORT_TARGET_IMG
        self.rect = self.image.get_rect()
        self.rect.y = 120
        self.base_speed = speed
        self.direction = 1
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
        surface.blit(self.image, self.rect)
        crate_img = CRATE_IMAGES[self.requested_type]
        icon_rect = crate_img.get_rect(
            midbottom=(self.rect.centerx, max(self.rect.top - 5, UI_HEIGHT + crate_img.get_height()))
        )
        surface.blit(crate_img, icon_rect)

class BottleneckZone:
    def __init__(self, y_pos):
        self.image = LIEFERENGPASS_IMG
        self.rect = self.image.get_rect(midtop=(WIDTH//2, y_pos))
        self.active = False
        self.direction = 1
        self.speed = 2

    def activate(self):
        self.active = True
        self.rect.x = random.randint(0, WIDTH - self.rect.width)

    def deactivate(self):
        self.active = False

    def update(self):
        if not self.active:
            return
        self.rect.x += self.speed * self.direction
        if self.rect.left <= 0:
            self.rect.left = 0
            self.direction = 1
        elif self.rect.right >= WIDTH:
            self.rect.right = WIDTH
            self.direction = -1

    def draw(self, surface):
        if self.active:
            surface.blit(self.image, self.rect)
            font = pygame.font.SysFont("Arial", 28, bold=True)
            text_surf = font.render("Lieferengpass", True, (255, 0, 0))
            text_rect = text_surf.get_rect(center=self.rect.center)
            surface.blit(text_surf, text_rect)

# ----------------------------
# Game mode functions (unchanged logic, but use resource_path implicitly via loaded assets)
# ----------------------------
def run_mode_1(player_speed, tariff_speed):
    player = pygame.Rect(200, HEIGHT - PLAYER_HEIGHT, PLAYER_WIDTH, PLAYER_HEIGHT)
    trump = pygame.Rect(200, 5, TRUMP_WIDTH, TRUMP_HEIGHT)

    player_vel_y = 0
    gravity = 0.5
    jump_strength = -12
    on_ground = True

    dash_speed = 20
    dash_duration = 150
    dash_cooldown = 1500
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

    BASE_TARIFF_INTERVAL = 1500
    MIN_TARIFF_INTERVAL = 500

    walk_index = 0
    walk_timer = 0
    walk_anim_speed = 80
    facing = "right"

    TRUMP_ANIM_SPEED = 150
    trump_anim_index = 0
    trump_anim_timer = 0
    is_throwing = False
    trigger_throw = False

    spawn_pending = False
    spawn_ready_time = 0

    PLAYER_WALK_RIGHT_MASKS = [pygame.mask.from_surface(img) for img in PLAYER_WALK_RIGHT]
    PLAYER_WALK_LEFT_MASKS = [pygame.mask.from_surface(img) for img in PLAYER_WALK_LEFT]
    PLAYER_IDLE_MASK = pygame.mask.from_surface(PLAYER_IDLE)

    tariffs = []
    clock = pygame.time.Clock()
    start_time = time.time()

    TRUMP_VEL = random.choice([-5, 5])
    direction_timer = 0
    last_tariff_spawn = 0

    while True:
        dt = clock.tick(60)
        elapsed_time = time.time() - start_time
        now = pygame.time.get_ticks()
        direction_timer += dt
        money_timer += dt
        difficulty = min(1 + elapsed_time / 30, 3)

        current_interval = max(MIN_TARIFF_INTERVAL, BASE_TARIFF_INTERVAL - elapsed_time * 15)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None
                if event.key == pygame.K_LSHIFT:
                    if now - last_dash_time > dash_cooldown:
                        is_dashing = True
                        invincible = True
                        dash_timer = 0
                        last_dash_time = now
            if event.type == pygame.USEREVENT + 1:
                invincible = False

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

        player_vel_y += gravity
        player.y += player_vel_y
        if player.y + PLAYER_HEIGHT > GAME_BOTTOM_1:
            player.y = GAME_BOTTOM_1 - PLAYER_HEIGHT
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

        if direction_timer > 1000:
            TRUMP_VEL = random.choice([-7, -5, 5, 7])
            direction_timer = 0
        trump.x += TRUMP_VEL
        if trump.x <= 0 or trump.x + TRUMP_WIDTH >= WIDTH:
            TRUMP_VEL *= -1

        if trigger_throw and not is_throwing:
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
                    is_throwing = False
                    trump_anim_index = 0
            current_trump_img = TRUMP_FRAMES[trump_anim_index]
        else:
            current_trump_img = TRUMP_FRAMES[0]

        if now - last_tariff_spawn > current_interval and not spawn_pending:
            last_tariff_spawn = now
            trigger_throw = True
            spawn_pending = True
            spawn_ready_time = now + 2 * TRUMP_ANIM_SPEED
        if spawn_pending and now >= spawn_ready_time:
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
            for _ in range(random.randint(1, 2)):
                special_type = random.choices(["fast", "heavy"], weights=[50, 50])[0]
                if special_type == "fast":
                    width, height, img, mask = TARIFF_WIDTH_3, TARIFF_HEIGHT_3, TARIFF_ORANGE, pygame.mask.from_surface(TARIFF_ORANGE)
                else:
                    width, height, img, mask = TARIFF_WIDTH_2, TARIFF_HEIGHT_2, TARIFF_DARK_RED, pygame.mask.from_surface(TARIFF_DARK_RED)
                tariff_x = random.randint(0, WIDTH - width)
                tariff_y = TRUMP_HEIGHT
                tariffs.append({
                    "rect": pygame.Rect(tariff_x, tariff_y, width, height),
                    "type": special_type,
                    "shockwave": False,
                    "img": img,
                    "mask": mask
                })
            spawn_pending = False

        if money_timer >= money_interval:
            bill = MoneyBill()
            money_bills.add(bill)
            money_timer = 0
            money_interval = random.randint(10000, 15000)

        # Collisions
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
                    "duration": 300,
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

        for bill in money_bills:
            if player.colliderect(bill.rect):
                player_health += 1
                if player_health > max_health:
                    player_health = max_health
                bill.kill()

        draw_1(player, elapsed_time, tariffs, trump, current_player_img, current_trump_img)
        draw_health_bar(player, player_health, max_health)
        money_bills.update(dt)
        money_bills.draw(WIN)

        for exp in explosions[:]:
            exp["elapsed"] += dt
            exp["radius"] = exp["max_radius"] * (exp["elapsed"] / exp["duration"])
            alpha = max(0, 255 * (1 - exp["elapsed"] / exp["duration"]))
            surface = pygame.Surface((exp["radius"] * 2, exp["radius"] * 2), pygame.SRCALPHA)
            pygame.draw.circle(surface, (255, 50, 0, int(alpha)), (int(exp["radius"]), int(exp["radius"])), int(exp["radius"]))
            WIN.blit(surface, (exp["x"] - exp["radius"], exp["y"] - exp["radius"]))

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

        pygame.display.update()

        if dead:
            if first_death:
                first_death = False
                tariffs.clear()
                explosions.clear()
                pygame.time.set_timer(pygame.USEREVENT + 1, 0)
                invincible = False
                pause_start = time.time()
                restored_health = revive_player(max_health, MODE1_REVIVES, "mode1")
                pause_duration = time.time() - pause_start
                start_time += pause_duration

                if restored_health > 0:
                    player_health = restored_health
                    dead = False
                    continue
                else:
                    show_game_over_screen("mode1")
                    highscores = load_highscores()
                    if elapsed_time > highscores["mode1"]:
                        highscores["mode1"] = round(elapsed_time)
                        save_highscores(highscores)
                    return "menu"
            else:
                show_game_over_screen("mode1")
                highscores = load_highscores()
                if elapsed_time > highscores["mode1"]:
                    highscores["mode1"] = round(elapsed_time)
                    save_highscores(highscores)
                return "menu"

def run_mode_2(player_speed, tariff_speed):
    player = pygame.Rect(200, HEIGHT - PLAYER_HEIGHT, PLAYER_WIDTH, PLAYER_HEIGHT)
    clock = pygame.time.Clock()
    quartal = 1
    quota = 100
    money = 0
    MAX_QUOTA = 500
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
    dash_duration = 150
    dash_cooldown = 1500
    is_dashing = False
    dash_timer = 0
    last_dash_time = 0
    invincible = False

    dead = False
    first_death = True

    combo = 0
    base_reward = 25
    base_multiplier_cap = 2.0

    bottleneck = BottleneckZone(y_pos=HEIGHT // 2)
    bottleneck_timer = 0
    bottleneck_interval = random.randint(10000, 20000)
    bottleneck_duration = 8000
    bottleneck_active_time = 0

    walk_index = 0
    walk_timer = 0
    walk_anim_speed = 80
    facing = "right"

    PLAYER_WALK_RIGHT_MASKS = [pygame.mask.from_surface(img) for img in PLAYER_WALK_RIGHT]
    PLAYER_WALK_LEFT_MASKS = [pygame.mask.from_surface(img) for img in PLAYER_WALK_LEFT]
    PLAYER_IDLE_MASK = pygame.mask.from_surface(PLAYER_IDLE)

    tariffs = []
    tariff_count = 0
    tariff_interval = random.randint(10000, 15000)

    crates = []
    target = ExportTarget(base_target_speed)
    shoot_cooldown = 500
    last_shot = 0
    global selected_crate

    while True:
        dt = clock.tick(60)
        tariff_count += dt
        bottleneck_timer += dt
        elapsed_time = time.time() - quartal_start_time
        time_left = quartal_duration - elapsed_time
        multiplier_cap = base_multiplier_cap + (quartal - 1) * 0.5
        crate_speed = min(10, base_crate_speed + (quartal - 1) * 0.3)
        target_speed = min(15, base_target_speed + (quartal - 1) * 0.6)
        target.base_speed = target_speed

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None
                if event.key == pygame.K_f:
                    now = pygame.time.get_ticks()
                    if now - last_shot > shoot_cooldown:
                        crate = CrateProjectile(player.centerx, player.top, selected_crate)
                        crate.normal_speed = crate_speed
                        crates.append(crate)
                        last_shot = now
                if event.key == pygame.K_1:
                    selected_crate = 0
                if event.key == pygame.K_2 and len(CRATE_IMAGES) > 1:
                    selected_crate = 1
                if event.key == pygame.K_3 and len(CRATE_IMAGES) > 2:
                    selected_crate = 2
                if event.key == pygame.K_LSHIFT:
                    now = pygame.time.get_ticks()
                    if now - last_dash_time > dash_cooldown:
                        is_dashing = True
                        invincible = True
                        dash_timer = 0
                        last_dash_time = now
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    now = pygame.time.get_ticks()
                    if now - last_shot > shoot_cooldown:
                        crate = CrateProjectile(player.centerx, player.top, selected_crate)
                        crate.normal_speed = crate_speed
                        crates.append(crate)
                        last_shot = now
            if event.type == pygame.MOUSEWHEEL:
                selected_crate -= event.y
                selected_crate %= len(CRATE_IMAGES)

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

        if tariff_count > tariff_interval:
            for _ in range(2):
                tariff_x = random.randint(0, WIDTH - TARIFF_WIDTH_1)
                tariff_y = 100
                tariffs.append(pygame.Rect(tariff_x, tariff_y, TARIFF_WIDTH_1, TARIFF_HEIGHT_1))
            tariff_count = 0

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

        if money >= quota:
            quartal += 1
            if quota < MAX_QUOTA:
                quota += 50
            quartal_start_time = time.time()
            money = 0
        elif time_left <= 0:
            dead = True

        for crate in crates[:]:
            crate.update()
            if crate.rect.bottom < 0:
                combo = 0
                crates.remove(crate)

        target.update()

        for crate in crates[:]:
            if bottleneck.active and crate.rect.colliderect(bottleneck.rect):
                crate.speed = crate.normal_speed * 0.4
                crate.rect.x += random.randint(-2, 2)
            else:
                crate.speed = crate.normal_speed

            if crate.rect.colliderect(target.rect):
                if crate.type == target.requested_type:
                    combo += 1
                    multiplier = 1 + min(combo * 0.25, multiplier_cap)
                    money += int(base_reward * multiplier)
                    target.new_request()
                else:
                    combo = 0
                    money -= 10
                crates.remove(crate)

        if quartal >= 3:
            if not bottleneck.active and bottleneck_timer > bottleneck_interval:
                bottleneck.activate()
                bottleneck_active_time = 0
                bottleneck_timer = 0
            if bottleneck.active:
                bottleneck_active_time += dt
                current_duration = min(15000, bottleneck_duration + (quartal - 3) * 1000)
                if bottleneck_active_time > current_duration:
                    bottleneck.deactivate()
                    bottleneck_timer = 0
                    min_int = max(5000, 15000 - quartal * 1000)
                    max_int = max(6000, 25000 - quartal * 1500)
                    bottleneck_interval = random.randint(min_int, max_int)

        draw_2(player, time_left, tariffs, current_player_img, quartal, money, quota, target, crates, combo)
        bottleneck.update()
        bottleneck.draw(WIN)
        draw_health_bar(player, player_health, max_health)
        pygame.display.update()

        if dead:
            if first_death:
                first_death = False
                restored_health = revive_player(max_health, MODE2_REVIVES, "mode2")
                if restored_health > 0:
                    player_health = restored_health
                    dead = False
                    quartal_start_time = time.time()
                    continue
                else:
                    show_game_over_screen("mode2")
                    highscores = load_highscores()
                    if quartal > highscores["mode2"]:
                        highscores["mode2"] = quartal
                        save_highscores(highscores)
                    return "menu"
            else:
                show_game_over_screen("mode2")
                highscores = load_highscores()
                if quartal > highscores["mode2"]:
                    highscores["mode2"] = quartal
                    save_highscores(highscores)
                return "menu"

def game_mode1():
    run_cutscene(MODE1_CUTSCENE)
    return run_mode_1(player_speed=8, tariff_speed=6)

def game_mode2():
    run_cutscene(MODE2_CUTSCENE)
    return run_mode_2(player_speed=8, tariff_speed=6)

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
                        game_state = MENU
                    else:
                        run = False

        if game_state == MENU:
            draw_menu()
            pygame.time.Clock().tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()

#