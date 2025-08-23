import FreeCAD as App
import Part
from FreeCAD import Vector, Placement, Rotation
import math

doc = App.newDocument("Flange")

main_body_radius_val = 20.0
main_body_height_val = 50.0
flange_outer_radius_val = 40.0
flange_thickness_val = 10.0
pcd_val = 60.0
num_bolt_holes_val = 6
bolt_hole_radius_val = 5.0
inner_pipe_radius_val = 15.0

main_body = doc.addObject("Part::Cylinder", "MainBody")
main_body.Radius = main_body_radius_val
main_body.Height = main_body_height_val
main_body.Placement = Placement(Vector(0, 0, 0), Rotation())

flange_disc = doc.addObject("Part::Cylinder", "FlangeDisc")
flange_disc.Radius = flange_outer_radius_val
flange_disc.Height = flange_thickness_val
flange_disc.Placement = Placement(Vector(0, 0, 0), Rotation())

inner_pipe_hole = doc.addObject("Part::Cylinder", "InnerPipeHole")
inner_pipe_hole.Radius = inner_pipe_radius_val
inner_pipe_hole.Height = main_body_height_val + flange_thickness_val + 2.0
inner_pipe_hole.Placement = Placement(Vector(0, 0, -1.0), Rotation())

bolt_hole_cylinders = []
for i in range(num_bolt_holes_val):
    angle = 2 * math.pi * i / num_bolt_holes_val
    x = pcd_val / 2 * math.cos(angle)
    y = pcd_val / 2 * math.sin(angle)

    bolt_hole = doc.addObject("Part::Cylinder", f"BoltHole_{i+1}")
    bolt_hole.Radius = bolt_hole_radius_val
    bolt_hole.Height = flange_thickness_val + 2.0
    bolt_hole.Placement = Placement(Vector(x, y, -1.0), Rotation())
    bolt_hole_cylinders.append(bolt_hole)

base_flange_fuse = doc.addObject("Part::MultiFuse", "BaseFlange")
base_flange_fuse.Shapes = [main_body, flange_disc]
main_body.Visibility = False
flange_disc.Visibility = False

holes_to_cut_list = [inner_pipe_hole]
holes_to_cut_list.extend(bolt_hole_cylinders)

all_holes_fuse = doc.addObject("Part::MultiFuse", "AllHolesToCut")
all_holes_fuse.Shapes = holes_to_cut_list
inner_pipe_hole.Visibility = False
for hole_obj in bolt_hole_cylinders:
    hole_obj.Visibility = False

final_flange = doc.addObject("Part::Cut", "Flange")
final_flange.Base = base_flange_fuse
final_flange.Tool = all_holes_fuse
base_flange_fuse.Visibility = False
all_holes_fuse.Visibility = False

doc.recompute()


import FreeCADGui
FreeCADGui.activeDocument().activeView().viewAxometric()
FreeCADGui.SendMsgToActiveView("ViewFit")
