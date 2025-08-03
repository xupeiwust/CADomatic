import FreeCAD as App
<<<<<<< HEAD
import FreeCADGui as Gui
from FreeCAD import Vector
import math

def createFlangeAssembly():
    doc = App.newDocument("Flange")

    # === Parameters ===
    FLANGE_OUTER_DIAMETER = 100.0
    FLANGE_THICKNESS = 7.5
    BORE_INNER_DIAMETER = 50.0
    NECK_HEIGHT = 15.0
    NECK_OUTER_DIAMETER = 60.0
    NUM_BOLT_HOLES = 6
    BOLT_HOLE_DIAMETER = 12.0
    PCD = 75.0

    total_height = FLANGE_THICKNESS + NECK_HEIGHT

    # === 1. Create flange base ===
    flange = doc.addObject("Part::Cylinder", "Flange")
    flange.Radius = FLANGE_OUTER_DIAMETER / 2
    flange.Height = FLANGE_THICKNESS

    # === 2. Cut central bore from flange ===
    bore = doc.addObject("Part::Cylinder", "CentralBore")
    bore.Radius = BORE_INNER_DIAMETER / 2
    bore.Height = FLANGE_THICKNESS
    bore_cut = doc.addObject("Part::Cut", "FlangeWithBore")
    bore_cut.Base = flange
    bore_cut.Tool = bore

    # === 3. Create neck ===
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

    # === 4. Fuse flange (with central hole) and neck ===
    fused = doc.addObject("Part::Fuse", "FlangeAndNeck")
    fused.Base = bore_cut
    fused.Tool = neck_hollow

    # === 5. Cut bolt holes sequentially ===
    current_shape = fused
    bolt_radius = BOLT_HOLE_DIAMETER / 2
    bolt_circle_radius = PCD / 2

    for i in range(NUM_BOLT_HOLES):
        angle_deg = 360 * i / NUM_BOLT_HOLES
        angle_rad = math.radians(angle_deg)
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

    # === 6. Final result ===
    
    doc.recompute()
    Gui.activeDocument().activeView().viewAxometric()
    Gui.SendMsgToActiveView("ViewFit")

    return doc

if __name__ == "__main__":
    createFlangeAssembly()

=======
import Part
from FreeCAD import Vector, Placement, Rotation
import math

# Create a new document
DOC_NAME = "Screw"
DOC = App.newDocument(DOC_NAME)
App.setActiveDocument(DOC.Name)

# --- Dimensions ---
# Screw Head Dimensions (Hexagonal)
head_across_flats = 10.0  # Distance across the flats of the hex head
head_height = 5.0

# Screw Shank Dimensions (Nominal Major Diameter)
shank_major_diameter = 6.0  # e.g., for M6 screw
shank_length = 25.0

# Thread Dimensions (for a V-groove cut, approximating a metric thread)
pitch = 1.0  # Distance between threads
thread_depth = 0.54127 * pitch 
thread_half_angle_rad = math.radians(30) # Half angle for a 60 degree V-thread

# --- Create Screw Head (Hexagonal) ---
hex_radius_to_vertex = (head_across_flats / 2.0) / math.cos(math.radians(30))
num_sides = 6
hex_points = []

for i in range(num_sides + 1):
    angle_rad = math.radians(i * 360.0 / num_sides)
    x = hex_radius_to_vertex * math.cos(angle_rad)
    y = hex_radius_to_vertex * math.sin(angle_rad)
    hex_points.append(Vector(x, y, 0))

hex_profile_wire = Part.makePolygon(hex_points)
hex_profile_wire.Placement = Placement(Vector(0,0,0), Rotation(0,0,30))
screw_head = hex_profile_wire.extrude(Vector(0,0,head_height))

# --- Create Screw Shank ---
screw_shank = Part.makeCylinder(shank_major_diameter / 2.0, shank_length)
shank_placement = Placement(Vector(0, 0, head_height), Rotation(0, 0, 0))
screw_shank.Placement = shank_placement

# --- Create Thread ---
shank_major_radius = shank_major_diameter / 2.0
thread_root_radius = shank_major_radius - thread_depth
helix_total_length = shank_length + 2 * pitch
helix_start_z = head_height - pitch

# ✅ Fixed: use positional arguments only
helix_cut_path = Part.makeHelix(pitch, helix_total_length, thread_root_radius)
helix_cut_path.Placement = Placement(Vector(0,0,helix_start_z), Rotation(0,0,0))

groove_half_width_at_base = thread_depth * math.tan(thread_half_angle_rad)
vtx_cut_1 = Vector(0, 0, 0)
vtx_cut_2 = Vector(thread_depth, -groove_half_width_at_base, 0)
vtx_cut_3 = Vector(thread_depth, groove_half_width_at_base, 0)

thread_groove_profile_wire = Part.Wire([
    Part.LineSegment(vtx_cut_1, vtx_cut_2).toShape(),
    Part.LineSegment(vtx_cut_2, vtx_cut_3).toShape(),
    Part.LineSegment(vtx_cut_3, vtx_cut_1).toShape()
])


helical_groove_solid = thread_groove_profile_wire.makePipe(helix_cut_path)

# --- Combine and Cut ---
all_base_parts = [screw_head, screw_shank]
combined_screw_base = all_base_parts[0]
for part_shape in all_base_parts[1:]:
    combined_screw_base = combined_screw_base.fuse(part_shape)

final_screw_shape = combined_screw_base.cut(helical_groove_solid)
final_screw_obj = DOC.addObject("Part::Feature", "CompleteScrew")
final_screw_obj.Shape = final_screw_shape
DOC.recompute()
>>>>>>> eb18b58eb3dc22a6c926d1ac6a67c3797a546658

import FreeCADGui
FreeCADGui.activeDocument().activeView().viewAxometric()
FreeCADGui.SendMsgToActiveView("ViewFit")
