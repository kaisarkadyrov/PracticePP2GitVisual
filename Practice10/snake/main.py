import pygame
import random
import sys

# Константы
WIDTH, HEIGHT = 600, 400
BLOCK_SIZE = 20

# Цвета
WHITE = (255, 255, 255)
RED = (213, 50, 80)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 102)

class SnakeGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption('Snake Game')
        self.clock = pygame.time.Clock()
        self.font_style = pygame.font.SysFont("arial", 25)
        self.score_font = pygame.font.SysFont("arial", 20)
        self.reset_game()

    def reset_game(self):
        """Полный сброс параметров для новой игры."""
        self.snake_pos = [[100, 60], [80, 60], [60, 60]]
        self.direction = 'RIGHT'
        self.change_to = self.direction
        self.score = 0
        self.level = 1
        self.speed = 10
        self.food_pos = self.generate_food()
        self.game_over = False
        self.game_close = False # Состояние экрана "Game Over"

    def generate_food(self):
        """Генерирует еду так, чтобы она не попала на змейку."""
        while True:
            x = random.randrange(0, WIDTH // BLOCK_SIZE) * BLOCK_SIZE
            y = random.randrange(0, HEIGHT // BLOCK_SIZE) * BLOCK_SIZE
            pos = [x, y]
            if pos not in self.snake_pos:
                return pos

    def draw_ui(self):
        """Отрисовка счета и уровня на экране."""
        value = self.score_font.render(f"Score: {self.score}  Level: {self.level}", True, YELLOW)
        self.screen.blit(value, [10, 10])

    def show_game_over_screen(self):
        """Экран после столкновения."""
        self.screen.fill(BLACK)
        msg = self.font_style.render("GAME OVER", True, RED)
        instr = self.font_style.render("Press R-Restart or Q-Quit", True, WHITE)
        score_msg = self.font_style.render(f"Final Score: {self.score}", True, YELLOW)
        
        # Центрирование текста
        self.screen.blit(msg, [WIDTH / 2.5, HEIGHT / 3])
        self.screen.blit(score_msg, [WIDTH / 2.7, HEIGHT / 2.2])
        self.screen.blit(instr, [WIDTH / 4, HEIGHT / 1.6])
        
        pygame.display.update()

    def run(self):
        while not self.game_over:

            # Цикл экрана Game Over
            while self.game_close:
                self.show_game_over_screen()
                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_q: # Выход
                            self.game_over = True
                            self.game_close = False
                        if event.key == pygame.K_r: # Перезапуск
                            self.reset_game()
                    if event.type == pygame.QUIT:
                        self.game_over = True
                        self.game_close = False

            # Основная логика игры
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game_over = True
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP and self.direction != 'DOWN':
                        self.change_to = 'UP'
                    elif event.key == pygame.K_DOWN and self.direction != 'UP':
                        self.change_to = 'DOWN'
                    elif event.key == pygame.K_LEFT and self.direction != 'RIGHT':
                        self.change_to = 'LEFT'
                    elif event.key == pygame.K_RIGHT and self.direction != 'LEFT':
                        self.change_to = 'RIGHT'

            self.direction = self.change_to
            head = list(self.snake_pos[0])

            if self.direction == 'UP': head[1] -= BLOCK_SIZE
            elif self.direction == 'DOWN': head[1] += BLOCK_SIZE
            elif self.direction == 'LEFT': head[0] -= BLOCK_SIZE
            elif self.direction == 'RIGHT': head[0] += BLOCK_SIZE

            self.snake_pos.insert(0, head)

            # Проверка столкновения со стенами
            if head[0] < 0 or head[0] >= WIDTH or head[1] < 0 or head[1] >= HEIGHT:
                self.game_close = True

            # Проверка столкновения с собой
            if head in self.snake_pos[1:]:
                self.game_close = True

            # Поедание еды
            if head == self.food_pos:
                self.score += 1
                # Повышение уровня каждые 3 очка
                if self.score % 3 == 0:
                    self.level += 1
                    self.speed += 2
                self.food_pos = self.generate_food()
            else:
                self.snake_pos.pop()

            # Отрисовка кадра
            self.screen.fill(BLACK)
            pygame.draw.rect(self.screen, RED, [self.food_pos[0], self.food_pos[1], BLOCK_SIZE, BLOCK_SIZE])
            
            for segment in self.snake_pos:
                pygame.draw.rect(self.screen, GREEN, [segment[0], segment[1], BLOCK_SIZE, BLOCK_SIZE])
            
            self.draw_ui()
            pygame.display.update()
            self.clock.tick(self.speed)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = SnakeGame()
    game.run()