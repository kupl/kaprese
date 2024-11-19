class Eval:
    def __init__(self, tool: str):
        self.tool = tool
        self.total_count = 0
        self.correct_count = 0

    @property
    def increase_total_count(self):
        self.total_count += 1

    @property
    def increase_correct_count(self):
        self.correct_count += 1
        self.increase_total_count

    @property
    def get_total_count(self):
        return self.total_count

    @property
    def get_correct_count(self):
        return self.correct_count

    @property
    def accuracy(self):
        return self.correct_count / self.total_count if self.total_count > 0 else 0
