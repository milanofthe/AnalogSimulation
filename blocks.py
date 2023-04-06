#############################################################################
##
##                            FUNCTIONAL BLOCKS
##
##                            Milan Rother 2023
##
#############################################################################

from math import *

class Block:
    def __init__(self):
        self.inputs = {}
        self.output = 0

    def connect(self, input_name, other_block):
        self.inputs[input_name] = other_block

    def __str__(self):
        raise NotImplementedError()

    def compute(self, t, dt):
        raise NotImplementedError()

class Amplifier(Block):

    def __init__(self, gain=1.0):
        super().__init__()
        self.gain = float(gain)

    def __str__(self):
        return f"Amplifier {self.gain}"

    def compute(self, t, dt):
        input_signal = self.inputs['input'].output
        self.output = self.gain * input_signal
        return self.output 

class Integrator(Block):

    def __init__(self, initial_value=0.0):
        super().__init__()
        self.output = float(initial_value)
        self.temp_output = float(initial_value)

    def __str__(self):
        return f"Integrator {self.output}"

    def compute(self, t, dt):
        input_signal = self.inputs['input'].output
        self.temp_output = self.output + input_signal * dt

    def update_output(self):
        self.output = self.temp_output

class Comparator(Block):

    def __init__(self, threshold=0.0):
        super().__init__()
        self.threshold = float(threshold)

    def __str__(self):
        return f"Comparator {self.threshold}"

    def compute(self, t, dt):
        input_signal = self.inputs['input'].output
        self.output = 1 if input_signal >= self.threshold else 0

class Adder(Block):

    def __str__(self):
        return "Adder"

    def compute(self, t, dt):
        self.output = 0
        for input_block in self.inputs.values():
            self.output += input_block.output

class Multiplier(Block):

    def __str__(self):
        return "Multiplier"

    def compute(self, t, dt):
        self.output = 1
        for input_block in self.inputs.values():
            self.output *= input_block.output

class Constant(Block):

    def __init__(self, value):
        super().__init__()
        self.output = float(value)

    def __str__(self):
        return f"Constant {self.output}"

    def compute(self, t, dt):
        pass

class Inverter(Block):

    def __str__(self):
        return "Inverter"

    def compute(self, t, dt):
        self.output = -1 * self.inputs['input'].output

class Generator(Block):

    def __init__(self, fx="sin(x)"):
        super().__init__()
        self.fx = fx
        self.func = lambda x: eval(fx)

    def __str__(self):
        return f"Generator {self.fx}"

    def compute(self, t, dt):
        self.output = self.func(t)


class Function(Block):

    def __init__(self, fx="x+1"):
        super().__init__()
        self.fx = fx
        self.func = lambda x : eval(fx)

    def __str__(self):
        return f"Function {self.fx}"

    def compute(self, t, dt):
        input_signal = self.inputs['input'].output
        self.output = self.func(input_signal)

class Delay(Block):
    
    def __init__(self, initial_value=0.0):
        super().__init__()
        self.output = float(initial_value)
        self.prev_output = float(initial_value)
        self.time = 0

    def __str__(self):
        return f"Delay {self.output}"

    def compute(self, t, dt):
        if self.time < t:
            self.time = t
            input_signal = self.inputs['input'].output
            self.output, self.prev_output = self.prev_output, input_signal