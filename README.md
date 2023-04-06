# AnalogSimulation

This project is a small analog simulation framework that allows you to model and simulate various analog components and their connections. The simulator supports components such as amplifiers, integrators, comparators, adders, multipliers, constant sources, inverters and arbitrary signal generators.

The simulator uses a fixed-point iteration method to compute the output values of the blocks, making it suitable for systems that include feedback loops and other complex interconnections.


## Features
- Support for various analog components.
- Ability to add custom components by extending the Block class.
- Load and save simulation configurations and states from/to files.
- Easily modifiable and extensible codebase.
- Fixed-point iteration for simulating feedback loops.

## Imports


```python
import matplotlib.pyplot as plt
plt.style.use('dark_background')
cycle = plt.rcParams['axes.prop_cycle'].by_key()['color']

from utils import load_simulation_from_file
```

## Usage 
To create a new simulation, you need to define the components (blocks) and their connections. First, instantiate the components, then create connections between them, and finally, create a Simulation object with the blocks and connections. 

Alternatively the blocks, connections and initial states together with the timestep can be defined witin an external file with the following syntax:

    BLOCK <id> <type> <args>
    CONNECTION <to_id> <to_input> <from_id>
    STATE <id> <value> (optional)
    TIME <dt> <time>
    


```python
#sim = load_simulation_from_file("oscillator.txt")
#sim = load_simulation_from_file("driven_nonlinear_oscillator.txt")
#sim = load_simulation_from_file("two_mass_oscillator.txt")
sim = load_simulation_from_file("nonlinear_pendulum.txt")
```

## Simulation

To run the simulation for a specific duration, call the run() method on the Simulation object with the desired duration.


```python
time, data = sim.run(duration=60, debug=False)
```


```python
#plot the results
fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(10,5), dpi=120, tight_layout=True)

for d, block in zip(data, sim.blocks):
    if type(block).__name__ == "Scope":
        ax.plot(time, d, label=block.label)
    
ax.grid(True)
ax.set_xlabel("time [s]")
ax.set_ylabel("states")
ax.legend(loc="lower right", ncol=2)

plt.savefig("plot.png")
```


![plot](https://user-images.githubusercontent.com/105657697/230493584-a86a185d-b194-40ef-aa2e-4f3a7367113c.png)


