import sys
import os
import subprocess
import platform
from pathlib import Path

# Define paths
APP_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = APP_DIR.parent
GEN_DIR = APP_DIR / "generated"
GEN_SCRIPT = GEN_DIR / "result_script.py"
OBJ_PATH = GEN_DIR / "model.obj"
FCSTD_PATH = GEN_DIR / "model.FCStd"
PREVIEW_PATH = GEN_DIR / "preview.txt"  # Dummy preview

sys.path.append(str(PROJECT_ROOT))

from src.llm_client import prompt_llm

def get_freecad_cmd():
    """Get FreeCAD command path for Windows/Linux"""
    if platform.system() == "Windows":
        for path in [
            r"C:\Program Files\FreeCAD 1.0\bin\freecadcmd.exe",
            r"C:\Program Files\FreeCAD\bin\freecadcmd.exe"
        ]:
            if os.path.exists(path):
                return path
    return "freecadcmd"

# Appended export logic
# Escape Windows paths manually outside the f-string
fcstd_path_str = str(FCSTD_PATH).replace("\\", "\\\\")
obj_path_str = str(OBJ_PATH).replace("\\", "\\\\")
preview_path_str = str(PREVIEW_PATH).replace("\\", "\\\\")

EXPORT_SNIPPET = f"""
import Mesh
import os

try:
    if App.ActiveDocument:
        doc = App.ActiveDocument
        doc.saveAs(r"{fcstd_path_str}")
        
        objs = []
        for obj in doc.Objects:
            if hasattr(obj, "Shape"):
                objs.append(obj)
        
        if objs:
            Mesh.export(objs, r"{obj_path_str}")
        with open(r"{preview_path_str}", "w") as f:
            f.write("Preview placeholder")

except Exception as e:
    App.Console.PrintError("Export failed: " + str(e) + "\\n")
"""


def generate_script_and_run(user_input: str):
    # Build prompt for LLM
    prompt = f"Generate FreeCAD 1.0 Python code to create: {user_input}\n" \
             "Requirements:\n" \
             "- Must work in FreeCAD command-line mode\n" \
             "- No GUI functions (FreeCADGui)\n" \
             "- Ensure valid geometry creation"

    generated_code = prompt_llm(prompt)

    #TODO import the llm prompt from main.py

    # Clean up markdown ```python block
    if generated_code.startswith("```"):
        generated_code = generated_code[generated_code.find("\n")+1:].rsplit("```", 1)[0]

    # Prepare output folder
    GEN_DIR.mkdir(exist_ok=True)

    # Append the export logic to the generated code
    full_script = f"{generated_code.strip()}\n\n{EXPORT_SNIPPET}"

    # Write to script file
    GEN_SCRIPT.write_text(full_script, encoding="utf-8")

    # Run with FreeCAD
    freecad_cmd = get_freecad_cmd()
    try:
        result = subprocess.run(
            [freecad_cmd, str(GEN_SCRIPT)],
            cwd=APP_DIR,
            capture_output=True,
            text=True,
            timeout=60
        )
        if result.returncode != 0:
            raise RuntimeError(result.stderr or result.stdout)

        # Confirm file exists
        if not FCSTD_PATH.exists() or not OBJ_PATH.exists():
            raise FileNotFoundError("One or more output files not created.")

    except Exception as e:
        FCSTD_PATH.write_text(f"Error: {e}")
        PREVIEW_PATH.write_text(f"Error: {e}")

    return str(FCSTD_PATH), str(PREVIEW_PATH)
