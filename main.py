from agents.classifier_agent import ClassifierAgent
from agents.block_solver_agent import BlockSolverAgent
from agents.jug_solver_agent import JugSolverAgent

def main():
    print("🔍 Πληκτρολόγησε την περιγραφή του προβλήματος σε φυσική γλώσσα:")
    prompt = input("> ")

    classifier = ClassifierAgent()
    problem_type = classifier.classify(prompt)

    print(f"\n Το LLM (Mistral) αναγνώρισε το πρόβλημα ως: {problem_type}")

    if problem_type == "blocks":
        solver = BlockSolverAgent()
        solver.solve(prompt)

    elif problem_type == "jug":
        solver = JugSolverAgent()
        solver.solve(prompt)

    else:
        print("Δεν κατάλαβα τον τύπο του προβλήματος.")

if __name__ == "__main__":
    main()
