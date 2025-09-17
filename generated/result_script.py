import Part
import FreeCAD as App

doc = App.newDocument("CubeDoc")

cube_size = 10.0

cube_shape = Part.makeBox(cube_size, cube_size, cube_size)

obj = doc.addObject("Part::Feature", "Cube_10mm")
obj.Shape = cube_shape

doc.recompute()


import FreeCADGui
FreeCADGui.activeDocument().activeView().viewAxometric()
FreeCADGui.SendMsgToActiveView("ViewFit")
