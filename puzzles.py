import pygame
import sys
import heapq
from collections import deque

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

# grid colours
COL_EMPTY =    (50, 52, 68)
COL_WALL =     (30, 30, 40)
COL_START =    (220, 80, 80)
COL_END =      (80, 200, 120)
COL_OPEN =     (100, 160, 220)
COL_CLOSED =   (60, 80, 140)
COL_PATH =     (255, 220, 50)
COL_GRID =     (60, 62, 78)


def get_fonts():
    return {
        "title": pygame.font.SysFont("consolas", 28, bold=True),
        "btn":   pygame.font.SysFont("consolas", 20),
        "small": pygame.font.SysFont("consolas", 16),
        "node":  pygame.font.SysFont("consolas", 14, bold=True),
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


# ─── A* Pathfinding 

ROWS, COLS = 20, 28
CELL = 26
GRID_X = 40
GRID_Y = 110


def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def astar(grid, start, end):
    """Returns list of steps: (open_set, closed_set, current, path_so_far)"""
    steps = []
    open_heap = []
    heapq.heappush(open_heap, (0, start))
    came_from = {}
    g_score = {start: 0}
    f_score = {start: heuristic(start, end)}
    open_set = {start}
    closed_set = set()

    while open_heap:
        _, current = heapq.heappop(open_heap)
        open_set.discard(current)

        if current == end:
            # reconstruct path
            path = []
            node = current
            while node in came_from:
                path.append(node)
                node = came_from[node]
            path.append(start)
            path.reverse()
            steps.append((set(open_set), set(closed_set), current, path))
            return steps

        closed_set.add(current)
        steps.append((set(open_set), set(closed_set), current, []))

        r, c = current
        for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
            nr, nc = r+dr, c+dc
            if 0 <= nr < ROWS and 0 <= nc < COLS and grid[nr][nc] != 1:
                nb = (nr, nc)
                if nb in closed_set:
                    continue
                tentative_g = g_score[current] + 1
                if tentative_g < g_score.get(nb, float('inf')):
                    came_from[nb] = current
                    g_score[nb] = tentative_g
                    f_score[nb] = tentative_g + heuristic(nb, end)
                    if nb not in open_set:
                        heapq.heappush(open_heap, (f_score[nb], nb))
                        open_set.add(nb)

    steps.append((set(), set(closed_set), None, []))
    return steps


def run_pathfinding(screen, clock, fonts):
    grid = [[0]*COLS for _ in range(ROWS)]
    start = (2, 2)
    end = (ROWS-3, COLS-3)
    steps = []
    step_idx = 0
    playing = False
    done = False
    speed = 2
    frame_count = 0
    mode = "wall"   # wall | start | end
    msg = "Click grid to place walls | Right-click to erase | Set Start/End with buttons"

    def rebuild():
        nonlocal steps, step_idx, playing, done
        steps = astar(grid, start, end)
        step_idx = 0
        playing = False
        done = False

    running = True
    while running:
        mx, my = pygame.mouse.get_pos()
        screen.fill(BG)

        screen.blit(fonts["title"].render("Puzzle – A* Pathfinding", True, ACCENT), (30, 10))

        btns = {
            "Run A*":     pygame.Rect(30, 65, 100, 34),
            "Reset":      pygame.Rect(143, 65, 90, 34),
            "Clear":      pygame.Rect(246, 65, 90, 34),
            "Set Start":  pygame.Rect(349, 65, 110, 34),
            "Set End":    pygame.Rect(472, 65, 100, 34),
            "Wall":       pygame.Rect(585, 65, 80, 34),
        }
        for t, r in btns.items():
            active = (t == "Wall" and mode == "wall") or \
                     (t == "Set Start" and mode == "start") or \
                     (t == "Set End" and mode == "end")
            col = ACCENT if active else (BTN_RED if t in ("Reset","Clear") else BTN)
            hover = r.collidepoint(mx, my)
            pygame.draw.rect(screen, (BTN_HOVER if hover and not active else col), r, border_radius=6)
            pygame.draw.rect(screen, BORDER, r, 2, border_radius=6)
            lbl = fonts["btn"].render(t, True, BG if active else TEXT)
            screen.blit(lbl, (r.x+(r.width-lbl.get_width())//2, r.y+(r.height-lbl.get_height())//2))

        # get current step state
        if steps and step_idx < len(steps):
            open_s, closed_s, current, path = steps[step_idx]
        else:
            open_s, closed_s, current, path = set(), set(), None, []

        # draw grid
        for r in range(ROWS):
            for c in range(COLS):
                x = GRID_X + c * CELL
                y = GRID_Y + r * CELL
                cell = (r, c)
                if cell == start:
                    col = COL_START
                elif cell == end:
                    col = COL_END
                elif path and cell in path:
                    col = COL_PATH
                elif grid[r][c] == 1:
                    col = COL_WALL
                elif cell == current:
                    col = HIGHLIGHT
                elif cell in closed_s:
                    col = COL_CLOSED
                elif cell in open_s:
                    col = COL_OPEN
                else:
                    col = COL_EMPTY
                pygame.draw.rect(screen, col, (x+1, y+1, CELL-2, CELL-2), border_radius=2)

        # legend
        legend = [
            (COL_START, "Start"), (COL_END, "End"), (COL_WALL, "Wall"),
            (COL_OPEN, "Open"), (COL_CLOSED, "Closed"), (COL_PATH, "Path"),
        ]
        for i, (col, lbl) in enumerate(legend):
            lx = 30 + i * 128
            pygame.draw.rect(screen, col, (lx, HEIGHT-30, 14, 14), border_radius=3)
            screen.blit(fonts["small"].render(lbl, True, TEXT), (lx+18, HEIGHT-32))

        if msg:
            screen.blit(fonts["small"].render(msg, True, HIGHLIGHT), (30, HEIGHT-55))

        back_r = back_button(screen, fonts)
        pygame.display.flip()

        # auto advance
        if playing and not done:
            frame_count += 1
            if frame_count >= speed:
                frame_count = 0
                step_idx += 1
                if step_idx >= len(steps) - 1:
                    step_idx = len(steps) - 1
                    done = True
                    playing = False
                    if steps and steps[-1][3]:
                        msg = f"Path found! Length: {len(steps[-1][3])} cells"
                    else:
                        msg = "No path found!"

        # mouse drag for walls
        mouse_pressed = pygame.mouse.get_pressed()
        if mouse_pressed[0] or mouse_pressed[2]:
            gx = (mx - GRID_X) // CELL
            gy = (my - GRID_Y) // CELL
            if 0 <= gy < ROWS and 0 <= gx < COLS and mode == "wall":
                cell = (gy, gx)
                if cell != start and cell != end:
                    grid[gy][gx] = 1 if mouse_pressed[0] else 0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                if back_r.collidepoint(pos):
                    return
                if btns["Run A*"].collidepoint(pos):
                    rebuild()
                    playing = True
                    msg = "Running A*..."
                elif btns["Reset"].collidepoint(pos):
                    rebuild()
                    msg = "Reset — press Run A* to go again"
                elif btns["Clear"].collidepoint(pos):
                    grid = [[0]*COLS for _ in range(ROWS)]
                    steps = []; step_idx = 0; playing = False; done = False
                    msg = "Grid cleared"
                elif btns["Set Start"].collidepoint(pos):
                    mode = "start"; msg = "Click a cell to set start"
                elif btns["Set End"].collidepoint(pos):
                    mode = "end"; msg = "Click a cell to set end"
                elif btns["Wall"].collidepoint(pos):
                    mode = "wall"; msg = "Click/drag to place walls, right-click to erase"
                else:
                    # grid click
                    gx = (mx - GRID_X) // CELL
                    gy = (my - GRID_Y) // CELL
                    if 0 <= gy < ROWS and 0 <= gx < COLS:
                        cell = (gy, gx)
                        if mode == "start" and cell != end:
                            start = cell
                            mode = "wall"
                            msg = "Start set"
                        elif mode == "end" and cell != start:
                            end = cell
                            mode = "wall"
                            msg = "End set"

        clock.tick(60)


# ─── Event Queue Simulator ─────────────────────────────────────────────────────

class Event:
    def __init__(self, name, priority, time):
        self.name = name
        self.priority = priority
        self.time = time

    def __lt__(self, other):
        if self.priority != other.priority:
            return self.priority < other.priority
        return self.time < other.time


EVENT_TEMPLATES = [
    ("Login Request",    1, 1),
    ("Payment Process",  2, 2),
    ("Send Email",       3, 3),
    ("Database Query",   2, 1),
    ("File Upload",      3, 2),
    ("Auth Check",       1, 3),
    ("API Call",         2, 4),
    ("Cache Refresh",    3, 1),
    ("Log Write",        4, 2),
    ("Session Timeout",  1, 5),
]

PRIORITY_COLS = {
    1: (220, 80, 80),
    2: (230, 160, 50),
    3: (100, 180, 255),
    4: (80, 200, 120),
}
PRIORITY_LABELS = {1: "Critical", 2: "High", 3: "Medium", 4: "Low"}


def run_event_queue(screen, clock, fonts):
    heap = []
    processed = []
    template_idx = [0]
    msg = "Add events to the queue, then Process them one by one"
    animating = None
    anim_timer = 0

    def add_event():
        t = EVENT_TEMPLATES[template_idx[0] % len(EVENT_TEMPLATES)]
        template_idx[0] += 1
        e = Event(t[0], t[1], t[2])
        heapq.heappush(heap, e)

    def process_event():
        nonlocal animating, anim_timer
        if heap:
            e = heapq.heappop(heap)
            processed.append(e)
            animating = e
            anim_timer = 30

    running = True
    while running:
        mx, my = pygame.mouse.get_pos()
        screen.fill(BG)

        screen.blit(fonts["title"].render("Puzzle – Event Queue Simulator", True, ACCENT), (30, 10))

        btns = {
            "Add Event":     pygame.Rect(30, 60, 130, 36),
            "Process Next":  pygame.Rect(175, 60, 150, 36),
            "Clear All":     pygame.Rect(338, 60, 110, 36),
        }
        for t, r in btns.items():
            draw_btn(screen, fonts, t, r, r.collidepoint(mx, my), red=(t=="Clear All"))

        # priority legend
        for p, col in PRIORITY_COLS.items():
            lx = 500 + (p-1)*95
            pygame.draw.rect(screen, col, (lx, 68, 14, 14), border_radius=3)
            screen.blit(fonts["small"].render(PRIORITY_LABELS[p], True, TEXT), (lx+18, 66))

        # heap visualisation (tree layout)
        heap_lbl = fonts["small"].render("Priority Heap (min-heap by priority):", True, ORANGE)
        screen.blit(heap_lbl, (30, 115))

        heap_list = sorted(heap)   # visual only, doesn't break heap property
        node_r = 28
        start_x = WIDTH // 2
        start_y = 165
        positions = {}

        def draw_heap_node(idx, x, y, gap):
            if idx >= len(heap_list):
                return
            e = heap_list[idx]
            col = PRIORITY_COLS.get(e.priority, ACCENT)
            # draw edges first
            left = 2*idx+1
            right = 2*idx+2
            if left < len(heap_list):
                lx2 = x - gap
                ly2 = y + 80
                pygame.draw.line(screen, BORDER, (x, y+node_r), (lx2, ly2-node_r), 2)
                draw_heap_node(left, lx2, ly2, gap//2)
            if right < len(heap_list):
                rx2 = x + gap
                ry2 = y + 80
                pygame.draw.line(screen, BORDER, (x, y+node_r), (rx2, ry2-node_r), 2)
                draw_heap_node(right, rx2, ry2, gap//2)
            # highlight animating
            border_col = HIGHLIGHT if (animating and e.name == animating.name and anim_timer > 0) else BORDER
            pygame.draw.circle(screen, col, (x, y), node_r)
            pygame.draw.circle(screen, border_col, (x, y), node_r, 3)
            # text
            name_parts = e.name.split()
            for i, part in enumerate(name_parts[:2]):
                lbl = fonts["node"].render(part, True, BG)
                screen.blit(lbl, (x - lbl.get_width()//2, y - 10 + i*14))
            p_lbl = fonts["node"].render(f"P{e.priority}", True, (255,255,255))
            screen.blit(p_lbl, (x - p_lbl.get_width()//2, y + node_r + 2))

        if heap_list:
            draw_heap_node(0, start_x, start_y, 160)
        else:
            empty = fonts["small"].render("Heap is empty — add some events!", True, (120,120,140))
            screen.blit(empty, (WIDTH//2 - empty.get_width()//2, 200))

        # processed list
        proc_lbl = fonts["small"].render("Processed (in order):", True, GREEN)
        screen.blit(proc_lbl, (30, HEIGHT - 130))

        for i, e in enumerate(processed[-6:]):   # show last 6
            col = PRIORITY_COLS.get(e.priority, ACCENT)
            rx = 30 + i * 138
            ry = HEIGHT - 108
            highlight = (animating == e and anim_timer > 0)
            pygame.draw.rect(screen, col, (rx, ry, 128, 44), border_radius=6)
            pygame.draw.rect(screen, HIGHLIGHT if highlight else BORDER, (rx, ry, 128, 44), 2, border_radius=6)
            screen.blit(fonts["node"].render(e.name[:12], True, BG), (rx+6, ry+6))
            screen.blit(fonts["node"].render(f"P{e.priority} T{e.time}", True, BG), (rx+6, ry+24))

        if msg:
            screen.blit(fonts["small"].render(msg, True, HIGHLIGHT), (30, HEIGHT-40))

        if anim_timer > 0:
            anim_timer -= 1

        back_r = back_button(screen, fonts)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                if back_r.collidepoint(pos):
                    return
                if btns["Add Event"].collidepoint(pos):
                    if len(heap) < 10:
                        add_event()
                        msg = f"Added '{heap[0].name if heap else ''}' to heap"
                    else:
                        msg = "Heap full! Process some events first"
                elif btns["Process Next"].collidepoint(pos):
                    if heap:
                        e_name = heap[0].name
                        process_event()
                        msg = f"Processed: {e_name}"
                    else:
                        msg = "Heap is empty!"
                elif btns["Clear All"].collidepoint(pos):
                    heap.clear()
                    processed.clear()
                    template_idx[0] = 0
                    msg = "Cleared all events"

        clock.tick(60)


# ─── Main puzzle runner ────────────────────────────────────────────────────────

def run_puzzles(screen, clock):
    fonts = get_fonts()

    running = True
    while running:
        mx, my = pygame.mouse.get_pos()
        screen.fill(BG)

        screen.blit(fonts["title"].render("Puzzle Challenges", True, ACCENT), (30, 10))

        btns = {
            "A* Pathfinding":       pygame.Rect(300, 200, 300, 60),
            "Event Queue Sim":      pygame.Rect(300, 290, 300, 60),
        }
        for t, r in btns.items():
            draw_btn(screen, fonts, t, r, r.collidepoint(mx, my))

        sub = fonts["small"].render("Choose a puzzle", True, (150,150,170))
        screen.blit(sub, (WIDTH//2 - sub.get_width()//2, 160))

        back_r = back_button(screen, fonts)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                if back_r.collidepoint(pos):
                    return
                if btns["A* Pathfinding"].collidepoint(pos):
                    run_pathfinding(screen, clock, fonts)
                elif btns["Event Queue Sim"].collidepoint(pos):
                    run_event_queue(screen, clock, fonts)

        clock.tick(60)
