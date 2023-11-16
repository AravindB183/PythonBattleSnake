class Node:
    def __init__(self, state):
        self.state = state
        self.visits = 0
        self.reward = 0
        self.children = []
