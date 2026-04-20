import pygame
import os

class MusicPlayer:
    def __init__(self, screen, music_dir):
        self.screen = screen
        self.music_dir = music_dir
        
        self.playlist = [f for f in os.listdir(music_dir) if f.endswith(('.mp3', '.wav'))]
        self.current_idx = 0
        self.is_playing = False
        
        pygame.mixer.init()
        
        self.font = pygame.font.SysFont("Arial", 24)
        self.title_font = pygame.font.SysFont("Arial", 32, bold=True)

    def play_track(self):
        if self.playlist:
            track_path = os.path.join(self.music_dir, self.playlist[self.current_idx])
            pygame.mixer.music.load(track_path)
            pygame.mixer.music.play()
            self.is_playing = True

    def stop_track(self):
        pygame.mixer.music.stop()
        self.is_playing = False

    def next_track(self):
        if self.playlist:
            self.current_idx = (self.current_idx + 1) % len(self.playlist)
            self.play_track()

    def prev_track(self):
        if self.playlist:
            self.current_idx = (self.current_idx - 1) % len(self.playlist)
            self.play_track()

    def draw(self):
        self.screen.fill((30, 30, 30)) 
        
        if not self.playlist:
            text = self.font.render("No music files found in /music folder", True, (255, 255, 255))
            self.screen.blit(text, (50, 100))
            return

        current_track = self.playlist[self.current_idx]
        title_surf = self.title_font.render(f"Now Playing:", True, (0, 255, 127))
        name_surf = self.font.render(current_track, True, (255, 255, 255))
        
        self.screen.blit(title_surf, (50, 50))
        self.screen.blit(name_surf, (50, 100))

        controls = [
            "P - Play",
            "S - Stop",
            "N - Next",
            "B - Back (Previous)",
            "Q - Quit"
        ]
        
        for i, line in enumerate(controls):
            ctrl_surf = self.font.render(line, True, (150, 150, 150))
            self.screen.blit(ctrl_surf, (50, 200 + i * 30))

        status = "Playing" if self.is_playing else "Stopped"
        color = (0, 255, 0) if self.is_playing else (255, 0, 0)
        status_surf = self.font.render(f"Status: {status}", True, color)
        self.screen.blit(status_surf, (50, 400))