"""
FINGER NINJA 3D
Webcam-controlled fruit slicing game.
Controls:
  - Extend ONLY your index finger to activate the blade.
  - Move your index finger through fruits to slice them.
  - Press R to restart, ESC to quit.
"""

import math
import random
import sys
import time

import cv2
import mediapipe as mp
import numpy as np
import pygame

# ---------------------------- CONFIGURATION ----------------------------

WIDTH, HEIGHT = 1100, 700
FPS = 60
CAMERA_INDEX = 0
HAND_DETECTION_CONFIDENCE = 0.65
HAND_TRACKING_CONFIDENCE = 0.60

pygame.init()
pygame.display.set_caption("FINGER NINJA 3D | AI Hand Tracking")
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

FONT = pygame.font.SysFont("arial", 25, bold=True)
SMALL_FONT = pygame.font.SysFont("arial", 17)
BIG_FONT = pygame.font.SysFont("arial", 64, bold=True)
TITLE_FONT = pygame.font.SysFont("arial", 42, bold=True)

# ---------------------------- COLORS / HELPERS ----------------------------

BG_TOP = (10, 16, 35)
BG_BOTTOM = (28, 12, 43)
WHITE = (245, 248, 255)
MUTED = (170, 184, 210)
CYAN = (70, 225, 255)
GOLD = (255, 205, 75)
RED = (255, 75, 95)

def clamp(value, low, high):
    return max(low, min(high, value))

def draw_text(surface, text, font, color, pos, center=False):
    image = font.render(str(text), True, color)
    rect = image.get_rect()
    if center:
        rect.center = pos
    else:
        rect.topleft = pos
    surface.blit(image, rect)

def make_gradient_background():
    bg = pygame.Surface((WIDTH, HEIGHT))
    for y in range(HEIGHT):
        t = y / HEIGHT
        color = tuple(int(BG_TOP[i] * (1 - t) + BG_BOTTOM[i] * t) for i in range(3))
        pygame.draw.line(bg, color, (0, y), (WIDTH, y))
    # Subtle decorative lights
    for _ in range(45):
        x = random.randint(0, WIDTH)
        y = random.randint(0, HEIGHT)
        r = random.randint(1, 3)
        pygame.draw.circle(bg, (45, 55, 88), (x, y), r)
    return bg

BACKGROUND = make_gradient_background()

def point_segment_distance(point, start, end):
    """Distance from a point to a line segment."""
    px, py = point
    ax, ay = start
    bx, by = end
    dx, dy = bx - ax, by - ay
    length_sq = dx * dx + dy * dy
    if length_sq == 0:
        return math.hypot(px - ax, py - ay)
    t = clamp(((px - ax) * dx + (py - ay) * dy) / length_sq, 0, 1)
    nearest = (ax + t * dx, ay + t * dy)
    return math.hypot(px - nearest[0], py - nearest[1])

# ---------------------------- GAME OBJECTS ----------------------------

FRUIT_TYPES = [
    ("WATERMELON", (40, 205, 105), (220, 55, 75)),
    ("ORANGE", (255, 145, 35), (255, 205, 70)),
    ("APPLE", (220, 55, 75), (255, 135, 115)),
    ("LEMON", (245, 215, 45), (255, 245, 135)),
    ("BLUEBERRY", (80, 110, 235), (165, 185, 255)),
    ("KIWI", (125, 185, 65), (205, 225, 120)),
]

class Fruit:
    def __init__(self, x, y, kind=None):
        self.x = float(x)
        self.y = float(y)
        self.kind = kind or random.choice(FRUIT_TYPES)
        self.name, self.base, self.light = self.kind
        self.radius = random.randint(29, 39)
        self.vx = random.uniform(-2.7, 2.7)
        self.vy = random.uniform(-13.5, -10.5)
        self.gravity = 0.27
        self.angle = random.uniform(-25, 25)
        self.spin = random.uniform(-3.0, 3.0)
        self.sliced = False
        self.slice_time = 0
        self.halves = []

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        self.angle += self.spin
        if self.sliced:
            for half in self.halves:
                half["x"] += half["vx"]
                half["y"] += half["vy"]
                half["vy"] += 0.25
                half["angle"] += half["spin"]
            self.slice_time += 1

    def slice(self):
        if self.sliced:
            return
        self.sliced = True
        self.slice_time = 0
        for direction in (-1, 1):
            self.halves.append({
                "x": self.x + direction * 8,
                "y": self.y,
                "vx": self.vx + direction * 2.0,
                "vy": self.vy - 1.0,
                "angle": self.angle,
                "spin": direction * random.uniform(3, 6),
                "direction": direction,
            })

    def draw(self, surface):
        if self.sliced:
            if self.slice_time > 42:
                return
            for half in self.halves:
                x, y = int(half["x"]), int(half["y"])
                r = self.radius
                pygame.draw.circle(surface, self.base, (x, y), r)
                pygame.draw.circle(surface, self.light, (x - 7, y - 9), int(r * .62))
                pygame.draw.circle(surface, (245, 235, 205), (x, y), int(r * .24))
                pygame.draw.circle(surface, (255, 255, 255), (x - 11, y - 14), 5)
                pygame.draw.circle(surface, (35, 35, 55), (x, y), r, 2)
            return

        x, y, r = int(self.x), int(self.y), self.radius
        # Soft shadow and glossy 3D-style layered shading
        shadow = pygame.Surface((r * 3, r * 3), pygame.SRCALPHA)
        pygame.draw.circle(shadow, (0, 0, 0, 75), (r * 1.5, r * 1.55), r)
        surface.blit(shadow, (x - int(r * 1.5) + 5, y - int(r * 1.5) + 8))
        pygame.draw.circle(surface, self.base, (x, y), r)
        pygame.draw.circle(surface, self.light, (x - 7, y - 9), int(r * .70))
        pygame.draw.circle(surface, self.base, (x + 8, y + 9), int(r * .58))
        pygame.draw.ellipse(surface, (255, 255, 255), (x - 17, y - 22, 12, 7))
        pygame.draw.circle(surface, (30, 35, 55), (x, y), r, 2)
        # Stem / leaf
        if self.name in ("APPLE", "WATERMELON"):
            pygame.draw.line(surface, (80, 65, 40), (x, y-r+3), (x+3, y-r-8), 4)
            pygame.draw.ellipse(surface, (65, 190, 105), (x+1, y-r-10, 15, 7))

class Bomb:
    def __init__(self, x, y):
        self.x, self.y = float(x), float(y)
        self.radius = 31
        self.vx = random.uniform(-2, 2)
        self.vy = random.uniform(-12.5, -10)
        self.sliced = False

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.27

    def draw(self, surface):
        x, y, r = int(self.x), int(self.y), self.radius
        pygame.draw.circle(surface, (10, 10, 18), (x, y), r)
        pygame.draw.circle(surface, (75, 80, 100), (x-8, y-9), int(r*.65))
        pygame.draw.circle(surface, (25, 28, 42), (x, y), r, 3)
        pygame.draw.line(surface, (180, 145, 75), (x+8, y-r+4), (x+17, y-r-10), 5)
        pygame.draw.circle(surface, (255, 145, 50), (x+18, y-r-11), 5)
        pygame.draw.circle(surface, (255, 235, 140), (x-10, y-13), 5)

class Particle:
    def __init__(self, x, y, color):
        self.x, self.y = float(x), float(y)
        angle = random.random() * math.tau
        speed = random.uniform(2, 7)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.life = random.randint(18, 32)
        self.max_life = self.life
        self.color = color
        self.size = random.randint(3, 7)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += .16
        self.life -= 1

    def draw(self, surface):
        if self.life > 0:
            radius = max(1, int(self.size * self.life / self.max_life))
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), radius)

# ---------------------------- HAND TRACKING ----------------------------

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    model_complexity=1,
    min_detection_confidence=HAND_DETECTION_CONFIDENCE,
    min_tracking_confidence=HAND_TRACKING_CONFIDENCE,
)


def is_index_only(landmarks):
    index_up = landmarks[8].y < landmarks[6].y
    return index_up

def get_hand_position(frame):
    """Return (screen_position, index_only, annotated_frame)."""
    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)
    position = None
    active = False

    if result.multi_hand_landmarks:
        hand_landmarks = result.multi_hand_landmarks[0]
        lm = hand_landmarks.landmark
        active = is_index_only(lm)

        # Mirror coordinates are already applied to the frame.
        px = int(lm[8].x * WIDTH)
        py = int(lm[8].y * HEIGHT)
        position = (clamp(px, 0, WIDTH), clamp(py, 0, HEIGHT))

        mp.solutions.drawing_utils.draw_landmarks(
            frame, hand_landmarks, mp_hands.HAND_CONNECTIONS
        )

    return position, active, frame

# ---------------------------- GAME STATE ----------------------------

fruits = []
bombs = []
particles = []
blade_points = []
score = 0
lives = 3
missed = 0
game_over = False
paused = False
spawn_timer = 0
last_hand_pos = None
hand_active = False
camera_preview = None
camera_ok = False
start_time = time.time()

def reset_game():
    global fruits, bombs, particles, blade_points
    global score, lives, missed, game_over, paused, spawn_timer
    fruits, bombs, particles, blade_points = [], [], [], []
    score, lives, missed = 0, 3, 0
    game_over, paused = False, False
    spawn_timer = 0

def spawn_wave():
    count = random.choices([1, 2, 3], weights=[55, 35, 10])[0]
    for _ in range(count):
        x = random.randint(100, WIDTH - 100)
        y = HEIGHT + random.randint(10, 90)
        fruits.append(Fruit(x, y))
    if random.random() < 0.13:
        bombs.append(Bomb(random.randint(120, WIDTH - 120), HEIGHT + 45))

def make_slice_effect(x, y, color):
    for _ in range(18):
        particles.append(Particle(x, y, color))

def draw_hud():
    # Top HUD glass-like panels
    pygame.draw.rect(screen, (20, 29, 55), (22, 18, 220, 62), border_radius=16)
    pygame.draw.rect(screen, (80, 110, 160), (22, 18, 220, 62), 2, border_radius=16)
    draw_text(screen, "SCORE", SMALL_FONT, MUTED, (42, 27))
    draw_text(screen, score, TITLE_FONT, WHITE, (42, 43))

    pygame.draw.rect(screen, (20, 29, 55), (WIDTH-205, 18, 183, 62), border_radius=16)
    pygame.draw.rect(screen, (80, 110, 160), (WIDTH-205, 18, 183, 62), 2, border_radius=16)
    draw_text(screen, "LIVES", SMALL_FONT, MUTED, (WIDTH-185, 27))
    for i in range(3):
        color = RED if i < lives else (75, 80, 100)
        pygame.draw.circle(screen, color, (WIDTH-175 + i*42, 57), 12)
        pygame.draw.circle(screen, (255, 190, 195), (WIDTH-179 + i*42, 53), 4)

    draw_text(screen, "FINGER NINJA 3D", SMALL_FONT, (130, 155, 205),
              (WIDTH//2, 28), center=True)

def draw_camera_preview(frame):
    if frame is None:
        return
    preview = cv2.resize(frame, (190, 120))
    preview = cv2.cvtColor(preview, cv2.COLOR_BGR2RGB)
    preview_surface = pygame.surfarray.make_surface(np.rot90(preview))
    x, y = WIDTH - 210, HEIGHT - 145
    screen.blit(preview_surface, (x, y))
    pygame.draw.rect(screen, CYAN if hand_active else (95, 110, 140),
                     (x, y, 190, 120), 2, border_radius=8)
    status = "BLADE ACTIVE" if hand_active else "SHOW INDEX FINGER"
    draw_text(screen, status, SMALL_FONT, CYAN if hand_active else MUTED,
              (x+95, y+127), center=True)

def draw_blade():
    if len(blade_points) < 2:
        return
    points = [(int(p[0]), int(p[1])) for p in blade_points]
    for i in range(1, len(points)):
        strength = i / len(points)
        color = (int(40+100*strength), int(150+90*strength), 255)
        width = max(2, int(3 + 13*strength))
        pygame.draw.line(screen, color, points[i-1], points[i], width)
    pygame.draw.circle(screen, (255, 255, 255), points[-1], 7)
    pygame.draw.circle(screen, CYAN, points[-1], 12, 2)

def draw_overlay(title, subtitle, hint):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((3, 6, 18, 175))
    screen.blit(overlay, (0, 0))
    draw_text(screen, title, BIG_FONT, WHITE, (WIDTH//2, HEIGHT//2-70), center=True)
    draw_text(screen, subtitle, FONT, GOLD, (WIDTH//2, HEIGHT//2), center=True)
    draw_text(screen, hint, SMALL_FONT, MUTED, (WIDTH//2, HEIGHT//2+55), center=True)

# ---------------------------- CAMERA ----------------------------

camera = cv2.VideoCapture(CAMERA_INDEX)
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

if not camera.isOpened():
    print("ERROR: Webcam could not be opened. Check camera permission or CAMERA_INDEX.")
    pygame.quit()
    sys.exit()

# ---------------------------- MAIN LOOP ----------------------------

running = True
while running:
    dt = clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_r:
                reset_game()
            elif event.key == pygame.K_p and not game_over:
                paused = not paused

    ok, camera_frame = camera.read()
    hand_pos = None
    detected_active = False
    camera_preview = None

    if ok:
        hand_pos, detected_active, camera_preview = get_hand_position(camera_frame)

    # Keep the blade active briefly if hand tracking flickers for a frame.
    if "blade_grace_frames" not in globals():
        blade_grace_frames = 0

    if hand_pos is not None and detected_active:
        blade_grace_frames = 7
    else:
        blade_grace_frames = max(0, blade_grace_frames - 1)

    hand_active = hand_pos is not None and blade_grace_frames > 0

    if hand_pos is not None and hand_active and not game_over and not paused:
        blade_points.append(hand_pos)
        blade_points = blade_points[-12:]
    else:
        if blade_points:
            blade_points = blade_points[-1:]
        if not hand_active:
            last_hand_pos = None

    if not game_over and not paused:
        spawn_timer += 1
        if spawn_timer > 48:
            spawn_wave()
            spawn_timer = 0

        # Detect collisions along the complete movement path of the fingertip.
        current_pos = hand_pos if (hand_pos is not None and hand_active) else None

        if current_pos is not None and last_hand_pos is not None:
            # Fruit collision detection
            for fruit in fruits:
                if fruit.sliced:
                    continue

                distance = point_segment_distance(
                    (fruit.x, fruit.y),
                    last_hand_pos,
                    current_pos
                )

                if distance < fruit.radius + 42:
                    fruit.slice()
                    score += 10
                    make_slice_effect(fruit.x, fruit.y, fruit.light)

            # Bomb collision detection
            for bomb in bombs:
                if bomb.sliced:
                    continue

                distance = point_segment_distance(
                    (bomb.x, bomb.y),
                    last_hand_pos,
                    current_pos
                )

                if distance < bomb.radius + 22:
                    bomb.sliced = True
                    lives = 0
                    game_over = True
                    make_slice_effect(bomb.x, bomb.y, RED)
                    break

        last_hand_pos = current_pos

        # Update fruits and count missed fruit.
        for fruit in fruits:
            fruit.update()
            if not fruit.sliced and fruit.y > HEIGHT + 80:
                fruit.sliced = True
                missed += 1
                lives -= 1
                if lives <= 0:
                    game_over = True

        fruits = [f for f in fruits if (not f.sliced) or f.slice_time < 42]

        # Update bombs.
        for bomb in bombs:
            bomb.update()
        bombs = [b for b in bombs if b.y < HEIGHT + 100 and not b.sliced]

        # Update slice particles.
        for particle in particles:
            particle.update()
        particles = [p for p in particles if p.life > 0]

    # ---------------------------- DRAW ----------------------------

    screen.blit(BACKGROUND, (0, 0))

    # Decorative bottom glow
    glow = pygame.Surface((WIDTH, 120), pygame.SRCALPHA)
    pygame.draw.ellipse(glow, (60, 45, 130, 35), (100, 20, WIDTH-200, 90))
    screen.blit(glow, (0, HEIGHT-120))

    for fruit in fruits:
        fruit.draw(screen)
    for bomb in bombs:
        bomb.draw(screen)
    for particle in particles:
        particle.draw(screen)

    draw_blade()
    draw_hud()
    draw_camera_preview(camera_preview)

    if not camera_ok and camera_preview is None:
        draw_text(screen, "CAMERA NOT DETECTED", FONT, RED,
                  (WIDTH//2, HEIGHT-35), center=True)

    if paused:
        draw_overlay("PAUSED", "Take a break!", "Press P to continue")
    elif game_over:
        draw_overlay("GAME OVER", f"Final Score: {score}",
                     "Press R to play again  |  ESC to exit")
    elif score == 0 and time.time() - start_time < 12:
        draw_text(screen, "Extend ONLY your index finger to activate the blade",
                  SMALL_FONT, MUTED, (WIDTH//2, HEIGHT-35), center=True)

    pygame.display.flip()

# ---------------------------- CLEANUP ----------------------------

camera.release()
hands.close()
cv2.destroyAllWindows()
pygame.quit()
sys.exit()
