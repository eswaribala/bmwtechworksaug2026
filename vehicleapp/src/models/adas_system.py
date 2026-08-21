class ADASSystem:
    def __init__(self, name: str, version: str):
        self.name = name
        self.version = version

    def activate(self):
        return f"{self.name} v{self.version} activated."

    def deactivate(self):
        return f"{self.name} v{self.version} deactivated."