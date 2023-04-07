


#############################################################################
##
##                      FUNCTIONAL BLOCKS (blocks.py)
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

        #general properties for simulation
        self.inputs = {}
        self.output = 0
        
        #display propertiers
        self.label  = type(self).__name__.lower()

    def connect(self, input_name, other_block):
        self.inputs[input_name] = other_block

    def __str__(self):
        raise NotImplementedError()

    def compute(self, t, dt):
        raise NotImplementedError()

    def update_output(self):
        pass


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
    integrates the input signal using the 
    trapezoidal integration rule, except for the 
    first step, that uses the forward euler rule
    """

    def __init__(self, initial_value=0.0):
        super().__init__()
        self.output = float(initial_value)
        self.temp_output = float(initial_value)
        self.prev_input = None

    def __str__(self):
        return f"Integrator {self.output}"

    def compute(self, t, dt):
        input_signal = self.inputs['input'].output
        if self.prev_input is None:
            self.temp_output = self.output + input_signal * dt
        else:
            self.temp_output = self.output + (input_signal + self.prev_input) * dt / 2

    def update_output(self):
        self.prev_input = self.inputs['input'].output
        self.output = self.temp_output


class Differentiator(Block):

    """
    differentiates the input signal
    """

    def __init__(self):
        super().__init__()
        self.prev_input = None
        self.temp_output = 0

    def __str__(self):
        return "Differentiator"

    def compute(self, t, dt):
        input_signal = self.inputs['input'].output
        if self.prev_input is not None:
            self.temp_output = (input_signal - self.prev_input) / dt

    def update_output(self):
        self.prev_input = self.inputs['input'].output
        self.output = self.temp_output


class Comparator(Block):

    """
    compares the input value to a threshold 
    and returns 0 if smaller and 1 if larger
    (essentially heaviside function)
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

    def __init__(self, expression="sin(x)"):
        super().__init__()
        self.expression = expression
        self.func = lambda x: eval(expression)

    def __str__(self):
        return f"Generator {self.expression}"

    def compute(self, t, dt):
        self.output = self.func(t)


class Function(Block):

    """
    arbitrary function block, defined 
    by the string as the argument
    """

    def __init__(self, expression="x+1"):
        super().__init__()
        self.expression = expression
        self.func = lambda x : eval(expression)

    def __str__(self):
        return f"Function {self.expression}"

    def compute(self, t, dt):
        input_signal = self.inputs['input'].output
        self.output = self.func(input_signal)


class Scope(Block):
    
    """
    block for visualization, input pass through
    """

    def __init__(self, label=""):
        super().__init__()
        self.label = label

    def __str__(self):
        return f"Scope {self.label}"
    
    def compute(self, t, dt):
        self.output = self.inputs['input'].output


class ODE(Block):

    """
    implements first order ordinary differential equation, 
    solved with the trapezoidal rule (euler rule for the first timestep)
    
        d/dt x = f(x, y)
             u = g(x, y)

    the functions f and g are defined by expressions where x is the state variable and y is the input variable
    """

    def __init__(self, initial_value=0, expression_f="x+y", expression_g="x+y"):
        super().__init__()
        self.state = initial_value
        self.prev_state = None
        self.prev_input = None
        self.expression_f = expression_f
        self.expression_g = expression_g
        self.func_f = lambda x, y : eval(expression_f)
        self.func_g = lambda x, y : eval(expression_g)

    def __str__(self):
        return f"ODE {self.state} {self.expression_f} {self.expression_g}"

    def compute(self, t, dt):
        input_signal = self.inputs['input'].output
        if self.prev_state is None or self.prev_input is None :
            self.temp_state = self.state + dt * self.func_f(self.state, input_signal)
        else:
            self.temp_state = self.state + dt/2 * (self.func_f(self.state, input_signal) + self.func_f(self.prev_state, self.prev_input))

    def update_output(self):
        self.prev_input, input_signal = sinput_signal, self.inputs['input'].output
        self.prev_state, self.state   = self.state   , self.temp_state
        self.output = self.func_g(self.state, input_signal)
