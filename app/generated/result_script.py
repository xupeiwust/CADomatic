import FreeCAD as App
import Part

# Create a new document
doc = App.newDocument()

# Create a cube of side 10mm
cube = Part.makeBox(10, 10, 10)

# Add the cube to the document
doc.addObject("Part::Feature", "MyCube").Shape = cube

# Recompute the document to update the view (important for non-GUI mode or saving)
doc.recompute()


import Mesh
import os

try:
    if App.ActiveDocument:
        doc = App.ActiveDocument
        doc.saveAs(r"C:\\Users\\yasin\\Desktop\\Code\\CADomatic\\app\\generated\\model.FCStd")
        
        objs = []
        for obj in doc.Objects:
            if hasattr(obj, "Shape"):
                objs.append(obj)
        
        if objs:
            Mesh.export(objs, r"C:\\Users\\yasin\\Desktop\\Code\\CADomatic\\app\\generated\\model.obj")
        with open(r"C:\\Users\\yasin\\Desktop\\Code\\CADomatic\\app\\generated\\preview.txt", "w") as f:
            f.write("Preview placeholder")

except Exception as e:
    App.Console.PrintError("Export failed: " + str(e) + "\n")
