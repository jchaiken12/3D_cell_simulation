# Project Directory
Here is where the simulation script was run. The contained sub directories are examples from the mcell team that work and
can be used to quickly test if the project is working correctly. 

## General Setup for Linux
Conda was used to manage the python version for the required minimum version of python. The minimum desired version of python 
was version 3.11 as stated on the mcell website. Then the environment variable MCELL_PATH was set in the command line by:

    export MCELL_PATH=<install_path>/Blender-2.93-CellBlender/2.93/scripts/addons/cellblender/extensions/mcell

Once the correct python version is set to be run for the command line and the environment variable is set to the correct path
one can run the main python script. The main python script to run each simulation is called model.py.
On the command line we would write the following line with reference to the correct path:

    python model.py

A data_layout.json file and viz_data, reports, and __pycache__ folders should be created with data constantly being added to the
viz_data folder until all iterations are finished.
## General Setup for Microsoft Windows 11

