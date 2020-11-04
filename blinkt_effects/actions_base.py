import random

class ActionBase(object):
    def __init__(self):
        self.action_type = "action_base"


class VariableDelay(ActionBase):
    def __init__(self, min_=0, max_=3):
        super().__init__()
        self.action_type = "variable_delay"
        self.min = min_
        self.max = max_

    def frames_delay(self):
        return random.randint(self.min, self.max)