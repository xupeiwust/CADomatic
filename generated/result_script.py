import FreeCAD as App
import Part
from FreeCAD import Vector

doc = App.newDocument("Cube")

side_length = 10.0

cube_shape = Part.makeBox(side_length, side_length, side_length)

cube_obj = doc.addObject("Part::Feature", "Cube")
cube_obj.Shape = cube_shape

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
