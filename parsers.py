#############################################################################
##
##                            PARSER FUNCTIONS
##
##                            Milan Rother 2023
##
#############################################################################

# IMPORTS ===================================================================

from blocks import *
from simulation import *


# FUNCS =====================================================================

def parse_simulation_file(filename):

    """
    load simulation blocks, connections and state 
    from .txt file and returns blocks, connections 
    and time if available

    INPUTS:
        filename : path to file
    """

    block_types = {
        "Amplifier"      : Amplifier,
        "Integrator"     : Integrator,
        "Comparator"     : Comparator,
        "Adder"          : Adder,
        "Multiplier"     : Multiplier,
        "Constant"       : Constant,
        "Inverter"       : Inverter,
        "Generator"      : Generator,
        "Function"       : Function,
        "Scope"          : Scope,
        "Differentiator" : Differentiator,
        "Subsystem"      : Subsystem
    }


    #sort lines by prefixes

    block_lines = []
    connection_lines = []
    state_lines = []
    parameter_lines = []
    equation_lines = []
    
    dt, time = None, None

    with open(filename, 'r') as file:

        for line in file:

            #remove junk
            line = line.strip()

            #skip empty lines and comments
            if not line or line.startswith('#'):
                continue

            #remove inline comment
            line, *_ = line.split("#")

            #extract info from line
            prefix, *parts = line.split()

            if prefix == "BLOCK":
                block_lines.append(parts)

            elif prefix == "CONNECTION":
                connection_lines.append(parts)

            elif prefix == "TIME":
                dt, time = parts
                dt, time = float(dt), float(time)

            elif prefix == "PARAMETER":
                parameter_lines.append(parts)

            elif prefix == "EQUATION":
                equation_lines.append(parts)

            else:
                raise ValueError(f"Unknown line prefix: {prefix}")

    #handle parameters
    parameters = {}
    for line in parameter_lines:
        if len(line)==1:
            param, *_ = line
            value = None
        else:
            param, value = line
        parameters[param] = Parameter(param, value)

    #handle equations
    equations = []
    for expr in equation_lines:
        equations.append(Equation("".join(expr)))

    #handle blocks
    blocks = {}
    for block_id, block_type, *block_args in block_lines:

        #check if subsystem
        if block_type == "Subsystem":
            block = load_subsystem_from_file(*block_args)
            continue

        #check if parameter given
        for i, arg in enumerate(block_args): 
            if arg in parameters:
                block_args[i] = parameters[arg]

        #initialize block
        block = block_types[block_type](*block_args)
        block.id = block_id

        blocks[block_id] = block

    #handle connections
    connections = []
    for source_block_id, target_block_id, target_input_name in connection_lines:
        connections.append(Connection(blocks[target_block_id], 
                                      target_input_name, 
                                      blocks[source_block_id]))

    #rearrange into list
    blocks = list(blocks.values())
    parameters = list(parameters.values())

    return blocks, connections, parameters, equations, dt, time
        

def load_subsystem_from_file(filename):

    """
    load simulation blocks, connections and state 
    from .txt file and returns subsystem object

    INPUTS:
        filename : path to file
    """
    
    blocks, connections, *_ = parse_simulation_file(filename)

    return Subsystem(blocks, connections, filename)


def load_simulation_from_file(filename):

    """
    load simulation blocks, connections and state 
    from .txt file and returns simulation object

    INPUTS:
        filename : path to file
    """

    blocks, connections, parameters, equations, dt, time = parse_simulation_file(filename)

    if time is None or dt is None:
        return Simulation(blocks, connections, parameters, equations)
    else:
        return Simulation(blocks, connections, parameters, equations, dt, time)