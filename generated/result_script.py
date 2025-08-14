import FreeCAD as App
import FreeCADGui as Gui
from FreeCAD import Vector, Placement, Rotation
import Part

BODY_BOTTOM_RADIUS = 50.0
BODY_MAX_RADIUS = 80.0
BODY_HEIGHT = 100.0
LID_OPENING_RADIUS = 35.0

SPOUT_ATTACH_HEIGHT = BODY_HEIGHT * 0.5
SPOUT_OFFSET_Y = BODY_MAX_RADIUS * 0.7
SPOUT_LENGTH_HORIZONTAL = 60.0
SPOUT_LENGTH_VERTICAL = 30.0
SPOUT_RADIUS = 7.0

HANDLE_ATTACH_TOP_HEIGHT = BODY_HEIGHT * 0.7
HANDLE_ATTACH_BOTTOM_HEIGHT = BODY_HEIGHT * 0.3
HANDLE_OFFSET_Y = -BODY_MAX_RADIUS * 0.7
HANDLE_RADIUS = 6.0

def createTeapot():
    doc = App.newDocument("Teapot")

    body_profile_pts = [
        Vector(BODY_BOTTOM_RADIUS, 0, 0),
        Vector(BODY_MAX_RADIUS, 0, BODY_HEIGHT * 0.4),
        Vector(BODY_MAX_RADIUS * 0.8, 0, BODY_HEIGHT * 0.7),
        Vector(LID_OPENING_RADIUS, 0, BODY_HEIGHT)
    ]
    body_spline = Part.BSplineCurve(body_profile_pts)
    body_edge = body_spline.toShape()
    line1 = Part.LineSegment(Vector(LID_OPENING_RADIUS, 0, BODY_HEIGHT), Vector(0, 0, BODY_HEIGHT)).toShape()
    line2 = Part.LineSegment(Vector(0, 0, BODY_HEIGHT), Vector(0, 0, 0)).toShape()
    line3 = Part.LineSegment(Vector(0, 0, 0), Vector(BODY_BOTTOM_RADIUS, 0, 0)).toShape()
    wire = Part.Wire([body_edge, line1, line2, line3])
    face = Part.Face(wire)
    body_solid = face.revolve(Vector(0, 0, 0), Vector(0, 0, 1), 360)

    obj_body = doc.addObject("Part::Feature", "Body")
    obj_body.Shape = body_solid
    obj_body.ViewObject.ShapeColor = (0.9, 0.7, 0.7)

    lid_profile_pts = [
        Vector(36.0, 0, 0),
        Vector(36.0, 0, 3.0),
        Vector(35.0, 0, 3.0 + 20.0 * 0.2),
        Vector(17.5, 0, 3.0 + 20.0 * 0.7),
        Vector(10.0, 0, 3.0 + 20.0),
        Vector(5.0, 0, 3.0 + 20.0 + 15.0 * 0.8),
        Vector(0, 0, 3.0 + 20.0 + 15.0)
    ]
    lid_spline = Part.BSplineCurve(lid_profile_pts)
    lid_edge = lid_spline.toShape()
    line4 = Part.LineSegment(Vector(0, 0, 3.0 + 20.0 + 15.0), Vector(0, 0, 0)).toShape()
    line5 = Part.LineSegment(Vector(0, 0, 0), Vector(36.0, 0, 0)).toShape()
    wire_lid = Part.Wire([lid_edge, line4, line5])
    face_lid = Part.Face(wire_lid)
    lid_solid = face_lid.revolve(Vector(0, 0, 0), Vector(0, 0, 1), 360)

    obj_lid = doc.addObject("Part::Feature", "Lid")
    obj_lid.Shape = lid_solid
    obj_lid.Placement = Placement(Vector(0, 0, BODY_HEIGHT), Rotation())
    obj_lid.ViewObject.ShapeColor = (0.9, 0.7, 0.7)

    spout_path_pts = [
        Vector(0, -121, 66),
        Vector(0, -91, 51),
        Vector(0, -61, 36)
    ]

    spout_curve = Part.BSplineCurve(spout_path_pts)
    spout_wire = Part.Wire(spout_curve.toShape())

    tangent_spout = spout_curve.tangent(spout_curve.FirstParameter)[0]
    tangent_spout.normalize()

    spout_circle = Part.Circle()
    spout_circle.Center = spout_path_pts[0]
    spout_circle.Axis = tangent_spout
    spout_circle.Radius = SPOUT_RADIUS
    spout_profile = Part.Wire(spout_circle.toShape())

    spout_solid = spout_wire.makePipe(spout_profile)
    obj_spout = doc.addObject("Part::Feature", "Spout")
    obj_spout.Shape = spout_solid
    obj_spout.ViewObject.ShapeColor = (0.9, 0.7, 0.7)

    handle_path_pts = [
        Vector(0, 56, 31),
        Vector(0, 78, 43),
        Vector(0, 78, 79),
        Vector(0, 56, 71)
    ]

    handle_curve = Part.BSplineCurve(handle_path_pts)
    handle_wire = Part.Wire(handle_curve.toShape())

    tangent_handle = handle_curve.tangent(handle_curve.FirstParameter)[0]
    tangent_handle.normalize()

    handle_circle = Part.Circle()
    handle_circle.Center = handle_path_pts[0]
    handle_circle.Axis = tangent_handle
    handle_circle.Radius = HANDLE_RADIUS
    handle_profile = Part.Wire(handle_circle.toShape())

    handle_solid = handle_wire.makePipe(handle_profile)
    obj_handle = doc.addObject("Part::Feature", "Handle")
    obj_handle.Shape = handle_solid
    obj_handle.ViewObject.ShapeColor = (0.9, 0.7, 0.7)

    fused = obj_body.Shape.fuse(obj_lid.Shape)
    fused = fused.fuse(obj_spout.Shape)
    fused = fused.fuse(obj_handle.Shape)

    obj_final = doc.addObject("Part::Feature", "Teapot_Complete")
    obj_final.Shape = fused
    obj_final.ViewObject.ShapeColor = (0.9, 0.6, 0.6)

    obj_body.ViewObject.Visibility = False
    obj_lid.ViewObject.Visibility = False
    obj_spout.ViewObject.Visibility = False
    obj_handle.ViewObject.Visibility = False

    doc.recompute()

    Gui.activeDocument().activeView().viewAxometric()
    Gui.SendMsgToActiveView("ViewFit")

    return doc

if __name__ == "__main__":
    createTeapot()


import FreeCADGui
FreeCADGui.activeDocument().activeView().viewAxometric()
FreeCADGui.SendMsgToActiveView("ViewFit")
