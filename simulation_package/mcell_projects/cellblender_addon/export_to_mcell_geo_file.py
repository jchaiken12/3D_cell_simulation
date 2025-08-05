# this works for a textured blender file

# import bpy, bmesh
#
# def print(data):
#     for window in bpy.context.window_manager.windows:
#         screen = window.screen
#         for area in screen.areas:
#             if area.type == 'CONSOLE':
#                 override = {'window': window, 'screen': screen, 'area': area}
#                 bpy.ops.console.scrollback_append(override, text=str(data), type="OUTPUT")
#
# obj = bpy.context.active_object
#
# depsgraph = bpy.context.evaluated_depsgraph_get()
#
# bm = bmesh.new()
#
# bm.from_object( obj, depsgraph )
#
# bm.verts.ensure_lookup_table()
#
# # change path name and string name to change the names of the place saved
# # and the name of the lists
# name_str = 'Organelle_2'
# path = '/home/jonah/Jonah/mcell_project/realistic_cell/bottom_cell_geo.py'
#
# f = open(path,'w')
# f.write('import mcell as m' + '\n')
# f.write('\n')
#
# f.write(name_str + '_vertex_list = [' + '\n')
# for i, v in enumerate(bm.verts):
#     if i == len(bm.verts)-1:
#         f.write('\t' + '[' + str(v.co.x) + ',' + str(v.co.y) + ',' + str(v.co.z) + ']' + '\n')
#     else:
#         f.write('\t' + '[' + str(v.co.x) + ',' + str(v.co.y) + ',' + str(v.co.z) + '],' + '\n')
# #    print( v.co )
# f.write(']' + '\n')
#
# f.write('\n')
#
# f.write(name_str + '_wall_list = [' + '\n')
# for j, fa in enumerate(bm.faces):
#     f.write('\t' + '[')
#     for i, v in enumerate(fa.verts):
#         if i == len(fa.verts)-1 and j == len(bm.faces)-1:
#             f.write(str(v.index) + ']' + '\n')
#         elif i == len(fa.verts)-1:
#             f.write(str(v.index) + '],' + '\n')
#         else:
#             f.write(str(v.index) + ',')
#
# f.write(']' + '\n')
#
# f.write('\n')
#
# f.write(name_str + ' = ' + 'm.GeometryObject(' + '\n')
# f.write('\t' + 'name = ' + '\'' + name_str + '\'' + ',' + '\n')
# f.write('\t' + 'vertex_list = ' + name_str + '_vertex_list' + ',' + '\n')
# f.write('\t' + 'wall_list = ' + name_str + '_wall_list' + ',' + '\n')
# f.write(')' + '\n')
#
# f.close()
#
# bm.free()

import bpy
import bmesh

# ExportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy_extras.io_utils import ExportHelper
from bpy.types import Operator

def save(operator,
         context, filepath="",
         use_selection=True,
         global_matrix=None,
         ):

    if filepath == "":
        return {'FINISHED'}

    if not filepath.endswith(".py"):
        filepath += ".py"

    obj_list = []
    obj_list = bpy.data.objects

    global the_scene
    the_scene = context.scene

    print('Exporting', filepath, 'Objects', len(obj_list))

    if len(obj_list) > 0:
        write_some_data(obj_list, filepath)

    return {'FINISHED'}

def write_some_data(context, filepath):

    # forcing one of the cells to be active
    # my_obj = bpy.context.scene.objects["top_cell"]
    # bpy.context.view_layer.objects.active = my_obj

    obj = bpy.context.active_object

    depsgraph = bpy.context.evaluated_depsgraph_get()

    object_matrix = obj.matrix_world

    bm = bmesh.new()

    bm.from_object(obj, depsgraph)
    bm.verts.ensure_lookup_table()
    bmesh.ops.transform(bm, matrix=object_matrix, verts=bm.verts)

    name_str = 'Organelle_1'
#    path = '/home/jonah/Jonah/mcell_project/realistic_cell/top_cell_geo.py'

    f = open(filepath,'w')
    f.write('import mcell as m' + '\n')
    f.write('\n')

    f.write(name_str + '_vertex_list = [' + '\n')
    for i, v in enumerate(bm.verts):
        if i == len(bm.verts)-1:
            f.write('\t' + '[' + str(v.co.x) + ',' + str(v.co.y) + ',' + str(v.co.z) + ']' + '\n')
        else:
            f.write('\t' + '[' + str(v.co.x) + ',' + str(v.co.y) + ',' + str(v.co.z) + '],' + '\n')
    #    print( v.co )
    f.write(']' + '\n')

    f.write('\n')

    f.write(name_str + '_wall_list = [' + '\n')
    for j, fa in enumerate(bm.faces):
        f.write('\t' + '[')
        for i, v in enumerate(fa.verts):
            if i == len(fa.verts)-1 and j == len(bm.faces)-1:
                f.write(str(v.index) + ']' + '\n')
            elif i == len(fa.verts)-1:
                f.write(str(v.index) + '],' + '\n')
            else:
                f.write(str(v.index) + ',')

    f.write(']' + '\n')

    f.write('\n')

    f.write(name_str + ' = ' + 'm.GeometryObject(' + '\n')
    f.write('\t' + 'name = ' + '\'' + name_str + '\'' + ',' + '\n')
    f.write('\t' + 'vertex_list = ' + name_str + '_vertex_list' + ',' + '\n')
    f.write('\t' + 'wall_list = ' + name_str + '_wall_list' + ',' + '\n')
    f.write(')' + '\n')

    f.close()

    bm.free()

    return {'FINISHED'}

class ExportSomeData(Operator, ExportHelper):
    """This appears in the tooltip of the operator and in the generated docs"""
    bl_idname = "export_test.some_data"
    bl_label = "Export Some Data"

    # ExportHelper mixin class uses this
    filename_ext = ".py"
    filter_glob: bpy.props.StringProperty(default="*.py", options={'HIDDEN'})

    def execute(self, context):
        return write_some_data(context, self.filepath)

from bpy.props import (
        BoolProperty,
        StringProperty,
        )
from bpy_extras.io_utils import (
        ExportHelper,
        axis_conversion,
        )

# start of init.py when make addon
bl_info = {
    "name": "Mcell Geometry File (.py)",
    "author": "Jonah",
    "blender": (2, 80, 0),
    "location": "File > Import-Export",
    "description": "Export cellblender meshes",
    "warning": "",
    "category": "Import-Export"}

class Mcell_Geo(bpy.types.Operator, ExportHelper):
    """Export to mcell geometry file format (.py)"""
    bl_idname = "export_scene.mcell_geo"
    bl_label = 'Export Mcell Geo'
    axis_forward='Y'
    axis_up='Z'

    filename_ext = ".py"

    filter_glob: StringProperty(
            default="*.py",
            options={'HIDDEN'},
            )

    use_selection: BoolProperty(
            name="Selection Only",
            description="Export selected objects only",
            default=False,
            )

    def execute(self, context):

        keywords = self.as_keywords(ignore=("axis_forward",
                                            "axis_up",
                                            "filter_glob",
                                            "check_existing",
                                            ))
        global_matrix = axis_conversion(to_forward=self.axis_forward,
                                        to_up=self.axis_up,
                                        ).to_4x4()
        keywords["global_matrix"] = global_matrix

        return save(self, context, **keywords)


# Add to a menu
def menu_func_export(self, context):
    self.layout.operator(Mcell_Geo.bl_idname, text="Mcell Geometry (.py)")


classes = (
    Mcell_Geo,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)

if __name__ == "__main__":
    register()
