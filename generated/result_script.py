import FreeCAD as App
import FreeCADGui as Gui
from FreeCAD import Vector, Placement, Rotation
import Part
import math

def createFlangeAssembly():
    doc = App.newDocument("Flange")
    FLANGE_OUTER_DIAMETER = 100.0
    FLANGE_THICKNESS = 7.5
    BORE_INNER_DIAMETER = 50.0
    NECK_HEIGHT = 15.0
    NECK_OUTER_DIAMETER = 60.0
    NUM_BOLT_HOLES = 6
    BOLT_HOLE_DIAMETER = 12.0
    PCD = 75.0
    total_height = FLANGE_THICKNESS + NECK_HEIGHT
    flange = doc.addObject("Part::Cylinder", "Flange")
    flange.Radius = FLANGE_OUTER_DIAMETER / 2
    flange.Height = FLANGE_THICKNESS
    bore = doc.addObject("Part::Cylinder", "CentralBore")
    bore.Radius = BORE_INNER_DIAMETER / 2
    bore.Height = FLANGE_THICKNESS
    bore_cut = doc.addObject("Part::Cut", "FlangeWithBore")
    bore_cut.Base = flange
    bore_cut.Tool = bore
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
    fused = doc.addObject("Part::Fuse", "FlangeAndNeck")
    fused.Base = bore_cut
    fused.Tool = neck_hollow
    current_shape = fused
    bolt_radius = BOLT_HOLE_DIAMETER / 2
    bolt_circle_radius = PCD / 2
    for i in range(NUM_BOLT_HOLES):
        angle_rad = math.radians(360 * i / NUM_BOLT_HOLES)
        x = bolt_circle_radius * math.cos(angle_rad)
        y = bolt_circle_radius * math.sin(angle_rad)
        hole = doc.addObject("Part::Cylinder", f"BoltHole_{i+1:02d}")
        hole.Radius = bolt_radius
        hole.Height = total_height
        hole.Placement.Base = Vector(x, y, 0)
        cut = doc.addObject("Part::Cut", f"Cut_Bolt_{i+1:02d}")
        cut.Base = current_shape
        cut.Tool = hole
        current_shape = cut
    doc.recompute()
    Gui.activeDocument().activeView().viewAxometric()
    Gui.SendMsgToActiveView("ViewFit")
    return doc

if __name__ == "__main__":
    createFlangeAssembly()



import FreeCADGui
FreeCADGui.activeDocument().activeView().viewAxometric()
FreeCADGui.SendMsgToActiveView("ViewFit")
