import re
from collections import deque

class JugSolverAgent:
    def strip_accents(self, text):
        import unicodedata
        return ''.join(c for c in unicodedata.normalize('NFD', text)
                       if unicodedata.category(c) != 'Mn')

    def extract_jug_data(self, prompt):
        text = self.strip_accents(prompt.lower())

        # Βρες όλες τις εμφανίσεις αριθμών
        numbers = [int(n) for n in re.findall(r'\d+', text)]

        # Βρες τον στόχο με βάση λέξεις όπως: 'θέλω', 'ζητάω', 'να έχω'
        target_keywords = ['θελω', 'ζηταω', 'να εχω', 'χρειαζομαι']

        # Προσπάθεια να εντοπίσει ποιος είναι ο στόχος
        goal = None
        for keyword in target_keywords:
            if keyword in text:
                after = text.split(keyword)[-1]
                match = re.search(r'\d+', after)
                if match:
                    goal = int(match.group())
                    break

        if goal is None:
            goal = numbers[-1]

        # Εξαίρεσε τον στόχο από τα capacities
        capacities = [n for n in numbers if n != goal]

        return capacities, goal

    def solve(self, prompt):
        capacities, goal = self.extract_jug_data(prompt)
        print(f"Αναγνωρίστηκαν δοχεία: {capacities}, Στόχος: {goal}")
        num_jugs = len(capacities)
        initial_state = tuple([0] * num_jugs)
        visited = set()
        queue = deque([(initial_state, [])])
        visited.add(initial_state)

        while queue:
            current_state, path = queue.popleft()
            if goal in current_state:
                print("\n Επιτεύχθηκε ο στόχος (jug)!")
                for i, (desc, state) in enumerate(path, 1):
                    print(f"{i}. {desc} -> {list(state)}")
                return
            for i in range(num_jugs):
                # Fill
                new_state = list(current_state)
                new_state[i] = capacities[i]
                new_state = tuple(new_state)
                if new_state not in visited:
                    visited.add(new_state)
                    queue.append((new_state, path + [(f"Γέμισμα δοχείου {i+1}", new_state)]))
                # Empty
                new_state = list(current_state)
                new_state[i] = 0
                new_state = tuple(new_state)
                if new_state not in visited:
                    visited.add(new_state)
                    queue.append((new_state, path + [(f"Άδειασμα δοχείου {i+1}", new_state)]))
            # Pour
            for i in range(num_jugs):
                for j in range(num_jugs):
                    if i != j and current_state[i] > 0 and current_state[j] < capacities[j]:
                        new_state = list(current_state)
                        transfer = min(current_state[i], capacities[j] - current_state[j])
                        new_state[i] -= transfer
                        new_state[j] += transfer
                        new_state = tuple(new_state)
                        if new_state not in visited:
                            visited.add(new_state)
                            queue.append((new_state, path + [(f"Μεταφορά από δοχείο {i+1} στο {j+1}", new_state)]))
        print("Δεν βρέθηκε λύση για τα δοχεία.")
