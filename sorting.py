import pygame
import sys
import random
import time

WIDTH, HEIGHT = 900, 650

BG =        (30, 30, 40)
PANEL =     (40, 42, 58)
BTN =       (60, 80, 120)
BTN_HOVER = (80, 110, 160)
BTN_RED =   (140, 50, 60)
BTN_RED_H = (180, 70, 80)
TEXT =      (220, 220, 220)
ACCENT =    (100, 180, 255)
GREEN =     (80, 200, 120)
ORANGE =    (230, 160, 50)
BORDER =    (90, 90, 120)
HIGHLIGHT = (255, 220, 50)
BAR_DEFAULT = (80, 120, 200)
BAR_COMPARE = (255, 140, 0)
BAR_SWAP    = (220, 60, 60)
BAR_SORTED  = (80, 200, 120)

def get_fonts():
    return {
        "title": pygame.font.SysFont("consolas", 28, bold=True),
        "btn":   pygame.font.SysFont("consolas", 20),
        "small": pygame.font.SysFont("consolas", 16),
        "node":  pygame.font.SysFont("consolas", 14),
    }

def draw_btn(surface, fonts, text, rect, hover=False, red=False):
    if red:
        col = BTN_RED_H if hover else BTN_RED
    else:
        col = BTN_HOVER if hover else BTN
    pygame.draw.rect(surface, col, rect, border_radius=6)
    pygame.draw.rect(surface, BORDER, rect, 2, border_radius=6)
    lbl = fonts["btn"].render(text, True, TEXT)
    surface.blit(lbl, (rect.x + (rect.width - lbl.get_width())//2,
                       rect.y + (rect.height - lbl.get_height())//2))

def back_button(surface, fonts):
    r = pygame.Rect(10, 10, 90, 35)
    mx, my = pygame.mouse.get_pos()
    draw_btn(surface, fonts, "< Back", r, r.collidepoint(mx, my))
    return r


def draw_bars(surface, fonts, arr, colors, offset_y=160, label_arr=None):
    n = len(arr)
    max_val = max(arr) if arr else 1
    bar_area_w = WIDTH - 80
    bar_w = max(8, bar_area_w // n - 2)
    max_bar_h = HEIGHT - offset_y - 80

    for i, val in enumerate(arr):
        bh = int(val / max_val * max_bar_h)
        bx = 40 + i * (bar_w + 2)
        by = offset_y + max_bar_h - bh
        col = colors[i] if i < len(colors) else BAR_DEFAULT
        pygame.draw.rect(surface, col, (bx, by, bar_w, bh), border_radius=3)
        if bar_w >= 20:
            lbl = fonts["node"].render(str(val), True, TEXT)
            surface.blit(lbl, (bx + bar_w//2 - lbl.get_width()//2, by - 18))


def bubble_sort_steps(arr):
    """Generate list of (array_copy, compare_indices, swap_happened) steps"""
    steps = []
    a = arr[:]
    n = len(a)
    sorted_from = n  # tracks sorted portion from the right
    for i in range(n):
        swapped = False
        for j in range(0, n - i - 1):
            steps.append((a[:], (j, j+1), False, sorted_from))
            if a[j] > a[j+1]:
                a[j], a[j+1] = a[j+1], a[j]
                steps.append((a[:], (j, j+1), True, sorted_from))
                swapped = True
        sorted_from = n - i - 1
        if not swapped:
            break
    steps.append((a[:], (-1, -1), False, 0))
    return steps


def selection_sort_steps(arr):
    steps = []
    a = arr[:]
    n = len(a)
    for i in range(n):
        min_idx = i
        for j in range(i+1, n):
            steps.append((a[:], (min_idx, j), False, i))
            if a[j] < a[min_idx]:
                min_idx = j
        if min_idx != i:
            a[i], a[min_idx] = a[min_idx], a[i]
            steps.append((a[:], (i, min_idx), True, i))
        else:
            steps.append((a[:], (i, i), False, i))
    steps.append((a[:], (-1, -1), False, n))
    return steps


def run_sorting(screen, clock):
    fonts = get_fonts()

    arr_size = 18
    arr = random.sample(range(5, 100), arr_size)

    mode = "bubble"   # bubble | selection
    steps = []
    step_idx = 0
    playing = False
    done = False
    speed = 8   # frames between steps
    frame_count = 0
    msg = "Press Start to begin"

    def rebuild_steps():
        nonlocal steps, step_idx, playing, done, msg
        if mode == "bubble":
            steps = bubble_sort_steps(arr[:])
        else:
            steps = selection_sort_steps(arr[:])
        step_idx = 0
        playing = False
        done = False
        msg = "Press Start to begin"

    rebuild_steps()

    running = True
    while running:
        mx, my = pygame.mouse.get_pos()
        screen.fill(BG)

        title_str = f"Sorting – {'Bubble Sort' if mode=='bubble' else 'Selection Sort'}"
        screen.blit(fonts["title"].render(title_str, True, ACCENT), (30, 10))

        # tabs
        tab_b = pygame.Rect(30, 55, 130, 34)
        tab_s = pygame.Rect(175, 55, 150, 34)
        pygame.draw.rect(screen, ACCENT if mode=="bubble" else BTN, tab_b, border_radius=6)
        pygame.draw.rect(screen, ACCENT if mode=="selection" else BTN, tab_s, border_radius=6)
        screen.blit(fonts["btn"].render("Bubble", True, BG if mode=="bubble" else TEXT), (tab_b.x+25, tab_b.y+7))
        screen.blit(fonts["btn"].render("Selection", True, BG if mode=="selection" else TEXT), (tab_s.x+18, tab_s.y+7))

        btns = {
            "Start":    pygame.Rect(340, 55, 100, 34),
            "Reset":    pygame.Rect(453, 55, 100, 34),
            "New Array":pygame.Rect(566, 55, 130, 34),
        }
        for t, r in btns.items():
            draw_btn(screen, fonts, t, r, r.collidepoint(mx, my), red=(t=="Reset"))

        # speed label
        spd_lbl = fonts["small"].render(f"Speed: {'Fast' if speed<=4 else 'Med' if speed<=10 else 'Slow'}", True, TEXT)
        screen.blit(spd_lbl, (710, 62))
        spd_up = pygame.Rect(800, 58, 28, 28)
        spd_dn = pygame.Rect(835, 58, 28, 28)
        draw_btn(screen, fonts, "+", spd_up, spd_up.collidepoint(mx, my))
        draw_btn(screen, fonts, "-", spd_dn, spd_dn.collidepoint(mx, my))

        # get current frame state
        if steps and step_idx < len(steps):
            cur_arr, (ci, cj), swapped, sorted_mark = steps[step_idx]
        else:
            cur_arr = arr
            ci = cj = -1
            swapped = False
            sorted_mark = 0

        # build colors
        colors = []
        for i in range(len(cur_arr)):
            if done or step_idx == len(steps) - 1:
                colors.append(BAR_SORTED)
            elif mode == "bubble":
                if i >= sorted_mark:
                    colors.append(BAR_SORTED)
                elif i == ci or i == cj:
                    colors.append(BAR_SWAP if swapped else BAR_COMPARE)
                else:
                    colors.append(BAR_DEFAULT)
            else:  # selection
                if i < sorted_mark:
                    colors.append(BAR_SORTED)
                elif i == ci:
                    colors.append(BAR_SWAP if swapped else HIGHLIGHT)
                elif i == cj:
                    colors.append(BAR_COMPARE)
                else:
                    colors.append(BAR_DEFAULT)

        draw_bars(screen, fonts, cur_arr, colors)

        # legend
        legend = [
            (BAR_DEFAULT, "Unsorted"),
            (BAR_COMPARE, "Comparing"),
            (BAR_SWAP,    "Swapping"),
            (BAR_SORTED,  "Sorted"),
        ]
        for idx, (col, lbl) in enumerate(legend):
            lx = 30 + idx * 160
            pygame.draw.rect(screen, col, (lx, HEIGHT - 35, 16, 16), border_radius=3)
            screen.blit(fonts["small"].render(lbl, True, TEXT), (lx + 22, HEIGHT - 36))

        # step counter
        sc = fonts["small"].render(f"Step {step_idx}/{len(steps)-1}", True, ORANGE)
        screen.blit(sc, (WIDTH - 160, HEIGHT - 36))

        # msg
        if msg:
            screen.blit(fonts["small"].render(msg, True, HIGHLIGHT), (30, 105))

        back_r = back_button(screen, fonts)
        pygame.display.flip()

        # advance step
        if playing and not done:
            frame_count += 1
            if frame_count >= speed:
                frame_count = 0
                step_idx += 1
                if step_idx >= len(steps) - 1:
                    step_idx = len(steps) - 1
                    done = True
                    playing = False
                    msg = "Sorting complete!"

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                if back_r.collidepoint(pos):
                    return
                if tab_b.collidepoint(pos) and mode != "bubble":
                    mode = "bubble"; rebuild_steps()
                if tab_s.collidepoint(pos) and mode != "selection":
                    mode = "selection"; rebuild_steps()
                if btns["Start"].collidepoint(pos):
                    if done:
                        rebuild_steps()
                    playing = True
                    msg = f"Running {'Bubble' if mode=='bubble' else 'Selection'} Sort..."
                if btns["Reset"].collidepoint(pos):
                    rebuild_steps()
                if btns["New Array"].collidepoint(pos):
                    arr = random.sample(range(5, 100), arr_size)
                    rebuild_steps()
                if spd_up.collidepoint(pos):
                    speed = max(1, speed - 3)
                if spd_dn.collidepoint(pos):
                    speed = min(30, speed + 3)

        clock.tick(60)
