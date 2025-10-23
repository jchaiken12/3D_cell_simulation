import mcell as m

from geometry import *

# ---- model parameters ----

# load parameters from BNGL
bngl_params = m.bngl_utils.load_bngl_parameters('model.bngl')

k_bind = bngl_params['k_bind']
k_unbind = bngl_params['k_unbind']

# ---- simulation setup ----

ITERATIONS = 1000
TIME_STEP = 1e-6
DUMP = False
EXPORT_DATA_MODEL = True

# basic geometry parameters for our given simulation
CELL_NUM_VERTICES = len(Cell_vertex_list)
COVER_SLIP_NUM_VERTICES = len(Cover_slip_vertex_list)
PAIRING_DISTANCE = 0.05 # probably desirable radius 0.005

# do not use the variable module_seed_value directly,
# Python on import creates copies that do not reflect the current value
module_seed_value = 1

def update_seed(new_value):
    global module_seed_value
    module_seed_value = new_value

def get_seed():
    return module_seed_value
