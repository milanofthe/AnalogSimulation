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
    Delay
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
        "Delay"      : Delay
    }

    for line in lines:
        line = line.strip()

        # Skip empty lines and comments
        if not line or line.startswith('#'):
            continue

        parts = line.split()
        prefix = parts[0]

        if prefix == "BLOCK":
            block_id, block_type = int(parts[1]), parts[2]
            block_args = [eval(arg) for arg in parts[3:]]
            block = block_types[block_type](*block_args)
            blocks.append(block)

        elif prefix == "CONNECTION":
            target_block_id, target_input_name, source_block_id = int(parts[1]), parts[2], int(parts[3])
            connection = Connection(blocks[target_block_id], target_input_name, blocks[source_block_id])
            connections.append(connection)

        elif prefix == "STATE":
            block_id, state_value = int(parts[1]), eval(parts[2])
            state_values[block_id] = state_value

        elif prefix == "TIME":
            dt, time = eval(parts[1]), eval(parts[2])

        else:
            raise ValueError(f"Unknown line prefix: {prefix}")

    if dt is None or time is None:
        raise ValueError("Simulation time or timestep not found in file")

    for block_id, state_value in state_values.items():
        blocks[block_id].output = state_value

    return Simulation(blocks, connections, dt, time)


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
            block_type = type(block).__name__
            block_specific_params = []
            if isinstance(block, Amplifier):
                block_specific_params = [block.gain]
            elif isinstance(block, Integrator):
                block_specific_params = [block.output]
            elif isinstance(block, Comparator):
                block_specific_params = [block.threshold]
            elif isinstance(block, Constant):
                block_specific_params = [block.output]

            block_specific_params_str = ' '.join(repr(p) for p in block_specific_params)
            f.write(f"BLOCK {i} {block_type} {block_specific_params_str}\n")

        for connection in simulation.connections:
            target_block_id = simulation.blocks.index(connection.target)
            source_block_id = simulation.blocks.index(connection.source)
            f.write(f"CONNECTION {target_block_id} {connection.target_input} {source_block_id}\n")

        for i, block in enumerate(simulation.blocks):
            f.write(f"STATE {i} {repr(block.output)}\n")

        f.write(f"TIME {repr(simulation.dt)} {repr(simulation.time)}\n")