
# Here we a file that contains all 3d euclidean geomtry helpers used
# for things like volume, area, and so on.
# Geometry is done on shapes made of triangles to create a mesh.

from parameters import *
import numpy as np

class stereometry_tools:

    _instance = None

    #src is vertex number being operated on

    def signed_vol_w(self, p1, p2, p3):

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

    def VolumeOfMesh(self):
        vol = 0
        for w in self.geometry_obj.wall_list:
            p1 = self.main_model.get_vertex(self.geometry_obj, w[0])
            p2 = self.main_model.get_vertex(self.geometry_obj, w[1])
            p3 = self.main_model.get_vertex(self.geometry_obj, w[2])
            vol += self.signed_vol_w(p1, p2, p3)

        return abs(vol)

    def get_area(self, vert_ind, ind_nbrs, new_move=np.array([0,0,0])):

        new_move = np.asarray(new_move)
        area = 0
        rcp_length_unit = 0.01
        # approximation but twice as fast at least
        #type(verts)
        for i in range(int(len(ind_nbrs))-1):
            # v1 = [b-a for a, b in zip(verts[nbrs[4]], verts[src])]
            # v2 = [b-a for a, b in zip(verts[nbrs[5]], verts[src])]
            # area += .5 * np.linalg.norm(np.cross(v1,v2))
            p1 = np.asarray(self.main_model.get_vertex(self.geometry_obj, ind_nbrs[i]))
            p2 = np.asarray(self.main_model.get_vertex(self.geometry_obj, ind_nbrs[i+1]))
            sp = np.asarray(self.main_model.get_vertex(self.geometry_obj, vert_ind))
            v1 = p1-sp-new_move
            v2 = p2-sp-new_move
            area += .5 * np.linalg.norm(np.cross(v1,v2))

        return area

    # returns neighbors of certain vertex for each vertex in verts
    # assumed to have faces composed of 3 verticies
    def calc_nbrs(self, verts, faces):

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
    def get_surface_norm(self, vert_ind, nbrs):

        sp = np.asarray(self.main_model.get_vertex(self.geometry_obj, vert_ind))
        vec = np.array([0.0,0.0,0.0])
        for ver in nbrs:
            p = np.asarray(self.main_model.get_vertex(self.geometry_obj, ver))
            vec += p-sp

        for i in range(len(vec)):
            vec[i] = vec[i]/len(nbrs)

        my_norm = np.linalg.norm(vec)
        if my_norm >= 10**(-6):
            for i in range(len(vec)):
                vec[i] = vec[i]/my_norm

        return vec

    def set_model(self, model):
        self.main_model = model

    def set_geometry_obj(self, shape):
        self.geometry_obj = shape

    def set_lists(self):
            self.vertex_list = self.geometry_obj.vertex_list
            self.wall_list = self.geometry_obj.wall_list


    def set_init_area(self, nbrs):
        self.init_area = []
        for j in range(CELL_NUM_VERTICES):
            self.init_area.append(self.get_area(j, nbrs.get(j)))
        return self.init_area

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, model=None, geo_obj=None):
        if not hasattr(self, '_initialized'):
            self.main_model = model
            self.geometry_obj = geo_obj
            self._initialized = True
