import mcell as m

from parameters import *
from subsystem import *
from geometry import *

# ---- instantiation ----

# ---- release sites ----

rel_a = m.ReleaseSite(
    name = 'rel_a',
    complex = species_a,
    shape = m.Shape.SPHERICAL,
    location = (0.0, 0.0, 0.1),
    site_diameter = 0,
    number_to_release = 1000
)

rel_b = m.ReleaseSite(
    name = 'rel_b',
    complex = species_b,
    shape = m.Shape.SPHERICAL,
    location = (0.0, 0.0, -0.1),
    site_diameter = 0,
    number_to_release = 1000
)

# ---- surface classes assignment ----


# ---- instantiation data ----

instantiation = m.Instantiation()
instantiation.add_geometry_object(Cube)
instantiation.add_geometry_object(Plane)
instantiation.add_release_site(rel_a)
instantiation.add_release_site(rel_b)
