import pygame

class Ball:
    def __init__(self, screen_w, screen_h):
        self.screen_w = screen_w
        self.screen_h = screen_h
        
        self.x = float(screen_w // 2)
        self.y = float(screen_h // 2)
        
        self.radius = 25
        self.speed = 5 
        self.color = (255, 0, 0)

    def update(self, keys):
        if keys[pygame.K_UP]:
            if self.y - self.radius - self.speed >= 0:
                self.y -= self.speed
        if keys[pygame.K_DOWN]:
            if self.y + self.radius + self.speed <= self.screen_h:
                self.y += self.speed
        if keys[pygame.K_LEFT]:
            if self.x - self.radius - self.speed >= 0:
                self.x -= self.speed
        if keys[pygame.K_RIGHT]:
            if self.x + self.radius + self.speed <= self.screen_w:
                self.x += self.speed

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)