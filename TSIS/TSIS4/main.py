# main.py — Pygame application entry point
# Screens: Main Menu -> Game -> Game Over -> Leaderboard -> Settings
# Uses pygame.font.SysFont + render/blit — works on all platforms, no emoji.

import sys
import json
import pathlib
import pygame

from config import *
from game   import GameState, UP, DOWN, LEFT, RIGHT
from db     import init_db, get_or_create_player, save_session, get_personal_best, get_leaderboard

# ── Settings I/O ─────────────────────────────────────────────────────────────
SETTINGS_PATH    = pathlib.Path(__file__).parent / "settings.json"
DEFAULT_SETTINGS = {"snake_color": list(GREEN), "grid_overlay": False, "sound": True}

def load_settings() -> dict:
    try:
        data = json.loads(SETTINGS_PATH.read_text())
        return {**DEFAULT_SETTINGS, **data}
    except Exception:
        return dict(DEFAULT_SETTINGS)

def save_settings(settings: dict):
    SETTINGS_PATH.write_text(json.dumps(settings, indent=4))

# ── Drawing helpers ───────────────────────────────────────────────────────────

def ft(font, text, color):
    """Render a text surface (antialiased)."""
    return font.render(str(text), True, color)

def blit_cx(surf, text_surf, cy):
    """Blit a surface centred horizontally at vertical midpoint cy."""
    x = (surf.get_width() - text_surf.get_width()) // 2
    y = cy - text_surf.get_height() // 2
    surf.blit(text_surf, (x, y))

def blit_at(surf, text_surf, x, y):
    surf.blit(text_surf, (x, y))

def draw_button(surf, font, text, rect, hover=False, color=None):
    bg = color if color else (BUTTON_HOVER if hover else BUTTON_COLOR)
    pygame.draw.rect(surf, bg, rect, border_radius=8)
    pygame.draw.rect(surf, BORDER_COLOR, rect, 2, border_radius=8)
    ts = ft(font, text, TEXT_COLOR)
    surf.blit(ts, (rect.centerx - ts.get_width() // 2,
                   rect.centery - ts.get_height() // 2))

def draw_panel(surf, rect, alpha=200):
    panel = pygame.Surface(rect.size, pygame.SRCALPHA)
    panel.fill((*PANEL_COLOR, alpha))
    surf.blit(panel, rect.topleft)
    pygame.draw.rect(surf, BORDER_COLOR, rect, 2, border_radius=10)

def draw_background(surf):
    surf.fill(BG_COLOR)
    for x in range(0, WINDOW_WIDTH, 40):
        for y in range(0, WINDOW_HEIGHT, 40):
            pygame.draw.circle(surf, (30, 30, 45), (x, y), 1)

# ── App ───────────────────────────────────────────────────────────────────────

class App:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock  = pygame.time.Clock()

        # pygame.font.SysFont works reliably on Windows/Mac/Linux
        self.font_lg = pygame.font.SysFont("Consolas,Courier New,monospace", 48, bold=True)
        self.font_md = pygame.font.SysFont("Consolas,Courier New,monospace", 26)
        self.font_sm = pygame.font.SysFont("Consolas,Courier New,monospace", 18)
        self.font_xs = pygame.font.SysFont("Consolas,Courier New,monospace", 14)

        self.settings      = load_settings()
        self.screen_name   = "menu"
        self.username      = ""
        self.player_id     = None
        self.personal_best = 0
        self.last_score    = 0
        self.last_level    = 1
        self.gs            = None
        self._lb_rows      = []

        self.db_ok = init_db()
        if not self.db_ok:
            print("[WARN] DB unavailable — running without persistence.")

    # ── Main loop ─────────────────────────────────────────────────────────────
    def run(self):
        while True:
            if   self.screen_name == "menu":        self._screen_menu()
            elif self.screen_name == "game":        self._screen_game()
            elif self.screen_name == "gameover":    self._screen_gameover()
            elif self.screen_name == "leaderboard": self._screen_leaderboard()
            elif self.screen_name == "settings":    self._screen_settings()
            else:
                self.screen_name = "menu"

    # ═════════════════════════════════════════════════════════════════════════
    # SCREEN: Main Menu
    # ═════════════════════════════════════════════════════════════════════════
    def _screen_menu(self):
        username_buf = list(self.username)
        input_active = True

        btn_play = pygame.Rect(300, 310, 200, 46)
        btn_lb   = pygame.Rect(300, 368, 200, 46)
        btn_set  = pygame.Rect(300, 426, 200, 46)
        btn_quit = pygame.Rect(300, 484, 200, 46)

        while self.screen_name == "menu":
            mouse = pygame.mouse.get_pos()
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    self._quit()
                if ev.type == pygame.KEYDOWN:
                    if input_active:
                        if ev.key == pygame.K_BACKSPACE:
                            if username_buf:
                                username_buf.pop()
                        elif ev.key == pygame.K_RETURN:
                            input_active = False
                        elif len(username_buf) < 20 and ev.unicode.isprintable():
                            username_buf.append(ev.unicode)
                if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                    if btn_play.collidepoint(mouse):
                        uname = "".join(username_buf).strip() or "Player"
                        self.username = uname
                        if self.db_ok:
                            self.player_id = get_or_create_player(uname)
                            self.personal_best = (
                                get_personal_best(self.player_id) if self.player_id else 0)
                        self.screen_name = "game"
                    elif btn_lb.collidepoint(mouse):
                        if self.db_ok:
                            self._lb_rows = get_leaderboard()
                        self.screen_name = "leaderboard"
                    elif btn_set.collidepoint(mouse):
                        self.screen_name = "settings"
                    elif btn_quit.collidepoint(mouse):
                        self._quit()

            draw_background(self.screen)
            blit_cx(self.screen, ft(self.font_lg, "SNAKE  DELUXE", ACCENT_COLOR), 75)
            blit_cx(self.screen, ft(self.font_xs,
                "Arrow keys to move  |  eat food  |  avoid walls", MUTED_COLOR), 112)

            # Username input box
            ub = pygame.Rect(240, 185, 320, 42)
            draw_panel(self.screen, ub, alpha=180)
            pygame.draw.rect(self.screen,
                ACCENT_COLOR if input_active else BORDER_COLOR, ub, 2, border_radius=8)
            blit_at(self.screen, ft(self.font_xs, "USERNAME", MUTED_COLOR), ub.x, ub.y - 18)
            display_name = "".join(username_buf) + ("|" if input_active else "")
            blit_at(self.screen,
                ft(self.font_sm, display_name or "Enter username...",
                   TEXT_COLOR if username_buf else MUTED_COLOR),
                ub.x + 12, ub.y + 10)

            for rect, label in [
                (btn_play, "PLAY"),
                (btn_lb,   "LEADERBOARD"),
                (btn_set,  "SETTINGS"),
                (btn_quit, "QUIT"),
            ]:
                draw_button(self.screen, self.font_sm, label, rect, rect.collidepoint(mouse))

            if not self.db_ok:
                blit_at(self.screen,
                    ft(self.font_xs, "DB offline — scores won't be saved", (200, 80, 80)),
                    10, WINDOW_HEIGHT - 22)

            pygame.display.flip()
            self.clock.tick(60)

    # ═════════════════════════════════════════════════════════════════════════
    # SCREEN: Game
    # ═════════════════════════════════════════════════════════════════════════
    def _screen_game(self):
        self.gs = GameState(self.settings)
        gs = self.gs
        snake_color = tuple(self.settings["snake_color"])

        SIDEBAR_W = 160
        SIDE_RECT = pygame.Rect(WINDOW_WIDTH - SIDEBAR_W, 0, SIDEBAR_W, WINDOW_HEIGHT)

        def cell_rect(c, r):
            return pygame.Rect(c * CELL_SIZE, r * CELL_SIZE, CELL_SIZE, CELL_SIZE)

        tick_event = pygame.USEREVENT + 1
        pygame.time.set_timer(tick_event, 1000 // gs.current_fps)

        dir_map = {
            pygame.K_UP: UP,    pygame.K_w: UP,
            pygame.K_DOWN: DOWN, pygame.K_s: DOWN,
            pygame.K_LEFT: LEFT, pygame.K_a: LEFT,
            pygame.K_RIGHT: RIGHT, pygame.K_d: RIGHT,
        }

        while self.screen_name == "game":
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    self._quit()
                if ev.type == pygame.KEYDOWN:
                    if ev.key in dir_map:
                        gs.set_direction(dir_map[ev.key])
                    elif ev.key == pygame.K_ESCAPE:
                        pygame.time.set_timer(tick_event, 0)
                        self.screen_name = "menu"
                        return
                if ev.type == tick_event:
                    result = gs.update()
                    pygame.time.set_timer(tick_event, 1000 // gs.current_fps)
                    if result == "game_over":
                        pygame.time.set_timer(tick_event, 0)
                        self._do_gameover(gs)
                        return

            # ── Render ────────────────────────────────────────────────────
            self.screen.fill(BG_COLOR)

            if self.settings.get("grid_overlay"):
                for c in range(GRID_COLS):
                    for r in range(GRID_ROWS):
                        pygame.draw.rect(self.screen, (25, 25, 35), cell_rect(c, r), 1)

            # Obstacles
            for (oc, or_) in gs.obstacles:
                pygame.draw.rect(self.screen, OBSTACLE_COLOR, cell_rect(oc, or_))
                pygame.draw.rect(self.screen, (80, 60, 40), cell_rect(oc, or_), 1)

            # Food
            now = pygame.time.get_ticks()
            for food in gs.foods:
                fc, fr = food.pos
                color = FOOD_COLORS[food.kind]
                pygame.draw.ellipse(self.screen, color, cell_rect(fc, fr).inflate(-2, -2))
                elapsed = now - food.spawn
                ratio   = max(0.0, 1.0 - elapsed / food.ttl)
                bar_w   = int((CELL_SIZE - 4) * ratio)
                if bar_w > 0:
                    pygame.draw.rect(self.screen, color,
                        pygame.Rect(fc * CELL_SIZE + 2,
                                    fr * CELL_SIZE + CELL_SIZE - 4, bar_w, 3))

            # Power-up — no text labels, shapes only
            if gs.powerup:
                import math
                pc, pr = gs.powerup.pos
                pu_color = POWERUP_COLORS[gs.powerup.kind]
                cr = cell_rect(pc, pr)
                cx_pu = cr.centerx
                cy_pu = cr.centery
                r_pu  = CELL_SIZE // 2 - 2
                if gs.powerup.kind == "speed":
                    # Lightning bolt shape
                    pts = [
                        (cx_pu - r_pu + 3, cy_pu - r_pu + 2),
                        (cx_pu + 2,         cy_pu - 1),
                        (cx_pu - 1,         cy_pu - 1),
                        (cx_pu + r_pu - 3,  cy_pu + r_pu - 2),
                        (cx_pu - 2,         cy_pu + 1),
                        (cx_pu + 1,         cy_pu + 1),
                    ]
                    pygame.draw.polygon(self.screen, pu_color, pts)
                elif gs.powerup.kind == "slow":
                    # Snowflake: 4 lines through centre
                    for angle in range(0, 180, 45):
                        rad = math.radians(angle)
                        dx  = int(r_pu * math.cos(rad))
                        dy  = int(r_pu * math.sin(rad))
                        pygame.draw.line(self.screen, pu_color,
                            (cx_pu - dx, cy_pu - dy),
                            (cx_pu + dx, cy_pu + dy), 2)
                else:  # shield — filled diamond
                    pts = [
                        (cx_pu,         cy_pu - r_pu),
                        (cx_pu + r_pu,  cy_pu),
                        (cx_pu,         cy_pu + r_pu),
                        (cx_pu - r_pu,  cy_pu),
                    ]
                    pygame.draw.polygon(self.screen, pu_color, pts)
                    pygame.draw.polygon(self.screen, WHITE, pts, 1)

            # Snake
            for i, (sc, sr) in enumerate(gs.snake):
                ratio = max(0.15, 1.0 - i * 0.02)
                seg_color = snake_color if i == 0 else (
                    int(snake_color[0] * ratio),
                    int(snake_color[1] * ratio),
                    int(snake_color[2] * ratio),
                )
                pygame.draw.rect(self.screen, seg_color,
                    cell_rect(sc, sr).inflate(-2, -2), border_radius=3)

            if gs.shield_active:
                hc, hr = gs.head
                pygame.draw.rect(self.screen, BLUE, cell_rect(hc, hr), 3, border_radius=3)

            # ── Sidebar ───────────────────────────────────────────────────
            self.screen.fill(PANEL_COLOR, SIDE_RECT)
            pygame.draw.line(self.screen, BORDER_COLOR,
                SIDE_RECT.topleft, SIDE_RECT.bottomleft, 2)

            sx, sy = SIDE_RECT.x + 10, 16

            def side_row(label, value, val_color=TEXT_COLOR):
                nonlocal sy
                self.screen.blit(ft(self.font_xs, label, MUTED_COLOR), (sx, sy)); sy += 16
                self.screen.blit(ft(self.font_md, str(value), val_color), (sx, sy)); sy += 32

            side_row("SCORE",  gs.score,  ACCENT_COLOR)
            side_row("LEVEL",  gs.level)
            side_row("LENGTH", len(gs.snake))
            side_row("BEST",   self.personal_best, YELLOW)
            side_row("PLAYER", self.username[:10])

            sy += 6
            if gs.active_effect:
                rem = max(0, gs.effect_end_time - now) // 1000
                eff = ("SPEED +" if gs.active_effect == "speed" else "SLOW -") + f"{rem}s"
                self.screen.blit(ft(self.font_xs, eff, POWERUP_COLORS[gs.active_effect]), (sx, sy))
                sy += 18
            if gs.shield_active:
                self.screen.blit(ft(self.font_xs, "SHIELD ON", BLUE), (sx, sy))
                sy += 18

            # ── Food + Power-up legend (bottom of sidebar) ───────────────
            legend_items = [
                ("Normal",  "+10",  FOOD_COLORS["normal"],  "circle"),
                ("Bonus",   "+25",  FOOD_COLORS["bonus"],   "circle"),
                ("Rare",    "+50",  FOOD_COLORS["rare"],    "circle"),
                ("Poison",  "-2",   FOOD_COLORS["poison"],  "circle"),
                ("Speed",   "",     POWERUP_COLORS["speed"],  "bolt"),
                ("Slow",    "",     POWERUP_COLORS["slow"],   "snow"),
                ("Shield",  "",     POWERUP_COLORS["shield"], "diamond"),
            ]
            legend_line_h = 17
            legend_total  = len(legend_items) * legend_line_h + 20
            sy = WINDOW_HEIGHT - legend_total - 4

            self.screen.blit(ft(self.font_xs, "FOOD / PWR-UP", MUTED_COLOR), (sx, sy))
            sy += 15
            pygame.draw.line(self.screen, BORDER_COLOR,
                (sx, sy), (SIDE_RECT.right - 6, sy), 1)
            sy += 4

            import math as _m
            for label, pts_text, col, shape in legend_items:
                icx = sx + 7
                icy = sy + 7
                r   = 5
                if shape == "circle":
                    pygame.draw.ellipse(self.screen, col,
                        pygame.Rect(icx - r, icy - r, r*2, r*2))
                elif shape == "bolt":
                    bpts = [
                        (icx - r + 2, icy - r),
                        (icx + 1,     icy - 1),
                        (icx - 1,     icy - 1),
                        (icx + r - 2, icy + r),
                        (icx - 1,     icy + 1),
                        (icx + 1,     icy + 1),
                    ]
                    pygame.draw.polygon(self.screen, col, bpts)
                elif shape == "snow":
                    for ang in range(0, 180, 45):
                        rad = _m.radians(ang)
                        ddx = int(r * _m.cos(rad))
                        ddy = int(r * _m.sin(rad))
                        pygame.draw.line(self.screen, col,
                            (icx - ddx, icy - ddy), (icx + ddx, icy + ddy), 2)
                elif shape == "diamond":
                    dpts = [(icx, icy - r), (icx + r, icy),
                            (icx, icy + r), (icx - r, icy)]
                    pygame.draw.polygon(self.screen, col, dpts)

                self.screen.blit(ft(self.font_xs, label, col), (sx + 16, sy))
                if pts_text:
                    pts_col = ACCENT_COLOR if pts_text.startswith("+") else RED
                    pts_surf = ft(self.font_xs, pts_text, pts_col)
                    self.screen.blit(pts_surf,
                        (SIDE_RECT.right - pts_surf.get_width() - 6, sy))
                sy += legend_line_h

            pygame.display.flip()
            self.clock.tick(120)

    def _do_gameover(self, gs):
        self.last_score = gs.score
        self.last_level = gs.level
        if self.db_ok and self.player_id:
            save_session(self.player_id, gs.score, gs.level)
            self.personal_best = get_personal_best(self.player_id)
        self.screen_name = "gameover"

    # ═════════════════════════════════════════════════════════════════════════
    # SCREEN: Game Over
    # ═════════════════════════════════════════════════════════════════════════
    def _screen_gameover(self):
        btn_retry = pygame.Rect(220, 390, 160, 46)
        btn_menu  = pygame.Rect(420, 390, 160, 46)

        while self.screen_name == "gameover":
            mouse = pygame.mouse.get_pos()
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    self._quit()
                if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                    if btn_retry.collidepoint(mouse): self.screen_name = "game"
                    elif btn_menu.collidepoint(mouse): self.screen_name = "menu"
                if ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_r:      self.screen_name = "game"
                    elif ev.key == pygame.K_ESCAPE: self.screen_name = "menu"

            draw_background(self.screen)
            panel = pygame.Rect(190, 155, 420, 280)
            draw_panel(self.screen, panel)

            blit_cx(self.screen, ft(self.font_lg, "GAME  OVER", RED), 210)
            blit_at(self.screen, ft(self.font_sm, f"Score  :  {self.last_score}", TEXT_COLOR), 270, 272)
            blit_at(self.screen, ft(self.font_sm, f"Level  :  {self.last_level}", TEXT_COLOR), 270, 308)
            blit_at(self.screen, ft(self.font_sm, f"Best   :  {self.personal_best}", YELLOW),  270, 344)

            draw_button(self.screen, self.font_sm, "RETRY",     btn_retry, btn_retry.collidepoint(mouse))
            draw_button(self.screen, self.font_sm, "MAIN MENU", btn_menu,  btn_menu.collidepoint(mouse))
            blit_cx(self.screen, ft(self.font_xs, "R = retry     ESC = menu", MUTED_COLOR), 452)

            pygame.display.flip()
            self.clock.tick(60)

    # ═════════════════════════════════════════════════════════════════════════
    # SCREEN: Leaderboard
    # ═════════════════════════════════════════════════════════════════════════
    def _screen_leaderboard(self):
        btn_back = pygame.Rect(330, 540, 140, 42)

        while self.screen_name == "leaderboard":
            mouse = pygame.mouse.get_pos()
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    self._quit()
                if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                    if btn_back.collidepoint(mouse): self.screen_name = "menu"
                if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                    self.screen_name = "menu"

            draw_background(self.screen)
            blit_cx(self.screen, ft(self.font_lg, "LEADERBOARD", YELLOW), 50)

            hx, hy = 50, 100
            for cx, label in [(30,"#"),(90,"USERNAME"),(260,"SCORE"),(360,"LEVEL"),(450,"DATE")]:
                blit_at(self.screen, ft(self.font_sm, label, ACCENT_COLOR), hx + cx, hy)
            pygame.draw.line(self.screen, BORDER_COLOR, (50, hy + 28), (750, hy + 28), 1)

            row_y = hy + 38
            rank_colors = [YELLOW, (192, 192, 192), (205, 127, 50)]
            for i, row in enumerate(self._lb_rows[:10]):
                rc = rank_colors[i] if i < 3 else TEXT_COLOR
                blit_at(self.screen, ft(self.font_sm, str(i + 1),                 MUTED_COLOR),  hx + 30,  row_y)
                blit_at(self.screen, ft(self.font_sm, str(row["username"])[:14],   rc),            hx + 90,  row_y)
                blit_at(self.screen, ft(self.font_sm, str(row["score"]),           ACCENT_COLOR),  hx + 260, row_y)
                blit_at(self.screen, ft(self.font_sm, str(row["level_reached"]),   TEXT_COLOR),    hx + 360, row_y)
                blit_at(self.screen, ft(self.font_sm, str(row.get("played_date","?")), MUTED_COLOR), hx + 450, row_y)
                row_y += 36

            if not self._lb_rows:
                blit_cx(self.screen, ft(self.font_md, "No scores yet — play a game!", MUTED_COLOR), 310)

            draw_button(self.screen, self.font_sm, "BACK", btn_back, btn_back.collidepoint(mouse))
            pygame.display.flip()
            self.clock.tick(60)

    # ═════════════════════════════════════════════════════════════════════════
    # SCREEN: Settings
    # ═════════════════════════════════════════════════════════════════════════
    def _screen_settings(self):
        local = {**self.settings, "snake_color": list(self.settings["snake_color"])}

        btn_grid  = pygame.Rect(300, 200, 200, 42)
        btn_sound = pygame.Rect(300, 260, 200, 42)
        btn_save  = pygame.Rect(300, 470, 200, 46)

        COLOR_OPTIONS = [
            ("Green",  [50,  200,  50]),
            ("Blue",   [50,  100, 220]),
            ("Red",    [220,  60,  60]),
            ("Yellow", [240, 200,  30]),
            ("Cyan",   [30,  220, 220]),
            ("Purple", [160,  40, 220]),
            ("White",  [220, 220, 220]),
            ("Orange", [230, 130,  20]),
        ]
        color_rects = [(pygame.Rect(220 + i * 50, 360, 38, 38), rgb, name)
                       for i, (name, rgb) in enumerate(COLOR_OPTIONS)]

        while self.screen_name == "settings":
            mouse = pygame.mouse.get_pos()
            hovered_name = ""
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    self._quit()
                if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                    self.screen_name = "menu"
                if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                    if btn_grid.collidepoint(mouse):
                        local["grid_overlay"] = not local["grid_overlay"]
                    elif btn_sound.collidepoint(mouse):
                        local["sound"] = not local["sound"]
                    elif btn_save.collidepoint(mouse):
                        self.settings = {**local, "snake_color": list(local["snake_color"])}
                        save_settings(self.settings)
                        self.screen_name = "menu"
                    for rect, rgb, _ in color_rects:
                        if rect.collidepoint(mouse):
                            local["snake_color"] = list(rgb)

            draw_background(self.screen)
            blit_cx(self.screen, ft(self.font_lg, "SETTINGS", ACCENT_COLOR), 70)

            grid_on = local["grid_overlay"]
            draw_button(self.screen, self.font_sm,
                f"Grid Overlay:  {'ON [v]' if grid_on else 'OFF'}",
                btn_grid, btn_grid.collidepoint(mouse),
                color=ACCENT_COLOR if grid_on else None)

            snd_on = local["sound"]
            draw_button(self.screen, self.font_sm,
                f"Sound:         {'ON [v]' if snd_on else 'OFF'}",
                btn_sound, btn_sound.collidepoint(mouse),
                color=ACCENT_COLOR if snd_on else None)

            blit_cx(self.screen, ft(self.font_sm, "Snake Color", MUTED_COLOR), 335)
            for rect, rgb, name in color_rects:
                pygame.draw.rect(self.screen, rgb, rect, border_radius=6)
                if list(rgb) == list(local["snake_color"]):
                    pygame.draw.rect(self.screen, WHITE, rect, 3, border_radius=6)
                else:
                    pygame.draw.rect(self.screen, BORDER_COLOR, rect, 1, border_radius=6)
                if rect.collidepoint(mouse):
                    hovered_name = name

            if hovered_name:
                blit_cx(self.screen, ft(self.font_xs, hovered_name, TEXT_COLOR), 415)

            draw_button(self.screen, self.font_md, "SAVE & BACK", btn_save,
                btn_save.collidepoint(mouse), color=DARK_GREEN)

            pygame.display.flip()
            self.clock.tick(60)

    def _quit(self):
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    App().run()