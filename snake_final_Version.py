# snake_enhanced.py
import pygame
import sys
import random
import os
from pygame.math import Vector2

# ================= إعداد المسارات =================
base_path = os.path.dirname(__file__)

# ================= إعدادات عامة =================
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()

# شاشة وخلية
cell_size = 40
cell_number = 15
WIDTH = cell_number * cell_size
HEIGHT = cell_number * cell_size
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake - Classic (Enhanced)")

clock = pygame.time.Clock()

# ملفات ثابتة (تأكد إنها موجودة)
APPLE_IMG = os.path.join(base_path, 'Graphics', 'apple.png')
GOLD_APPLE_IMG = os.path.join(base_path, 'Graphics', 'gold_apple.png')  # optional
FONT_FILE = os.path.join(base_path, 'Font', 'PoetsenOne-Regular.ttf')
CRUNCH_SOUND = os.path.join(base_path, 'Sound', 'crunch.wav')
HIGHSCORE_FILE = os.path.join(base_path, 'highscore.txt')

# ================= تحميل آمن للصور / أصوات مع تصغير/تكبير تلقائي =================
def safe_image(path, fallback=None, size=(cell_size, cell_size)):
    try:
        img = pygame.image.load(path).convert_alpha()
        if img.get_size() != size:
            img = pygame.transform.smoothscale(img, size)
        return img
    except Exception:
        if fallback:
            try:
                img = pygame.image.load(fallback).convert_alpha()
                if img.get_size() != size:
                    img = pygame.transform.smoothscale(img, size)
                return img
            except Exception:
                return None
        return None

def safe_sound(path):
    try:

        return pygame.mixer.Sound(path)
    except Exception:
        return None

# تحميل الموارد
apple = safe_image(APPLE_IMG)
gold_apple = safe_image(GOLD_APPLE_IMG, APPLE_IMG)
crunch_sound = safe_sound(CRUNCH_SOUND)

# تحميل خط
try:
    game_font = pygame.font.Font(FONT_FILE, 25)
except Exception:
    game_font = pygame.font.SysFont('arial', 25)

# ثيم افتراضي
theme = {'bg': (175,215,70), 'grass': (167,209,61), 'accent': (56,74,12)}

# (اختياري) مجموعات ثيمات — فكّ التعليق أو عدّل كما تريد
THEMES = [
    {'bg': (175,215,70), 'grass': (167,209,61), 'accent': (56,74,12)},
    {'bg': (60,179,113), 'grass': (72,201,125), 'accent': (20,40,20)},
    {'bg': (140,200,90), 'grass': (120,180,70), 'accent': (30,60,20)},
]

# ================= وظائف High Score =================
def load_highscore():
    try:
        if not os.path.exists(HIGHSCORE_FILE):
            with open(HIGHSCORE_FILE, 'w') as f:
                f.write('0')
            return 0
        with open(HIGHSCORE_FILE, 'r') as f:
            return int(f.read().strip() or 0)
    except Exception:
        return 0

def save_highscore(value):
    try:
        with open(HIGHSCORE_FILE, 'w') as f:
            f.write(str(int(value)))
    except Exception:
        pass

highscore = load_highscore()

# ================= كلاس SNAKE =================
class SNAKE:
    def __init__(self):
        self.reset()
        # تحميل صور الرأس/ذيل/جسم — مقاسها يتم توحيده عبر safe_image
        self.head_up = safe_image(os.path.join(base_path,'Graphics','head_up.png'))
        self.head_down = safe_image(os.path.join(base_path,'Graphics','head_down.png'))
        self.head_right = safe_image(os.path.join(base_path,'Graphics','head_right.png'))
        self.head_left = safe_image(os.path.join(base_path,'Graphics','head_left.png'))
        self.tail_up = safe_image(os.path.join(base_path,'Graphics','tail_up.png'))
        self.tail_down = safe_image(os.path.join(base_path,'Graphics','tail_down.png'))
        self.tail_right = safe_image(os.path.join(base_path,'Graphics','tail_right.png'))
        self.tail_left = safe_image(os.path.join(base_path,'Graphics','tail_left.png'))
        self.body_vertical = safe_image(os.path.join(base_path,'Graphics','body_vertical.png'))
        self.body_horizontal = safe_image(os.path.join(base_path,'Graphics','body_horizontal.png'))
        self.body_tr = safe_image(os.path.join(base_path,'Graphics','body_tr.png'))
        self.body_tl = safe_image(os.path.join(base_path,'Graphics','body_tl.png'))
        self.body_br = safe_image(os.path.join(base_path,'Graphics','body_br.png'))
        self.body_bl = safe_image(os.path.join(base_path,'Graphics','body_bl.png'))

        # fallback simple square if missing textures
        self.simple_rect = pygame.Surface((cell_size, cell_size), pygame.SRCALPHA)
        self.simple_rect.fill(theme['accent'])

    def greedy_move(self, fruit):
        """Use Greedy Best-First Search to move the snake toward the fruit."""
        possible_directions = [Vector2(0, -1), Vector2(1, 0), Vector2(0, 1), Vector2(-1, 0)]  # Up, right, down, left
        best_direction = None
        min_distance = float('inf')

        for direction in possible_directions:
            new_pos = self.body[0] + direction
            if self.is_valid(new_pos):
                distance = self.manhattan_distance(new_pos, fruit.pos)
                if distance < min_distance:
                    min_distance = distance
                    best_direction = direction

        if best_direction is not None:
            self.direction = best_direction

    def reset(self):
        self.body = [Vector2(5,10), Vector2(4,10), Vector2(3,10)]
        self.direction = Vector2(0,0)
        self.new_block = False
        # default graphic placeholders
        self.head = None
        self.tail = None

    def draw_snake(self, surface):
        self.update_head_graphics()
        self.update_tail_graphics()
        for index, block in enumerate(self.body):
            x_pos = int(block.x * cell_size)
            y_pos = int(block.y * cell_size)
            block_rect = pygame.Rect(x_pos, y_pos, cell_size, cell_size)

            if index == 0:
                if self.head:
                    surface.blit(self.head, block_rect)
                else:
                    surface.blit(self.simple_rect, block_rect)
            elif index == len(self.body) - 1:
                if self.tail:
                    surface.blit(self.tail, block_rect)
                else:
                    surface.blit(self.simple_rect, block_rect)
            else:
                previous_block = self.body[index + 1] - block
                next_block = self.body[index - 1] - block
                # vertical
                if previous_block.x == next_block.x:
                    if self.body_vertical:
                        surface.blit(self.body_vertical, block_rect)
                    else:
                        surface.blit(self.simple_rect, block_rect)
                # horizontal
                elif previous_block.y == next_block.y:
                    if self.body_horizontal:
                        surface.blit(self.body_horizontal, block_rect)
                    else:
                        surface.blit(self.simple_rect, block_rect)
                else:
                    # corners
                    # note: check all corner combos
                    if (previous_block.x == -1 and next_block.y == -1) or (previous_block.y == -1 and next_block.x == -1):
                        if self.body_tl: surface.blit(self.body_tl, block_rect)
                        else: surface.blit(self.simple_rect, block_rect)
                    elif (previous_block.x == -1 and next_block.y == 1) or (previous_block.y == 1 and next_block.x == -1):
                        if self.body_bl: surface.blit(self.body_bl, block_rect)
                        else: surface.blit(self.simple_rect, block_rect)
                    elif (previous_block.x == 1 and next_block.y == -1) or (previous_block.y == -1 and next_block.x == 1):
                        if self.body_tr: surface.blit(self.body_tr, block_rect)
                        else: surface.blit(self.simple_rect, block_rect)
                    elif (previous_block.x == 1 and next_block.y == 1) or (previous_block.y == 1 and next_block.x == 1):
                        if self.body_br: surface.blit(self.body_br, block_rect)
                        else: surface.blit(self.simple_rect, block_rect)
    def greedy_move(self, fruit):
        """Use Greedy Best-First Search to move the snake toward the fruit."""
        possible_directions = [Vector2(0, -1), Vector2(1, 0), Vector2(0, 1), Vector2(-1, 0)]  # Up, right, down, left
        best_direction = None
        min_distance = float('inf')

        for direction in possible_directions:
            new_pos = self.body[0] + direction
            if self.is_valid(new_pos):
                distance = self.manhattan_distance(new_pos, fruit.pos)
                if distance < min_distance:
                    min_distance = distance
                    best_direction = direction

        if best_direction is not None:
            self.direction = best_direction
    def update_head_graphics(self):
        # guard
        if len(self.body) < 2:
            self.head = None
            return
        # direction from head to second block (where head came from)
        head_relation = self.body[1] - self.body[0]
        if head_relation == Vector2(1,0): self.head = self.head_left
        elif head_relation == Vector2(-1,0): self.head = self.head_right
        elif head_relation == Vector2(0,1): self.head = self.head_up
        elif head_relation == Vector2(0,-1): self.head = self.head_down
        else: self.head = None

    def update_tail_graphics(self):
        if len(self.body) < 2:
            self.tail = None
            return
        tail_relation = self.body[-2] - self.body[-1]
        if tail_relation == Vector2(1,0): self.tail = self.tail_left
        elif tail_relation == Vector2(-1,0): self.tail = self.tail_right
        elif tail_relation == Vector2(0,1): self.tail = self.tail_up
        elif tail_relation == Vector2(0,-1): self.tail = self.tail_down
        else: self.tail = None

    def move_snake(self):
        if self.new_block:
            body_copy = self.body[:]
            body_copy.insert(0, body_copy[0] + self.direction)
            self.body = body_copy[:]
            self.new_block = False
        else:
            body_copy = self.body[:-1]
            body_copy.insert(0, body_copy[0] + self.direction)
            self.body = body_copy[:]

    def add_block(self):
        self.new_block = True

    def is_valid(self, pos):
        """Check if the new position is valid (inside the grid and not colliding with the snake body)."""
        if not (0 <= pos.x < cell_number and 0 <= pos.y < cell_number):
            return False  # Out of bounds
        if pos in self.body[1:]:
            return False  # Collides with itself
        return True

    def manhattan_distance(self, pos1, pos2):
        return abs(pos1.x - pos2.x) + abs(pos1.y - pos2.y)

    def play_crunch_sound(self):
        if crunch_sound:
            crunch_sound.play()

# =================  FRUIT ( golden special) =================
class FRUIT:
    def __init__(self):
        self.randomize()

    def draw_fruit(self, surface):
        r = pygame.Rect(int(self.pos.x * cell_size), int(self.pos.y * cell_size), cell_size, cell_size)
        if self.is_gold:
            if gold_apple:
                surface.blit(gold_apple, r)
            else:
                pygame.draw.ellipse(surface, (255,215,0), r)
        else:
            if apple:
                surface.blit(apple, r)
            else:
                pygame.draw.ellipse(surface, (200,0,0), r)

    def randomize(self, force_pos=None, gold_chance=0.08):
        # force_pos for safety placement
        tries = 0
        while True:
            if force_pos:
                x, y = force_pos
            else:
                x = random.randint(0, cell_number - 1)
                y = random.randint(0, cell_number - 1)
            self.pos = Vector2(x, y)
            self.is_gold = random.random() < gold_chance
            self.life = random.randint(20, 35) if self.is_gold else None
            return

# ================= الكلاس الرئيسي (GAME) =================
class Game:
    def __init__(self):
        self.snake = SNAKE()
        self.fruit = FRUIT()
        self.started = False
        self.game_over = False
        self.greedy_mode = False
        self.score = 0
        self.difficulty = 'Normal'  # default
        self.base_timer = 150  # ms per move (will vary by difficulty)
        self.timer_interval = self.base_timer
        self.SCREEN_UPDATE = pygame.USEREVENT + 1
        self.set_difficulty(self.difficulty)
        self.update_timer(self.timer_interval)
        self.spawn_safe_fruit()

    def set_difficulty(self, name):
        self.difficulty = name
        if name == 'Easy':
            self.base_timer = 200
        elif name == 'Normal':
            self.base_timer = 150
        elif name == 'Hard':
            self.base_timer = 110
        else:
            self.base_timer = 150
        self.timer_interval = self.base_timer
        self.update_timer(self.timer_interval)

    def update_timer(self, ms):
        # set event for game tick
        pygame.time.set_timer(self.SCREEN_UPDATE, ms)

    def reset(self):
        self.snake.reset()
        self.fruit.randomize()
        self.started = False
        self.game_over = False
        self.score = 0
        self.timer_interval = self.base_timer
        self.update_timer(self.timer_interval)
        self.spawn_safe_fruit()

    def spawn_safe_fruit(self):
        # ensure fruit isn't on snake
        tries = 0
        while True:
            self.fruit.randomize()
            if not any(self.fruit.pos == b for b in self.snake.body):
                break
            tries += 1
            if tries > 50:
                break

    def increase_speed_with_score(self):
        # Speed up slightly as snake grows
        factor = max(0.45, 1.0 - (len(self.snake.body) - 3) * 0.04)
        new_interval = int(self.base_timer * factor)
        if new_interval < 40:
            new_interval = 40
        if new_interval != self.timer_interval:
            self.timer_interval = new_interval
            self.update_timer(self.timer_interval)

    def update(self):
        if not self.started or self.game_over:
            return
        # if direction is zero, don't move
        if self.snake.direction == Vector2(0,0):
            return
        if self.greedy_mode:
            self.snake.greedy_move(self.fruit)  # Snake moves automatically using GBFS
        self.snake.move_snake()
        self.check_collision()
        self.check_fail()
        # decrease special fruit life if applicable
        if self.fruit.is_gold and self.fruit.life is not None:
            self.fruit.life -= 1
            if self.fruit.life <= 0:
                self.spawn_safe_fruit()
        self.increase_speed_with_score()

    def check_collision(self):
        if self.fruit.pos == self.snake.body[0]:
            gained = 2 if self.fruit.is_gold else 1
            self.score += gained
            self.snake.play_crunch_sound()
            # add blocks
            self.snake.add_block()
            if self.fruit.is_gold and random.random() < 0.6:
                self.snake.add_block()
            # respawn safely
            self.spawn_safe_fruit()

        # defensive: if fruit on snake body (other than head), respawn
        for b in self.snake.body[1:]:
            if b == self.fruit.pos:
                self.spawn_safe_fruit()
                break

    def check_fail(self):
        head = self.snake.body[0]
        # wall collision
        if head.x < 0 or head.x >= cell_number or head.y < 0 or head.y >= cell_number:
            self.finish_game()
            return
        # self collision (start from second block)
        for block in self.snake.body[1:]:
            if block == head:
                self.finish_game()
                return

    def finish_game(self):
        global highscore
        self.game_over = True
        if self.score > highscore:
            highscore = self.score
            save_highscore(highscore)

    # ======== Drawing ========
    def draw_grass(self, surface):
        grass_color = theme['grass']
        bg = theme['bg']
        surface.fill(bg)
        for row in range(cell_number):
            for col in range(cell_number):
                if (row + col) % 2 == 0:
                    r = pygame.Rect(col * cell_size, row * cell_size, cell_size, cell_size)
                    pygame.draw.rect(surface, grass_color, r)

    def draw_score(self, surface):
        score_text = str(self.score)
        score_surface = game_font.render(score_text, True, theme['accent'])
        score_x = WIDTH - 7
        score_y = HEIGHT - 7
        score_rect = score_surface.get_rect(bottomright=(score_x, score_y))
        # apple icon next to score
        if apple:
            # scale apple if needed (already scaled), position to left of text
            apple_w = apple.get_width()
            apple_rect = apple.get_rect(midright=(score_rect.left - 6, score_rect.centery))
            bg_rect = pygame.Rect(apple_rect.left - 6, apple_rect.top - 6, apple_rect.width + score_rect.width + 20, apple_rect.height + 12)
            # clamp bg_rect inside screen
            bg_rect.clamp_ip(pygame.Rect(0,0,WIDTH,HEIGHT))
            pygame.draw.rect(surface, theme['bg'], bg_rect)
            pygame.draw.rect(surface, theme['accent'], bg_rect, 2)
            surface.blit(score_surface, score_rect)
            surface.blit(apple, apple_rect)
        else:
            surface.blit(score_surface, score_rect)

    def draw(self, surface):
        self.draw_grass(surface)
        self.fruit.draw_fruit(surface)
        self.snake.draw_snake(surface)
        self.draw_score(surface)
        # if not started, show "Press arrow to start" hint
        if not self.started and not self.game_over:
            small = pygame.font.Font(FONT_FILE, 20) if os.path.exists(FONT_FILE) else pygame.font.SysFont('arial', 20)
            hint = small.render("Press any Arrow Key to start", True, theme['accent'])
            surface.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT // 2 - 20))

    # Game Over screen inside Pygame with Restart / Exit
    def draw_game_over_screen(self, surface):
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(200)
        overlay.fill((10,10,10))
        surface.blit(overlay, (0,0))

        large = pygame.font.Font(FONT_FILE, 52) if os.path.exists(FONT_FILE) else pygame.font.SysFont('arial', 52)
        mid = pygame.font.Font(FONT_FILE, 28) if os.path.exists(FONT_FILE) else pygame.font.SysFont('arial', 28)
        small = pygame.font.Font(FONT_FILE, 20) if os.path.exists(FONT_FILE) else pygame.font.SysFont('arial', 20)

        title = large.render("GAME OVER", True, (255,255,255))
        score_s = mid.render(f"Score: {self.score}", True, (255,255,255))
        high_s = mid.render(f"High Score: {highscore}", True, (255,255,255))

        surface.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//2 - 140))
        surface.blit(score_s, (WIDTH//2 - score_s.get_width()//2, HEIGHT//2 - 70))
        surface.blit(high_s, (WIDTH//2 - high_s.get_width()//2, HEIGHT//2 - 30))

        # buttons
        btn_w, btn_h = 160, 50
        gap = 20
        x1 = WIDTH//2 - btn_w - gap//2
        x2 = WIDTH//2 + gap//2
        y = HEIGHT//2 + 10

        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        # Restart button
        restart_rect = pygame.Rect(x1, y, btn_w, btn_h)
        exit_rect = pygame.Rect(x2, y, btn_w, btn_h)

        def draw_btn(rect, text):
            if rect.collidepoint(mouse):
                pygame.draw.rect(surface, (120,120,120), rect)
            else:
                pygame.draw.rect(surface, (80,80,80), rect)
            pygame.draw.rect(surface, (255,255,255), rect, 2)
            t = small.render(text, True, (255,255,255))
            surface.blit(t, (rect.x + rect.width//2 - t.get_width()//2, rect.y + rect.height//2 - t.get_height()//2))

        draw_btn(restart_rect, "Restart")
        draw_btn(exit_rect, "Exit")

        return restart_rect, exit_rect, click

# ================= شاشة البداية (مع اختيار صعوبة) =================

def start_menu():
    fonts = {
        'title': pygame.font.Font(FONT_FILE, 56) if os.path.exists(FONT_FILE) else pygame.font.SysFont('arial',56),
        'opt': pygame.font.Font(FONT_FILE, 28) if os.path.exists(FONT_FILE) else pygame.font.SysFont('arial',28),
        'small': pygame.font.Font(FONT_FILE, 18) if os.path.exists(FONT_FILE) else pygame.font.SysFont('arial',18)
    }
    title = fonts['title'].render("SNAKE - Classic", True, theme['accent'])
    prompt = fonts['small'].render("Choose difficulty and press Start (Space)", True, theme['accent'])

    options = ['Easy', 'Normal', 'Hard']
    selected = 1  # default Normal
    box_w, box_h = 160, 60
    spacing = 20
    total_width = len(options) * box_w + (len(options)-1) * spacing
    start_x = WIDTH//2 - total_width//2

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    selected = max(0, selected - 1)
                if event.key == pygame.K_RIGHT:
                    selected = min(len(options)-1, selected + 1)
                if event.key == pygame.K_SPACE:
                    return options[selected]
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx,my = pygame.mouse.get_pos()
                # allow clicking on option boxes
                for i in range(len(options)):
                    rect = pygame.Rect(start_x + i*(box_w+spacing), HEIGHT//2 - box_h//2, box_w, box_h)
                    if rect.collidepoint((mx,my)):
                        selected = i

        # draw
        screen.fill(theme['bg'])
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 80))
        screen.blit(prompt, (WIDTH//2 - prompt.get_width()//2, 150))

        # draw options
        for i, opt in enumerate(options):
            rect = pygame.Rect(start_x + i*(box_w+spacing), HEIGHT//2 - box_h//2, box_w, box_h)
            if i == selected:
                pygame.draw.rect(screen, (90,200,90), rect)
            else:
                pygame.draw.rect(screen, (200,200,200), rect)
            pygame.draw.rect(screen, theme['accent'], rect, 3)
            t = fonts['opt'].render(opt, True, theme['accent'])
            screen.blit(t, (rect.x + rect.width//2 - t.get_width()//2, rect.y + rect.height//2 - t.get_height()//2))

        # hint
        hint = fonts['small'].render("Use  <-  or  ->  to change difficulty, Space to start", True, theme['accent'])
        screen.blit(hint, (WIDTH//2 - hint.get_width()//2, HEIGHT - 80))
        pygame.display.update()
        clock.tick(60)

# ================= الإنطلاق =================
game = Game()
chosen = start_menu()
game.set_difficulty(chosen)
game.reset()

# ================= الحلقة الرئيسية =================
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == game.SCREEN_UPDATE:
            game.update()
        if event.type == pygame.KEYDOWN:
            # prevent reversing directly
            if event.key == pygame.K_UP and game.snake.direction.y != 1:
                game.snake.direction = Vector2(0,-1)
                game.started = True
            if event.key == pygame.K_RIGHT and game.snake.direction.x != -1:
                game.snake.direction = Vector2(1,0)
                game.started = True
            if event.key == pygame.K_DOWN and game.snake.direction.y != -1:
                game.snake.direction = Vector2(0,1)
                game.started = True
            if event.key == pygame.K_LEFT and game.snake.direction.x != 1:
                game.snake.direction = Vector2(-1,0)
                game.started = True
            # quick restart with R when gameover
            if event.key == pygame.K_r and game.game_over:
                game.reset()
            # change theme during play (optional) - safe check
            if event.key == pygame.K_t:
                if 'THEMES' in globals() and isinstance(THEMES, list) and THEMES:
                    theme = random.choice(THEMES)
            if event.key == pygame.K_a:  # Switch to greedy search mode
                game.greedy_mode = not game.greedy_mode

        # mouse click for game over buttons
        if event.type == pygame.MOUSEBUTTONDOWN and game.game_over:
            mx,my = pygame.mouse.get_pos()
            # we'll check click after drawing since draw_game_over_screen returns rects and click state

    # draw everything
    game.draw(screen)

    # if game over -> overlay and buttons
    if game.game_over:
        restart_rect, exit_rect, click = game.draw_game_over_screen(screen)
        # process click (mouse pressed)
        if click[0]:
            mx,my = pygame.mouse.get_pos()
            if restart_rect.collidepoint((mx,my)):
                game.reset()
            if exit_rect.collidepoint((mx,my)):
                running = False

    pygame.display.update()
    clock.tick(60)

pygame.quit()
sys.exit()
