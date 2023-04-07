#############################################################################
##
##                     SIMULATION ENGINE (simulator.py)
##
##                            Milan Rother 2023
##
#############################################################################

# IMPORTS ===================================================================

from utils import timer
from blocks import Integrator, Differentiator, Scope


# CLASSES ===================================================================

class Connection:

    """
    class to handle input-output relations of blocks
    by connecting them (directed graph)
    """

    def __init__(self, target, target_input, source):

        self.target       = target
        self.target_input = target_input
        self.source       = source


class Simulation:

    """
    main simulation class that handles all the blocks 
    and connections and the timestep update
    """

    def __init__(self, blocks, connections, dt, time=0):

        """
        initialize the simulation

        INPUTS:
            blocks      : (list) list of Block objects
            connections : (list) list of Connection objects
            dt          : (float) timestep
            time        : (float) sinulation time
        """

        self.blocks      = blocks
        self.connections = connections
        self.dt          = dt
        self.time        = time

        self._initialize_simulation()


    def _initialize_simulation(self):

        """
        Initialize the connections between the blocks and do 
        some preprocessing to improve the convergence of the simulation.
        """

        #initialize the input connections for each block
        for connection in self.connections:
            connection.target.connect(connection.target_input, connection.source)

        #sort the blocks based on their dependencies
        self.blocks = self._sort_blocks()

        #save the initial state
        self.initial_state = self.get_state()


    def add_block(self, block):
        """
        add block to existing simulation
        """
        self.blocks.append(block)
        self.blocks = self._sort_blocks()
        

    def add_connection(self, connection):
        """
        add connection to existing simulation
        """
        connection.target.connect(connection.target_input, connection.source)
        self.connections.append(connection)
        self.blocks = self._sort_blocks()
        

    def _sort_blocks(self):

        """
        sort the blocks chronologically by their connections 
        using a recursive depth-first search function 
        that visits each block and its dependencies
        """

        visited = set()
        sorted_blocks = []

        def visit(block):

            if block not in visited:

                visited.add(block)

                for connected_block in block.inputs.values():

                    if connected_block not in visited:
                        visit(connected_block)

                sorted_blocks.append(block)

        unsorted_blocks = list(self.blocks)

        while unsorted_blocks:

            current_block = unsorted_blocks.pop()

            if current_block not in visited:
                visit(current_block)

        return sorted_blocks


    def update(self, max_iterations=20, tolerance=1e-6, debug=False):

        """
        perform one update of the simulation (time increment by dt)
        resolve steady state by fixed-point iteration

        INPUTS:
            max_iterations : (int) maximum numbver of fixed-point iterations
            tolerance      : (float) tolerance for convergence of fixed-point iterations
            debug          : (bool) print debugging info (convergence etc.)
        """

        #increment simulation time
        self.time += self.dt

        if debug:
            print("\ndebug status:")
            print("    time :", self.time)

        steady_state = False

        #perform fixed-ppoint iterations
        for iteration in range(max_iterations):

            #save previous state for convergence checking
            prev_state = self.get_state()

            #update states of all blocks
            for block in self.blocks:
                block.compute(self.time, self.dt)

            #compute relative deviation
            max_rel_diff = max(abs((blk.output - prev_state[blk])/blk.output) 
                                for blk in self.blocks if blk.output != 0.0)

            if debug:
                print("        iteration  :", iteration+1)
                print("        difference :", max_rel_diff)

            #check for convergence
            if max_rel_diff < tolerance:
                steady_state = True
                break

        #update the outputs (blocks with internal states)
        for block in self.blocks:
            block.update_output()

        if not steady_state:
            print(f"Steady state not reached!")


    @timer
    def run(self, duration=10, max_iterations=100, tolerance=1e-6, debug=False):

        """
        performs multiple simulation steps and returns 
        the time series results over the time steps

        INPUTS:
            total_time     : (float) simulation time [s]
            max_iterations : (int) maximum numbver of fixed-point iterations
            tolerance      : (float) tolerance for convergence of fixed-point iterations
            debug          : (bool) print debugging info (convergence etc.)
        """

        #set local time
        start_time = self.time

        #initialize the time series data
        data = [[] for _ in range(len(self.blocks))]
        time = []

        #iterate until duration is reached
        while self.time - start_time < duration:

            #perform one iteration
            self.update(max_iterations, tolerance, debug)
            
            #save the current state
            time.append(self.time)
            for i, val in enumerate(self.get_state().values()):
                data[i].append(val)

        return time, data


    def reset(self):
        """
        reset the simulation to the initial state 
        and reset the simulation time
        """
        self.time = 0
        self.set_state(self.initial_state)


    def get_state(self):
        """
        returns the current state of the simulation 
        (output values of all blocks)
        """
        return {block: block.output for block in self.blocks}


    def set_state(self, state):
        """
        set the state of the simulation 
        (output values of all blocks)
        """
        for block, val in zip(self.blocks, state.values()):
            block.output = val

    def get_outputs(self):
        """
        collect outputs of scopes into a dict
        """
        outputs = {}
        for block in self.blocks:
            if isinstance(block, Scope):
                outputs[block.label] = block.output
        return outputs