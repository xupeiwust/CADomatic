import FreeCAD as App
import FreeCADGui as Gui
from FreeCAD import Vector, Placement, Rotation
import Part
import math

def createFlangeAssembly():
    doc = App.newDocument("Flange")

    # === Parameters ===
    FLANGE_OUTER_DIAMETER = 100.0
    FLANGE_THICKNESS = 7.5
    BORE_INNER_DIAMETER = 50.0
    NECK_HEIGHT = 15.0
    NECK_OUTER_DIAMETER = 60.0
    NUM_BOLT_HOLES = 6
    BOLT_HOLE_DIAMETER = 12.0
    PCD = 75.0

    total_height = FLANGE_THICKNESS + NECK_HEIGHT

    # === 1. Create flange base ===
    flange = doc.addObject("Part::Cylinder", "FlangeBody")
    flange.Radius = FLANGE_OUTER_DIAMETER / 2
    flange.Height = FLANGE_THICKNESS

    # === 2. Cut central bore from flange ===
    bore_cutter = doc.addObject("Part::Cylinder", "CentralBoreCutter")
    bore_cutter.Radius = BORE_INNER_DIAMETER / 2
    bore_cutter.Height = FLANGE_THICKNESS
    
    flange_with_bore = doc.addObject("Part::Cut", "FlangeWithBore")
    flange_with_bore.Base = flange
    flange_with_bore.Tool = bore_cutter

    # === 3. Create neck ===
    neck_outer = doc.addObject("Part::Cylinder", "NeckOuterBody")
    neck_outer.Radius = NECK_OUTER_DIAMETER / 2
    neck_outer.Height = NECK_HEIGHT
    neck_outer.Placement = Placement(Vector(0, 0, FLANGE_THICKNESS), Rotation())

    neck_inner = doc.addObject("Part::Cylinder", "NeckInnerCutter")
    neck_inner.Radius = BORE_INNER_DIAMETER / 2
    neck_inner.Height = NECK_HEIGHT
    neck_inner.Placement = Placement(Vector(0, 0, FLANGE_THICKNESS), Rotation())

    neck_hollow = doc.addObject("Part::Cut", "HollowNeck")
    neck_hollow.Base = neck_outer
    neck_hollow.Tool = neck_inner

    # === 4. Fuse flange (with central hole) and neck ===
    fused_body = doc.addObject("Part::Fuse", "FlangeAndNeck")
    fused_body.Base = flange_with_bore
    fused_body.Tool = neck_hollow

    # === 5. Cut bolt holes sequentially ===
    current_shape_obj = fused_body
    bolt_radius = BOLT_HOLE_DIAMETER / 2
    bolt_circle_radius = PCD / 2

    for i in range(NUM_BOLT_HOLES):
        angle_deg = 360 * i / NUM_BOLT_HOLES
        angle_rad = math.radians(angle_deg)
        x = bolt_circle_radius * math.cos(angle_rad)
        y = bolt_circle_radius * math.sin(angle_rad)

        hole_cutter = doc.addObject("Part::Cylinder", f"BoltHoleCutter_{i+1:02d}")
        hole_cutter.Radius = bolt_radius
        hole_cutter.Height = total_height
        hole_cutter.Placement = Placement(Vector(x, y, 0), Rotation())

        cut_operation = doc.addObject("Part::Cut", f"FlangeCut_Bolt_{i+1:02d}")
        cut_operation.Base = current_shape_obj
        cut_operation.Tool = hole_cutter
        current_shape_obj = cut_operation  # update for next iteration

    # Make the final object visible
    current_shape_obj.ViewObject.Visibility = True

    # Recompute and fit view
    doc.recompute()
    Gui.activeDocument().activeView().viewAxometric()
    Gui.SendMsgToActiveView("ViewFit")

    return doc

if __name__ == "__main__":
    createFlangeAssembly()


import FreeCADGui
FreeCADGui.activeDocument().activeView().viewAxometric()
FreeCADGui.SendMsgToActiveView("ViewFit")
