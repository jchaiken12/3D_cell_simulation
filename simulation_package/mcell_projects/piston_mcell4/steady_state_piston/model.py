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

from parameters import *

import subsystem
import instantiation
import observables

# create main model object
model = m.Model()

# ---- configuration ----

model.config.time_step = TIME_STEP
model.config.seed = SEED
model.config.total_iterations = ITERATIONS

model.notifications.rxn_and_species_report = True

model.config.partition_dimension = 1.25
model.config.subpartition_dimension = 0.02

# ---- add components ----

model.add_subsystem(subsystem.subsystem)
model.add_instantiation(instantiation.instantiation)
model.add_observables(observables.observables)

# ---- initialization and execution ----

import random as rnd
import math
from pprint import pprint
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import csv
import copy
import pandas as pd

model.initialize()

lu = .01 # some configuration constant

if DUMP:
    model.dump_internal_state()

if EXPORT_DATA_MODEL and model.viz_outputs:
    model.export_data_model()

plane_reg_face_list = [ 0, 1 ]

hit_info_list = []

class HitCount():
    def __init__(self):
        self.count = 0
        self.current_it = 0

def wall_hit_callback(wall_hit_info, context):
    #print("Wall hit callback called")
    #print(wall_hit_info)
    context.count += 1

    hit_info_list.append(wall_hit_info)

    global hit_occured
    hit_occured = True

    return 0

# this finds the angle of collision in our simulation by
# finding the hypotenus and height of before and at the collision
# to produce our angle
def get_angle(hit):

    squared_x_diff = (hit.pos3d[0] - hit.pos3d_before_hit[0])**2
    squared_y_diff = (hit.pos3d[1] - hit.pos3d_before_hit[1])**2
    squared_z_diff = (hit.pos3d[2] - hit.pos3d_before_hit[2])**2

    dist = math.pow(squared_x_diff + squared_y_diff + squared_z_diff, .5)
    height = math.fabs(hit.pos3d[2] - hit.pos3d_before_hit[2])
    angle = math.asin(height/dist)

    return angle

# this calulates the density of the particles in each half box
def calc_dens(mol_a, mol_b):

    vol = (0.25*(0.5**2))
    dens_a = mol_a/vol
    dens_b = mol_b/vol

    return dens_a, dens_b

# this calculates the total momentum from all the particel collisions
# in our PREDICTED case using a uniform distribution probabilty
# to produce an angle between 0 and 90 degrees
def get_pred_mom(speed, mass, hits):

    total_mom = 0
    for j in range(hits+1):
        angle_hit = np.random.uniform(0, math.pi)
        total_mom += speed*math.sin(angle_hit)*mass

    return total_mom

# this will simulate a run using just randomly generated values to
# compare to the actual mean squared displacement produced
def get_pred_msd(plane_cur_pos, box_t, box_b, lu, dt):

    #define all needed user inputs needed
    mol_a = MOL_A_NUM # number of a molcules
    mol_b =  MOL_B_NUM # number of b molecules
    mem_mass = MEM_MASS
    mola_mass = MOL_A_MASS
    molb_mass = MOL_B_MASS
    speed_a = MOL_A_SPEED
    speed_b = MOL_B_SPEED
    iter = ITERATIONS
    gravity_on = False

    dens_a, dens_b = calc_dens(mol_a, mol_b)

    plane_pos_list = [plane_cur_pos/lu]

    mem_v_l = 0
    mem_v_c = 0
    mem_dist_l = 0
    zeroed = False
    mem_force = -9.8*mem_mass

    for i in range(iter):

        pos_hits_a = dens_a*(0.5**2)*speed_a*dt/(lu**5)
        pos_hits_b = dens_b*(0.5**2)*speed_b*dt/(lu**5)
        hits_a = round(min(pos_hits_a, max(0, np.random.normal(pos_hits_a/2, pos_hits_a/4))))
        hits_b = round(min(pos_hits_b, max(0, np.random.normal(pos_hits_b/2, pos_hits_b/4))))

        total_a_mom = get_pred_mom(-speed_a, mola_mass, hits_a)
        total_b_mom = get_pred_mom(speed_b, molb_mass, hits_b)

        total_mom = total_a_mom + total_b_mom

        # mem_v = total_mom/mem_mass
        # mem_dist = mem_v * dt

        mem_v_c = total_mom/mem_mass
        new_mem_force = mem_mass*(mem_v_c-mem_v_l)/dt
        mem_v_l = mem_v_c
        mem_force += new_mem_force
        mem_ac = mem_force/mem_mass
        if not gravity_on:
            if zeroed:
                mem_dist_c = mem_v_c * dt + mem_dist_l
                zeroed = False
            else:
                mem_dist_c = mem_v_c * dt
        else:
            mem_dist_c = mem_v_c * dt + mem_ac*(dt**2)*i

        # where movement occurs
        #for ver in range(len(plane_vert_list)):
        # check that plane will not go past top of box to later move
        plane_move = mem_dist_c/lu
        if plane_move < box_t - .001 and plane_move > box_b + .001:
            plane_pos_list.append(plane_move)
            mem_dist_l = mem_dist_c

        elif plane_move >= box_t - .001 or plane_move <= box_b + .001:
            total_mom = 0
            zeroed = True
            plane_pos_list.append(plane_pos_list[-1])

    msd = find_msd(plane_pos_list)

    return msd

# this calculates the mean squared displacement for the
# plane's movements in the z axis
def find_msd(y_data):

    npy = np.asarray(y_data, dtype=np.float32)
    diff = np.diff(npy) #this calculates differences
    diff_sq = diff**2
    msd = np.mean(diff_sq)

    return msd

mol_a = MOL_A_NUM # number of a molcules
mol_b =  MOL_B_NUM # number of b molecules
mem_mass = MEM_MASS
mola_mass = MOL_A_MASS
molb_mass = MOL_B_MASS
speed_a = MOL_A_SPEED
speed_b = MOL_B_SPEED
iter = ITERATIONS
dt = TIME_STEP
gravity_on = False

context = HitCount()

# the object and species are optional, this simple test contains single
# object and species anyway
model.register_mol_wall_hit_callback(
    wall_hit_callback, context
)

current_hits = []
marker = 0 # used to keep track of only current hits that occurred in iteration
total_mom = 0
plane_cur_pos = max(instantiation.Plane.vertex_list,key=lambda item:item[2])[2]
plane_pos_list = []
mem_force = -9.8*mem_mass

# obtain coordinates for max top and min bottom of the box
box_t = 0.25
box_b = -0.25

count_a = 0
count_b = 0
last_hits_l = 0
current_hits_l = 0
mem_force_ls = []

p_msd = get_pred_msd(plane_cur_pos, box_t, box_b, lu, dt)

mem_v_l = 0
mem_v_c = 0
mem_dist_l = 0
zeroed = False # used as flag to perform special operation when momentum zeroed
cur_mol_locs = []
past_mol_locs = []
mol_velocities = []
all_locations = []
total_mom_list = []
mol_data = []
count_data = []

for i in range(ITERATIONS):

    if i % 10 == 0:
        model.export_data_model()

    model.run_iterations(1)

    if i == 0:
        all_ids = model.get_molecule_ids()

    # store each molecule location past/present each iteration to then deduce velocity
    if i >= 1:
        past_mol_locs = copy.deepcopy(cur_mol_locs)
        cur_mol_locs = []

    for id in all_ids:
        mol = model.get_molecule(id)
        cur_mol_locs.append(list(mol.pos3d))

    for id_index in range(len(all_ids)):
        if i >= 1:
            temp_vel = list(map(lambda x, y: x - y, cur_mol_locs[id_index], past_mol_locs[id_index]))
            #print(temp_vel)
            mol_velocities.append(temp_vel)

    for index, id in enumerate(all_ids):
        if i >= 1:
            mol_data.append((i, id, cur_mol_locs[index][0], cur_mol_locs[index][1], cur_mol_locs[index][2], mol_velocities[index][0], mol_velocities[index][1], mol_velocities[index][2]))
        else:
            mol_data.append((i, id, cur_mol_locs[index][0], cur_mol_locs[index][1], cur_mol_locs[index][2], 0, 0, 0))

    if i % 10 == 0:
        #instantiation.Organelle_1.vertex_list
        # this will keep track of hits occuring only in the
        # current iteration
        current_hits = hit_info_list[marker:]
        current_hits_l = len(hit_info_list)
        marker += current_hits_l - last_hits_l
        last_hits_l = len(hit_info_list)

        # collect microscopic view of each velocity of particle for current energy


        # here we sum up momentum from all the particles
        for hit_index, hit in enumerate(current_hits):
            if hit.molecule_id < mol_a and hit.geometry_object is model.find_geometry_object('Plane'):
                count_a += 1
                angle = get_angle(hit)
                total_mom += -1*mola_mass*(speed_a*math.sin(angle))
            elif hit.molecule_id >= mol_b and hit.geometry_object is model.find_geometry_object('Plane'):
                angle = get_angle(hit)
                count_b += 1
                total_mom += molb_mass*(speed_b*math.sin(angle))

        total_mom_list.append((i, total_mom))
        count_data.append((i, count_a, count_b))
        # print('a mol hits: ' +str(count_a))
        # print('b mol hits: ' +str(count_b))
        #mem_force_ls.append(count_a)
        count_a=0
        count_b=0

        mem_v_c = total_mom/mem_mass
        new_mem_force = mem_mass*(mem_v_c-mem_v_l)/dt
        mem_v_l = mem_v_c
        mem_force += new_mem_force
        mem_ac = mem_force/mem_mass
        mem_force_ls.append(mem_ac*(dt**2))
        if not gravity_on:
            if zeroed:
                mem_dist_c = mem_v_c * dt + mem_dist_l
                zeroed = False
            else:
                mem_dist_c = mem_v_c * dt
        else:
            mem_dist_c = mem_v_c * dt + mem_ac*(dt**2)*i

        # obtain coordinates for max top and min bottom of the membrane
        plane_t = max(instantiation.Plane.vertex_list,key=lambda item:item[2])[2]
        plane_b = min(instantiation.Plane.vertex_list,key=lambda item:item[2])[2]

        # where movement occurs
        # check that plane will not go past top of box to later move
        plane_move = mem_dist_c/lu
        if plane_move < box_t - .001 and plane_move > box_b + .001:
            plane_pos_list.append((i, plane_move))
            displacement = np.asarray([0, 0, plane_move])
            mem_dist_l = mem_dist_c
            model.add_vertex_move(instantiation.Plane, 0, displacement)
            model.add_vertex_move(instantiation.Plane, 1, displacement)
            model.add_vertex_move(instantiation.Plane, 2, displacement)
            model.add_vertex_move(instantiation.Plane, 3, displacement)
            model.apply_vertex_moves()
        # these elif's check when the top and bottom of the box is to
        # 0 out the momentum
        elif plane_move >= box_t - .001 or plane_move <= box_b + .001:
            total_mom = 0
            zeroed = True
            plane_pos_list.append((i, plane_pos_list[-1][1]))
    else:
        plane_pos_list.append((i, plane_pos_list[-1][1]))

model.end_simulation()

print('Now starting data collection.')
print('Please Wait....')
df_molecules = pd.DataFrame(mol_data, columns=['iteration', 'mol_id', 'x', 'y', 'z', 'v_x', 'v_y', 'v_z'])
df_height = pd.DataFrame(plane_pos_list, columns=['iteration', 'height'])
df_p = pd.DataFrame(total_mom_list, columns=['iteration', 'delta_p']) # for total_mom
df_count = pd.DataFrame(count_data, columns=['iteration', 'count_a', 'count_b'])

df_molecules.to_csv('molecule_data.csv', index=False)
df_height.to_csv('membrane_height_data.csv', index=False)
df_p.to_csv('delta_p_data.csv', index=False)
df_count.to_csv('df_count.csv', index=False)
print("CSV's completed generation.")
# plt.xlabel("Time (Iteration number)", fontsize=30)
# plt.ylabel("Height (microns)", fontsize=30)

#print(plane_pos_list)
# plt.plot(list(range(0, ITERATIONS, 10)), plane_pos_list)
# plt.ylabel('Membrane Positions (m)', fontsize=30)
# plt.xlabel('Time (micro seconds)', fontsize=30)
#
# plt.xticks(fontsize=25)
# plt.yticks(fontsize=25)
