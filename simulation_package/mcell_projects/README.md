# Project Directory
Here is where the simulation script was run. The contained sub directories are examples from the mcell team that work and
can be used to quickly test if the project is working correctly. 

## General Setup for Ubuntu 20.04.6 LTS
Conda was used to manage the python version for the required minimum version of python. The minimum desired version of python 
was version 3.11 as stated on the mcell website. Then the environment variable MCELL_PATH was set in the command line by:

    export MCELL_PATH=<install_path>/Blender-2.93-CellBlender/2.93/scripts/addons/cellblender/extensions/mcell/

The same should be done for a later version of Blender and the corresponding cellblender addon. The path and file structure 
for the newest cellblender addon is different but what is needed is the reference to the same location of the mcell folder. 
Once the correct python version is set to be run for the command line and the environment variable is set to the correct path
one can run the main python script. The main python script to run each simulation is called model.py. Make sure all 
model.py, parameters.py, subsystem.py, model.bngl, observables.py, geometry.py, etc are all in the same folder.
On the command line we would write the following line with reference to the correct path:

    python model.py

A data_layout.json file and viz_data, reports, and pycache folders should be created with data constantly being added to the
viz_data folder until all iterations are finished. The number of iterations should be defined in paramters.py.

## General Setup for Microsoft Windows 11
Again we need at least python 3.11 to run the code. Then the environment variable MCELL_PATH must be set through Microsofts
environment variables window. To create a new variable: Click "New" under the desired section (User or System), enter the 
"Variable name" of MCELL_PATH and "Variable value" as 

    <install_path>/Blender-2.93-CellBlender/2.93/scripts/addons/cellblender/extensions/mcell/
    
and click "OK." <br/>
Next open a command line and navigate to the location where all the python files are downloaded just as in the above Linux
setup and run

    python model.py

The same output as above should be expected.

## Visualization with Blender using Cellblender
The command that starts Blender and allows a simulation run to be visualized is as follows:
    
    <install_path>/Blender-2.93-CellBlender/my_blender -P <install_path>/Blender-2.93-CellBlender/2.93/scripts/addons/cellblender/developer_utilities/mol_viz_scripts/viz_mcell_run.py -- viz_data/seed_00001/
