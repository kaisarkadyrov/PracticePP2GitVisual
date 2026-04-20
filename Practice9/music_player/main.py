import pygame
import os
import sys
from player import MusicPlayer

W, H = 600, 500
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MUSIC_DIR = os.path.join(BASE_DIR, "music")

def main():
    pygame.init()
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("Pygame Music Player")
    clock = pygame.time.Clock()
    
    player = MusicPlayer(screen, MUSIC_DIR)
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p: # Play
                    player.play_track()
                elif event.key == pygame.K_s: # Stop
                    player.stop_track()
                elif event.key == pygame.K_n: # Next
                    player.next_track()
                elif event.key == pygame.K_b: # Back
                    player.prev_track()
                elif event.key == pygame.K_q: # Quit
                    running = False

        player.draw()
        pygame.display.flip()
        clock.tick(30)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()