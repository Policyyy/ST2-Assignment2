import pygame
import sys
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

NODE_DEFAULT  = (70, 100, 160)
NODE_VISITED  = (80, 200, 120)
NODE_CURRENT  = (255, 180, 0)
NODE_QUEUED   = (180, 100, 200)
NODE_START    = (220, 80, 80)
EDGE_COL      = (100, 100, 130)
EDGE_VISITED  = (80, 200, 120)


def get_fonts():
    return {
        "title": pygame.font.SysFont("consolas", 28, bold=True),
        "btn":   pygame.font.SysFont("consolas", 20),
        "small": pygame.font.SysFont("consolas", 16),
        "node":  pygame.font.SysFont("consolas", 18, bold=True),
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


# graph definition: nodes with positions + edges
NODES = {
    'A': (200, 200),
    'B': (400, 140),
    'C': (600, 200),
    'D': (150, 380),
    'E': (380, 340),
    'F': (620, 370),
    'G': (300, 500),
    'H': (530, 500),
}

EDGES = [
    ('A', 'B'), ('A', 'D'),
    ('B', 'C'), ('B', 'E'),
    ('C', 'F'),
    ('D', 'E'), ('D', 'G'),
    ('E', 'F'), ('E', 'G'),
    ('F', 'H'),
    ('G', 'H'),
]

def build_adj():
    adj = {n: [] for n in NODES}
    for u, v in EDGES:
        adj[u].append(v)
        adj[v].append(u)
    return adj


def bfs_steps(start, adj):
    """Returns list of steps, each step = (visited set, current node, queue list, visited_edges)"""
    steps = []
    visited = set()
    queue = deque([start])
    visited.add(start)
    visited_edges = set()
    order = []

    while queue:
        node = queue.popleft()
        order.append(node)
        steps.append((set(visited), node, list(queue), set(visited_edges), list(order)))

        for nb in sorted(adj[node]):
            if nb not in visited:
                visited.add(nb)
                queue.append(nb)
                edge = tuple(sorted([node, nb]))
                visited_edges.add(edge)

    steps.append((set(visited), None, [], set(visited_edges), list(order)))
    return steps


def dfs_steps(start, adj):
    steps = []
    visited = set()
    visited_edges = set()
    order = []

    def dfs(node, parent):
        visited.add(node)
        order.append(node)
        steps.append((set(visited), node, [], set(visited_edges), list(order)))
        for nb in sorted(adj[node]):
            if nb not in visited:
                edge = tuple(sorted([node, nb]))
                visited_edges.add(edge)
                dfs(nb, node)

    dfs(start, None)
    steps.append((set(visited), None, [], set(visited_edges), list(order)))
    return steps


def node_at(pos, nodes, radius=24):
    for name, (nx, ny) in nodes.items():
        if (pos[0]-nx)**2 + (pos[1]-ny)**2 <= radius**2:
            return name
    return None


def draw_graph(surface, fonts, nodes, edges, visited, current, queued,
               visited_edges, start_node, order, mode, msg):
    # draw edges first
    for u, v in edges:
        ux, uy = nodes[u]
        vx, vy = nodes[v]
        edge_key = tuple(sorted([u, v]))
        col = EDGE_VISITED if edge_key in visited_edges else EDGE_COL
        width = 3 if edge_key in visited_edges else 1
        pygame.draw.line(surface, col, (ux, uy), (vx, vy), width)

    # draw nodes
    for name, (nx, ny) in nodes.items():
        if name == current:
            col = NODE_CURRENT
        elif name in visited and name != start_node:
            col = NODE_VISITED
        elif name == start_node:
            col = NODE_START
        elif name in queued:
            col = NODE_QUEUED
        else:
            col = NODE_DEFAULT

        r = 26 if name == current else 22
        pygame.draw.circle(surface, col, (nx, ny), r)
        pygame.draw.circle(surface, (200, 200, 220) if name==current else BORDER, (nx, ny), r, 2)

        lbl = fonts["node"].render(name, True, BG)
        surface.blit(lbl, (nx - lbl.get_width()//2, ny - lbl.get_height()//2))

    # order text
    if order:
        ot = fonts["small"].render("Visit order:  " + " → ".join(order), True, GREEN)
        surface.blit(ot, (30, HEIGHT - 60))

    if msg:
        surface.blit(fonts["small"].render(msg, True, HIGHLIGHT), (30, HEIGHT - 35))


def run_graphs(screen, clock):
    fonts = get_fonts()
    adj = build_adj()

    mode = "bfs"   # bfs | dfs
    start_node = 'A'
    steps = bfs_steps(start_node, adj)
    step_idx = 0
    playing = False
    done = False
    speed = 12
    frame_count = 0
    msg = f"Click a node to set start, then press Start  |  Start: {start_node}"
    selecting_start = False

    def rebuild(new_start=None):
        nonlocal steps, step_idx, playing, done, msg, start_node
        if new_start:
            start_node = new_start
        if mode == "bfs":
            steps = bfs_steps(start_node, adj)
        else:
            steps = dfs_steps(start_node, adj)
        step_idx = 0
        playing = False
        done = False
        msg = f"Mode: {'BFS' if mode=='bfs' else 'DFS'}  |  Start: {start_node}  |  Press Start"

    running = True
    while running:
        mx, my = pygame.mouse.get_pos()
        screen.fill(BG)

        screen.blit(fonts["title"].render("Graph Traversal", True, ACCENT), (30, 10))

        # tabs
        tab_b = pygame.Rect(30, 55, 80, 34)
        tab_d = pygame.Rect(122, 55, 80, 34)
        pygame.draw.rect(screen, ACCENT if mode=="bfs" else BTN, tab_b, border_radius=6)
        pygame.draw.rect(screen, ACCENT if mode=="dfs" else BTN, tab_d, border_radius=6)
        screen.blit(fonts["btn"].render("BFS", True, BG if mode=="bfs" else TEXT), (tab_b.x+22, tab_b.y+7))
        screen.blit(fonts["btn"].render("DFS", True, BG if mode=="dfs" else TEXT), (tab_d.x+22, tab_d.y+7))

        btns = {
            "Start":  pygame.Rect(215, 55, 90, 34),
            "Reset":  pygame.Rect(318, 55, 90, 34),
        }
        for t, r in btns.items():
            draw_btn(screen, fonts, t, r, r.collidepoint(mx, my), red=(t=="Reset"))

        hint = fonts["small"].render("Click node to change start", True, (150, 150, 180))
        screen.blit(hint, (420, 63))

        # legend
        legend = [
            (NODE_START,   "Start"),
            (NODE_CURRENT, "Current"),
            (NODE_QUEUED,  "In Queue/Stack"),
            (NODE_VISITED, "Visited"),
        ]
        for i, (col, lbl) in enumerate(legend):
            lx = 30 + i * 160
            pygame.draw.circle(screen, col, (lx + 8, HEIGHT - 22), 8)
            screen.blit(fonts["small"].render(lbl, True, TEXT), (lx + 22, HEIGHT - 30))

        # get state
        if steps and step_idx < len(steps):
            visited, current, queued_list, visited_edges, order = steps[step_idx]
        else:
            visited = set(NODES.keys())
            current = None
            queued_list = []
            visited_edges = set()
            order = []

        draw_graph(screen, fonts, NODES, EDGES,
                   visited, current, set(queued_list),
                   visited_edges, start_node, order, mode, msg)

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
                    msg = f"{'BFS' if mode=='bfs' else 'DFS'} complete from {start_node}!"

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                if back_r.collidepoint(pos):
                    return

                if tab_b.collidepoint(pos) and mode != "bfs":
                    mode = "bfs"; rebuild()
                elif tab_d.collidepoint(pos) and mode != "dfs":
                    mode = "dfs"; rebuild()
                elif btns["Start"].collidepoint(pos):
                    if done:
                        rebuild()
                    playing = True
                    msg = f"Running {'BFS' if mode=='bfs' else 'DFS'} from {start_node}..."
                elif btns["Reset"].collidepoint(pos):
                    rebuild()
                else:
                    # check if clicked a node
                    clicked = node_at(pos, NODES)
                    if clicked:
                        rebuild(new_start=clicked)

        clock.tick(60)
