import FreeCAD as App
import Part

doc = App.newDocument("Box")

# Create a box
box_shape = Part.makeBox(10.0, 10.0, 10.0)

# Add the shape to the document
box_object = doc.addObject("Part::Feature", "MyBox")
box_object.Shape = box_shape

doc.recompute()


import Mesh
import os

print(">>> Running export snippet...")

try:
    if App.ActiveDocument:
        print(">>> Active document found")
        doc = App.ActiveDocument
        doc.recompute()
        doc.saveAs(r"C:\\Users\\yasin\\Desktop\\Code\\CADomatic\\app\\generated\\model.FCStd")
        print(">>> Document saved")

        objs = []
        for obj in doc.Objects:
            if hasattr(obj, "Shape"):
                objs.append(obj)

        print(f">>> Found {len(objs)} shape object(s)")

        if objs:
            Mesh.export(objs, r"C:\\Users\\yasin\\Desktop\\Code\\CADomatic\\app\\generated\\model.obj")
            print(">>> Exported OBJ file")

        with open(r"C:\\Users\\yasin\\Desktop\\Code\\CADomatic\\app\\generated\\preview.txt", "w") as f:
            f.write("Preview placeholder")

    else:
        print(">>> No active document!")

except Exception as e:
    App.Console.PrintError("Export failed: " + str(e) + "\n")
