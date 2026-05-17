import pygame
import sys

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
    hover = r.collidepoint(mx, my)
    draw_btn(surface, fonts, "< Back", r, hover)
    return r


# ─── Stack/Queue tab ───────────────────────────────────────────────────────────

def draw_stack_queue(surface, fonts, stack, queue, active_tab, msg):
    surface.fill(BG)
    # tab buttons
    tab_s = pygame.Rect(30, 55, 130, 36)
    tab_q = pygame.Rect(175, 55, 130, 36)
    mx, my = pygame.mouse.get_pos()
    pygame.draw.rect(surface, ACCENT if active_tab == "stack" else BTN, tab_s, border_radius=6)
    pygame.draw.rect(surface, ACCENT if active_tab == "queue" else BTN, tab_q, border_radius=6)
    surface.blit(fonts["btn"].render("Stack", True, BG if active_tab=="stack" else TEXT), (tab_s.x+30, tab_s.y+8))
    surface.blit(fonts["btn"].render("Queue", True, BG if active_tab=="queue" else TEXT), (tab_q.x+30, tab_q.y+8))

    title = fonts["title"].render("Data Structures – Stack & Queue", True, ACCENT)
    surface.blit(title, (30, 10))

    # action buttons
    if active_tab == "stack":
        btns = {
            "Push": pygame.Rect(30, 110, 100, 38),
            "Pop":  pygame.Rect(145, 110, 100, 38),
        }
        items = stack
        label = "Stack (LIFO)"
    else:
        btns = {
            "Enqueue": pygame.Rect(30, 110, 120, 38),
            "Dequeue": pygame.Rect(165, 110, 120, 38),
        }
        items = queue
        label = "Queue (FIFO)"

    for t, r in btns.items():
        draw_btn(surface, fonts, t, r, r.collidepoint(mx, my),
                 red=(t in ("Pop", "Dequeue")))

    # draw items
    lbl = fonts["small"].render(label, True, ORANGE)
    surface.blit(lbl, (30, 165))

    if active_tab == "stack":
        for i, val in enumerate(reversed(items)):
            bx, by = 30, 195 + i * 52
            rect = pygame.Rect(bx, by, 120, 44)
            col = GREEN if i == 0 else PANEL
            pygame.draw.rect(surface, col, rect, border_radius=5)
            pygame.draw.rect(surface, BORDER, rect, 2, border_radius=5)
            surface.blit(fonts["node"].render(str(val), True, BG if i==0 else TEXT),
                         (bx + 40, by + 12))
            if i == 0:
                surface.blit(fonts["small"].render("← TOP", True, HIGHLIGHT), (bx + 130, by + 14))
    else:
        for i, val in enumerate(items):
            bx, by = 30 + i * 90, 195
            rect = pygame.Rect(bx, by, 80, 44)
            col = GREEN if i == 0 else PANEL
            pygame.draw.rect(surface, col, rect, border_radius=5)
            pygame.draw.rect(surface, BORDER, rect, 2, border_radius=5)
            surface.blit(fonts["node"].render(str(val), True, BG if i==0 else TEXT),
                         (bx + 22, by + 12))
            if i == 0:
                surface.blit(fonts["small"].render("FRONT", True, HIGHLIGHT), (bx + 5, by + 52))
            # arrow
            if i < len(items) - 1:
                ax = bx + 82
                pygame.draw.line(surface, BORDER, (ax, by+22), (ax+6, by+22), 2)

    # message
    if msg:
        m = fonts["small"].render(msg, True, HIGHLIGHT)
        surface.blit(m, (30, HEIGHT - 40))

    return btns, tab_s, tab_q


# ─── Linked List tab ───────────────────────────────────────────────────────────

class Node:
    def __init__(self, val):
        self.val = val
        self.next = None

class LinkedList:
    def __init__(self):
        self.head = None

    def insert(self, val, pos=None):
        new = Node(val)
        if self.head is None or pos == 0:
            new.next = self.head
            self.head = new
            return
        cur = self.head
        i = 0
        while cur.next and (pos is None or i < pos - 1):
            cur = cur.next
            i += 1
        new.next = cur.next
        cur.next = new

    def delete(self, val):
        if self.head is None:
            return False
        if self.head.val == val:
            self.head = self.head.next
            return True
        cur = self.head
        while cur.next:
            if cur.next.val == val:
                cur.next = cur.next.next
                return True
            cur = cur.next
        return False

    def reverse(self):
        prev = None
        cur = self.head
        while cur:
            nxt = cur.next
            cur.next = prev
            prev = cur
            cur = nxt
        self.head = prev

    def to_list(self):
        vals = []
        cur = self.head
        while cur:
            vals.append(cur.val)
            cur = cur.next
        return vals


def draw_linked_list(surface, fonts, ll, msg, highlight_val=None):
    surface.fill(BG)
    title = fonts["title"].render("Data Structures – Linked List", True, ACCENT)
    surface.blit(title, (30, 10))

    btns = {
        "Insert Head": pygame.Rect(30, 60, 140, 36),
        "Insert Tail": pygame.Rect(185, 60, 140, 36),
        "Delete Head": pygame.Rect(340, 60, 140, 36),
        "Reverse":     pygame.Rect(495, 60, 100, 36),
    }
    mx, my = pygame.mouse.get_pos()
    for t, r in btns.items():
        draw_btn(surface, fonts, t, r, r.collidepoint(mx, my),
                 red=("Delete" in t))

    nodes = ll.to_list()
    sx, sy = 60, 200
    node_w, node_h = 70, 40
    gap = 50

    head_lbl = fonts["small"].render("HEAD", True, HIGHLIGHT)
    if nodes:
        surface.blit(head_lbl, (sx + 12, sy - 22))

    for i, val in enumerate(nodes):
        x = sx + i * (node_w + gap)
        col = HIGHLIGHT if val == highlight_val else PANEL
        pygame.draw.rect(surface, col, (x, sy, node_w, node_h), border_radius=5)
        pygame.draw.rect(surface, BORDER, (x, sy, node_w, node_h), 2, border_radius=5)
        # pointer box
        pygame.draw.rect(surface, (70, 70, 90), (x + node_w, sy, 20, node_h), border_radius=3)
        pygame.draw.rect(surface, BORDER, (x + node_w, sy, 20, node_h), 2, border_radius=3)
        lbl = fonts["node"].render(str(val), True, BG if val==highlight_val else TEXT)
        surface.blit(lbl, (x + (node_w - lbl.get_width())//2, sy + 10))
        # arrow
        if i < len(nodes) - 1:
            ax = x + node_w + 20
            pygame.draw.line(surface, ACCENT, (ax, sy + node_h//2), (ax + gap - 2, sy + node_h//2), 2)
            pygame.draw.polygon(surface, ACCENT, [
                (ax + gap - 2, sy + node_h//2),
                (ax + gap - 10, sy + node_h//2 - 5),
                (ax + gap - 10, sy + node_h//2 + 5),
            ])
        else:
            # NULL
            nx = x + node_w + 5
            surface.blit(fonts["small"].render("NULL", True, (160,80,80)), (nx, sy + 12))

    if msg:
        surface.blit(fonts["small"].render(msg, True, HIGHLIGHT), (30, HEIGHT - 40))

    return btns


# ─── BST tab ───────────────────────────────────────────────────────────────────

class BSTNode:
    def __init__(self, val):
        self.val = val
        self.left = None
        self.right = None

class BST:
    def __init__(self):
        self.root = None

    def insert(self, val):
        def _ins(node, v):
            if node is None:
                return BSTNode(v)
            if v < node.val:
                node.left = _ins(node.left, v)
            elif v > node.val:
                node.right = _ins(node.right, v)
            return node
        self.root = _ins(self.root, val)

    def inorder(self):
        res = []
        def _in(n):
            if n:
                _in(n.left); res.append(n.val); _in(n.right)
        _in(self.root)
        return res

    def preorder(self):
        res = []
        def _pre(n):
            if n:
                res.append(n.val); _pre(n.left); _pre(n.right)
        _pre(self.root)
        return res

    def postorder(self):
        res = []
        def _post(n):
            if n:
                _post(n.left); _post(n.right); res.append(n.val)
        _post(self.root)
        return res


def draw_bst_node(surface, fonts, node, x, y, gap, depth, highlight=None):
    if node is None:
        return
    r = 22
    col = HIGHLIGHT if node.val == highlight else ACCENT
    pygame.draw.circle(surface, col, (x, y), r)
    pygame.draw.circle(surface, BORDER, (x, y), r, 2)
    lbl = fonts["node"].render(str(node.val), True, BG)
    surface.blit(lbl, (x - lbl.get_width()//2, y - lbl.get_height()//2))

    ng = max(gap // 2, 30)
    if node.left:
        lx = x - gap
        ly = y + 70
        pygame.draw.line(surface, BORDER, (x, y + r), (lx, ly - r), 2)
        draw_bst_node(surface, fonts, node.left, lx, ly, ng, depth+1, highlight)
    if node.right:
        rx = x + gap
        ry = y + 70
        pygame.draw.line(surface, BORDER, (x, y + r), (rx, ry - r), 2)
        draw_bst_node(surface, fonts, node.right, rx, ry, ng, depth+1, highlight)


def draw_bst(surface, fonts, bst, traversal, msg):
    surface.fill(BG)
    title = fonts["title"].render("Data Structures – Binary Search Tree", True, ACCENT)
    surface.blit(title, (30, 10))

    btns = {
        "Insert":   pygame.Rect(30, 60, 100, 36),
        "Inorder":  pygame.Rect(145, 60, 110, 36),
        "Preorder": pygame.Rect(268, 60, 115, 36),
        "Postorder":pygame.Rect(396, 60, 125, 36),
        "Clear":    pygame.Rect(534, 60, 90, 36),
    }
    mx, my = pygame.mouse.get_pos()
    for t, r in btns.items():
        draw_btn(surface, fonts, t, r, r.collidepoint(mx, my), red=(t=="Clear"))

    draw_bst_node(surface, fonts, bst.root, WIDTH//2, 170, 180, 0)

    if traversal:
        tstr = "Traversal: " + " → ".join(str(v) for v in traversal)
        tl = fonts["small"].render(tstr, True, GREEN)
        surface.blit(tl, (30, HEIGHT - 60))

    if msg:
        surface.blit(fonts["small"].render(msg, True, HIGHLIGHT), (30, HEIGHT - 35))

    return btns


# ─── Main module runner ────────────────────────────────────────────────────────

def run_data_structures(screen, clock):
    fonts = get_fonts()

    # state
    stack = []
    queue = []
    ll = LinkedList()
    bst = BST()
    counter = [1]   # auto-increment values so it's not boring

    active_tab = "stack"   # stack | queue | linked_list | bst
    msg = ""
    traversal = []
    input_mode = None   # for BST insert prompt (simple)

    def next_val():
        v = counter[0]
        counter[0] += 1
        return v

    running = True
    while running:
        mx, my = pygame.mouse.get_pos()

        # draw
        if active_tab in ("stack", "queue"):
            action_btns, tab_s, tab_q = draw_stack_queue(
                screen, fonts, stack, queue, active_tab, msg)
        elif active_tab == "linked_list":
            action_btns = draw_linked_list(screen, fonts, ll, msg)
        elif active_tab == "bst":
            action_btns = draw_bst(screen, fonts, bst, traversal, msg)

        # side nav tabs for linked_list / bst
        side_tabs = {
            "Linked List": pygame.Rect(WIDTH - 200, 55, 130, 36),
            "BST":         pygame.Rect(WIDTH - 200, 100, 130, 36),
        }
        for t, r in side_tabs.items():
            is_active = (active_tab == t.lower().replace(" ", "_"))
            pygame.draw.rect(screen, ACCENT if is_active else BTN, r, border_radius=6)
            pygame.draw.rect(screen, BORDER, r, 2, border_radius=6)
            screen.blit(fonts["btn"].render(t, True, BG if is_active else TEXT),
                        (r.x + 10, r.y + 8))

        back_r = back_button(screen, fonts)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos

                # back
                if back_r.collidepoint(pos):
                    return

                # side nav
                if side_tabs["Linked List"].collidepoint(pos):
                    active_tab = "linked_list"; msg = ""; continue
                if side_tabs["BST"].collidepoint(pos):
                    active_tab = "bst"; msg = ""; traversal = []; continue

                # stack/queue tabs
                if active_tab in ("stack", "queue"):
                    if tab_s.collidepoint(pos):
                        active_tab = "stack"; msg = ""; continue
                    if tab_q.collidepoint(pos):
                        active_tab = "queue"; msg = ""; continue

                # actions
                if active_tab == "stack":
                    if action_btns["Push"].collidepoint(pos):
                        v = next_val()
                        stack.append(v)
                        msg = f"Pushed {v} onto stack"
                    elif action_btns["Pop"].collidepoint(pos):
                        if stack:
                            v = stack.pop()
                            msg = f"Popped {v} from stack"
                        else:
                            msg = "Stack is empty!"

                elif active_tab == "queue":
                    if action_btns["Enqueue"].collidepoint(pos):
                        v = next_val()
                        queue.append(v)
                        msg = f"Enqueued {v}"
                    elif action_btns["Dequeue"].collidepoint(pos):
                        if queue:
                            v = queue.pop(0)
                            msg = f"Dequeued {v} (FIFO)"
                        else:
                            msg = "Queue is empty!"

                elif active_tab == "linked_list":
                    if action_btns["Insert Head"].collidepoint(pos):
                        v = next_val()
                        ll.insert(v, 0)
                        msg = f"Inserted {v} at head"
                    elif action_btns["Insert Tail"].collidepoint(pos):
                        v = next_val()
                        ll.insert(v)
                        msg = f"Inserted {v} at tail"
                    elif action_btns["Delete Head"].collidepoint(pos):
                        nodes = ll.to_list()
                        if nodes:
                            ll.delete(nodes[0])
                            msg = f"Deleted head ({nodes[0]})"
                        else:
                            msg = "List is empty!"
                    elif action_btns["Reverse"].collidepoint(pos):
                        ll.reverse()
                        msg = "List reversed"

                elif active_tab == "bst":
                    if action_btns["Insert"].collidepoint(pos):
                        v = next_val()
                        bst.insert(v)
                        msg = f"Inserted {v} into BST"
                        traversal = []
                    elif action_btns["Inorder"].collidepoint(pos):
                        traversal = bst.inorder()
                        msg = "Inorder traversal (Left → Root → Right)"
                    elif action_btns["Preorder"].collidepoint(pos):
                        traversal = bst.preorder()
                        msg = "Preorder traversal (Root → Left → Right)"
                    elif action_btns["Postorder"].collidepoint(pos):
                        traversal = bst.postorder()
                        msg = "Postorder traversal (Left → Right → Root)"
                    elif action_btns["Clear"].collidepoint(pos):
                        bst = BST(); traversal = []; msg = "BST cleared"

        clock.tick(60)
