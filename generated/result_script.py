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
    NECK_OUTER_DIAMETER = 60.0 # Keeping this from the template as not specified in prompt
    NUM_BOLT_HOLES = 6
    BOLT_HOLE_DIAMETER = 12.0
    PCD = 75.0

    total_height = FLANGE_THICKNESS + NECK_HEIGHT

    # === 1. Create flange base ===
    flange = doc.addObject("Part::Cylinder", "Flange_Base")
    flange.Radius = FLANGE_OUTER_DIAMETER / 2
    flange.Height = FLANGE_THICKNESS

    # === 2. Cut central bore from flange ===
    bore = doc.addObject("Part::Cylinder", "Central_Bore_Cutter")
    bore.Radius = BORE_INNER_DIAMETER / 2
    bore.Height = FLANGE_THICKNESS
    bore_cut = doc.addObject("Part::Cut", "Flange_with_Bore")
    bore_cut.Base = flange
    bore_cut.Tool = bore

    # === 3. Create neck ===
    neck_outer = doc.addObject("Part::Cylinder", "Neck_Outer")
    neck_outer.Radius = NECK_OUTER_DIAMETER / 2
    neck_outer.Height = NECK_HEIGHT
    neck_outer.Placement.Base = Vector(0, 0, FLANGE_THICKNESS)

    neck_inner = doc.addObject("Part::Cylinder", "Neck_Inner_Cutter")
    neck_inner.Radius = BORE_INNER_DIAMETER / 2
    neck_inner.Height = NECK_HEIGHT
    neck_inner.Placement.Base = Vector(0, 0, FLANGE_THICKNESS)

    neck_hollow = doc.addObject("Part::Cut", "Hollow_Neck_Part")
    neck_hollow.Base = neck_outer
    neck_hollow.Tool = neck_inner

    # === 4. Fuse flange (with central hole) and neck ===
    fused = doc.addObject("Part::Fuse", "Flange_and_Neck_Fused")
    fused.Base = bore_cut
    fused.Tool = neck_hollow

    # === 5. Cut bolt holes sequentially ===
    current_shape_obj = fused # Reference to the last cut object in the tree
    bolt_radius = BOLT_HOLE_DIAMETER / 2
    bolt_circle_radius = PCD / 2

    for i in range(NUM_BOLT_HOLES):
        angle_deg = 360 * i / NUM_BOLT_HOLES
        angle_rad = math.radians(angle_deg)
        x = bolt_circle_radius * math.cos(angle_rad)
        y = bolt_circle_radius * math.sin(angle_rad)

        hole_cutter = doc.addObject("Part::Cylinder", f"Bolt_Hole_Cutter_{i+1:02d}")
        hole_cutter.Radius = bolt_radius
        hole_cutter.Height = total_height
        hole_cutter.Placement.Base = Vector(x, y, 0)

        cut_obj = doc.addObject("Part::Cut", f"Flange_with_Hole_{i+1:02d}")
        cut_obj.Base = current_shape_obj
        cut_obj.Tool = hole_cutter
        current_shape_obj = cut_obj  # Update for the next iteration

    # === 6. Final result ===
    # The final object is current_shape_obj after all cuts

    # Recompute and fit view
    doc.recompute()
    Gui.activeDocument().activeView().viewAxometric()
    Gui.SendMsgToActiveView("ViewFit")

    return doc

if __name__ == "__main__":
    createFlangeAssembly()

