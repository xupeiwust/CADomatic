import gradio as gr
from pathlib import Path
import sys

# Paths
PROJECT_ROOT = Path(__file__).resolve().parent
GENERATED_SCRIPT_PATH = PROJECT_ROOT / "generated" / "result_script.py"

# Add root to sys.path so we can import process.py from app/
sys.path.insert(0, str(PROJECT_ROOT / "app"))

from app.process import main as generate_from_llm  # This runs generation

def generate_script_and_preview(description):
    """
    Generates the FreeCAD script using process.py logic and returns:
    - The script text for preview
    - The file path for download
    """
    import builtins
    original_input = builtins.input
    builtins.input = lambda _: description
    try:
        generate_from_llm()
    finally:
        builtins.input = original_input

    if GENERATED_SCRIPT_PATH.exists():
        script_text = GENERATED_SCRIPT_PATH.read_text(encoding="utf-8")
        return script_text, str(GENERATED_SCRIPT_PATH)
    else:
        return "Error: Script was not generated.", None


css = """
    body { background-color: #202020; color: white; margin: 0; padding: 0; }
    .gradio-container {
        max-width: 1400px;
        width: 95vw;
        margin: auto;
    }
    .title { text-align: center; font-size: 2.5em; margin-bottom: 0.1em; }
    .description { text-align: center; font-size: 1.1em; margin-bottom: 1em; color: #ccc; }
    .preview-box { 
        max-height: 400px;
        background-color: #111;
        border: 1px solid #444;
        padding: 10px;
        font-family: monospace;
        white-space: pre-wrap;
        color: #0f0;
    }
    .download-container {
        display: flex;
        flex-direction: column;
        align-items: flex-start;
        gap: 0.5em;
        padding-left: 15px;
        height: 400px;
        justify-content: flex-start;
        width: 500px;
    }
    .download-button { width: 100%; }
    .instructions {
        font-size: 0.9em; color: #aaa;
        max-width: 300px;
        white-space: pre-line;
    }
    .footer { 
        margin-top: 2em; 
        text-align: center; 
        font-size: 0.9em; 
        color: #888;
        border-top: 1px solid #444;
        padding-top: 1em;
    }
    .footer a { color: #6af; text-decoration: none; }
    .footer a:hover { text-decoration: underline; }
"""

# Description 
# ToDo write as features
cadomatic_description_md = """ 
<div style="text-align: center;">
Seamlessly creating python scripts for FreeCAD — from prompt to model.
CADomatic is a Python-powered tool that transforms prompts into **editable** parametric CAD scripts for FreeCAD. Rather than static models, it generates fully customizable Python code that programmatically builds CAD geometry — enabling engineers to define parts, reuse templates, and iterate rapidly.<br>
CADomatic primarily aims at **reducing product development time** by making a base design which can be modified to suit the designer's main goal.<br>
CADomatic creates native FreeCAD Python scripts for simple parts **with a complete design tree**.<br>
 <br>
Explore [CADomatic on GitHub](https://github.com/yas1nsyed/CADomatic) and if you find it useful, please ⭐ star the repository!
"""

with gr.Blocks(css=css) as demo:
    gr.Markdown("<div class='title'>CADomatic - AI powered CAD design generator</div>") # Title
    gr.Markdown(cadomatic_description_md)

    description_input = gr.Textbox(
        label="Describe your desired CAD model below-",
        lines=2,
        placeholder="e.g., Create a flange with OD 100mm, bore size 50mm and 6 m8 holes at PCD 75mm..."
    )

    generate_btn = gr.Button("Generate Script", variant="primary")

    with gr.Row():
        with gr.Column(scale=1):
            preview_output = gr.Code(
                label="Generated Script Preview",
                language="python",
                elem_classes="preview-box"
            )
            download_btn = gr.DownloadButton(
                label="Download Python Script",
                elem_classes="download-button"
            )
        with gr.Column(scale=1):
            gr.Markdown( #ToDo 
                """
                <div class='instructions'>
                <b>Instructions:</b><br>
                - Enter the description for your desired CAD part.<br>
                - Click on "Generate Script".<br>
                - Preview the generated Python code.<br>
                - Paste the generated code into the python console of your FreeCAD app.<br>
                - (or)<br> 
                - Download the script.<br>
                - In your FreeCAD python console, paste - exec(open(r"path to your python script").read())
                </div>
                """
            )

    # Footer
    gr.Markdown( 
        """
        <div class='footer'>
        CADomatic is still under development and may sometimes produce inaccurate results.<br>
         <br>
        Made with ❤️ by Yasin
        </div>
        """
    )

    generate_btn.click(
        fn=generate_script_and_preview,
        inputs=description_input,
        outputs=[preview_output, download_btn]
    )

if __name__ == "__main__":
    demo.launch()