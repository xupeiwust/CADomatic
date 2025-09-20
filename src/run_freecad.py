# run_freecad.py
import subprocess
from pathlib import Path

freecad_exe = r"C:\Program Files\FreeCAD 1.0\bin\freecad.exe"
freecadcmd_exe = r"C:\Program Files\FreeCAD 1.0\bin\freecadcmd.exe"
script_path = Path("generated/result_script.py")

if not script_path.exists():
    raise FileNotFoundError("Generated script not found. Run main.py first.")

# Capture stdout and stderr
process = subprocess.run(
    [freecadcmd_exe, str(script_path)],
    capture_output=True,
    text=True
)

# Combine STDOUT and STDERR for full context
full_output = f"""
{process.stderr}
"""

# Save logs for feedback
log_file = Path("generated/last_run_log.txt")
log_file.write_text(full_output)

# Print result
if process.returncode != 0:
    print("❌ FreeCAD execution failed. Check log at generated/last_run_log.txt")
else:
    print("✅ FreeCAD executed successfully.")


def open_freecad():
    freecad_exe = r"C:\Program Files\FreeCAD 1.0\bin\freecad.exe"
    script_path = Path("generated/result_script.py")

    subprocess.Popen([freecad_exe, str(script_path)])
    print("Opened the part in FreeCAD GUI. Enjoy :)")
