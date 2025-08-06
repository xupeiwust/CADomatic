import FreeCAD as App
import FreeCADGui as Gui
from FreeCAD import Vector
import math


def createFlangeAssembly():
    doc = App.newDocument("Flange")

    # === Parameters ===
    FLANGE_OUTER_DIAMETER = 100.0
    FLANGE_THICKNESS = 7.5
    BORE_INNER_DIAMETER = 50.0
    NECK_HEIGHT = 15.0
    NECK_OUTER_DIAMETER = 60.0 # This parameter is not explicitly given in the prompt, but is standard for a neck. Keeping it from the template.
    NUM_BOLT_HOLES = 6
    BOLT_HOLE_DIAMETER = 12.0
    PCD = 75.0

    total_height = FLANGE_THICKNESS + NECK_HEIGHT

    # === 1. Create flange base ===
    flange = doc.addObject("Part::Cylinder", "Flange")
    flange.Radius = FLANGE_OUTER_DIAMETER / 2
    flange.Height = FLANGE_THICKNESS

    # === 2. Cut central bore from flange ===
    bore = doc.addObject("Part::Cylinder", "CentralBore")
    bore.Radius = BORE_INNER_DIAMETER / 2
    bore.Height = FLANGE_THICKNESS
    bore_cut = doc.addObject("Part::Cut", "FlangeWithBore")
    bore_cut.Base = flange
    bore_cut.Tool = bore

    # === 3. Create neck ===
    neck_outer = doc.addObject("Part::Cylinder", "NeckOuter")
    neck_outer.Radius = NECK_OUTER_DIAMETER / 2
    neck_outer.Height = NECK_HEIGHT
    neck_outer.Placement.Base = Vector(0, 0, FLANGE_THICKNESS)

    neck_inner = doc.addObject("Part::Cylinder", "NeckInner")
    neck_inner.Radius = BORE_INNER_DIAMETER / 2
    neck_inner.Height = NECK_HEIGHT
    neck_inner.Placement.Base = Vector(0, 0, FLANGE_THICKNESS)

    neck_hollow = doc.addObject("Part::Cut", "HollowNeck")
    neck_hollow.Base = neck_outer
    neck_hollow.Tool = neck_inner

    # === 4. Fuse flange (with central hole) and neck ===
    fused = doc.addObject("Part::Fuse", "FlangeAndNeck")
    fused.Base = bore_cut
    fused.Tool = neck_hollow

    # === 5. Cut bolt holes sequentially ===
    current_shape = fused
    bolt_radius = BOLT_HOLE_DIAMETER / 2
    bolt_circle_radius = PCD / 2

    for i in range(NUM_BOLT_HOLES):
        angle_deg = 360 * i / NUM_BOLT_HOLES
        angle_rad = math.radians(angle_deg)
        x = bolt_circle_radius * math.cos(angle_rad)
        y = bolt_circle_radius * math.sin(angle_rad)

        hole = doc.addObject("Part::Cylinder", f"BoltHole_{i+1:02d}")
        hole.Radius = bolt_radius
        hole.Height = total_height
        hole.Placement.Base = Vector(x, y, 0)

        cut = doc.addObject("Part::Cut", f"Cut_Bolt_{i+1:02d}")
        cut.Base = current_shape
        cut.Tool = hole
        current_shape = cut  # update for next iteration

    # === 6. Final result ===


    # Recompute and fit view
    doc.recompute()
    Gui.activeDocument().activeView().viewAxometric()
    Gui.SendMsgToActiveView("ViewFit")

    return doc

createFlangeAssembly()


import Mesh
import os

print(">>> Running export snippet...")

try:
    if App.ActiveDocument:
        print(">>> Active document found")
        doc = App.ActiveDocument
        doc.recompute()
        doc.saveAs(r"C:\\Users\\yasin\\Desktop\\Code\\CADomatic\\app\\generated\\model.FCStd")
        print(">>> Document saved")

        objs = []
        for obj in doc.Objects:
            if hasattr(obj, "Shape"):
                objs.append(obj)

        print(f">>> Found {len(objs)} shape object(s)")

        if objs:
            Mesh.export(objs, r"C:\\Users\\yasin\\Desktop\\Code\\CADomatic\\app\\generated\\model.obj")
            print(">>> Exported OBJ file")

        with open(r"C:\\Users\\yasin\\Desktop\\Code\\CADomatic\\app\\generated\\preview.txt", "w") as f:
            f.write("Preview placeholder")

    else:
        print(">>> No active document!")

except Exception as e:
    App.Console.PrintError("Export failed: " + str(e) + "\n")
