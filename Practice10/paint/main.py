import pygame

def main():
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    clock = pygame.time.Clock()
    
    radius = 5
    color = (255, 0, 0)
    mode = 'pen'
    
    canvas = pygame.Surface((640, 480))
    canvas.fill((0, 0, 0))
    
    drawing = False
    start_pos = None
    last_pos = None

    while True:
        screen.fill((0, 0, 0))
        screen.blit(canvas, (0, 0))
        
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r: color = (255, 0, 0)
                elif event.key == pygame.K_g: color = (0, 255, 0)
                elif event.key == pygame.K_b: color = (0, 0, 255)
                
                elif event.key == pygame.K_p: mode = 'pen'
                elif event.key == pygame.K_s: mode = 'rect'
                elif event.key == pygame.K_o: mode = 'circle'
                elif event.key == pygame.K_e: 
                    mode = 'pen'
                    color = (0, 0, 0)

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    drawing = True
                    start_pos = event.pos
                    last_pos = event.pos
                elif event.button == 3:
                    radius = min(100, radius + 1)
                elif event.button == 4:
                    radius = min(100, radius + 1)
                elif event.button == 5:
                    radius = max(1, radius - 1)
                elif event.button == 2:
                    radius = max(1, radius - 1)

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and drawing:
                    if mode == 'rect':
                        draw_rect(canvas, start_pos, mouse_pos, color, radius)
                    elif mode == 'circle':
                        draw_circle(canvas, start_pos, mouse_pos, color, radius)
                    drawing = False

            if event.type == pygame.MOUSEMOTION:
                if drawing and mode == 'pen':
                    draw_line(canvas, last_pos, mouse_pos, radius, color)
                    last_pos = mouse_pos

        if drawing:
            if mode == 'rect':
                draw_rect(screen, start_pos, mouse_pos, color, radius)
            elif mode == 'circle':
                draw_circle(screen, start_pos, mouse_pos, color, radius)

        pygame.display.set_caption(f"Tool: {mode} | Size: {radius} | Color: {color}")
        pygame.display.flip()
        clock.tick(60)

def draw_line(surface, start, end, width, color):
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    distance = max(abs(dx), abs(dy), 1)
    for i in range(distance):
        x = int(start[0] + float(i) / distance * dx)
        y = int(start[1] + float(i) / distance * dy)
        pygame.draw.circle(surface, color, (x, y), width)

def draw_rect(surface, start, end, color, thickness):
    x1, y1 = start
    x2, y2 = end
    rect_x = min(x1, x2)
    rect_y = min(y1, y2)
    width = abs(x1 - x2)
    height = abs(y1 - y2)
    if width > 0 and height > 0:
        pygame.draw.rect(surface, color, (rect_x, rect_y, width, height), thickness)

def draw_circle(surface, start, end, color, thickness):
    x1, y1 = start
    x2, y2 = end
    r = int(((x1 - x2)**2 + (y1 - y2)**2)**0.5)
    if r > 0:
        pygame.draw.circle(surface, color, (x1, y1), r, thickness)

if __name__ == "__main__":
    main()