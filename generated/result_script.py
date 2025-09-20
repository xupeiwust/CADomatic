import Part
import FreeCAD as App
from FreeCAD import Vector
from FreeCAD import Placement
from FreeCAD import Rotation
import FreeCADGui
import time

doc = App.newDocument("Cube")

cube_length = 10.0
cube_width = 10.0
cube_height = 10.0

cube_shape = Part.makeBox(cube_length, cube_width, cube_height)

obj = doc.addObject("Part::Feature", "Cube")
obj.Shape = cube_shape
obj.Placement = Placement(Vector(0,0,0), Rotation(0,0,0,1))

doc.recompute()
FreeCADGui.activeDocument().getObject("Cube").Visibility = True

FreeCADGui.activeDocument().activeView().viewAxometric()
FreeCADGui.SendMsgToActiveView("ViewFit")

time.sleep(5)
view = FreeCADGui.ActiveDocument.ActiveView
view.saveImage(r'generated/screenshot.png', 720, 480, 'White')
print("📸 Screenshot saved at generated/screenshot.png")


import FreeCADGui
FreeCADGui.activeDocument().activeView().viewAxometric()
FreeCADGui.SendMsgToActiveView("ViewFit")
