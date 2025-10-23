#!/usr/bin/env python3

import sys
import os

MCELL_PATH = os.environ.get('MCELL_PATH', '')
if MCELL_PATH:
    sys.path.append(os.path.join(MCELL_PATH, 'lib'))
else:
    print("Error: variable MCELL_PATH that is used to find the mcell library was not set.")
    sys.exit(1)

import mcell as m
import math
import numpy as np
from scipy.spatial import KDTree

from parameters import *

if len(sys.argv) == 3 and sys.argv[1] == '-seed':
    # overwrite value of seed defined in module parameters
    update_seed(int(sys.argv[2]))

import subsystem
import instantiation
import observables

# create main model object
model = m.Model()

# ---- configuration ----

model.config.time_step = TIME_STEP
model.config.seed = get_seed()
model.config.total_iterations = ITERATIONS
#model.config.surface_grid_density = 1000
model.notifications.rxn_and_species_report = True

# too small so is automatically calculated
model.config.partition_dimension = 200
#model.config.subpartition_dimension = 0.02

# ---- default configuration overrides ----


# ---- add components ----

model.add_subsystem(subsystem.subsystem)
model.add_instantiation(instantiation.instantiation)
model.add_observables(observables.observables)

# ---- initialization and execution ----

import numpy as np
import math
import matplotlib.pyplot as plt

model.initialize()

if DUMP:
    model.dump_internal_state()

if EXPORT_DATA_MODEL and model.viz_outputs:
    model.export_data_model()

import membrane_physics as mp
from stereometry import stereometry_tools

class RxnCallbackContext():
    def __init__(self):
        self.count = 0
        self.current_it = 0

rxn_info_array = []

def check_time(time, it):
    # cannot start before iteration start
    assert time >= it * TIME_STEP
    # we are running iterations one by one therefore
    # the max time is the end of this iteration
    assert time <= (it + 1) * TIME_STEP

def check_pos(pos3d):
    EPS = 1e-9
    # min and max coordinates from Cube
    assert pos3d[0] >= -70 - EPS and pos3d[0] <= 70 + EPS
    assert pos3d[1] >= -70 - EPS and pos3d[1] <= 70 + EPS
    assert pos3d[2] >= -70 - EPS and pos3d[2] <= 70 + EPS

rxn = model.find_reaction_rule('t1_plus_t2')

def rxn_callback(rxn_info, context):
    print('reaction occurred')
    context.count += 1

    #rxn_info_array.append(context.current_it)

    # print(rxn_info.reactant_ids);
    # assert len(rxn_info.reactant_ids) == 2
    # assert len(rxn_info.product_ids) == 1
    #
    # assert rxn_info.reactant_ids[0] >= 0 and rxn_info.reactant_ids[0] < 20000
    # assert rxn_info.reactant_ids[1] >= 0 and rxn_info.reactant_ids[1] < 20000
    #
    assert rxn_info.reaction_rule is rxn
    #
    # check_time(rxn_info.time, context.current_it)
    #
    # check_pos(rxn_info.pos3d)

    assert rxn_info.geometry_object is None

def norm_vec(vec):
    my_norm = np.linalg.norm(vec)
    if my_norm >= 10**(-6):
        for i in range(len(vec)):
            vec[i] = vec[i]/my_norm
    return vec


context = RxnCallbackContext()
rxn = model.find_reaction_rule('t1_plus_t2')

model.register_reaction_callback(
    rxn_callback, context, rxn
)

# here we define the the amount the cell membrane will expand or contract to defined
# equilibrium state based on pressure in system
displacement_const = 1

st = stereometry_tools(model, instantiation.Cell)
st.set_lists()
# place in membrane_physics since this is related to pressure
#vol = st.VolumeOfMesh()
#init_vol = vol*displacement_const

mp.set_stereometry(st)
nbrs = st.calc_nbrs(st.vertex_list, st.wall_list)
st.set_init_area(nbrs)

uniform_array = np.random.uniform(size=ITERATIONS)

z_height = 2
poly_push_const = 10
friction_const = 0
poly_push_attenuation_const = 1
pos_array = []

node_freeze_array = []
top_mols = []
bottom_mols = []
bottom_mols_xyz = []
paired_top_mol_ids = []
paired_bot_mol_ids = []

pairing_count = 0
print(CELL_NUM_VERTICES)

for i in range(ITERATIONS):

    if i % 10 == 0:
        model.export_data_model()

    if i % 100 == 0:
        np.savetxt('rxn_data1.csv', rxn_info_array, delimiter=",")
        np.savetxt('spreading_pos_data1.csv', pos_array, delimiter=",")

    # print('iteration number:')
    # print(i)
    context.current_it = i
    model.run_iterations(1)

    #initial set up of getting molecule ids and simple organization
    if i == 1:
        all_ids = model.get_molecule_ids()
        for mol_id in all_ids:
            mol = model.get_molecule(mol_id)
            if model.get_species_name(mol.species_id) == 't1(r)':
                top_mols.append(mol)
            else:
                bottom_mols.append(mol)
                bottom_mols_xyz.append(mol.pos3d)
                # Create a KDTree
                tree = KDTree(bottom_mols_xyz)

        #print('top molecules')
        #print(top_mols)
        # print()
        # print('bottom molecules pos3d')
        # print(bottom_mols_xyz)

    if i % 10 == 0:

        if i != 0:
            all_ids = model.get_molecule_ids()
            top_mols = []
            for mol_id in all_ids:
                mol = model.get_molecule(mol_id)
                if model.get_species_name(mol.species_id) == 't1(r)':
                    top_mols.append(mol)

            for top_mol in top_mols:

                # Query for the k-nearest neighbors to a specific point
                query_point = top_mol.pos3d
                k_neighbors = 2  # Find the 2 closest points

                # this code would be optimized significantly if run inside the mcell4
                # engine using a gpu since this is the classic case where you want that
                distances, indices = tree.query(query_point, k=k_neighbors)

                # if distances[0] < z_height:
                #     print('closest distance between particles')
                #     print(distances[0])
                #     print()

                bot_mol_id = bottom_mols[indices[0]].id
                not_paired_condition = (top_mol.id not in paired_top_mol_ids) and (bot_mol_id not in paired_bot_mol_ids)

                if distances[0] < PAIRING_DISTANCE and not_paired_condition:
                    #print('occurs before crossing partition')
                    model.pair_molecules(top_mol.id, bot_mol_id)
                    paired_top_mol_ids.append(top_mol.id)
                    paired_bot_mol_ids.append(bot_mol_id)
                    pairing_count += 1
                    print('pairing occurred')
                    rxn_info_array.append(i)
                    print(i)
                    wall_to_freeze = top_mol.wall_index
                    node_freeze_array.extend(st.wall_list[wall_to_freeze])
                    node_freeze_array = list(set(node_freeze_array))

        for k in range(CELL_NUM_VERTICES):

            if k in node_freeze_array:
                model.add_vertex_move(instantiation.Cell, k, (np.asarray([0.0, 0.0, 0.0])))
            else:
                cur_vert = model.get_vertex(instantiation.Cell, k)
                if cur_vert[2] <= z_height:
                    pos_array.append((i, cur_vert[0], cur_vert[1], cur_vert[2]))

                En = 0
                Ec = 0
                st = stereometry_tools(model, instantiation.Cell)
                st.set_lists()
                mp.set_stereometry(st)

                En, Ec, moves = mp.get_ens(k, nbrs.get(k))
                #En, Ec, moves = mp.get_ens(k, nbrs.get(k), init_vol)
                #Ev = ((vol-init_vol)**2)/init_vol

                num = uniform_array[i] # used to get probabilty if new energy is
                dif_const = .01
                if En < Ec:
                    # if new en is lower than current always make move
                    displacement = moves
                    #displacement += np.asarray([dif_const*Ev, dif_const*Ev, dif_const*Ev])

                elif num <= math.e**(-1*abs(En-Ec)):
                    # when higher then current energy only move with given probabilty
                    displacement = moves
                    #print('in chance')
                    #displacement += np.asarray([dif_const*Ev, dif_const*Ev, dif_const*Ev])
                    #model.add_vertex_move(instantiation.Cell, k, (displacement * np.asarray([0.01, 0.01, 0.01])))

                else:
                    displacement = np.asarray([0.0, 0.0, 0.0])
                    #displacement = np.asarray([dif_const*Ev, dif_const*Ev, dif_const*Ev])
                    #print(displacement)
                    #model.add_vertex_move(instantiation.Cell, k, (displacement * np.asarray([0.01, 0.01, 0.01])))


                # here we provide an initial push to the membrane to hit cover slip
                if i < 100 and cur_vert[2] > 0:
                    displacement += np.asarray([0,0,-30])
                elif i < 300 and cur_vert[2] > 0:
                    displacement += np.asarray([0,0,-5])
                # else:
                #     displacement += np.asarray([0,0,-7])
                # calculating binding dependent friction
                if (-5 <= cur_vert[0] <= -25) and (-15 <= cur_vert[1] <= -50):
                    # recenter expansion of local minima hard coded
                    vec = np.array([cur_vert[0]+13.5,cur_vert[1]+35,0.0])
                else:
                    vec = np.array([cur_vert[0],cur_vert[1],0.0])
                normalized_vec = norm_vec(vec)
                displacement += normalized_vec * friction_const * pairing_count

                # adding polymer pushing force
                if (cur_vert[2] < z_height):
                    displacement += normalized_vec * poly_push_const * math.e**(-1*cur_vert[2]* poly_push_attenuation_const)

                #print('last line above add_vertex_move')
                model.add_vertex_move(instantiation.Cell, k, (displacement * np.asarray([0.01, 0.01, 0.01])))
                # model.add_vertex_move(instantiation.Organelle_1, k, (0.01, 0.01, 0.01))

        if len(node_freeze_array) > 0:
            print('last line above apply_vertex_move')
        model.apply_vertex_moves(randomize_order=False)
        #vol = st.VolumeOfMesh()

model.end_simulation()

np.savetxt('rxn_data1.csv', rxn_info_array, delimiter=",")
np.savetxt('spreading_pos_data1.csv', pos_array, delimiter=",")
