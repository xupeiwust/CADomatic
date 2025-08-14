from pathlib import Path
import subprocess
import sys

# Make sure we can import from root/src
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.llm_client import prompt_llm

# File paths (relative to project root)
prompt_base = ROOT_DIR / "prompts" / "base_instruction.txt"
prompt_examples = ROOT_DIR / "prompts" / "example_code.txt"
GEN_SCRIPT = ROOT_DIR / "generated" / "result_script.py"
RUN_SCRIPT = ROOT_DIR / "src" / "run_freecad.py"

# Snippet to adjust FreeCAD GUI view
GUI_SNIPPET = """
import FreeCADGui
FreeCADGui.activeDocument().activeView().viewAxometric()
FreeCADGui.SendMsgToActiveView("ViewFit")
"""

def main():
    # Step 1: Get user input
    user_input = input("Describe your FreeCAD part: ")

    # Step 2: Build prompt
    base_prompt = prompt_base.read_text(encoding="utf-8").strip()
    example_prompt = prompt_examples.read_text(encoding="utf-8").strip()
    full_prompt = f"{base_prompt}\n\nExamples:\n{example_prompt}\n\nUser instruction: {user_input.strip()}"

    # Step 3: Get response from LLM
    generated_code = prompt_llm(full_prompt)

    # Step 4: Clean up ```python code blocks if any
    if generated_code.startswith("```"):
        generated_code = generated_code.strip("`\n ")
        if generated_code.lower().startswith("python"):
            generated_code = generated_code[len("python"):].lstrip()

    # Step 5: Append GUI snippet for viewing
    generated_code += "\n\n" + GUI_SNIPPET

    # Step 6: Save to script file
    GEN_SCRIPT.write_text(generated_code, encoding="utf-8")
    print(f"\n Code generated and written to {GEN_SCRIPT}")