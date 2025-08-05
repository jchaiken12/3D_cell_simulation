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

## Mcell Project
This folder is where all individual simulations were constucted and run using the command prompt. 
Python script would start with the line

    import mcell as m
    
to execute the necessary functions, parameters, etc. to run the physics based simulation. 

## Comments
All the code was run and tested in a linux environment. No code has been tested in a windows
operating system. 
