import pygame
import sys
from ball import Ball

def main():
    pygame.init()
    
    W, H = 800, 600
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("Moving Ball")
    
    clock = pygame.time.Clock()
    ball = Ball(W, H)
    
    running = True
    while running:
        clock.tick(60) 

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        ball.update(keys)

        screen.fill((255, 255, 255))
        ball.draw(screen)
        
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()