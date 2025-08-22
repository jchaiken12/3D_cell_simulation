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

## Mcell Projects
This folder is where all individual simulation projects were constucted and run using the command prompt.
Probably around 30 were created and then work began on the next project. The general project progression
was as follows:
1. A cellular piston done in mcell3, lost somewhere in the computer at the lab, 
2. Elasticity done in a developer version between mcell3 and mcell4, 
3. Pressure done in mcell4
4. Coverslip and car-t cell interaction with added polymerization and frictional forces


Python script would start approximately with the line

    #!/usr/bin/env python3
    import mcell as m
    
to execute the necessary functions, parameters, etc. to run the physics based simulation. 
Also this guarantees the correct version of python is run for the scripts.

