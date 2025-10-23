import numpy as np
import random as rnd

# here we will define the movements of the membrane based on the energies and forces at play
# that act on the cell

# first pressure can act powerfully on the cell if desired followed by the constant elastic energy present

# might have to ensure collisions never happen by ensuring all vertices are above z=0
# any crossing means that the membrane and Cover_slip phase through each other

# should have a pressure related function

stereometry_singelton = None

def get_ens(vert_ind, cur_nbrs):

    En = 0
    sphere = stereometry_singelton.geometry_obj

    tensile_const = 5 # was 2

    #(src, nbrs, model, sphere1, new_move=m.Vec3(0,0,0))
    area_c = stereometry_singelton.get_area(vert_ind, cur_nbrs)

    if abs(area_c - stereometry_singelton.init_area[vert_ind]) > 10:
        n = rnd.uniform(-5,5)
    else:
        n = rnd.uniform(-1,1)

    vert_surface_par = stereometry_singelton.get_surface_norm(vert_ind, cur_nbrs)
    x_move = tensile_const*n*vert_surface_par[0] # random move that will be checked
    y_move = tensile_const*n*vert_surface_par[1]
    z_move = tensile_const*n*vert_surface_par[2]
    par_moves = np.asarray([x_move,y_move,z_move])

    vert_un = stereometry_singelton.main_model.get_vertex_unit_normal(sphere, vert_ind)
    x_move = tensile_const*n*vert_un[0] # random move that will be checked
    y_move = tensile_const*n*vert_un[1]
    z_move = tensile_const*n*vert_un[2]
    perp_moves = np.asarray([x_move,y_move,z_move])

    moves = perp_moves+par_moves

    area_n = stereometry_singelton.get_area(vert_ind, cur_nbrs, moves)

    Ka = 10 # this is our area modulus

    # print(sphere)
    # print(sphere.vertex_list[ind])
    # volc = VolumeOfMesh(model, sphere, wall_list)
    # voln = VolumeOfMesh(model, sphere, wall_list)
    # Ev = ((vol-init_vol)**2)/init_vol
    En = (((1/2)*Ka*(area_n-stereometry_singelton.init_area[vert_ind])**2)/stereometry_singelton.init_area[vert_ind])
    Ec = (((1/2)*Ka*(area_c-stereometry_singelton.init_area[vert_ind])**2)/stereometry_singelton.init_area[vert_ind])

    return En, Ec, moves

def set_stereometry(singelton):
    global stereometry_singelton
    stereometry_singelton = singelton
