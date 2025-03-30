class BaseAgent:
    def __init__(self, name, goal, model="gemini-1.5-pro"):
        self.name = name
        self.goal = goal
        self.model = model
        
    async def run(self, callback=None):
        """
        Run the agent's main functionality.
        This is an abstract method that should be implemented by subclasses.
        
        Args:
            callback: An optional callback function to report progress
            
        Returns:
            The result of the agent's execution
        """
        raise NotImplementedError("This method should be implemented by subclasses")