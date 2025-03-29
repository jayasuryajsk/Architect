class BaseAgent:
    def __init__(self, name, goal, model="gemini-1.5-pro"):
        self.name = name
        self.goal = goal
        self.model = model