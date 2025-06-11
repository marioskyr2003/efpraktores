import copy
import re
from collections import deque

class BlockSolverAgent:
    def strip_accents(self, text):
        import unicodedata
        return ''.join(c for c in unicodedata.normalize('NFD', text)
                       if unicodedata.category(c) != 'Mn')

    def normalize_final_sigma(self, word):
        return word.replace('ς', 'σ')

    def parse_blocks_input(self, prompt):
        text = self.strip_accents(self.normalize_final_sigma(prompt.lower()))
        num_stacks = 3
        all_number_matches = list(re.finditer(r'\d+', text))
        stack_keywords = ['στοιβ', 'stoiv', 'stiv', 'stack', 'pile']
        stack_index = None
        for match in re.finditer(r'\b\w+\b', text):
            word = match.group()
            for key in stack_keywords:
                if key in word:
                    min_dist = float('inf')
                    for i, num_match in enumerate(all_number_matches):
                        dist = abs(num_match.start() - match.start())
                        if dist < min_dist:
                            min_dist = dist
                            num_stacks = int(num_match.group())
                            stack_index = i
                    break
        block_numbers = [int(match.group()) for i, match in enumerate(all_number_matches)
                         if i != stack_index]
        if not block_numbers:
            print("Δεν εντοπίστηκαν αριθμοί για τα μπλοκ.")
            return [], []
        initial_state = [block_numbers] + [[] for _ in range(num_stacks - 1)]
        goal_state = [sorted(block_numbers)] + [[] for _ in range(num_stacks - 1)]
        return initial_state, goal_state

    class Node:
        def __init__(self, state, goal=None, parent=None):
            self.state = state
            self.goal = goal
            self.parent = parent
            self.cost = 0 if not parent else parent.cost + 1

        def goalTest(self):
            return self.state == self.goal

        def pathCost(self):
            return self.heuristics() + self.cost

        def heuristics(self):
            return sum(1 for s, g in zip(self.state, self.goal) if s != g)

        def getSuccessors(self):
            children = []
            for i, stack in enumerate(self.state):
                if not stack:
                    continue
                for j in range(len(self.state)):
                    if i != j:
                        new_state = copy.deepcopy(self.state)
                        block = new_state[i].pop()
                        new_state[j].append(block)
                        children.append(BlockSolverAgent.Node(new_state, self.goal, parent=self))
            return children

        def traceback(self):
            s, path = self, []
            while s:
                path.append(s.state)
                s = s.parent
            print("\n Βρέθηκε λύση για blocks!")
            print("Αρχική:", path[-1])
            print("Τελικός στόχος:", self.goal)
            print("Βήματα:", len(path) - 1)
            for p in reversed(path):
                print(p)

    class PriorityQueue:
        def __init__(self):
            import heapq
            self.heap = []
            self.count = 0
            self.heapq = heapq

        def push(self, item, priority):
            self.heapq.heappush(self.heap, (priority, self.count, item))
            self.count += 1

        def pop(self):
            return self.heapq.heappop(self.heap)[2]

        def isEmpty(self):
            return len(self.heap) == 0

    def solve(self, prompt):
        initial, goal = self.parse_blocks_input(prompt)
        if not initial:
            return
        root = self.Node(initial, goal)
        queue = self.PriorityQueue()
        queue.push(root, root.pathCost())
        visited = set()
        while not queue.isEmpty():
            node = queue.pop()
            state_key = str(node.state)
            if state_key in visited:
                continue
            visited.add(state_key)
            if node.goalTest():
                node.traceback()
                return
            for child in node.getSuccessors():
                queue.push(child, child.pathCost())
        print("Δεν βρέθηκε λύση για τα blocks.")
