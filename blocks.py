#############################################################################
##
##                            FUNCTIONAL BLOCKS
##
##                            Milan Rother 2023
##
#############################################################################


class Block:
    def __init__(self):
        self.inputs = {}
        self.output = 0

    def connect(self, input_name, other_block):
        self.inputs[input_name] = other_block

    def compute(self, t, dt):
        raise NotImplementedError()

class Amplifier(Block):
    def __init__(self, gain):
        super().__init__()
        self.gain = gain

    def compute(self, t, dt):
        input_signal = self.inputs['input'].output
        self.output = self.gain * input_signal
        return self.output 

class Integrator(Block):

    def __init__(self, initial_value=0.0):
        super().__init__()
        self.output = initial_value
        self.temp_output = initial_value

    def compute(self, t, dt):
        input_signal = self.inputs['input'].output
        self.temp_output = self.output + input_signal * dt

    def update_output(self):
        self.output = self.temp_output

class Comparator(Block):

    def __init__(self, threshold=0):
        super().__init__()
        self.threshold = threshold

    def compute(self, t, dt):
        input_signal = self.inputs['input'].output
        self.output = 1 if input_signal >= self.threshold else 0

class Adder(Block):

    def compute(self, t, dt):
        self.output = 0
        for input_block in self.inputs.values():
            self.output += input_block.output

class Multiplier(Block):

    def compute(self, t, dt):
        self.output = 1
        for input_block in self.inputs.values():
            self.output *= input_block.output

class Constant(Block):

    def __init__(self, value):
        super().__init__()
        self.output = value

    def compute(self, t, dt):
        pass

class Inverter(Block):

    def compute(self, t, dt):
        self.output = -1 * self.inputs['input'].output

class Generator(Block):

    def __init__(self, func=lambda t:1):
        super().__init__()
        self.func = func

    def compute(self, t, dt):
        self.output = self.func(t)

class Delay(Block):
    
    def __init__(self, initial_value=0.0):
        super().__init__()
        self.output = initial_value
        self.prev_output = initial_value
        self.time = 0

    def compute(self, t, dt):
        if self.time < t:
            self.time = t
            input_signal = self.inputs['input'].output
            self.output, self.prev_output = self.prev_output, input_signal