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
    return "freecadcmd"  # Assume it's in PATH

# Escape Windows paths manually outside the f-string
fcstd_path_str = str(FCSTD_PATH).replace("\\", "\\\\")
obj_path_str = str(OBJ_PATH).replace("\\", "\\\\")
preview_path_str = str(PREVIEW_PATH).replace("\\", "\\\\")

# Updated export logic with debug logging
EXPORT_SNIPPET = f"""
import Mesh
import os

print(">>> Running export snippet...")

try:
    if App.ActiveDocument:
        print(">>> Active document found")
        doc = App.ActiveDocument
        doc.recompute()
        doc.saveAs(r"{fcstd_path_str}")
        print(">>> Document saved")

        objs = []
        for obj in doc.Objects:
            if hasattr(obj, "Shape"):
                objs.append(obj)

        print(f">>> Found {{len(objs)}} shape object(s)")

        if objs:
            Mesh.export(objs, r"{obj_path_str}")
            print(">>> Exported OBJ file")

        with open(r"{preview_path_str}", "w") as f:
            f.write("Preview placeholder")

    else:
        print(">>> No active document!")

except Exception as e:
    App.Console.PrintError("Export failed: " + str(e) + "\\n")
"""

def generate_script_and_run(user_input: str):
    # Load modular prompt parts
    base_prompt_path = PROJECT_ROOT / "prompts/base_instruction.txt"
    example_prompt_path = PROJECT_ROOT / "prompts/example_code.txt"
    app_prompt_path = APP_DIR / "app_prompt.txt"

    base_instruction = base_prompt_path.read_text(encoding="utf-8").strip()
    example_code = example_prompt_path.read_text(encoding="utf-8").strip()
    app_prompt = app_prompt_path.read_text(encoding="utf-8").strip()

    # Build prompt
    prompt = (
        f"{base_instruction}\n\n"
        f"{example_code}\n\n"
        f"{app_prompt}\n\n"
        f"User request: {user_input.strip()}"
    )

    # Generate LLM code
    generated_code = prompt_llm(prompt)

    # Auto-inject App.newDocument if missing
    if "App.newDocument" not in generated_code:
        generated_code = "App.newDocument('Unnamed')\n" + generated_code

    # Clean up markdown formatting
    # Clean up markdown formatting
    if generated_code.startswith("```"):
        generated_code = generated_code[generated_code.find("\n") + 1:].rsplit("```", 1)[0]

    # Unwrap if __name__ == "__main__" blocks (FreeCAD won't execute them)
    if "__name__" in generated_code and "def " in generated_code:
        lines = generated_code.splitlines()
        in_main = False
        unwrapped = []
        for line in lines:
            if line.strip().startswith("if __name__"):
                in_main = True
                continue
            if in_main:
                # Remove leading indentation (usually 4 spaces)
                unwrapped.append(line[4:] if line.startswith("    ") else line)
            else:
                unwrapped.append(line)
        generated_code = "\n".join(unwrapped)

    # Create output folder if needed
    GEN_DIR.mkdir(exist_ok=True)

    # Build final script with export logic
    full_script = f"{generated_code.strip()}\n\n{EXPORT_SNIPPET}"

    # Write script
    GEN_SCRIPT.write_text(full_script, encoding="utf-8")

    # Delete old outputs
    for path in [FCSTD_PATH, OBJ_PATH, PREVIEW_PATH]:
        if path.exists():
            path.unlink()

    # Run FreeCAD
    freecad_cmd = get_freecad_cmd()
    try:
        result = subprocess.run(
            [freecad_cmd, str(GEN_SCRIPT)],
            cwd=APP_DIR,
            capture_output=True,
            text=True,
            timeout=60
        )

        # Log output
        (GEN_DIR / "run_stdout.txt").write_text(result.stdout or "", encoding="utf-8")
        (GEN_DIR / "run_stderr.txt").write_text(result.stderr or "", encoding="utf-8")

        if result.returncode != 0:
            raise RuntimeError(result.stderr or result.stdout)

        if not FCSTD_PATH.exists() or not OBJ_PATH.exists():
            raise FileNotFoundError("One or more output files not created.")

    except Exception as e:
        FCSTD_PATH.write_text(f"Error: {e}")
        PREVIEW_PATH.write_text(f"Error: {e}")

    return str(FCSTD_PATH), str(PREVIEW_PATH)
