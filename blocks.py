#############################################################################
##
##                            FUNCTIONAL BLOCKS
##
##                            Milan Rother 2023
##
#############################################################################

# IMPORTS ===================================================================

from math import *


# CLASSES ===================================================================

class Block:

    """
    base Block object that defines the 
    inputs and the connect method
    """

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

    """
    amplifies the input signal by 
    multiplication with a constant gain term
    """

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

    """
    integrates the input signal
    """

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

    """
    compares the input value to a threshold 
    and returns 0 if smaller and 1 if larger
    """

    def __init__(self, threshold=0.0):
        super().__init__()
        self.threshold = float(threshold)

    def __str__(self):
        return f"Comparator {self.threshold}"

    def compute(self, t, dt):
        input_signal = self.inputs['input'].output
        self.output = 1 if input_signal >= self.threshold else 0


class Adder(Block):

    """
    adds all input signals
    """

    def __str__(self):
        return "Adder"

    def compute(self, t, dt):
        self.output = 0
        for input_block in self.inputs.values():
            self.output += input_block.output


class Multiplier(Block):

    """
    multiplies all input signals
    """

    def __str__(self):
        return "Multiplier"

    def compute(self, t, dt):
        self.output = 1
        for input_block in self.inputs.values():
            self.output *= input_block.output


class Constant(Block):

    """
    produces a constant output signal 
    (same as Generator with fx="1")
    """

    def __init__(self, value):
        super().__init__()
        self.output = float(value)

    def __str__(self):
        return f"Constant {self.output}"

    def compute(self, t, dt):
        pass


class Inverter(Block):

    """
    inverts the signal 
    (same as Amplifier with gain= -1)
    """

    def __str__(self):
        return "Inverter"

    def compute(self, t, dt):
        self.output = -1 * self.inputs['input'].output


class Generator(Block):

    """
    generator, or source that produces an 
    arbitrary time dependent output, defined 
    by the string in the argument
    """

    def __init__(self, fx="sin(x)"):
        super().__init__()
        self.fx = fx
        self.func = lambda x: eval(fx)

    def __str__(self):
        return f"Generator {self.fx}"

    def compute(self, t, dt):
        self.output = self.func(t)


class Function(Block):

    """
    arbitrary function block, defined 
    by the string as the argument
    """

    def __init__(self, fx="x+1"):
        super().__init__()
        self.fx = fx
        self.func = lambda x : eval(fx)

    def __str__(self):
        return f"Function {self.fx}"

    def compute(self, t, dt):
        input_signal = self.inputs['input'].output
        self.output = self.func(input_signal)