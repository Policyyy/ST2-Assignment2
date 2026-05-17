import pygame
import sys
from data_structures import run_data_structures
from sorting import run_sorting
from graphs import run_graphs
from puzzles import run_puzzles

pygame.init()

WIDTH, HEIGHT = 900, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("DSA Explorer")

clock = pygame.time.Clock()

# colours
BG = (30, 30, 40)
BTN = (60, 80, 120)
BTN_HOVER = (80, 110, 160)
TEXT_COL = (220, 220, 220)
TITLE_COL = (100, 180, 255)
BORDER = (90, 90, 120)

font_title = pygame.font.SysFont("consolas", 42, bold=True)
font_btn = pygame.font.SysFont("consolas", 26)
font_sub = pygame.font.SysFont("consolas", 17)


def draw_button(surface, text, rect, hover=False):
    col = BTN_HOVER if hover else BTN
    pygame.draw.rect(surface, col, rect, border_radius=8)
    pygame.draw.rect(surface, BORDER, rect, 2, border_radius=8)
    label = font_btn.render(text, True, TEXT_COL)
    lx = rect.x + (rect.width - label.get_width()) // 2
    ly = rect.y + (rect.height - label.get_height()) // 2
    surface.blit(label, (lx, ly))


def main_menu():
    buttons = {
        "Data Structures": pygame.Rect(300, 180, 300, 55),
        "Sorting Algorithms": pygame.Rect(300, 260, 300, 55),
        "Graph Traversal":   pygame.Rect(300, 300, 300, 55),
        "Puzzle Challenges": pygame.Rect(300, 375, 300, 55),
        "Quit":              pygame.Rect(350, 460, 200, 45),
    }

    while True:
        mx, my = pygame.mouse.get_pos()
        screen.fill(BG)

        title = font_title.render("DSA Explorer", True, TITLE_COL)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 80))

        sub = font_sub.render("Select a module to begin", True, (150, 150, 170))
        screen.blit(sub, (WIDTH//2 - sub.get_width()//2, 135))

        for text, rect in buttons.items():
            hover = rect.collidepoint(mx, my)
            draw_button(screen, text, rect, hover)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                for text, rect in buttons.items():
                    if rect.collidepoint(event.pos):
                        if text == "Data Structures":
                            run_data_structures(screen, clock)
                        elif text == "Sorting Algorithms":
                            run_sorting(screen, clock)
                        elif text == "Graph Traversal":
                            run_graphs(screen, clock)
                        elif text == "Puzzle Challenges":
                            run_puzzles(screen, clock)
                        elif text == "Quit":
                            pygame.quit()
                            sys.exit()

        clock.tick(60)


if __name__ == "__main__":
    main_menu()
