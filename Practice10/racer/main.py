import pygame, sys
from pygame.locals import *
import random, time

# Инициализация
pygame.init()

FPS = 60
FramePerSec = pygame.time.Clock()

# Цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED   = (255, 0, 0)
GREEN = (0, 255, 0)
GRAY  = (200, 200, 200)

# Размеры экрана
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600

# Глобальные переменные
SPEED = 10
SCORE = 0
COIN_SCORE = 0
PLAYER_SPEED = 6

# Шрифты
font = pygame.font.SysFont("Verdana", 60)
font_small = pygame.font.SysFont("Verdana", 20)
font_button = pygame.font.SysFont("Verdana", 30)

DISPLAYSURF = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Racer v9 - Restart Menu")

# --- ЗАГРУЗКА РЕСУРСОВ ---
try:
    bg_image = pygame.image.load("Images/AnimatedStreet.png").convert()
    bg_image = pygame.transform.scale(bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
    
    CAR_WIDTH, CAR_HEIGHT = 80, 120
    player_img = pygame.image.load("Images/blue_car.png").convert_alpha()
    player_img = pygame.transform.scale(player_img, (CAR_WIDTH, CAR_HEIGHT))

    enemy_raw = pygame.image.load("Images/red_car.png").convert_alpha()
    enemy_raw = pygame.transform.scale(enemy_raw, (CAR_WIDTH, CAR_HEIGHT))
    enemy_img = pygame.transform.rotate(enemy_raw, 180)

    coin_img = pygame.image.load("Images/coin.png").convert_alpha()
    coin_img = pygame.transform.scale(coin_img, (40, 40))
except:
    print("Ошибка загрузки картинок!")
    pygame.quit()
    sys.exit()

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__() 
        self.image = enemy_img
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.spawn()
    def spawn(self):
        self.rect.center = (random.randint(60, SCREEN_WIDTH-60), -200)
    def move(self):
        global SCORE
        self.rect.y += SPEED 
        if (self.rect.top > SCREEN_HEIGHT):
            SCORE += 1
            self.spawn()

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__() 
        self.image = player_img
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.center = (SCREEN_WIDTH/2, 520)
    def move(self):
        keys = pygame.key.get_pressed()
        if (keys[K_LEFT] or keys[K_a]) and self.rect.left > 0:
            self.rect.move_ip(-PLAYER_SPEED, 0)
        if (keys[K_RIGHT] or keys[K_d]) and self.rect.right < SCREEN_WIDTH:
            self.rect.move_ip(PLAYER_SPEED, 0)

class Coin(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = coin_img
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.spawn()
    def spawn(self):
        self.rect.center = (random.randint(40, SCREEN_WIDTH - 40), -100)
    def move(self):
        self.rect.y += SPEED
        if (self.rect.top > SCREEN_HEIGHT):
            self.spawn()

# Функция для отрисовки экрана завершения игры
def game_over_screen():
    while True:
        DISPLAYSURF.fill(RED)
        msg = font.render("GAME OVER", True, BLACK)
        DISPLAYSURF.blit(msg, (msg.get_rect(center=(SCREEN_WIDTH/2, 150))))
        
        # Инфо о счете
        score_msg = font_small.render(f"Final Score: {SCORE} | Coins: {COIN_SCORE}", True, WHITE)
        DISPLAYSURF.blit(score_msg, (score_msg.get_rect(center=(SCREEN_WIDTH/2, 230))))

        # Кнопки (прямоугольники)
        btn_restart = pygame.Rect(100, 300, 200, 50)
        btn_exit = pygame.Rect(100, 380, 200, 50)
        
        pygame.draw.rect(DISPLAYSURF, GREEN, btn_restart)
        pygame.draw.rect(DISPLAYSURF, GRAY, btn_exit)

        # Текст на кнопках
        txt_restart = font_button.render("RESTART", True, BLACK)
        txt_exit = font_button.render("EXIT", True, BLACK)
        DISPLAYSURF.blit(txt_restart, (txt_restart.get_rect(center=btn_restart.center)))
        DISPLAYSURF.blit(txt_exit, (txt_exit.get_rect(center=btn_exit.center)))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == MOUSEBUTTONDOWN:
                if btn_restart.collidepoint(event.pos):
                    return True  # Возвращаемся в игру
                if btn_exit.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()

def reset_game():
    global SPEED, SCORE, COIN_SCORE
    SPEED = 10
    SCORE = 0
    COIN_SCORE = 0
    # Пересоздаем объекты
    new_p = Player()
    new_e = Enemy()
    new_c = Coin()
    
    enemies = pygame.sprite.Group()
    enemies.add(new_e)
    coins = pygame.sprite.Group()
    coins.add(new_c)
    all_sprites = pygame.sprite.Group()
    all_sprites.add(new_p, new_e, new_c)
    
    return new_p, new_e, new_c, enemies, coins, all_sprites

# Основной запуск
while True:
    P1, E1, C1, enemies, coins, all_sprites = reset_game()
    bg_y1, bg_y2 = 0, -SCREEN_HEIGHT
    
    INC_SPEED = pygame.USEREVENT + 1
    pygame.time.set_timer(INC_SPEED, 3000)

    playing = True
    while playing:
        for event in pygame.event.get():
            if event.type == INC_SPEED:
                SPEED += 1
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

        bg_y1 += SPEED
        bg_y2 += SPEED
        if bg_y1 >= SCREEN_HEIGHT: bg_y1 = -SCREEN_HEIGHT
        if bg_y2 >= SCREEN_HEIGHT: bg_y2 = -SCREEN_HEIGHT

        DISPLAYSURF.blit(bg_image, (0, bg_y1))
        DISPLAYSURF.blit(bg_image, (0, bg_y2))
        
        DISPLAYSURF.blit(font_small.render(f"Coins: {COIN_SCORE}", True, WHITE), (SCREEN_WIDTH - 120, 10))
        DISPLAYSURF.blit(font_small.render(f"Score: {SCORE}", True, WHITE), (10, 10))

        for entity in all_sprites:
            entity.move()
            DISPLAYSURF.blit(entity.image, entity.rect)

        # Сбор монет
        if pygame.sprite.spritecollide(P1, coins, False, pygame.sprite.collide_mask):
            COIN_SCORE += 1
            C1.spawn()

        # Столкновение
        if pygame.sprite.spritecollide(P1, enemies, False, pygame.sprite.collide_mask):
            playing = False # Выходим из игрового цикла в экран меню

        pygame.display.update()
        FramePerSec.tick(FPS)

    # Если вышли из игрового цикла — запускаем экран Game Over
    if not game_over_screen():
        break