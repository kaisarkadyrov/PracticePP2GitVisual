import pygame, sys, os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from persistence import load_settings, save_settings, load_leaderboard, save_score
from ui import (Button, TextInput, draw_hud, draw_menu, draw_name_input,
                draw_leaderboard, draw_gameover, draw_settings)
from racer import (Player, Enemy, Obstacle, OilSpill, MovingBarrier,
                   NitroStrip, Coin, PowerUp, draw_road, RACE_LENGTH)

# ── Init ──────────────────────────────────────────────────────────────────────
pygame.init()
pygame.mixer.init()
W, H  = 600, 600
CX    = W // 2
screen    = pygame.display.set_mode((W, H))
pygame.display.set_caption("TSIS 3: Racer")
clock     = pygame.time.Clock()
font      = pygame.font.Font(None, 30)
big_font  = pygame.font.Font(None, 64)

# ── Audio ─────────────────────────────────────────────────────────────────────
def _load_snd(name):
    try: return pygame.mixer.Sound(os.path.join('assets', 'sounds', name))
    except Exception: return None

snd_crash   = _load_snd('crash.wav')
snd_powerup = _load_snd('powerup.wav')
music_ok = False
try:
    pygame.mixer.music.load(os.path.join('assets', 'sounds', 'bg_music.mp3'))
    music_ok = True
except Exception: pass

settings = load_settings()

def play_music():
    if music_ok and settings['sound']: pygame.mixer.music.play(-1)
def play_sfx(s):
    if settings['sound'] and s: s.play()

# ── Sprite groups ─────────────────────────────────────────────────────────────
all_sprites  = pygame.sprite.Group()
enemies      = pygame.sprite.Group()
obstacles    = pygame.sprite.Group()
oil_spills   = pygame.sprite.Group()
barriers     = pygame.sprite.Group()
nitro_strips = pygame.sprite.Group()
powerups     = pygame.sprite.Group()
coins        = pygame.sprite.Group()

# ── Game state ────────────────────────────────────────────────────────────────
state           = "MENU"
player_name     = "Player"
player          = None
score           = 0
distance        = 0
coins_collected = 0
speed_tier      = 0

# ── Buttons ───────────────────────────────────────────────────────────────────
menu_btns  = [Button(CX-100, 170, 200, 48, "Play"),
              Button(CX-100, 232, 200, 48, "Leaderboard"),
              Button(CX-100, 294, 200, 48, "Settings"),
              Button(CX-100, 356, 200, 48, "Quit")]
btn_back   = Button(CX-100, 522, 200, 48, "Back")
btn_retry  = Button(CX-100, 360, 200, 48, "Retry")
btn_to_menu= Button(CX-100, 422, 200, 48, "Main Menu")
set_toggles= [Button(CX+30, 130, 150, 38, "Toggle"),
              Button(CX+30, 220, 150, 38, "Toggle"),
              Button(CX+30, 310, 150, 38, "Toggle")]
name_input = TextInput(CX-100, 272, 200, 42, placeholder="your name")

# ── Spawn event IDs ───────────────────────────────────────────────────────────
EV = {k: pygame.USEREVENT + i for i, k in
      enumerate(["ENEMY","OBS","OIL","BARRIER","NITRO","POWERUP","COIN"], 1)}

def set_timers(tier):
    pygame.time.set_timer(EV["ENEMY"],   max(500, 1500 - tier * 90))
    pygame.time.set_timer(EV["OBS"],     max(900, 2400 - tier * 130))
    pygame.time.set_timer(EV["OIL"],     max(1500, 4000 - tier * 100))
    pygame.time.set_timer(EV["BARRIER"], 7000)
    pygame.time.set_timer(EV["NITRO"],   9000)
    pygame.time.set_timer(EV["POWERUP"], 5500)
    pygame.time.set_timer(EV["COIN"],    1600)

# ── Helpers ───────────────────────────────────────────────────────────────────
ALL_HAZARD_GROUPS = lambda: [enemies, obstacles, oil_spills, barriers]

def no_overlap(spr):
    return all(not pygame.sprite.spritecollideany(spr, g) for g in ALL_HAZARD_GROUPS())

def add(spr, *groups):
    all_sprites.add(spr)
    for g in groups: g.add(spr)

def reset_game():
    global player, score, distance, coins_collected, speed_tier
    for g in (all_sprites, enemies, obstacles, oil_spills, barriers,
              nitro_strips, powerups, coins):
        g.empty()
    player = Player(settings['car_color'])
    all_sprites.add(player)
    score = distance = coins_collected = speed_tier = 0
    set_timers(0)
    play_music()

def handle_spawn(ev_type):
    tier = speed_tier
    if ev_type == EV["ENEMY"]:
        e = Enemy(settings['difficulty'], tier)
        if no_overlap(e): add(e, enemies)
    elif ev_type == EV["OBS"]:
        o = Obstacle(tier)
        if no_overlap(o): add(o, obstacles)
    elif ev_type == EV["OIL"]:
        o = OilSpill()
        if no_overlap(o): add(o, oil_spills)
    elif ev_type == EV["BARRIER"]:
        b = MovingBarrier()
        add(b, barriers)
    elif ev_type == EV["NITRO"]:
        ns = NitroStrip()
        add(ns, nitro_strips)
    elif ev_type == EV["POWERUP"]:
        p = PowerUp()
        if no_overlap(p): add(p, powerups)
    elif ev_type == EV["COIN"]:
        c = Coin()
        if no_overlap(c): add(c, coins)

def handle_collisions():
    global score, distance, coins_collected, state
    # Nitro strip
    for _ in pygame.sprite.spritecollide(player, nitro_strips, True):
        player.activate_powerup("Nitro", 3500)
    # Oil spill – slow player
    if pygame.sprite.spritecollideany(player, oil_spills):
        player.apply_slow(2500)
    # Coins
    for c in pygame.sprite.spritecollide(player, coins, True):
        score += c.value
        coins_collected += 1
    # Power-ups
    for hit in pygame.sprite.spritecollide(player, powerups, True):
        play_sfx(snd_powerup)
        if hit.type == "Nitro":
            player.activate_powerup("Nitro", 4000)
        elif hit.type == "Shield":
            player.activate_powerup("Shield", 4000)
        elif hit.type == "Repair":
            player.crashes_allowed += 1
    # Deadly collisions
    if not player.shield_active:
        h_e = pygame.sprite.spritecollideany(player, enemies)
        h_o = pygame.sprite.spritecollideany(player, obstacles)
        h_b = pygame.sprite.spritecollideany(player, barriers)
        hit = h_e or h_o or h_b
        if hit:
            if player.crashes_allowed > 0:
                player.crashes_allowed -= 1
                player.activate_powerup("Shield", 2000)
                player.start_flash(36)
                play_sfx(snd_crash)
                hit.kill()
            else:
                play_sfx(snd_crash)
                pygame.mixer.music.stop()
                save_score(player_name, int(score), int(distance), coins_collected)
                state = "GAMEOVER"

# ── Main loop ─────────────────────────────────────────────────────────────────
running = True
while running:
    clock.tick(60)
    events = pygame.event.get()

    for ev in events:
        if ev.type == pygame.QUIT:
            running = False

        # MENU
        if state == "MENU":
            if menu_btns[0].is_clicked(ev): state = "NAME_INPUT"
            if menu_btns[1].is_clicked(ev): state = "LEADERBOARD"
            if menu_btns[2].is_clicked(ev): state = "SETTINGS"
            if menu_btns[3].is_clicked(ev): running = False

        # NAME INPUT
        elif state == "NAME_INPUT":
            name_input.handle_event(ev)
            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_RETURN:
                player_name = name_input.text.strip() or "Player"
                reset_game()
                state = "PLAY"

        # PLAY – spawn events
        elif state == "PLAY":
            if ev.type in EV.values():
                handle_spawn(ev.type)

        # LEADERBOARD / SETTINGS
        elif state in ("LEADERBOARD", "SETTINGS"):
            if btn_back.is_clicked(ev):
                save_settings(settings)
                state = "MENU"
            if state == "SETTINGS":
                if set_toggles[0].is_clicked(ev):
                    settings['sound'] = not settings['sound']
                if set_toggles[1].is_clicked(ev):
                    cols = ["red", "blue", "green"]
                    settings['car_color'] = cols[(cols.index(settings['car_color']) + 1) % 3]
                if set_toggles[2].is_clicked(ev):
                    settings['difficulty'] = "hard" if settings['difficulty'] == "normal" else "normal"

        # GAME OVER
        elif state == "GAMEOVER":
            if btn_retry.is_clicked(ev):   reset_game(); state = "PLAY"
            if btn_to_menu.is_clicked(ev): state = "MENU"

    # ── DRAW ─────────────────────────────────────────────────────────────────
    draw_road(screen, distance)

    if state == "MENU":
        draw_menu(screen, font, big_font, menu_btns)

    elif state == "NAME_INPUT":
        draw_name_input(screen, font, big_font, name_input)

    elif state == "PLAY":
        all_sprites.update()
        # Speed tier update
        new_tier = int(score // 500)
        if new_tier != speed_tier:
            speed_tier = new_tier
            set_timers(speed_tier)

        # Score / distance
        nitro_mult = 2.0 if player.nitro_active else 1.0
        distance   += (0.1 + speed_tier * 0.02) * nitro_mult
        score      += 0.4 if player.nitro_active else 0.15
        # Nitro world-scroll boost
        if player.nitro_active:
            for spr in list(enemies) + list(obstacles) + list(oil_spills) + \
                        list(barriers) + list(coins) + list(powerups):
                spr.rect.y += 3

        handle_collisions()

        # Draw (player handled separately for flash)
        for spr in all_sprites:
            if spr is player: player.draw(screen)
            else: screen.blit(spr.image, spr.rect)

        draw_hud(screen, font, score, distance, coins_collected, player)

        # Finish line
        if distance >= RACE_LENGTH:
            save_score(player_name, int(score), int(distance), coins_collected)
            state = "GAMEOVER"

    elif state == "LEADERBOARD":
        draw_leaderboard(screen, font, big_font, load_leaderboard(), btn_back)

    elif state == "SETTINGS":
        draw_settings(screen, font, big_font, settings, set_toggles, btn_back)

    elif state == "GAMEOVER":
        draw_gameover(screen, font, big_font, score, distance,
                      coins_collected, btn_retry, btn_to_menu)

    pygame.display.flip()

pygame.quit()
sys.exit()