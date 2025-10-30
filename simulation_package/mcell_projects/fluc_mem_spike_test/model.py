#!/usr/bin/env python3

import sys
import os
import matplotlib.pyplot as plt

MCELL_PATH = os.environ.get('MCELL_PATH', '')
if MCELL_PATH:
    sys.path.append(os.path.join(MCELL_PATH, 'lib'))
else:
    print("Error: variable MCELL_PATH that is used to find the mcell library was not set.")
    sys.exit(1)

import mcell as m

from parameters import *

if len(sys.argv) == 3 and sys.argv[1] == '-seed':
    # overwrite value of seed defined in module parameters
    update_seed(int(sys.argv[2]))

if os.path.exists(os.path.join(MCELL_PATH, 'customization.py')):
    import customization
else:
    customization = None

if customization and 'custom_argparse_and_parameters' in dir(customization):
    # custom argument processing and parameter setup
    customization.custom_argparse_and_parameters()
else:
    if len(sys.argv) == 1:
        # no arguments
        pass
    elif len(sys.argv) == 3 and sys.argv[1] == '-seed':
        # overwrite value of seed defined in module parameters
        parameters.SEED = int(sys.argv[2])
    else:
        print("Error: invalid command line arguments")
        print("  usage: " + sys.argv[0] + "[-seed N]")
        sys.exit(1)


import subsystem
import instantiation
import observables

# create main model object
model = m.Model()

# ---- configuration ----

model.config.time_step = TIME_STEP
model.config.seed = get_seed()
print('Below will be the seed number')
print(model.config.seed)
model.config.total_iterations = ITERATIONS

model.notifications.rxn_and_species_report = True

model.config.partition_dimension = 5
model.config.subpartition_dimension = 1

# ---- default configuration overrides ----

if customization and 'custom_config' in dir(customization):
    # user-defined model configuration
    customization.custom_config(model)

# ---- add components ----

model.add_subsystem(subsystem.subsystem)
model.add_instantiation(instantiation.instantiation)
model.add_observables(observables.observables)

# ---- initialization and execution ----

import numpy as np
import random as rnd
import math
from scipy.spatial.distance import cdist

def signed_vol_w(p1, p2, p3):

    p3_x = p3[0]
    p3_y = p3[1]
    p3_z = p3[2]

    p2_x = p2[0]
    p2_y = p2[1]
    p2_z = p2[2]

    p1_x = p1[0]
    p1_y = p1[1]
    p1_z = p1[2]

    v321 = p3_x*p2_y*p1_z
    v231 = p2_x*p3_y*p1_z
    v312 = p3_x*p1_y*p2_z
    v132 = p1_x*p3_y*p2_z
    v213 = p2_x*p1_y*p3_z
    v123 = p1_x*p2_y*p3_z

    return (1.0/6.0)*(-v321 + v231 + v312 - v132 - v213 + v123)

def VolumeOfMesh(model, sphere, wall_list):
    vol = 0
    for w in wall_list:
        p1 = model.get_vertex(sphere, w[0])
        p2 = model.get_vertex(sphere, w[1])
        p3 = model.get_vertex(sphere, w[2])
        vol += signed_vol_w(p1, p2, p3)

    return abs(vol)

def get_area(src, nbrs, model, sphere, new_move=np.array([0,0,0])):

    new_move = np.asarray(new_move)
    area = 0
    start_node = rnd.randrange(0,len(nbrs)-1)
    rcp_length_unit = 0.01
    # approximation but twice as fast at least
    #type(verts)
    for i in range(int(len(nbrs))-1):
        # v1 = [b-a for a, b in zip(verts[nbrs[4]], verts[src])]
        # v2 = [b-a for a, b in zip(verts[nbrs[5]], verts[src])]
        # area += .5 * np.linalg.norm(np.cross(v1,v2))
        p1 = np.asarray(model.get_vertex(sphere, nbrs[i]))
        p2 = np.asarray(model.get_vertex(sphere, nbrs[i+1]))
        sp = np.asarray(model.get_vertex(sphere, src))
        v1 = p1-sp-new_move
        v2 = p2-sp-new_move
        area += .5 * np.linalg.norm(np.cross(v1,v2))

    # num = rnd.randint(0, len(nbrs)-2)
    # v1 = np.array(verts[nbrs[start_node]]) - np.array(verts[src]+new_move)
    # v2 = np.array(verts[nbrs[start_node+1]]) - np.array(verts[src]+new_move)

    #area = .5 * np.linalg.norm(np.cross(v1,v2))
    #area = area * len(nbrs) #* (rcp_length_unit**2)
    return area

def get_n(verts, faces):

    nbrs = dict()
    for i in range(len(verts)):
        nbrs[i] = set()

    for face in faces:
        nbrs[face[0]].add(face[1])
        nbrs[face[0]].add(face[2])
        nbrs[face[1]].add(face[2])
        nbrs[face[1]].add(face[0])
        nbrs[face[2]].add(face[0])
        nbrs[face[2]].add(face[1])

    for i in range(len(verts)):
        nbrs[i] = np.array(list(nbrs[i]))

    return nbrs

# this will return normalized vector that is
# in the direction of the surface shape
def get_surface_norm(model, sphere, src, nbrs):

    sp = np.asarray(model.get_vertex(sphere, src))
    vec = np.array([0.0,0.0,0.0])
    for ver in nbrs:
        p = np.asarray(model.get_vertex(sphere, ver))
        vec += p-sp

    for i in range(len(vec)):
        vec[i] = vec[i]/len(nbrs)

    my_norm = np.linalg.norm(vec)
    for i in range(len(vec)):
        vec[i] = vec[i]/my_norm

    return vec

def get_ens(ind, model, wall_list, sphere, cur_nbrs, init_area):

    rcp_length_unit = 0.01 # constant used internally in simulator

    En = 0

    #(src, nbrs, model, sphere1, new_move=m.Vec3(0,0,0))
    area_c = get_area(ind, cur_nbrs, model, sphere)

    if abs(area_c - init_area[ind]) > 5:
        n = rnd.uniform(-6,6)
    elif abs(area_c - init_area[ind]) > 3:
        n = rnd.uniform(-4,4)
    else:
        n = rnd.uniform(-1,1)

    vert_surface_par = get_surface_norm(model, sphere, ind, cur_nbrs)
    x_move = 10*n*vert_surface_par[0] # random move that will be checked
    y_move = 10*n*vert_surface_par[1]
    z_move = 10*n*vert_surface_par[2]
    par_moves = np.asarray([x_move,y_move,z_move])

    const = 2
    vert_un = model.get_vertex_unit_normal(sphere, ind)
    x_move = const*n*vert_un[0] # random move that will be checked
    y_move = const*n*vert_un[1]
    z_move = 1.4*const*n*vert_un[2]
    perp_moves = np.asarray([x_move,y_move,z_move])

    moves = perp_moves#+par_moves

    area_n = get_area(ind, cur_nbrs, model, sphere, moves)

    Ka = 10 # this is our area modulus

    # print(sphere)
    # print(sphere.vertex_list[ind])
    # volc = VolumeOfMesh(model, sphere, wall_list)
    # voln = VolumeOfMesh(model, sphere, wall_list)
    # Ev = ((vol-init_vol)**2)/init_vol
    En = (((1/2)*Ka*(area_n-init_area[ind])**2)/init_area[ind])
    Ec = (((1/2)*Ka*(area_c-init_area[ind])**2)/init_area[ind])

    return En, Ec, moves

def dist(mol_pos, vert_pos):
    return cdist([mol_pos], [vert_pos], metric='euclidean')

model.initialize()

if DUMP:
    model.dump_internal_state()

if EXPORT_DATA_MODEL and model.viz_outputs:
    model.export_data_model()

# vol = VolumeOfMesh(model, instantiation.Organelle_1, instantiation.Organelle_1.wall_list)
# init_vol = vol*100
#
nbrs = get_n(instantiation.bottom.vertex_list, instantiation.bottom.wall_list)
init_area = []
for j in range(len(instantiation.bottom.vertex_list)):
    area = get_area(j, nbrs.get(j), model, instantiation.bottom)
    if area > 1:
        #area = 0.1862734
        init_area.append(area)
    else:
        init_area.append(area)
    #print(area)

heights = []

for i in range(ITERATIONS):

    if i % 10 == 0:
        model.export_data_model()

    model.run_iterations(1)
    rod_moved_nodes = [] # (vertex index, 0=close or 1=far)
    all_ids = model.get_molecule_ids()
    fact = np.asarray([0.01, 0.01, 0.01])
    if i % 10 == 0:
        for k in range(len(instantiation.bottom.vertex_list)):

            if k == 36:
                heights.append(instantiation.bottom.vertex_list[k][2])

            En = 0
            Ec = 0
            En, Ec, moves = get_ens(k, model, instantiation.bottom.wall_list, instantiation.bottom, nbrs.get(k), init_area)
            # Ev = ((vol-init_vol)**2)/init_vol
            # En += Ev
            # Ec += Ev
            # print(Ec)
            # print(En)
            # print(Ev)
            # print()
            num = rnd.uniform(0,1) # used to get probabilty if new energy is
            dif_const = .01
            if En < Ec:
                # if new en is lower than current always make move
                displacement = moves
                #print(displacement)
                # displacement += dif_const*Ev * np.asarray(model.get_vertex_unit_normal(instantiation.Organelle_1, k))
                model.add_vertex_move(instantiation.bottom, k, (displacement * np.asarray([0.01, 0.01, 0.01])))

            elif num <= math.e**(-1*abs(En-Ec)):
                # when higher then current energy only move with given probabilty
                displacement = moves
                # displacement += dif_const*Ev * np.asarray(model.get_vertex_unit_normal(instantiation.Organelle_1, k))
                model.add_vertex_move(instantiation.bottom, k, (displacement * np.asarray([0.01, 0.01, 0.01])))

            # else:
            #     displacement = dif_const*Ev * np.asarray(model.get_vertex_unit_normal(instantiation.Organelle_1, k))
            #     model.add_vertex_move(instantiation.Organelle_1, k, (displacement * np.asarray([0.01, 0.01, 0.01])))
        # for k in range(len(instantiation.top.vertex_list)):
        #     for mol_ind in all_ids:
        #         mol = model.get_molecule(all_ids[mol_ind])
        #         cur_dist = dist(mol.pos3d, model.get_vertex(instantiation.top, k))[0][0]
        #         # positive number multiplied goes up
        #         if cur_dist < .1:
        #             rod_moved_nodes.append((k, 0))
        #             displ = 3 * np.asarray(model.get_vertex_unit_normal(instantiation.top, k))
        #             model.add_vertex_move(instantiation.top, k, displ * fact)
        #         elif cur_dist < .3:
        #             rod_moved_nodes.append((k, 1))
        #             displ = 1 * np.asarray(model.get_vertex_unit_normal(instantiation.top, k))
        #             model.add_vertex_move(instantiation.top, k, displ * fact)
        #
        # moved_vert = []
        # for node in rod_moved_nodes:
        #     for k in range(len(instantiation.bottom.vertex_list)):
        #         cur_dist = dist(model.get_vertex(instantiation.top, node[0]), model.get_vertex(instantiation.bottom, k))
        #         if node[1] == 0:
        #             if cur_dist < .1 and k not in moved_vert:
        #                 moved_vert.append(k)
        #                 displ = -.3 * np.asarray(model.get_vertex_unit_normal(instantiation.bottom, k))
        #                 model.add_vertex_move(instantiation.bottom, k, displ * fact)
        #             elif cur_dist < .3 and k not in moved_vert:
        #                 moved_vert.append(k)
        #                 displ = -.1 * np.asarray(model.get_vertex_unit_normal(instantiation.bottom, k))
        #                 model.add_vertex_move(instantiation.bottom, k, displ * fact)
        #         else:
        #             if cur_dist < .3 and k not in moved_vert:
        #                 moved_vert.append(k)
        #                 displ = -.3 * np.asarray(model.get_vertex_unit_normal(instantiation.bottom, k))
        #                 model.add_vertex_move(instantiation.bottom, k, displ * fact)

        model.apply_vertex_moves(randomize_order=False)


model.end_simulation()

plt.plot(list(range(0, ITERATIONS, 10)), heights)

plt.xlabel("Time (Iteration number)", fontsize=30)
plt.ylabel("Height (microns)", fontsize=30)

plt.xticks(fontsize=25)
plt.yticks(fontsize=25)

#plt.ylabel(r"$\frac{1}{N}\sum_{i=1}^n x_i$")
#plt.ylabel("test")
plt.show()
