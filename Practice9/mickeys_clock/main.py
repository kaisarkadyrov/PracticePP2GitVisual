import os
import sys
import datetime
import pygame

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
W, H = 620, 720
FPS = 60  

def main():
    pygame.init()
    pygame.display.set_caption("Mickey's Clock")
    screen = pygame.display.set_mode((W, H))
    clock = pygame.time.Clock()

    from clock import ClockRenderer
    renderer = ClockRenderer(screen, BASE_DIR)

    fullscreen = False
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_q, pygame.K_ESCAPE):
                    running = False

                elif event.key == pygame.K_f:
                    fullscreen = not fullscreen
                    flags = pygame.FULLSCREEN if fullscreen else 0
                    screen = pygame.display.set_mode((W, H), flags)
                    renderer.screen = screen

        now = datetime.datetime.now()

        minutes = now.minute + now.second / 60
        seconds = now.second

        renderer.draw(minutes, seconds)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()