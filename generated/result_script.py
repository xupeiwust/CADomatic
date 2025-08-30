import Part
import FreeCAD as App
from FreeCAD import Vector

doc = App.newDocument("Cube")

cube_side = 10.0

cube = Part.makeBox(cube_side, cube_side, cube_side)

obj = doc.addObject("Part::Feature", "CubeFeature")
obj.Shape = cube

doc.recompute()


import FreeCADGui
FreeCADGui.activeDocument().activeView().viewAxometric()
FreeCADGui.SendMsgToActiveView("ViewFit")
