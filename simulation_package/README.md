# Description
This was the file structure and code used to run the multiple cellular simulations.
Steps for installation can be found here <br/>
https://mcell.org/mcell4_documentation/installation.html <br/>
**Blender** version 2.93 and **Mcell** version 4.0.5 were used for all the simulations.
These older versions can be found here <br/>
https://mcell.org/download_previous_versions.html <br/>


## Mcell
This folder contains the required code to run the cellular simulation. The build files are included
in this folder allowing use of the code in other python scripts.
### Limitations
Over the course of the time doing projects limitations on what the engine could do for our desired 
physical simulation were encountered. 
1. We could not implement bulky molecules with just mcell4
2. No k-d tree or octree was implemented within the mcell4 engine drastically slowing down our implementation of frictional forces.

### For Future Development
There exist around 100 examples of scripts utilizing the mcell library in python that can be found here <br/>
https://github.com/mcellteam/mcell_tests/tree/master

Also lots of good documentation references on the examples with a nice search engine and what functions they utilize can be found below <br/>
https://mcell.org/mcell4_documentation/index.html

If for example some documentation on an object is missing the pymcell.pyi contained inside the mcell engine 
contains the rough outline of all the functions available to be used in python using the mcell library.
Modifying the Cellblender addon is signifigantly easier than modifying the mcell4 engine given the complexity
contained with the mcell4 engine. Both are doable but knowledge in topics of computer architecture, parallelization,
etc. are required to understand the mcell4 engine in its totality.

## Mcell Projects
This folder is where all individual simulation projects were constucted and run using the command prompt.
Probably around 30 projects and their accompanying scripts were created sequentially and then work began 
on the next project to be done. The general project  progression
was as follows:
1. A cellular piston done in mcell3, lost somewhere in the computer at the lab, 
2. Elasticity done in a developer version between mcell3 and mcell4, 
3. Pressure done in mcell4
4. Coverslip and car-t cell interaction with added polymerization, frictional forces, and existing elasticity

Once one project was finished there was no maintaince work done to see how the piston simulation ran in 
mcell4 for example.

Python script would start approximately with the lines

    #!/usr/bin/env python3
    import mcell as m
    
to execute the necessary functions, parameters, etc. to run the physics based simulation. 
Also this guarantees the correct version of python is run for the scripts.

