import os
import pygame

def blitRotate(surf, image, pos, originPos, angle):
    image_rect = image.get_rect(topleft=(pos[0] - originPos[0], pos[1] - originPos[1])) #чтобы точка originPos внутри неё совпала с точкой pos на экране
    #  Этот вектор показывает как далеко центр картинки находится от оси вращения, чтобы потом скорректировать положение повёрнутой картинки.
    offset_center_to_pivot = pygame.math.Vector2(pos) - image_rect.center # Это вектор от центра картинки до основания стрелки
    rotated_offset = offset_center_to_pivot.rotate(-angle) #
    rotated_center = (pos[0] - rotated_offset.x, pos[1] - rotated_offset.y)
    rotated_image = pygame.transform.rotozoom(image, angle, 1.0)
    rotated_rect = rotated_image.get_rect(center=rotated_center)
    surf.blit(rotated_image, rotated_rect)

class ClockRenderer:
    def __init__(self, screen, base_dir):
        self.screen = screen
        self.W, self.H = screen.get_size()
        self.cx, self.cy = self.W // 2, self.H // 2 - 20

        face_path = os.path.join(base_dir, "images", "clock_face.png")
        raw_face = pygame.image.load(face_path).convert_alpha()
        size = min(self.W, self.H) - 60
        self.face = pygame.transform.smoothscale(raw_face, (size, size))
        self.face_rect = self.face.get_rect(center=(self.cx, self.cy))
        self.radius = size // 2

        hand_path = os.path.join(base_dir, "images", "mickey_hand.png")
        raw_hand = pygame.image.load(hand_path).convert_alpha()
        
        self.hand = pygame.transform.smoothscale(raw_hand, (150, 180))

        self.pivot = (self.hand.get_width() // 2, self.hand.get_height() - 15)

        pygame.font.init()
        self.font = pygame.font.SysFont("monospace", 40)

    def draw(self, minutes, seconds):
        self.screen.fill((255, 255, 255))
        self.screen.blit(self.face, self.face_rect)
        center = (self.cx, self.cy)

        sec_angle = -(seconds * 6) 
        min_angle = -(minutes * 6)

        blitRotate(self.screen, self.hand, center, self.pivot, sec_angle)

        blitRotate(self.screen, self.hand, center, self.pivot, min_angle)

        pygame.draw.circle(self.screen, (0, 0, 0), center, 8)

        
        time_text = f"{int(minutes % 60):02d}:{int(seconds):02d}"
        text_surf = self.font.render(time_text, True, (0, 0, 0))
        self.screen.blit(text_surf, text_surf.get_rect(center=(self.cx, self.cy + self.radius + 40)))