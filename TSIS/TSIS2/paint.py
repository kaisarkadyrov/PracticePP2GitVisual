import pygame, sys, math
from datetime import datetime
from tools import flood_fill, draw_shape

pygame.init()

W, H = 1000, 650
TOOLBAR = 160
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Paint")
canvas = pygame.Surface((W - TOOLBAR, H))
canvas.fill((255, 255, 255))
clock = pygame.time.Clock()
font = pygame.font.SysFont("arial", 13)

TOOLS   = ["pencil","line","rect","circle","square","rtriangle","etriangle","rhombus","fill","text","eraser"]
LABELS  = ["Pencil","Line","Rectangle","Circle","Square","Right Triangle","Equil. Triangle","Rhombus","Fill","Text","Eraser"]
KEYS    = [pygame.K_p, pygame.K_l, pygame.K_r, pygame.K_c, pygame.K_q,
           pygame.K_t, pygame.K_e, pygame.K_h, pygame.K_f, pygame.K_x, pygame.K_z]
COLORS  = [(0,0,0),(255,255,255),(220,50,50),(50,200,80),(60,110,220),
           (255,200,0),(255,140,0),(160,0,200),(0,200,200),(200,100,150),(100,60,30),(150,150,150)]
SIZES   = {1: 2, 2: 5, 3: 10}

tool    = "pencil"
color   = COLORS[0]
size_k  = 1
drawing = False
start   = prev = None
snap    = None

# text state
txt_active = False
txt_pos    = (0, 0)
txt_buf    = ""
txt_font   = pygame.font.SysFont("monospace", 22)


def draw_toolbar():
    pygame.draw.rect(screen, (45, 45, 55), (0, 0, TOOLBAR, H))
    y = 8
    for t, label in zip(TOOLS, LABELS):
        bg = (80, 120, 180) if t == tool else (60, 60, 75)
        r = pygame.Rect(6, y, TOOLBAR-12, 26)
        pygame.draw.rect(screen, bg, r, border_radius=4)
        screen.blit(font.render(label, True, (220,220,220)), (10, y+6))
        y += 30
    y += 6
    # sizes
    for i, (k, px) in enumerate(SIZES.items()):
        bg = (80,120,180) if k == size_k else (60,60,75)
        r = pygame.Rect(6 + i*50, y, 44, 24)
        pygame.draw.rect(screen, bg, r, border_radius=4)
        screen.blit(font.render(f"{px}px", True, (220,220,220)), (10+i*50, y+5))
    y += 30
    # colors
    for i, c in enumerate(COLORS):
        rx = 6 + (i % 4) * 36
        ry = y + (i // 4) * 36
        pygame.draw.rect(screen, c, (rx, ry, 32, 32), border_radius=4)
        if c == color:
            pygame.draw.rect(screen, (255,255,255), (rx,ry,32,32), 2, border_radius=4)
    y += (math.ceil(len(COLORS)/4)) * 36 + 6
    # active color
    pygame.draw.rect(screen, color, (6, y, TOOLBAR-12, 20), border_radius=4)
    screen.blit(font.render("Ctrl+S=save", True, (120,120,130)), (6, y+26))


def toolbar_click(pos):
    global tool, size_k, color, txt_active, txt_buf
    x, y = pos
    # tools
    ty = 8
    for t in TOOLS:
        if pygame.Rect(6, ty, TOOLBAR-12, 26).collidepoint(x, y):
            tool = t
            if txt_active: txt_active = False; txt_buf = ""
            return
        ty += 30
    ty += 6
    # sizes
    for i, k in enumerate(SIZES):
        if pygame.Rect(6+i*50, ty, 44, 24).collidepoint(x, y):
            size_k = k; return
    ty += 30
    # colors
    for i, c in enumerate(COLORS):
        rx = 6 + (i%4)*36
        ry = ty + (i//4)*36
        if pygame.Rect(rx, ry, 32, 32).collidepoint(x, y):
            color = c; return


running = True
while running:
    clock.tick(60)

    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False

        elif e.type == pygame.KEYDOWN:
            mods = pygame.key.get_mods()
            if e.key == pygame.K_s and (mods & pygame.KMOD_CTRL):
                ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                pygame.image.save(canvas, f"canvas_{ts}.png")
                pygame.display.set_caption(f"Paint — saved canvas_{ts}.png")
                continue
            if txt_active:
                if   e.key == pygame.K_RETURN:
                    if txt_buf:
                        canvas.blit(txt_font.render(txt_buf, True, color), txt_pos)
                    txt_active = False; txt_buf = ""
                elif e.key == pygame.K_ESCAPE:
                    txt_active = False; txt_buf = ""
                elif e.key == pygame.K_BACKSPACE:
                    txt_buf = txt_buf[:-1]
                elif e.unicode and e.unicode.isprintable():
                    txt_buf += e.unicode
                continue
            if e.key == pygame.K_1: size_k = 1
            elif e.key == pygame.K_2: size_k = 2
            elif e.key == pygame.K_3: size_k = 3
            for k, t in zip(KEYS, TOOLS):
                if e.key == k: tool = t

        elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            mx, my = e.pos
            if mx < TOOLBAR:
                toolbar_click(e.pos); continue
            cx, cy = mx - TOOLBAR, my
            if tool == "text":
                if txt_active:
                    if txt_buf: canvas.blit(txt_font.render(txt_buf, True, color), txt_pos)
                txt_active = True; txt_pos = (cx, cy); txt_buf = ""; continue
            if tool == "fill":
                flood_fill(canvas, cx, cy, color); continue
            drawing = True
            start = prev = (cx, cy)
            if tool not in ("pencil", "eraser"):
                snap = canvas.copy()

        elif e.type == pygame.MOUSEMOTION and drawing:
            mx, my = e.pos
            cx, cy = mx - TOOLBAR, my
            sz = SIZES[size_k]
            if tool == "pencil":
                pygame.draw.line(canvas, color, prev, (cx,cy), sz)
                prev = (cx, cy)
            elif tool == "eraser":
                pygame.draw.circle(canvas, (255,255,255), (cx,cy), sz*4)
                prev = (cx, cy)
            else:
                snap = canvas.copy()   # update snapshot so preview refreshes

        elif e.type == pygame.MOUSEBUTTONUP and e.button == 1 and drawing:
            drawing = False
            mx, my = e.pos
            cx, cy = mx - TOOLBAR, my
            sz = SIZES[size_k]
            if tool not in ("pencil", "eraser", "fill", "text"):
                draw_shape(canvas, tool, start, (cx,cy), color, sz)
            snap = None; start = None

    # --- render ---
    screen.fill((30, 30, 38))

    # canvas: show preview while dragging a shape
    disp = canvas.copy()
    if drawing and snap is not None and tool not in ("pencil","eraser"):
        mx, my = pygame.mouse.get_pos()
        cx, cy = mx - TOOLBAR, my
        draw_shape(disp, tool, start, (cx,cy), color, SIZES[size_k])

    # text preview
    if txt_active:
        disp.blit(txt_font.render(txt_buf + "|", True, color), txt_pos)

    screen.blit(disp, (TOOLBAR, 0))
    draw_toolbar()
    pygame.draw.line(screen, (60,60,70), (TOOLBAR,0), (TOOLBAR,H))
    pygame.display.flip()

pygame.quit()
sys.exit()