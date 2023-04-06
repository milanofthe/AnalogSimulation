# GraphSimulation

This project is a small analog simulation framework that allows you to model and simulate various analog components and their connections. The simulator supports components such as amplifiers, integrators, comparators, adders, multipliers, constant sources, inverters, generators, delays, and displays.

The simulator uses a fixed-point iteration method to compute the output values of the blocks, making it suitable for systems that include feedback loops and other complex interconnections.


## Features
- Support for various analog components.
- Ability to add custom components by extending the Block class.
- Load and save simulation configurations and states from/to files.
- Easily modifiable and extensible codebase.
- Fixed-point iteration for simulating feedback loops.

## Imports


```python
import numpy as np
import matplotlib.pyplot as plt
plt.style.use('dark_background')
cycle = plt.rcParams['axes.prop_cycle'].by_key()['color']

from utils import (
    load_simulation_from_file,
    save_simulation_to_file
)
```

## Usage 
To create a new simulation, you need to define the components (blocks) and their connections. First, instantiate the components, then create connections between them, and finally, create a Simulation object with the blocks and connections. 

Alternatively the blocks, connections and initial states together with the timestep can be defined witin an external file.

    SYNTAX
    BLOCK <id> <type> <args>
    CONNECTION <to_id> <to_input> <from_id>
    STATE <id> <value> (optional)
    TIME <dt> <time>
    


```python
sim = load_simulation_from_file("oscillator.txt")
```

## Iterations

To run the simulation, call the .update() method on the Simulation object to compute the next timestep.


```python
data = [[] for _ in range(len(sim.blocks))]
time = []

for _ in range(4000):
    
    sim.update()
    
    time.append(sim.time)
    for i, val in enumerate(sim.get_state().values()):
        data[i].append(val)

```


```python
fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(10,5), dpi=120)

for d, block in zip(data, sim.blocks):
    ax.plot(time, d, label=type(block).__name__)
    
ax.grid(True)
ax.set_xlabel("time [s]")
ax.set_ylabel("states")
ax.legend()

plt.savefig("plot.png")
```


    
![png](README_files/README_7_0.png)
    



```python
!jupyter nbconvert --ClearMetadataPreprocessor.enabled=True --ClearOutput.enabled=True --to markdown README.ipynb
```

    [NbConvertApp] Converting notebook README.ipynb to markdown
    [NbConvertApp] Support files will be in README_files\
    [NbConvertApp] Making directory README_files
    [NbConvertApp] Writing 2554 bytes to README.md
    
