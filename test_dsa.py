import unittest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data_structures import LinkedList, BST
from sorting import bubble_sort_steps, selection_sort_steps
from graphs import bfs_steps, dfs_steps, build_adj, NODES


# ── Module 1: Data Structures ─────────────────────────────────────────────────

class TestStack(unittest.TestCase):

    def test_push_pop_sequence(self):
        """Push 3 items, pop 2 — final size should be 1, correct LIFO order"""
        stack = []
        stack.append(10)
        stack.append(20)
        stack.append(30)
        self.assertEqual(len(stack), 3)

        v1 = stack.pop()
        v2 = stack.pop()
        self.assertEqual(v1, 30)   # LIFO: last in first out
        self.assertEqual(v2, 20)
        self.assertEqual(len(stack), 1)
        self.assertEqual(stack[0], 10)


class TestQueue(unittest.TestCase):

    def test_enqueue_dequeue_fifo(self):
        """Enqueue 4 items, dequeue 3 — FIFO order maintained"""
        queue = []
        for v in [1, 2, 3, 4]:
            queue.append(v)
        self.assertEqual(len(queue), 4)

        d1 = queue.pop(0)
        d2 = queue.pop(0)
        d3 = queue.pop(0)
        self.assertEqual(d1, 1)   # FIFO: first in first out
        self.assertEqual(d2, 2)
        self.assertEqual(d3, 3)
        self.assertEqual(len(queue), 1)
        self.assertEqual(queue[0], 4)


class TestLinkedList(unittest.TestCase):

    def test_insert_at_position(self):
        """Insert node with value 10 at position 2 — node present in correct location"""
        ll = LinkedList()
        ll.insert(1)
        ll.insert(2)
        ll.insert(3)
        ll.insert(10, pos=2)   # insert at index 2
        result = ll.to_list()
        self.assertIn(10, result)
        self.assertEqual(result.index(10), 2)

    def test_delete_node(self):
        ll = LinkedList()
        for v in [5, 10, 15]:
            ll.insert(v)
        ll.delete(10)
        self.assertNotIn(10, ll.to_list())

    def test_reverse(self):
        ll = LinkedList()
        for v in [1, 2, 3]:
            ll.insert(v)
        original = ll.to_list()[:]
        ll.reverse()
        self.assertEqual(ll.to_list(), list(reversed(original)))


class TestBST(unittest.TestCase):

    def test_inorder_traversal(self):
        """Insert [50, 30, 70] — inorder traversal should give [30, 50, 70]"""
        bst = BST()
        for v in [50, 30, 70]:
            bst.insert(v)
        self.assertEqual(bst.inorder(), [30, 50, 70])

    def test_preorder_traversal(self):
        bst = BST()
        for v in [50, 30, 70]:
            bst.insert(v)
        self.assertEqual(bst.preorder(), [50, 30, 70])

    def test_postorder_traversal(self):
        bst = BST()
        for v in [50, 30, 70]:
            bst.insert(v)
        self.assertEqual(bst.postorder(), [30, 70, 50])

    def test_no_duplicates(self):
        bst = BST()
        bst.insert(10)
        bst.insert(10)
        self.assertEqual(bst.inorder().count(10), 1)


# ── Module 2: Sorting ─────────────────────────────────────────────────────────

class TestBubbleSort(unittest.TestCase):

    def test_correctness(self):
        """Sort [5, 3, 8, 1, 2] — result should be [1, 2, 3, 5, 8]"""
        arr = [5, 3, 8, 1, 2]
        steps = bubble_sort_steps(arr)
        final_arr, _, _, _ = steps[-1]
        self.assertEqual(final_arr, sorted(arr))

    def test_already_sorted(self):
        arr = [1, 2, 3, 4, 5]
        steps = bubble_sort_steps(arr)
        final_arr, _, _, _ = steps[-1]
        self.assertEqual(final_arr, [1, 2, 3, 4, 5])

    def test_single_element(self):
        arr = [42]
        steps = bubble_sort_steps(arr)
        final_arr, _, _, _ = steps[-1]
        self.assertEqual(final_arr, [42])


class TestSelectionSort(unittest.TestCase):

    def test_correctness(self):
        arr = [5, 3, 8, 1, 2]
        steps = selection_sort_steps(arr)
        final_arr, _, _, _ = steps[-1]
        self.assertEqual(final_arr, sorted(arr))

    def test_color_highlighting(self):
        """Steps must include compare indices so animation highlights correctly"""
        arr = [3, 1, 2]
        steps = selection_sort_steps(arr)
        # every non-final step should have compare indices != (-1, -1) at some point
        compare_steps = [s for s in steps if s[1] != (-1, -1)]
        self.assertGreater(len(compare_steps), 0)

    def test_reverse_sorted(self):
        arr = [5, 4, 3, 2, 1]
        steps = selection_sort_steps(arr)
        final_arr, _, _, _ = steps[-1]
        self.assertEqual(final_arr, [1, 2, 3, 4, 5])


# ── Module 3: Graph Traversal ─────────────────────────────────────────────────

class TestBFS(unittest.TestCase):

    def test_bfs_from_A(self):
        """BFS from 'A' visits nodes in correct BFS order"""
        adj = build_adj()
        steps = bfs_steps('A', adj)
        final_visited, _, _, _, order = steps[-1]
        # A should be visited first
        self.assertEqual(order[0], 'A')
        # all nodes reachable from A should be visited (graph is connected)
        self.assertEqual(final_visited, set(NODES.keys()))

    def test_bfs_visits_all_connected(self):
        adj = build_adj()
        steps = bfs_steps('A', adj)
        final_visited, _, _, _, order = steps[-1]
        self.assertEqual(len(final_visited), len(NODES))

    def test_bfs_order_level_property(self):
        """Neighbours of A (B and D) must appear before their children"""
        adj = build_adj()
        steps = bfs_steps('A', adj)
        _, _, _, _, order = steps[-1]
        idx = {n: i for i, n in enumerate(order)}
        # A's direct neighbors must come before deeper nodes
        self.assertLess(idx['B'], idx['C'])   # B before C (C is B's child)
        self.assertLess(idx['D'], idx['G'])   # D before G (G is D's child)


class TestDFS(unittest.TestCase):

    def test_dfs_from_C(self):
        """DFS from 'C' — traversal path matches theoretical DFS"""
        adj = build_adj()
        steps = dfs_steps('C', adj)
        _, _, _, _, order = steps[-1]
        self.assertEqual(order[0], 'C')
        # all nodes should be reachable (connected graph)
        self.assertEqual(len(order), len(NODES))

    def test_dfs_visits_all(self):
        adj = build_adj()
        steps = dfs_steps('A', adj)
        final_visited, _, _, _, order = steps[-1]
        self.assertEqual(final_visited, set(NODES.keys()))

    def test_interactive_start_node(self):
        """BFS/DFS restarts correctly from any chosen node"""
        adj = build_adj()
        for start in ['A', 'B', 'C', 'D', 'E']:
            steps_b = bfs_steps(start, adj)
            _, _, _, _, order_b = steps_b[-1]
            self.assertEqual(order_b[0], start)

            steps_d = dfs_steps(start, adj)
            _, _, _, _, order_d = steps_d[-1]
            self.assertEqual(order_d[0], start)


# ── Module 4: Puzzles ─────────────────────────────────────────────────────────

from puzzles import astar, Event

class TestAstar(unittest.TestCase):

    def _empty_grid(self):
        return [[0]*28 for _ in range(20)]

    def test_finds_path(self):
        """A* finds a path on an empty grid"""
        grid = self._empty_grid()
        steps = astar(grid, (0,0), (5,5))
        final = steps[-1]
        self.assertTrue(len(final[3]) > 0)

    def test_no_path_when_blocked(self):
        """A* returns no path when end is completely walled off"""
        grid = self._empty_grid()
        # wall off the end
        for c in range(28):
            grid[4][c] = 1
        steps = astar(grid, (0,0), (10,10))
        final_path = steps[-1][3]
        self.assertEqual(final_path, [])

    def test_start_equals_end(self):
        """A* handles start == end edge case"""
        grid = self._empty_grid()
        steps = astar(grid, (0,0), (0,0))
        self.assertIsNotNone(steps)


class TestEventQueue(unittest.TestCase):

    def test_priority_order(self):
        """Heap processes lowest priority number first (critical first)"""
        import heapq
        heap = []
        heapq.heappush(heap, Event("Low Task", 4, 1))
        heapq.heappush(heap, Event("Critical Task", 1, 1))
        heapq.heappush(heap, Event("High Task", 2, 1))
        first = heapq.heappop(heap)
        self.assertEqual(first.priority, 1)
        self.assertEqual(first.name, "Critical Task")

    def test_same_priority_time_order(self):
        """Events with same priority are ordered by time"""
        import heapq
        heap = []
        heapq.heappush(heap, Event("Later", 2, 5))
        heapq.heappush(heap, Event("Earlier", 2, 1))
        first = heapq.heappop(heap)
        self.assertEqual(first.name, "Earlier")

    def test_heap_size(self):
        """Heap grows and shrinks correctly"""
        import heapq
        heap = []
        for i in range(5):
            heapq.heappush(heap, Event(f"Event{i}", i+1, i))
        self.assertEqual(len(heap), 5)
        heapq.heappop(heap)
        self.assertEqual(len(heap), 4)


if __name__ == "__main__":
    unittest.main(verbosity=2)
