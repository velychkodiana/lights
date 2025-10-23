import pygame
import random
import math
import mido

#   SETTINGS

WIDTH = 1280
HEIGHT = 720
FPS = 60
SPAWN_MODE = "chaos"   # "chaos" / "circle"
PASTEL_COLORS = [
    (0x88, 0x35, 0x56),
    (0xD6, 0x97, 0xA5),
    (0xCC, 0xD1, 0xDB),
    (0x85, 0x8F, 0xB4),
    (0xF2, 0xD5, 0xE5),
    (0xE3, 0xA7, 0xC0),
    (0xBA, 0xC7, 0xE8),
]

pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("✨ Pastel MIDI Star Show")
clock = pygame.time.Clock()

# =====================
#   SOUND
# =====================
pygame.mixer.music.load("just_dance.mid")
pygame.mixer.music.play()

# =====================
#   STAR CLASS
# =====================
class Light:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.base_size = 8     # dynamic change
        self.size = 0
        self.brightness = 0
        self.angle = random.random() * math.pi
        self.scale = 1
        self.color = random.choice(PASTEL_COLORS)

    def trigger(self, note, velocity=100):
        self.color = random.choice(PASTEL_COLORS)
        self.brightness = 255
        # bigger stars on lower notes
        self.base_size = max(5, 35 - (note // 3))
        self.size = self.base_size
        # scale pulse boost
        self.scale = 1.5 + (velocity / 200)

    def update(self):
        if self.brightness > 0:
            self.brightness -= 4
        # scale relax animation
        self.scale = max(1.0, self.scale - 0.05)

    def draw(self, screen):
        if self.brightness <= 0:
            return

        alpha = self.brightness / 255
        r, g, b = self.color
        color = (int(r * alpha), int(g * alpha), int(b * alpha))

        points = []
        spikes = 5
        radius_outer = self.size * self.scale
        radius_inner = radius_outer * 0.45

        angle = self.angle
        step = math.pi / spikes

        for i in range(spikes * 2):
            r = radius_outer if i % 2 == 0 else radius_inner
            px = self.x + math.cos(angle) * r
            py = self.y + math.sin(angle) * r
            points.append((px, py))
            angle += step

        # GLOW — a faint halo
        glow = 3
        for i in range(glow):
            fade = max(1 - (i / glow), 0.05)
            glow_color = (
                int(color[0] * fade),
                int(color[1] * fade),
                int(color[2] * fade)
            )
            pygame.draw.polygon(screen, glow_color, points, width=max(1, glow - i))

        pygame.draw.polygon(screen, color, points)

#   LIGHT GENERATION

def spawn_position(i):
    if SPAWN_MODE == "chaos":
        return (
            random.randint(50, WIDTH - 50),
            random.randint(50, HEIGHT - 50)
        )
    else: # circle mode
        angle = i * (2 * math.pi / 25)
        r = 250
        return (
            WIDTH//2 + math.cos(angle) * r,
            HEIGHT//2 + math.sin(angle) * r
        )

lights = [Light(*spawn_position(i)) for i in range(25)]

#   MIDI EVENTS

midi = mido.MidiFile("just_dance.mid")
midi_iter = midi.play()

running = True
while running:
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    try:
        msg = next(midi_iter)
        if msg.type == "note_on" and msg.velocity > 0:
            random.choice(lights).trigger(msg.note, msg.velocity)
    except StopIteration:
        running = False

    for l in lights:
        l.update()

    screen.fill((20, 20, 30))  # darker mood
    for l in lights:
        l.draw(screen)

    pygame.display.flip()

pygame.quit()
