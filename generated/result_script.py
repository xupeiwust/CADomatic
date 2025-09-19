import Part
import math
import FreeCAD
from FreeCAD import Vector, Placement, Rotation

flange_outer_radius = 50.0
flange_inner_radius = 25.0
flange_thickness = 10.0
bolt_hole_radius = 4.0
num_bolt_holes = 6
bolt_circle_diameter = 75.0

doc = FreeCAD.newDocument("Flange")

outer_cylinder = Part.makeCylinder(flange_outer_radius, flange_thickness)
inner_cylinder = Part.makeCylinder(flange_inner_radius, flange_thickness)
flange_body = outer_cylinder.cut(inner_cylinder)

bolt_hole_shapes = []
for i in range(num_bolt_holes):
    angle_deg = i * (360.0 / num_bolt_holes)
    angle_rad = math.radians(angle_deg)

    x_pos = (bolt_circle_diameter / 2) * math.cos(angle_rad)
    y_pos = (bolt_circle_diameter / 2) * math.sin(angle_rad)

    single_bolt_hole = Part.makeCylinder(bolt_hole_radius, flange_thickness)
    translated_bolt_hole = single_bolt_hole.translated(Vector(x_pos, y_pos, 0))
    bolt_hole_shapes.append(translated_bolt_hole)

bolt_holes_compound = Part.makeCompound(bolt_hole_shapes)

final_flange_shape = flange_body.cut(bolt_holes_compound)

obj = doc.addObject("Part::Feature", "Flange")
obj.Shape = final_flange_shape
doc.recompute()


import FreeCADGui
FreeCADGui.activeDocument().activeView().viewAxometric()
FreeCADGui.SendMsgToActiveView("ViewFit")

import FreeCADGui
import time
time.sleep(5)  # allow GUI to load
view = FreeCADGui.ActiveDocument.ActiveView
view.saveImage(r'generated/screenshot.png', 480, 270, 'White')
print("📸 Screenshot saved at generated/screenshot.png")
