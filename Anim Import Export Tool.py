''' 
Navin Kamal
Anim Import Export Tool.v01
Free Licence
Dont forget to give credit :)
'''

import maya.cmds as cmds
import json
import maya.mel as mel

# UI Window
def show_anim_tool_cmds():

    if cmds.window("animToolWin", exists=True):
        cmds.deleteUI("animToolWin")

    cmds.window("animToolWin", title="NvN Tools", widthHeight=(380, 1000))
    cmds.columnLayout(adjustableColumn=True, rowSpacing=10)
    
    cmds.text(label = "Anim Import Export Tool.v01", h = 30,fn="boldLabelFont", bgc=(0.188, 0.627, 0.627))

    # Row 1: File Path (Read Only)
    cmds.textField("filePathField", editable=False)

    # Row 2: Namespace
    cmds.rowLayout(nc=2, adjustableColumn=2)
    cmds.text(label="Namespace")
    cmds.textField("namespaceTF")
    cmds.setParent("..")

    # Row 3: Bake Button
    cmds.button(label="🔥 Bake Selected Controllers", height=30, c=run_bake)

    # Row 4: Import / Export (2 columns)
    cmds.columnLayout(adjustableColumn=True)
    cmds.button(label="Import Animation", height=35, c=run_import)
    cmds.button(label="Export Animation", height=35, c=run_export)
    cmds.setParent("..")

    # Row 5: Timeline + Frame Range
    cmds.columnLayout(adjustableColumn=True)

    cmds.checkBox("timelineCB", label="Use Timeline Range", value=True, cc=toggle_frame_inputs)

    cmds.rowLayout(nc=4)
    cmds.text(label="Start")
    cmds.intField("startFrameIF", value=int(cmds.playbackOptions(q=True, min=True)))
    cmds.text(label="End")
    cmds.intField("endFrameIF", value=int(cmds.playbackOptions(q=True, max=True)))
    cmds.setParent("..")

    cmds.setParent("..")

    # Row 6: Close Button
    cmds.button(label="Close", height=30, c=close_window)

    cmds.showWindow("animToolWin")

    toggle_frame_inputs()


# Timeline Range
def get_timeline_range():
    gPlayBackSlider = mel.eval('$tmpVar=$gPlayBackSlider')

    if cmds.timeControl(gPlayBackSlider, q=True, rangeVisible=True):
        time_range = cmds.timeControl(gPlayBackSlider, q=True, rangeArray=True)
        return int(time_range[0]), int(time_range[1])

    start = cmds.playbackOptions(q=True, min=True)
    end = cmds.playbackOptions(q=True, max=True)

    return int(start), int(end)

# Export Animation
def export_animation(file_path, start_frame, end_frame):
    selection = cmds.ls(selection=True)

    if not selection:
        cmds.warning("Select at least one object")
        return

    data = {
        "start_frame": start_frame,
        "end_frame": end_frame,
        "objects": {}
    }

    attrs = ["tx","ty","tz","rx","ry","rz","sx","sy","sz"]

    for obj in selection:
        data["objects"][obj] = {}

        for attr in attrs:
            full_attr = obj + "." + attr

            if not cmds.objExists(full_attr):
                continue

            keys = cmds.keyframe(full_attr, q=True)
            if not keys:
                continue

            key_data = []

            for frame in keys:
                value = cmds.getAttr(full_attr, time=frame)
                key_data.append([frame, value])

            if key_data:
                data["objects"][obj][attr] = key_data

    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)

    print("✅ Export Done")

# Import Animation
def import_animation(file_path, namespace=""):
    with open(file_path, "r") as f:
        data = json.load(f)

    for obj, attrs in data["objects"].items():

        target = obj if not namespace else namespace + ":" + obj

        if not cmds.objExists(target):
            cmds.warning("Missing: " + target)
            continue

        for attr, key_data in attrs.items():
            full_attr = target + "." + attr

            if not cmds.objExists(full_attr):
                continue

            cmds.cutKey(full_attr)

            for frame, value in key_data:
                cmds.setKeyframe(full_attr, time=frame, value=value)

    print("✅ Import Done")

# Bake Selected Controllers
def bake_selected_animation(start_frame, end_frame):
    selection = cmds.ls(selection=True)

    if not selection:
        cmds.warning("Select at least one object to bake")
        return

    cmds.bakeResults(
        selection,
        t=(start_frame, end_frame),
        simulation=True,
        sampleBy=1,
        minimizeRotation=True
    )

    print("🔥 Bake Completed")

# UI Functions
def toggle_frame_inputs(*args):
    use_timeline = cmds.checkBox("timelineCB", q=True, v=True)

    cmds.intField("startFrameIF", e=True, enable=not use_timeline)
    cmds.intField("endFrameIF", e=True, enable=not use_timeline)


def run_export(*args):

    result = cmds.fileDialog2(
        fileMode=0,
        caption="Export Animation",
        fileFilter="JSON Files (*.json)"
    )

    if not result:
        return

    path = result[0]

    if not path.lower().endswith(".json"):
        path += ".json"

    cmds.textField("filePathField", e=True, text=path)

    if cmds.checkBox("timelineCB", q=True, v=True):
        start, end = get_timeline_range()
    else:
        start = cmds.intField("startFrameIF", q=True, v=True)
        end = cmds.intField("endFrameIF", q=True, v=True)

    export_animation(path, start, end)


def run_import(*args):

    result = cmds.fileDialog2(
        fileMode=1,
        caption="Import Animation",
        fileFilter="JSON Files (*.json)"
    )

    if not result:
        return

    path = result[0]

    cmds.textField("filePathField", e=True, text=path)

    namespace = cmds.textField("namespaceTF", q=True, text=True)

    import_animation(path, namespace)


def run_bake(*args):
    if cmds.checkBox("timelineCB", q=True, v=True):
        start, end = get_timeline_range()
    else:
        start = cmds.intField("startFrameIF", q=True, v=True)
        end = cmds.intField("endFrameIF", q=True, v=True)

    bake_selected_animation(start, end)


def close_window(*args):
    if cmds.window("animToolWin", exists=True):
        cmds.deleteUI("animToolWin")

# Run
show_anim_tool_cmds()
