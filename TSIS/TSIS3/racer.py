import pygame
import random
import os

LANES       = [200, 300, 400]
SPEED_BASE  = 5
RACE_LENGTH = 2000          # finish line distance

# ── image loader ──────────────────────────────────────────────────────────────
def load_image(name, w, h):
    for folder in (os.path.join('assets', 'images'), 'assets'):
        path = os.path.join(folder, name)
        try:
            img = pygame.image.load(path).convert_alpha()
            return pygame.transform.scale(img, (w, h))
        except Exception:
            pass
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    surf.fill((80, 80, 80, 220))
    return surf


# ── Player ────────────────────────────────────────────────────────────────────
class Player(pygame.sprite.Sprite):
    def __init__(self, color_name):
        super().__init__()
        self.image         = load_image(f"player_{color_name}.png", 52, 88)
        self.rect          = self.image.get_rect(center=(300, 490))
        self.base_speed    = 6
        self.slow_timer    = 0
        self.nitro_active  = False
        self.shield_active = False
        self.powerup_timer = 0
        self.crashes_allowed = 0
        self._flash_timer  = 0
        self._visible      = True

    def get_speed(self):
        if self.nitro_active:
            return self.base_speed * 2.0
        if pygame.time.get_ticks() < self.slow_timer:
            return self.base_speed * 0.45
        return self.base_speed

    def activate_powerup(self, kind, duration_ms=4000):
        self.nitro_active  = kind == "Nitro"
        self.shield_active = kind == "Shield"
        self.powerup_timer = pygame.time.get_ticks() + duration_ms

    def apply_slow(self, duration_ms=2500):
        self.slow_timer = pygame.time.get_ticks() + duration_ms

    def start_flash(self, frames=36):
        self._flash_timer = frames

    def update(self):
        keys = pygame.key.get_pressed()
        s = self.get_speed() 

        if keys[pygame.K_LEFT]  and self.rect.left  > 152:
            self.rect.x -= s
        if keys[pygame.K_RIGHT] and self.rect.right < 448:
            self.rect.x += s

        now = pygame.time.get_ticks()

        if (self.nitro_active or self.shield_active) and now > self.powerup_timer:
            self.nitro_active = self.shield_active = False

        if self._flash_timer > 0:
            self._flash_timer -= 1
            self._visible = (self._flash_timer % 6) < 3
        else:
            self._visible = True

    def draw(self, surface):
        if self._visible:
            surface.blit(self.image, self.rect)


# ── Enemy (traffic) ───────────────────────────────────────────────────────────
class Enemy(pygame.sprite.Sprite):
    def __init__(self, difficulty, speed_bonus=0):
        super().__init__()
        self.image = load_image("enemy.png", 52, 88)
        self.rect  = self.image.get_rect(center=(random.choice(LANES), -110))
        self.speed = SPEED_BASE + (2 if difficulty == "hard" else 0) + speed_bonus

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > 630: self.kill()


# ── Obstacle ──────────────────────────────────────────────────────────────────
class Obstacle(pygame.sprite.Sprite):
    def __init__(self, speed_bonus=0):
        super().__init__()
        self.image = load_image("obstacle.png", 48, 48)
        self.rect  = self.image.get_rect(center=(random.choice(LANES), -70))
        self.speed = SPEED_BASE + speed_bonus

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > 630: self.kill()


# ── OilSpill – slow-down lane hazard ─────────────────────────────────────────
class OilSpill(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        surf = pygame.Surface((64, 32), pygame.SRCALPHA)
        pygame.draw.ellipse(surf, (20, 10, 50, 210), (0, 0, 64, 32))
        pygame.draw.ellipse(surf, (90, 50, 140, 130), (14, 9, 24, 12))
        self.image = surf
        self.rect  = self.image.get_rect(center=(random.choice(LANES), -50))
        self.speed = SPEED_BASE

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > 630: self.kill()


# ── MovingBarrier – dynamic road event ───────────────────────────────────────
class MovingBarrier(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        surf = pygame.Surface((96, 22), pygame.SRCALPHA)
        for i in range(7):
            col = (220, 40, 40) if i % 2 == 0 else (255, 255, 255)
            pygame.draw.rect(surf, col, (i * 14, 0, 14, 22))
        pygame.draw.rect(surf, (50, 50, 50), (0, 0, 96, 22), 2)
        self.image  = surf
        self.rect   = self.image.get_rect(center=(random.choice(LANES), -30))
        self.vy     = SPEED_BASE
        self.vx     = random.choice([-2, 2])

    def update(self):
        self.rect.y += self.vy
        self.rect.x += self.vx
        if self.rect.left < 155 or self.rect.right > 445: self.vx = -self.vx
        if self.rect.top > 630: self.kill()


# ── NitroStrip – boost strip road event ──────────────────────────────────────
class NitroStrip(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        surf = pygame.Surface((294, 18), pygame.SRCALPHA)
        for x in range(0, 294, 18):
            a = 160 + random.randint(-20, 40)
            pygame.draw.rect(surf, (0, 200, 255, a), (x, 0, 12, 18))
        self.image = surf
        self.rect  = self.image.get_rect(center=(300, -20))
        self.speed = SPEED_BASE

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > 630: self.kill()


# ── Coin (weighted values) ────────────────────────────────────────────────────
_COIN_POOL = [10]*5 + [25]*3 + [50]*2 + [100]*1   # weighted

class Coin(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = load_image("coin.png", 30, 30)
        self.rect  = self.image.get_rect(center=(random.choice(LANES), -45))
        self.speed = SPEED_BASE
        self.value = random.choice(_COIN_POOL)

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > 630: self.kill()


# ── PowerUp ───────────────────────────────────────────────────────────────────
_PU_IMGS = {"Nitro": "nitro.png", "Shield": "shield.png", "Repair": "repair.png"}

class PowerUp(pygame.sprite.Sprite):
    LIFETIME_MS = 7000

    def __init__(self):
        super().__init__()
        self.type       = random.choice(list(_PU_IMGS))
        self.image      = load_image(_PU_IMGS[self.type], 36, 36)
        self.rect       = self.image.get_rect(center=(random.choice(LANES), -55))
        self.spawn_time = pygame.time.get_ticks()
        self.speed      = SPEED_BASE

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > 630 or pygame.time.get_ticks() - self.spawn_time > self.LIFETIME_MS:
            self.kill()


# ── Road renderer ─────────────────────────────────────────────────────────────
def draw_road(surface, distance):
    surface.fill((34, 110, 34))
    pygame.draw.rect(surface, (55, 55, 55), (152, 0, 296, 600))
    pygame.draw.rect(surface, (220, 200, 0), (152, 0, 5, 600))
    pygame.draw.rect(surface, (220, 200, 0), (443, 0, 5, 600))
    offset = int(distance * 12) % 44
    for y in range(-44 + offset, 640, 44):
        pygame.draw.rect(surface, (240, 240, 240), (247, y, 7, 24))
        pygame.draw.rect(surface, (240, 240, 240), (346, y, 7, 24))