#############################################################################
##
##                            UTILITY FUNCTIONS
##
##                            Milan Rother 2023
##
#############################################################################

# IMPORTS ===================================================================

from blocks import (
    Amplifier, 
    Integrator, 
    Comparator, 
    Adder, 
    Multiplier, 
    Constant, 
    Inverter, 
    Generator, 
    Delay,
    Function
)

from simulator import (
    Simulation, 
    Connection
)


# FUNCS ====================================================================

def load_simulation_from_file(filename):

    """
    load simulation blocks, connections and state 
    from .txt file and returns simulation object

    INPUTS:
        filename : path to file
    """

    with open(filename, 'r') as f:
        lines = f.readlines()

    blocks = []
    connections = []
    state_values = {}
    dt, time = None, None

    block_types = {
        "Amplifier"  : Amplifier,
        "Integrator" : Integrator,
        "Comparator" : Comparator,
        "Adder"      : Adder,
        "Multiplier" : Multiplier,
        "Constant"   : Constant,
        "Inverter"   : Inverter,
        "Generator"  : Generator,
        "Delay"      : Delay,
        "Function"   : Function
    }

    for line in lines:
        line = line.strip()

        # Skip empty lines and comments
        if not line or line.startswith('#'):
            continue

        parts = line.split()
        prefix = parts[0]

        if prefix == "BLOCK":
            _, block_id, block_type, *block_args = parts
            block = block_types[block_type](*block_args)
            blocks.append(block)

        elif prefix == "CONNECTION":
            _, target_block_id, target_input_name, source_block_id = parts
            connection = Connection(blocks[int(target_block_id)], 
                                    target_input_name, 
                                    blocks[int(source_block_id)])
            connections.append(connection)

        elif prefix == "STATE":
            _, block_id, state_value = parts
            state_values[int(block_id)] = float(state_value)

        elif prefix == "TIME":
            _, dt, time = parts

        else:
            raise ValueError(f"Unknown line prefix: {prefix}")

    if dt is None or time is None:
        raise ValueError("Simulation time or timestep not found in file")

    for block_id, state_value in state_values.items():
        blocks[block_id].output = state_value

    return Simulation(blocks, connections, float(dt), float(time))


def save_simulation_to_file(simulation, filename):

    """
    saves simulation blocks, connections and state 
    to .txt file in custom format.
    
    INPUTS:
        simulation : Simulation object
        filename   : path to file
    """
    
    with open(filename, 'w') as f:

        for i, block in enumerate(simulation.blocks):
            f.write(f"BLOCK {i} {repr(block)}\n")

        for connection in simulation.connections:
            target_block_id = simulation.blocks.index(connection.target)
            source_block_id = simulation.blocks.index(connection.source)
            f.write(f"CONNECTION {target_block_id} {connection.target_input} {source_block_id}\n")

        for i, block in enumerate(simulation.blocks):
            f.write(f"STATE {i} {repr(block.output)}\n")

        f.write(f"TIME {repr(simulation.dt)} {repr(simulation.time)}\n")