import mcell as m

from parameters import *

# ---- subsystem ----

species_a = m.Species(
    name = 'a',
    diffusion_constant_3d = MOL_A_SPEED
)

species_b = m.Species(
    name = 'b',
    diffusion_constant_3d = MOL_B_SPEED
)

subsystem = m.Subsystem()
subsystem.add_species(species_a)
subsystem.add_species(species_b)
