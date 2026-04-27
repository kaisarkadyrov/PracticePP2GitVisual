import pygame

W, H = 600, 600
CX   = W // 2


# ── Button ────────────────────────────────────────────────────────────────────
class Button:
    def __init__(self, x, y, w, h, text,
                 color=(55, 110, 170), hover=(85, 145, 210)):
        self.rect  = pygame.Rect(x, y, w, h)
        self.text  = text
        self.color = color
        self.hover = hover
        self.font  = pygame.font.Font(None, 34)

    def draw(self, surface):
        c = self.hover if self.rect.collidepoint(pygame.mouse.get_pos()) else self.color
        pygame.draw.rect(surface, c,           self.rect, border_radius=9)
        pygame.draw.rect(surface, (200,200,200), self.rect, 2, border_radius=9)
        ts = self.font.render(self.text, True, (255, 255, 255))
        surface.blit(ts, ts.get_rect(center=self.rect.center))

    def is_clicked(self, event):
        return (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1
                and self.rect.collidepoint(event.pos))


# ── TextInput ─────────────────────────────────────────────────────────────────
class TextInput:
    def __init__(self, x, y, w, h, placeholder=""):
        self.rect        = pygame.Rect(x, y, w, h)
        self.text        = ""
        self.placeholder = placeholder
        self.font        = pygame.font.Font(None, 34)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.unicode.isprintable() and len(self.text) < 15:
                self.text += event.unicode

    def draw(self, surface):
        pygame.draw.rect(surface, (255, 255, 255), self.rect, border_radius=6)
        pygame.draw.rect(surface, (55, 110, 170),  self.rect, 2, border_radius=6)
        disp  = self.text if self.text else self.placeholder
        color = (10, 10, 10) if self.text else (160, 160, 160)
        surface.blit(self.font.render(disp, True, color),
                     (self.rect.x + 10, self.rect.y + 8))


# ── HUD (in-game overlay) ─────────────────────────────────────────────────────
def draw_hud(surface, font, score, distance, coins_collected, player):
    from racer import RACE_LENGTH
    remaining = max(0, RACE_LENGTH - int(distance))

    # Left panel: score / distance / coins
    panel = pygame.Surface((210, 110), pygame.SRCALPHA)
    panel.fill((0, 0, 0, 130))
    surface.blit(panel, (5, 5))
    surface.blit(font.render(f"Score:  {int(score)}",        True, (255,255,255)), (12,  12))
    surface.blit(font.render(f"Dist:   {int(distance)}m",   True, (255,255,255)), (12,  40))
    surface.blit(font.render(f"Left:   {remaining}m",        True, (200,200,100)), (12, 68))
    surface.blit(font.render(f"Coins:  {coins_collected}",   True, (255,215,  0)), (12,  96))

    # Right panel: active powerup
    now = pygame.time.get_ticks()
    if player.nitro_active:
        secs = max(0, (player.powerup_timer - now) // 1000)
        _draw_badge(surface, font, f"NITRO  {secs}s", (0, 200, 255))
    elif player.shield_active:
        secs = max(0, (player.powerup_timer - now) // 1000)
        _draw_badge(surface, font, f"SHIELD {secs}s", (255, 215, 0))
    elif pygame.time.get_ticks() < player.slow_timer:
        secs = max(0, (player.slow_timer - now) // 1000)
        _draw_badge(surface, font, f"SLOW   {secs}s", (180, 80, 220))
    if player.crashes_allowed > 0:
        _draw_badge(surface, font, f"REPAIR x{player.crashes_allowed}", (80, 220, 80), y=570)


def _draw_badge(surface, font, text, color, y=540):
    ts = font.render(text, True, color)
    bg = pygame.Surface((ts.get_width() + 16, 28), pygame.SRCALPHA)
    bg.fill((0, 0, 0, 150))
    surface.blit(bg, (CX - bg.get_width() // 2, y - 2))
    surface.blit(ts, ts.get_rect(centerx=CX, y=y))


# ── MENU screen ───────────────────────────────────────────────────────────────
def draw_menu(surface, font, big_font, buttons):
    surface.fill((18, 18, 38))
    # decorative road strip
    pygame.draw.rect(surface, (45, 45, 45), (180, 0, 240, 600))
    for y in range(0, 600, 60):
        pygame.draw.rect(surface, (200, 200, 200), (295, y, 8, 36))
    # title
    shadow = big_font.render("RACER", True, (0, 0, 0))
    title  = big_font.render("RACER", True, (255, 200, 0))
    surface.blit(shadow, shadow.get_rect(centerx=CX + 3, y=65))
    surface.blit(title,  title.get_rect(centerx=CX,      y=62))
    sub = font.render("Arcade Road Racing", True, (140, 180, 255))
    surface.blit(sub, sub.get_rect(centerx=CX, y=128))
    for btn in buttons: btn.draw(surface)


# ── NAME INPUT screen ─────────────────────────────────────────────────────────
def draw_name_input(surface, font, big_font, name_input):
    surface.fill((18, 18, 38))
    title = big_font.render("RACER", True, (255, 200, 0))
    surface.blit(title, title.get_rect(centerx=CX, y=80))
    surface.blit(font.render("Enter your name:", True, (200, 200, 200)),
                 font.render("Enter your name:", True, (0,0,0)).get_rect(centerx=CX, y=220))
    name_input.draw(surface)
    hint = font.render("Press ENTER to start", True, (140, 180, 255))
    surface.blit(hint, hint.get_rect(centerx=CX, y=340))


# ── LEADERBOARD screen ────────────────────────────────────────────────────────
def draw_leaderboard(surface, font, big_font, board, btn_back):
    surface.fill((12, 12, 32))
    title = big_font.render("TOP 10", True, (255, 215, 0))
    surface.blit(title, title.get_rect(centerx=CX, y=18))
    pygame.draw.line(surface, (80, 80, 120), (50, 80), (550, 80), 1)
    hdr_font = pygame.font.Font(None, 24)
    hdr = hdr_font.render(f"{'#':<3}  {'Name':<13}  {'Score':>6}  {'Dist':>5}  {'Coins':>5}", True, (160, 160, 180))
    surface.blit(hdr, (55, 88))
    pygame.draw.line(surface, (60, 60, 100), (50, 106), (550, 106), 1)
    row_font = pygame.font.Font(None, 26)
    for i, e in enumerate(board):
        col   = (255, 215, 0) if i == 0 else (200, 200, 210)
        coins = e.get('coins', 0)
        row   = f"{i+1:<3}  {e['name']:<13}  {e['score']:>6}  {e['distance']:>4}m  {coins:>5}"
        surface.blit(row_font.render(row, True, col), (55, 112 + i * 34))
    btn_back.draw(surface)


# ── GAME OVER screen ──────────────────────────────────────────────────────────
def draw_gameover(surface, font, big_font, score, distance, coins, btn_retry, btn_menu):
    surface.fill((8, 0, 0))
    go = big_font.render("GAME OVER", True, (210, 30, 30))
    surface.blit(go, go.get_rect(centerx=CX, y=100))
    med = pygame.font.Font(None, 38)
    lines = [
        (f"Score:     {int(score)}",    (255, 255, 255)),
        (f"Distance:  {int(distance)} m",(200, 255, 200)),
        (f"Coins:     {coins}",          (255, 215,   0)),
    ]
    for i, (txt, col) in enumerate(lines):
        ts = med.render(txt, True, col)
        surface.blit(ts, ts.get_rect(centerx=CX, y=215 + i * 44))
    btn_retry.draw(surface)
    btn_menu.draw(surface)


# ── SETTINGS screen ───────────────────────────────────────────────────────────
def draw_settings(surface, font, big_font, settings, toggles, btn_back):
    surface.fill((16, 28, 16))
    title = big_font.render("SETTINGS", True, (80, 210, 80))
    surface.blit(title, title.get_rect(centerx=CX, y=30))

    items = [
        ("Sound",      f"{'ON' if settings['sound'] else 'OFF'}"),
        ("Car Color",  settings['car_color'].upper()),
        ("Difficulty", settings['difficulty'].upper()),
    ]
    for i, ((lbl, val), btn) in enumerate(zip(items, toggles)):
        y = 135 + i * 90
        surface.blit(font.render(lbl, True, (180, 180, 180)), (90, y))
        surface.blit(font.render(val, True, (255, 255, 100)),  (90, y + 28))
        btn.draw(surface)
    btn_back.draw(surface)