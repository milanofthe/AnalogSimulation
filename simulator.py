#############################################################################
##
##                            SIMULATION ENGINE
##
##                            Milan Rother 2023
##
#############################################################################

# IMPORTS ===================================================================

from blocks import (
    Integrator, 
    Delay
)


# CLASSES ====================================================================

class Connection:

    """
    class to handle input-output relations of blocks
    by connecting them (directed graph)
    """

    def __init__(self, target, target_input, source):
        self.target = target
        self.target_input = target_input
        self.source = source

    def connect(self):
        self.target.connect(self.target_input, self.source)


class Simulation:

    def __init__(self, blocks, connections, dt, time=0):
        self.blocks = blocks
        self.connections = connections
        self.dt = dt
        self.time = time

        self.initialize_simulation()


    def initialize_simulation(self):

        """
        Initialize the connections between the blocks and do 
        some preprocessing to improve the convergence od the simulation.
        """

        # Initialize the input connections for each block
        for connection in self.connections:
            connection.connect(connection.target_input, connection.source)

        # break algebraic loops by introducing small delay
        self.detect_and_break_loops()

        # sort the blocks based on their dependencies
        self.blocks = self.sort_blocks()


    def add_block(self, block):

        """
        add block to existing simulation
        """

        self.blocks.append(block)
        self.detect_and_break_loops()
        self.blocks = self.sort_blocks()
        

    def add_connection(self, connection):

        """
        add connection to existing simulation
        """

        connection.connect(connection.target_input, connection.source)
        self.connections.append(connection)
        self.detect_and_break_loops()
        self.blocks = self.sort_blocks()
        

    def sort_blocks(self):

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


    def detect_and_break_loops(self):

        """
        Performs a depth-first search on each block to detect loops. 
        If a loop is detected and the connected block isn't a Delay block, 
        a new Delay block is created, connected to the block, 
        and added to the list of blocks in the simulation. 
        This breaks the loop by introducing a small delay in the signal path.
        """

        visited = set()

        def visit(block, path, prev_input_name=None):

            if block in visited:
                return False

            if block in path:
                return True

            path.add(block)
            
            loop_detected = False

            for input_name, connected_block in block.inputs.items():

                if visit(connected_block, path, input_name):
                    loop_detected = True
                    
                    if not isinstance(connected_block, Delay):
                        delay_block = Delay()
                        delay_block.connect('input', connected_block)
                        self.blocks.append(delay_block)
                        block.connect(input_name, delay_block) 
            
            path.remove(block)

            visited.add(block)
            
            return loop_detected

        for block in self.blocks:

            if block not in visited:
                visit(block, set())


    def update(self, max_iterations=100, tolerance=1e-5):

        """
        perform one update of the simulation (time increment by dt)
        resolve steady state by fixed-point iteration

        INPUTS:
            max_iterations : (int) maximum numbver of fixed-point iterations
            tolerance      : (float) tolerance for convergence of fixed-point iterations
        """

        self.time += self.dt

        steady_state   = False

        for it in range(max_iterations):

            prev_outputs = self.get_state()

            for block in self.blocks:
                block.compute(self.time, self.dt)

            max_difference = max(abs(block.output - prev_outputs[block]) for block in self.blocks)

            if max_difference < tolerance:
                steady_state = True
                break

        # Update the output of the Integrators
        for block in self.blocks:
            if isinstance(block, Integrator):
                block.update_output()

        if not steady_state:
            print("Warning: Steady state not reached within the maximum number of iterations")


    def get_state(self):

        """
        returns the current state of the simulation 
        (output values of all blocks)
        """

        return {block: block.output for block in self.blocks}
