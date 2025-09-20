# main.py
from src.llm_client import prompt_llm
from pathlib import Path
import subprocess
from src.run_freecad import open_freecad

GEN_SCRIPT = Path("generated/result_script.py")
RUN_SCRIPT = Path("src/run_freecad.py")
LOG_FILE = Path("generated/last_run_log.txt")
BASE_INSTRUCTION = Path("prompts/base_instruction.txt")

GUI_SNIPPET = """
import FreeCADGui
FreeCADGui.activeDocument().activeView().viewAxometric()
FreeCADGui.SendMsgToActiveView("ViewFit")
"""

screenshot_code = """
import FreeCADGui
import time
time.sleep(5)  # allow GUI to load
view = FreeCADGui.ActiveDocument.ActiveView
view.saveImage(r'generated/screenshot.png', 720, 480, 'White')
print("📸 Screenshot saved at generated/screenshot.png")
"""

MAX_RETRIES = 3  # Maximum auto-fix attempts

def run_freecad_script():
    """Run FreeCAD script via run_freecad.py and return success flag."""
    process = subprocess.run(
        ["python", str(RUN_SCRIPT)],
        capture_output=True,
        text=True
    )

    # Read the log file after running
    if LOG_FILE.exists():
        log_content = LOG_FILE.read_text().strip()
    else:
        log_content = ""

    harmless_messages = {
        "Exception while processing file: generated/result_script.py [module 'FreeCADGui' has no attribute 'activeDocument']",
        "Exception while processing file: generated/result_script.py [module 'FreeCADGui' has no attribute 'ActiveDocument']"
        }
    
    if log_content:
        if any(msg in log_content for msg in harmless_messages):
            return True
        elif "FreeCADGui" in log_content:
            print("⚠️ Harmless FreeCADGui error detected. Ignoring...")
            return True
        else:
            print("❌ FreeCAD execution failed. See log for details.")
            return False
    else:
        print("No errors in generated code!")
        return True

def main():
    user_input = input("Describe your FreeCAD part: ")

    # Read base instructions
    base_instruction = BASE_INSTRUCTION.read_text().strip()
    full_prompt = f"{base_instruction}\n\nUser instruction: {user_input}"

    # Initial LLM generation
    generated_code = prompt_llm(full_prompt)

    # Clean code fences if any
    if generated_code.startswith("```"):
        generated_code = generated_code.strip("`\n ")
        if generated_code.lower().startswith("python"):
            generated_code = generated_code[len("python"):].lstrip()

    # Append GUI snippet
    generated_code += "\n\n" + GUI_SNIPPET + screenshot_code

    # Save initial script
    GEN_SCRIPT.write_text(generated_code)
    print(f"\n     Initial code written to {GEN_SCRIPT}")

    for attempt in range(1, MAX_RETRIES + 1):
        print(f"\n▶ Attempt {attempt} running FreeCAD...")
        success = run_freecad_script()

        if success:
            open_freecad()
            break

        # Read captured FreeCAD logs
        error_logs = LOG_FILE.read_text() if LOG_FILE.exists() else "No log found."

        # Prepare prompt for LLM to fix the code
        fix_prompt = f"""
I want to make the following part using FreeCAD 1.0.1 python scripting

{user_input}

The following FreeCAD script was created but it failed during execution:

{generated_code}

Here is the error log:
{error_logs}

Please provide a corrected FreeCAD script. Keep the logic same, just correct the given error. Respond with valid FreeCAD 1.0.1 Python code only, no extra comments.
"""
        # Get fixed code from LLM
        fixed_code = prompt_llm(fix_prompt)

        # Clean code fences if present
        if fixed_code.startswith("```"):
            fixed_code = fixed_code.strip("`\n ")
            if fixed_code.lower().startswith("python"):
                fixed_code = fixed_code[len("python"):].lstrip()

        # Save fixed code for next attempt
        generated_code = fixed_code + "\n\n" + GUI_SNIPPET
        GEN_SCRIPT.write_text(generated_code)
        print(f"     Fixed code written to {GEN_SCRIPT}. Retrying...")

    else:
        print(f"❌ Max retries ({MAX_RETRIES}) reached. Check {LOG_FILE} for details.")

if __name__ == "__main__":
    main()
