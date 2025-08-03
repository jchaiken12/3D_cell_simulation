Dynamic Geometry
=========================================================================

Overview
-------------------------------------------------------------------------

Before we get into how the algorithm works, here is how it is used:

Mesh "snapshots" are referenced in a text file similar to how variable rate
constant files are handled. The first column contains MDL filenames and the
second column contains the time at which the geometry should be used. As an
example, imagine we have a file called geometry_snapshots.txt that contained
the following:

    my_geometry0.mdl 0e-6
    my_geometry1.mdl 1e-6
    my_geometry2.mdl 2e-6
    my_geometry3.mdl 3e-6
    ...

Each MDL listed would contain mesh object definitions (usually one wouldn't add
new meshes or remove existing ones, but this is now allowed) where the vertices
and elements might be different. You would also need to re-instantiate the
existing mesh objects. For example, my_geometry0.mdl might contain the
following:

    Cube POLYGON_LIST {
      VERTEX_LIST {
        [  0.1,  0.1, -0.1 ]
        ...
      }
      ELEMENT_CONNECTIONS {
        [ 0, 1, 2 ]
        ...
      }
    }
    INSTANTIATE Scene OBJECT
    {
      Cube OBJECT Cube{}
    }

In this example, each subsequent file referenced in geometry_snapshots.txt
(e.g. my_geometry1.mdl, my_geometry2.mdl, etc) might have a definition and
instantiation of the Cube object. As mentioned before, the actual vertices and
elements can be different.

Finally, the file containing this list of MDLs and times
(geometry_snapshots.txt in this example) would be referenced somewhere in your
main MDL using a new keyword called DYNAMIC_GEOMETRY like this:

DYNAMIC_GEOMETRY = "geometry_snapshots.txt"

Note: For lack of a better term, we will refer to the file assigned to
DYNAMIC_GEOMETRY file as the "dynamic geometry file". Do not confuse this with
the MDLs that have the actual geometry/meshes and instantiations.

The usage is probably best explained in the wiki:

https://github.com/mcellteam/mcell/wiki/Using-Dynamic-Geometries

Algorithm
-------------------------------------------------------------------------

Now, we can move onto how the algorithm actually works:

### Initialization

Along with all the other data structures, memory for dynamic geometry events is
allocated in init_data_structures (init.c).

The scheduler is created in init_dynamic_geometry (init.c).

### Parsing

During parse time, we check what text file is assigned to DYNAMIC_GEOMETRY
(mcell_add_dynamic_geometry_file in mcell_dyngeom.c). We then process the
dynamic geometry file, adding an event to the dynamic_geometry_head
(add_dynamic_geometry_events in dyngeom.c) for each line in the DG file. Also,
we do a preliminary parse of all the geometry files listed in the DG file
(parse_dg in dyngeom_yacc.c). We need to do this to make sure that objects we
are counting in/on will exist at some point during the simulation. NOTE: This
is different than the regular geometry parsing done in mcell_parse_mdl and uses
a different parser. The preliminary parsing is somewhat involved and so is
covered more thoroughly in a later section of this document. After the
preliminary parsing is done, everything in dynamic_geometry_head is added to
the scheduler (end of schedule_dynamic_geometry in init.c).

### Set Up Some Data Structures

Create a data structure so we can quickly check if a molecule species can move
in or out of any given surface region. (init_species_mesh_transp in dyngeom.c)

### Run Simulation

Once the simulation starts, check for a scheduled geometry change every
timestep (process_geometry_changes in mcell_run.c). If a geometry change is
scheduled, we do the following:

- Save all the molecules available in the scheduler (save_all_molecules)
  - For volume molecules, keep track of enclosing meshes in the order of
    nesting. (save_volume_molecule)
  - For surface molecules, keep track of the mesh it is on as well as all
    regions. (save_surface_molecule)
  - Save common properties like next uni reaction, scheduling time, birthday,
    etc. (save_common_molecule_properties).
  - Side note: Finding what mesh a molecule is inside of is explained in point
    2 below. (find_enclosing_meshes)
- Save a list of names of all the meshes and regions in fully qualified form
  prior to trashing them (create_mesh_instantiation_sb). We'll get back to this
  in a minute.
- Now the fun part; destroy geometry, subvolumes, memory helpers, and pretty
  much the entire simulation (destroy_everything in mcell_redo_geom). We also
  zero out counts (reset_current_counts), because they'll get repopulated when
  we count from scratch later. Well, we leave things like molecule and reaction
  definitions alone, since they're not hurting anyone.
- Parse the new geometry and instantiation information. (mcell_parse_mdl in
  mcell_redo_geom)
- Re-initialize the things we just destroyed (init_partitions,
  init_vertices_walls, init_regions). 
- Save a list of the *new* mesh names (create_mesh_instantiation_sb) and
  compare them with the *old* names to see if anything has been added or
  removed (sym_diff_string_buffers). We will ignore newly added or removed
  meshes and regions for the purpose of placing molecules this time. New meshes
  will be tracked during subsequent dynamic geometry events.
- Place all the molecules that we previously saved, moving molecules if
  necessary to keep them in/on the appropriate compartment
  (place_all_molecules).

### Placement of Volume Molecules

To expand on the last point, here's how placement works for volume molecules
(insert_volume_molecule_encl_mesh):

1. Find what subvolume the molecule should be in now based on its saved
   location. (find_subvolume in vol_util.c)
2. Find the current enclosing meshes. (find_enclosing_meshes in dyngeom.c)
  A. Pick a random vector and scale it so that it's big enough to cross the
     entire world.
  B. Ray trace from the current molecule location along the direction of the
     random vector.
  C. Start working through all our collisions
    a. Keep track of how many times we cross each *closed* mesh. If odd number,
       then we are inside it. If even, then we are outside it.
       (http://en.wikipedia.org/wiki/Point_in_polygon)
    b. If we reach the edge of the world (outermost subvolume), return each
       enclosing mesh name (i.e. the first) we found, assuming there is one. If
       there isn't one, then we are outside all objects and just return NULL.
    c. If we ever hit an interior subvolume, then repeat 2.B and 2.C until we
       hit the edge of the world.
3. Compare where the molecule was (prior to the geometry change) with where
   it is now relative to the meshes. This also takes into account meshes nested
   inside other meshes. Ultimately, we want to see if movement is possible from
   the starting position to the ending position. (compare_molecule_nesting)

   If the compartment nesting never changed and there were no molecule
   transparencies, then we could ignore the nesting and simply track the
   closest enclosing mesh. In fact, this is what was done in an earlier version
   of the dynamic geometries code. But that is not the case. In fact, meshes
   can be selectively transparent to a molecule (in-to-out, out-to-in, both, or
   neither), the transparent properties can change from one dynamic geometry
   event to the next, and entire meshes/regions can disappear.

   Now, a little discussion on notation for the sake of being clear and
   concise. When we say something like A->B->C->null, this means that mesh A is
   inside mesh B which is inside mesh C. Lastly, C is an outermost mesh.

   First, find "overlap" if any exists. (check_overlapping_meshes)
   For example:
     mesh_names_old: A->B->C->D->null
     mesh_names_new:       C->D->null
   "A" was the closest enclosing mesh and then "C" became the closest enclosing
   mesh. That means the molecule moved from "A" to "C".

   The order could be reversed like this:
     mesh_names_old:       C->D->null
     mesh_names_new: A->B->C->D->null
   This means the molecule moved from "C" to "A".

   We could also have a case with no overlap (aside from null) like this:
     mesh_names_old: C->D->null
     mesh_names_new: E->F->null
   This means the molecule moved from "C" to "E".
   (check_nonoverlapping_meshes)

4. See if we can legally be where we are at (check_outin_or_inout)
5. If the nesting is the same, just place the molecule where it is.
6. If the nesting is different, we need to move the molecule
   (place_mol_relative_to_mesh).
  A. Go through all the walls in the subvolume that is shared with the
     molecule.
  B. Find the distance to the closest wall.
  C. Check neighboring subvolumes to see if there's an even closer wall.
  D. Find closest wall and put the molecule either slightly in front of or
     behind it. By default, this is done to the nearest point
     (DYNAMIC_GEOMETRY_MOLECULE_PLACEMENT = NEAREST_POINT), but it's also
     possible to just set it to a random point on the nearest triangle
     (DYNAMIC_GEOMETRY_MOLECULE_PLACEMENT = NEAREST_TRIANGLE).
7. Update subvolume, enable counting, schedule it, and do other book
   keeping.

### Placement of Surface Molecules

Now, here's how placement works for surface molecules (insert_surface_molecule
and place_surface_molecule in vol_util.c):

1. Find what subvolume the molecule is now in based on its saved location.
2. Go through every wall in the subvolume. (find_subvolume)
  A. Make sure the object name and region names match what we saved previously
  aside for newly-added/removed regions and regions that we are transparent to.
  (verify_wall_regions_match in grid_util.c)
  B. If they match, find the closest point on the wall to our molecule's
  location (closest_interior_point in wall_util.c).
  C. Of all the walls, keep the best (i.e. the closest) location.
3. Make sure there's not a better/closer location in adjacent subvolumes.
4. Then make sure there's actually a free slot on the wall's surface grid.
5. If not, check neighboring walls.
6. If everything is okay, put it on the grid.
7. Make it countable for reaction output.
8. Add it to the scheduler.


Preliminary Parsing Geometry
-------------------------------------------------------------------------

Before parsing, we call create_dg_parse which creates a global (BOO!) pointer
to a struct called dg_parse, which stores some useful information about the
object(s) we are currently parsing, symbol tables, etc. Next, we call
init_top_level_objs, which create the aforementioned symbol tables. These are
used to store the objects and regions. We also create two top level objects
(WORLD_OBJ and WORLD_INSTANCE), add them to object symbol table, and add them
to the top of the root_object and root_instance trees.

The actual parsing itself begins in parse_dg where we set the root object and
root instance (setup_root_obj_inst). NOTE: This is unnecessary the first time
through, since it's also done in init_top_level_objs. Then we open the geometry
files for parsing by calling yyparse.

The first thing we will likely encounter when parsing a geometry file is a
polygon_list object (dg_new_polygon_list in dyngeom_parse_extras.c). We prepare
the object_name_list. This is necessary in case the object is part of a meta
object (this needs tested more thoroughly), such that the fully qualified name
is something like Vesicles.Left.Ves1. Then we call dg_start_object_simple
(dyngeom_parse_extras.c), which adds the name to the object_name_list to form
the fully qualified name and makes the new object (make_new_object).  This is
where the object name gets added to the DG object symbol table. Next we create
an "ALL" region, which every polygon object has (dg_create_region and
dg_make_new_region). We make a fully qualified region name of the form
"object_name,region_name" and store the name in the DG region symbol table. We
may process other regions the user created at this time. When all of this is
finished, we call dg_finish_object which basically just pops the name off the
object_name_list.

The next major thing that the user is likely to do is instantiate the objects.
As every object is created we first call dg_start_object. This is very similar
to dg_start_object_simple. We add the object name to the object_name_list and
store it in the DG object symbol table.

Eventually, we will copy the contents of one object into another one using
dg_deep_copy_object. For normal cases, this mainly entails copying the regions
of the source/original object to the destination/new object
(dg_copy_object_regions).
