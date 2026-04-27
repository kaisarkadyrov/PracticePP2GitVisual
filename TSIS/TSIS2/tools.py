import pygame
import math


def flood_fill(surface, x, y, fill_color):
    w, h = surface.get_size()
    if not (0 <= x < w and 0 <= y < h):
        return
    fill_mapped   = surface.map_rgb(fill_color[:3])
    target_mapped = surface.map_rgb(surface.get_at((x, y))[:3])
    if target_mapped == fill_mapped:
        return
    px = pygame.PixelArray(surface)
    stack = [(x, y)]
    while stack:
        cx, cy = stack.pop()
        if 0 <= cx < w and 0 <= cy < h and px[cx, cy] == target_mapped:
            px[cx, cy] = fill_mapped
            stack += [(cx+1,cy),(cx-1,cy),(cx,cy+1),(cx,cy-1)]
    px.close()


def draw_shape(surface, tool, start, end, color, size):
    x1, y1 = start
    x2, y2 = end
    if tool in ("pencil", "line"):
        pygame.draw.line(surface, color, start, end, size)
    elif tool == "rect":
        r = pygame.Rect(min(x1,x2), min(y1,y2), abs(x2-x1), abs(y2-y1))
        if r.width and r.height: pygame.draw.rect(surface, color, r, size)
    elif tool == "circle":
        cx, cy = (x1+x2)//2, (y1+y2)//2
        r = int(math.hypot(x2-x1, y2-y1) / 2) # diagonal
        if r: pygame.draw.circle(surface, color, (cx, cy), r, size)
    elif tool == "square":
        s = min(abs(x2-x1), abs(y2-y1))
        sx = x1 if x2 >= x1 else x1 - s
        sy = y1 if y2 >= y1 else y1 - s
        if s: pygame.draw.rect(surface, color, (sx, sy, s, s), size)
    elif tool == "rtriangle":
        pygame.draw.polygon(surface, color, [start, (x1,y2), end], size)
    elif tool == "rhombus":
        cx, cy = (x1+x2)//2, (y1+y2)//2
        hw, hh = abs(x2-x1)//2, abs(y2-y1)//2
        if hw and hh:
            pygame.draw.polygon(surface, color,
                [(cx,cy-hh),(cx+hw,cy),(cx,cy+hh),(cx-hw,cy)], size)