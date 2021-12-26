bl_info = {
    'name': 'Image To Clipboard',
    'author': 'MrKleiner',
    'version': (1, 19),
    'blender': (3, 0, 0),
    'location': 'Image menu',
    'description': 'Copy rendered image to clipboard without saving it',
    'warning': '',
    'doc_url': '',
    'category': 'Image',
}

import bpy
from bpy.types import Operator
from bpy.props import FloatVectorProperty
from bpy_extras.object_utils import AddObjectHelper, object_data_add
from mathutils import Vector
import re
from shutil import copyfile
import os
import json
from re import search
import math
from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       FloatVectorProperty,
                       EnumProperty,
                       PointerProperty,
                       )
from bpy.types import (Panel,
                       Operator,
                       AddonPreferences,
                       PropertyGroup,
                       )
import hashlib
import random
import bmesh
import mathutils
import os.path, time
from pathlib import Path
import sys
import shutil
import subprocess
import datetime
import pathlib
from math import radians
from mathutils import Matrix
from os import path

# todo: use Image Magick to support the fuckton of image formats
# todo: Smarter batch export
# todo: finally figure out how to parse vtf headers
# todo: add "open in vtf edit button"
# todo: batch export from blender data blocks
# todo: "append name from image datablock" button/checkbox
# todo: automatically unpack on export
# todo: animated things support
# todo: embed selected image into alpha channel
# todo: some user if statements: if .tga then use DXT...
# todo: add an ability for manipulating existing vtf files
# todo: a button to create material paths based on selected objects according to given path or Source Ops one.


addon_root_dir = Path(__file__).absolute().parent

# vp_radpath = pathlib.Path(bpy.context.scene.blents.dn_str)
vtfcmd_path = pathlib.Path('E:\\!webdesign\\vtf_flags\\vtflib132-bin (1)\\bin\\x64\\VTFCmd.exe')


check_dp = [
    'PIL',
    'pythonwin',
    'pywin32_system32',
    'win32',
    'win32com',
    'win32comext'
]

nld = []

for dp in check_dp:
    if path.isdir(Path(sys.executable).absolute().parent.parent / 'lib' / 'site-packages' / dp):
        pass
    else:
        nld.append(dp)

for load_d in nld:
    shutil.copytree(addon_root_dir / 'spkg' / load_d, Path(sys.executable).absolute().parent.parent / 'lib' / 'site-packages' / load_d)





# =======================================================
#                   Actual exporter
# =======================================================

def do_export(self, context):

    import bpy
    import numpy as np
    from PIL import Image, ImageOps
    from io import BytesIO
    import win32clipboard



    # store state
    weuse_nodes = bpy.context.scene.use_nodes

    # Set to true
    bpy.context.scene.use_nodes = True




    # create roughness texture
    """
    rough_texnode = nodes.new("ShaderNodeTexImage")
    rough_texnode.image = bpy.data.images.load(str(rough).replace('\\', '\\\\'))
    rough_texnode.location = (-710, 72)
    rough_texnode.image.colorspace_settings.name = 'Non-Color'
    links.new(reuse_principled.inputs["Roughness"], rough_texnode.outputs["Color"])
    """


    # get first composite node that has links

    get_cmp_parent = 'nil'

    get_vw_parent = 'nil'


    # prioritise composite
    if len(bpy.context.scene.node_tree.nodes) > 0:
        for nd in bpy.context.scene.node_tree.nodes:
            if nd.type == 'COMPOSITE':
                if len(nd.inputs['Image'].links) > 0:
                    get_cmp_parent = nd.inputs['Image'].links[0].from_socket
                    break

        for vnd in bpy.context.scene.node_tree.nodes:
            if vnd.type == 'VIEWER':
                if len(vnd.inputs['Image'].links) > 0:
                    get_vw_parent = vnd.inputs['Image'].links[0].from_socket
                    break


    if get_cmp_parent == 'nil':
        links = bpy.context.scene.node_tree.links
        rlayer_n = bpy.context.scene.node_tree.nodes.new('CompositorNodeRLayers')
        viewer_n = bpy.context.scene.node_tree.nodes.new('CompositorNodeViewer')
        
        links.new(viewer_n.inputs['Image'], rlayer_n.outputs['Image'])

    if get_cmp_parent != None and get_cmp_parent != 'nil':
        links = bpy.context.scene.node_tree.links
        viewer_n = bpy.context.scene.node_tree.nodes.new('CompositorNodeViewer')
        
        links.new(viewer_n.inputs['Image'], get_cmp_parent)


    # find composite result image

    cmp_res_img = 'nil'

    for cri in bpy.data.images:
        if cri.type == 'COMPOSITING':
            cmp_res_img = cri

    if cmp_res_img == 'nil' or cmp_res_img == None:
        print('wtf')
    else:
        
        def send_to_clipboard(clip_type, data):
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardData(clip_type, data)
            win32clipboard.CloseClipboard()

        def clipboard_copy_image(pimg):
            import io

            import ctypes
            msvcrt = ctypes.cdll.msvcrt
            kernel32 = ctypes.windll.kernel32
            user32 = ctypes.windll.user32

            output = io.BytesIO()
            pimg.convert('RGB').save(output, 'BMP')
            data = output.getvalue()[14:]
            output.close()

            send_to_clipboard(win32clipboard.CF_DIB, data)
        
        W, H = cmp_res_img.size
        
        rw = np.array(cmp_res_img.pixels[:])

        rw[0::4] = np.power(rw[0::4]/rw[3::4], 1/2.2)
        rw[1::4] = np.power(rw[1::4]/rw[3::4], 1/2.2)
        rw[2::4] = np.power(rw[2::4]/rw[3::4], 1/2.2)

        a = (rw*255).astype(np.int)
        a[a < 0] = 0
        a[a > 255] = 255
        a = a.astype(np.uint8)

        import array
        pimg = Image.frombytes("RGBA", (W, H), array.array("B", a).tobytes())
        pimg = ImageOps.flip(pimg)
        clipboard_copy_image(pimg)
        bpy.context.scene.node_tree.nodes.remove(viewer_n)







# =======================================================
#                   The config class
# =======================================================

# make this image datablock level. Or not ??

# class blender_foil_vtf(PropertyGroup):




# =======================================================
#                Class linker for function
# =======================================================

class IMAGE_MT_vmf_export_foil(Operator, AddObjectHelper):
    bl_idname = 'ci.img_to_clp'
    bl_label = 'Image To clipboard'
    bl_options = {'REGISTER'}

    def execute(self, context):
        do_export(self, context)
        return {'FINISHED'}






# =======================================================
#                       Viewpanel
# =======================================================

#
# General
#

def menu_func(self, context):
    # self.layout.label(OBJECT_OT_vmf_export_foil.bl_idname)
    self.layout.operator('ci.img_to_clp')

"""
class IMAGE_MT_image_imcopy_to_clp(bpy.types.Panel):
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = 'UI'
    bl_category = 'shitfuck'
    bl_label = 'Sexy Iguana'
    # https://youtu.be/sT3joXENOb0
    
    def draw(self, context):
        layout = self.layout
        
        dumpster = layout.column(align=False)
        dumpster.use_property_split = True
        dumpster.use_property_decorate = False
        
        dumpster.operator('mesh.exportvtf',
            text='Export VTF'
        )

        # sima
        # dumpster.label(text=context.space_data.image.name)
"""

# =======================================================
#                       Register
# =======================================================

"""
rclasses = (
    IMAGE_EDITOR_PT_blender_foil_dn_enum,
    IMAGE_EDITOR_PT_blender_foil_vtf_resize,
    IMAGE_EDITOR_PT_blender_foil_vtf_mipmaps,
    IMAGE_EDITOR_PT_blender_foil_vtf_version,
    IMAGE_EDITOR_PT_blender_foil_vtf_misc,
    IMAGE_EDITOR_PT_blender_foil_vtf_flags,
    IMAGE_EDITOR_PT_blender_foil_vtf_batch_e,
    OBJECT_OT_vmf_export_foil,
    blender_foil_vtf,

)
"""


rclasses = (
    IMAGE_MT_vmf_export_foil,
)


register_, unregister_ = bpy.utils.register_classes_factory(rclasses)




def register():
    register_()
    # bpy.types.Scene.blfoilvtf = PointerProperty(type=blender_foil_vtf)
    bpy.types.IMAGE_MT_image.append(menu_func)
    


def unregister():
    unregister_()
    # bpy.utils.unregister_class(blfoilvtf)
    bpy.types.IMAGE_MT_image.remove(menu_func)



















