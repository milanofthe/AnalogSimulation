#############################################################################
##
##                      FUNCTIONAL BLOCKS (blocks.py)
##
##                            Milan Rother 2023
##
#############################################################################

# IMPORTS ===================================================================

from math import * #needed for the evaluation of the expressions


# CLASSES ===================================================================

class Parameter:

    def __init__(self, parameter="x", value=1):
        self.parameter = parameter
        self.value = float(value) if value is not None else None


class Equation:

    def __init__(self, expression="z=3*x+y"):
        self.expression = expression
        self.left, self.right = expression.split("=")
        self.func = lambda **kwargs : eval(self.right, kwargs)

    def compute(self, parameters=[]):
        kwargs = {p.parameter : p.value for p in parameters if p.parameter in self.right}
        for p in parameters:
            if p.parameter == self.left:
                p.value = self.func(**kwargs)


class Block:

    """
    base Block object that defines the 
    inputs and the connect method
    """

    def __init__(self):

        #general properties for simulation
        self.inputs = {}
        self.output = 0

        #identifier for reference
        self.id = None
        
        #display propertiers
        self.label = type(self).__name__.lower()

    def __str__(self):
        raise NotImplementedError()    

    def connect(self, input_name, other_block):
        self.inputs[input_name] = other_block

    def compute(self, t, dt):
        raise NotImplementedError()

    def update_output(self):
        pass

    def check_parameter(self):
        pass


class Amplifier(Block):

    """
    amplifies the input signal by 
    multiplication with a constant gain term
    """

    def __init__(self, gain=1.0):
        super().__init__()
        self.gain = gain

    def __str__(self):
        return f"Amplifier {self.gain}"

    def check_parameter(self):
        #handle parameter for gain
        if isinstance(self.gain, Parameter):
            self.gain = self.gain.value
        else:
            self.gain = float(self.gain)

    def compute(self, t, dt):
        
        if len(self.inputs) == 0:
            raise ValueError(f"No input defined for block {self.label}_{self.id}")

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
        self.output = initial_value
        self.temp_output = initial_value
        self.prev_input = None

    def __str__(self):
        return f"Integrator {self.output}"

    def check_parameter(self):

        #handle parameter for initial condition
        if isinstance(self.output, Parameter):
            self.output = self.output.value
            self.temp_output = self.temp_output.value
        else:
            self.output = float(self.output)
            self.temp_output = float(self.temp_output)


    def compute(self, t, dt):

        #handle missing input
        if len(self.inputs) == 0:
            raise ValueError(f"No input defined for block {self.label}_{self.id}")

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

        if len(self.inputs) == 0:
            raise ValueError(f"No input defined for block {self.label}_{self.id}")

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
        self.threshold = threshold

    def __str__(self):
        return f"Comparator {self.threshold}"

    def check_parameter(self):

        #handle parameter for threshold
        if isinstance(self.threshold, Parameter):
            self.threshold = self.threshold.value
        else:
            self.threshold = float(self.threshold)

    def compute(self, t, dt):

        #handle missing input
        if len(self.inputs) == 0:
            raise ValueError(f"No input defined for block {self.label}_{self.id}")

        input_signal = self.inputs['input'].output
        self.output = 1 if input_signal >= self.threshold else 0


class Adder(Block):

    """
    adds all input signals
    """

    def __str__(self):
        return "Adder"

    def compute(self, t, dt):

        if len(self.inputs) == 0:
            raise ValueError(f"No input defined for block {self.label}_{self.id}")

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

        if len(self.inputs) == 0:
            raise ValueError(f"No input defined for block {self.label}_{self.id}")

        self.output = 1
        for input_block in self.inputs.values():
            self.output *= input_block.output


class Constant(Block):

    """
    produces a constant output signal 
    (same as Generator with fx="1")
    """

    def __init__(self, value=1):
        super().__init__()
        self.output = value

    def __str__(self):
        return f"Constant {self.output}"

    def check_parameter(self):
        #handle parameter for output
        if isinstance(self.output, Parameter):
            self.output = self.output.value
        else:
            self.output = float(self.output)

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

        if len(self.inputs) == 0:
            raise ValueError(f"No input defined for block {self.label}_{self.id}")

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

        if len(self.inputs) == 0:
            raise ValueError(f"No input defined for block {self.label}_{self.id}")

        input_signal = self.inputs['input'].output
        self.output = self.func(input_signal)


class Scope(Block):
    
    """
    block for visualization, input pass through
    """

    def __init__(self, label="output"):
        super().__init__()
        self.label = label

    def __str__(self):
        return f"Scope {self.label}"
    
    def compute(self, t, dt):

        if len(self.inputs) == 0:
            raise ValueError(f"No input defined for block {self.label}_{self.id}")

        self.output = self.inputs['input'].output


class Subsystem(Block):

    """
    this class implements a subsystem made of multiple 
    blocks and connections, where the first block is the 
    input block and the last block is the output block
    """

    def __init__(self, blocks=[], connections=[], label="Subsystem"):
        super().__init__()
        self.blocks = blocks
        self.connections = connections

    def __str__(self):
        return f"Subsystem {self.label}"
        
    def connect(self, input_name, other_block):
        self.blocks[0].connect(input_name, other_block)
        for connection in self.connections:
            connection.target.connect(connection.target_input, connection.source)

    def compute(self, t, dt):
        for block in self.blocks:
            block.compute(t, dt)

    def update_output(self):
        for block in self.blocks:
            block.update_output()
        self.output = self.blocks[-1].output

