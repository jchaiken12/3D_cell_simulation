import mcell as m

from parameters import *
from subsystem import *
from geometry import *

# ---- observables ----

viz_output = m.VizOutput(
    mode = m.VizMode.ASCII,
    output_files_prefix = './viz_data/seed_' + str(SEED).zfill(5) + '/Scene',
    every_n_timesteps = 10
)

# declaration of rxn rules defined in BNGL and used in counts

observables = m.Observables()
observables.add_viz_output(viz_output)
