import mcell as m

from parameters import *
from subsystem import *
from geometry import *

# ---- instantiation ----

# ---- release sites ----


rel_t1 = m.ReleaseSite(
    name = 'rel_t1',
    complex = m.Complex('t1', orientation = m.Orientation.UP),
    region = Cell,
    number_to_release = 700
)

rel_t2 = m.ReleaseSite(
    name = 'rel_t2',
    complex = m.Complex('t2', orientation = m.Orientation.UP),
    region = Cover_slip,
    number_to_release = 700
)

# ---- surface classes assignment ----


# ---- compartments assignment ----

# ---- instantiation data ----

instantiation = m.Instantiation()
instantiation.add_geometry_object(Cell)
instantiation.add_geometry_object(Cover_slip)
instantiation.add_release_site(rel_t1)
instantiation.add_release_site(rel_t2)
