import bpy
import os
from shutil import copyfile
from bpy.app.handlers import persistent

# Meta information.
bl_info = {
    "name": "Version Tracker",
    "description": "This script manages the multiple versions of a file.",
    "author": "Attila Dobos",
    "version": (0, 2, 1),
    "blender": (2, 79, 0),
    "location": "View3D > Toolshelf",
    "warning": "",
    "tracker_url": "",
    "category": "UI"
}

# Persistent load and save handlers

@persistent
def file_open_handler(scene):
    print("Loaded scene")

@persistent    
def file_save_handler(scene):
    head_marker = os.path.dirname(bpy.data.filepath) + "\\" + get_base_filename() + ".head"
    print(head_marker)
    if (os.path.exists(head_marker)):
        head_file_handle = open (head_marker,"r")
        head_file_name = head_file_handle.read()
        head_file_handle.close()
        copyfile(os.path.dirname(bpy.data.filepath) + "\\" + head_file_name,head_marker + ".blend")
        print("File is head, saving to head, too.")

# Helper functions

def save_head():
    directory = os.path.dirname(bpy.data.filepath)
    file_to_save = bpy.data.filepath
    head_to_save = directory + "\\" + get_base_filename() + ".head.blend"
    bpy.ops.wm.save_mainfile(filepath=head_to_save)
    bpy.ops.wm.save_mainfile(filepath=file_to_save)

def get_base_filename():
    currentfilename = bpy.path.basename(bpy.context.blend_data.filepath).lower()
    currentname = os.path.splitext(currentfilename)[0]
    currentbasename = os.path.splitext(currentname)[0]
    return currentbasename

def get_file_version():
    currentfilename = bpy.path.basename(bpy.context.blend_data.filepath).lower()
    currentname = os.path.splitext(currentfilename)[0]
    currentversion = os.path.splitext(currentname)[1][1:]
    return currentversion

def load_version(self, context):
    version_to_load = bpy.data.window_managers["WinMan"].all_versions
    directory = os.path.dirname(bpy.data.filepath)
    file_to_load = directory + "\\" + get_base_filename() + "." + version_to_load + ".blend"
    print("Loading %s" % file_to_load)
    bpy.ops.wm.open_mainfile(filepath=file_to_load)
    

# Dropdown menu for accessing all versions of the file

def enum_all_version_items(self, context):
    """EnumProperty callback"""
    enum_items = []

    if context is None:
        return enum_items

    wm = context.window_manager
    currentfilepath = bpy.data.filepath
    currentversion = get_file_version()
    currentbasename = get_base_filename()
#    print("Current base filename is %s (version is %s)" % (currentbasename, currentversion))
    directory = os.path.dirname(currentfilepath)

    if (currentfilepath == ""):
        print("No saved file present, no versions.")
        return enum_items

#    print("Scanning directory for other versions : %s" % directory)

    if directory and os.path.exists(directory):
        # Scan the directory for png files
        image_paths = []
        for fn in os.listdir(directory):
            if fn.lower().endswith(".blend") and fn.lower().startswith(currentbasename):
                name=os.path.splitext(fn)[0].lower()
                version=os.path.splitext(name)[1][1:].lower()
                if not (version == "") and not (version == "head"):
#                    print("Found version %s" % version)
                    enum_items.append((version,version,""))
    return enum_items

class OBJECT_PT_CreateNewVersionButton(bpy.types.Operator):
    bl_idname = "vtracker.create_new_version"
    bl_label = "Create new version"
    bl_region_type = "UI"
    
    def execute(self, context):
        if (get_file_version() == ""):
            new_file_version = "001"
            os.remove(bpy.data.filepath)
        else:
            new_file_version = (str(int(get_file_version())+1).rjust(3,"0"))
        directory = os.path.dirname(bpy.data.filepath)
        file_to_save = directory + "\\" + get_base_filename() + "." + new_file_version + ".blend"
            
        bpy.ops.wm.save_mainfile(filepath=file_to_save)
        print("New file is %s " % file_to_save)
        return{"FINISHED"}

class OBJECT_PT_MarkItAsHeadButton(bpy.types.Operator):
    bl_idname = "vtracker.mark_it_as_head"
    bl_label = "Mark it as head"
    bl_region_type = "UI"
    
    def execute(self, context):
        head_marker = os.path.dirname(bpy.data.filepath) + "\\" + get_base_filename() + ".head"
        head_file_name = get_base_filename() + "." + get_file_version() + ".blend"
        if (os.path.exists(head_marker)):
            os.remove(head_marker)
        head_file_handle = open(head_marker,"w")
        print(head_marker)
        head_file_handle.write(head_file_name)
        head_file_handle.close()
        print("Head marked as %s." % head_file_name)
        return{"FINISHED"}

# Class for the version tracker panel
class OBJECT_PT_VersionTrackerPanel(bpy.types.Panel):
    bl_label = "Version Tracker"
    bl_idname = "OBJECT_PT_VERSIONTRACKER"
    bl_space_type = "VIEW_3D"
    bl_region_type = 'TOOLS'
    bl_category = "VTracker"

    def draw(self, context):
        layout = self.layout
        wm = context.window_manager

        if (bpy.data.filepath == ""):
            row = layout.row()
            row.label(text="Tracing will be available after saving.")
        else:
            if (get_file_version() == ""):        
                row = layout.row()
                row.label(text="File is not tracked.")
                
                row = layout.row()
                row.operator("vtracker.create_new_version", text="Track this file")
            else:
                if (get_file_version() == "head"):
                    row = layout.row()
                    row.label(text="WARNING! This is the head version file. Please load and edit an other one!")
                    
                row = layout.row()
                row.label(text="Current version")
                
                row = layout.row()
                row.label(text=get_file_version())
                
                row = layout.row()
                row.label(text="Change to version")
            
                row = layout.row()
                row.prop(wm, "all_versions", text="")
            
                row = layout.row()
                row.operator("vtracker.create_new_version")

                row = layout.row()
                row.operator("vtracker.mark_it_as_head")
            return
    
    if not file_open_handler in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.append(file_open_handler)
    if not file_save_handler in bpy.app.handlers.save_post:
        bpy.app.handlers.save_post.append(file_save_handler)

# Register
def register():
    from bpy.types import WindowManager
    from bpy.props import (
            StringProperty,
            EnumProperty,
            )

    WindowManager.all_versions = EnumProperty(
            name="All versions",
            items=enum_all_version_items,
            update=load_version,
            )
    bpy.utils.register_module(__name__)

# Unregister
def unregister():
    from bpy.types import WindowManager
    
    del WindowManager.all_versions
    
    bpy.utils.unregister_module(__name__)
    
if __name__ == '__main__':
	register()
