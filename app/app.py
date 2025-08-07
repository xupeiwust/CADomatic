import gradio as gr
from pathlib import Path
from process import generate_script_and_run

# === File Paths ===
generated_dir = Path(__file__).parent / "generated"
fcstd_file = generated_dir / "model.FCStd"
obj_file = generated_dir / "model.obj"

# Remove stale files
for file in ["generated_model.FCStd", "generated_model.obj"]:
    fpath = generated_dir / file
    if fpath.exists():
        fpath.unlink()

# === CAD Generation Callback ===
def prepare_outputs(description):
    generate_script_and_run(description)
    return str(fcstd_file), str(obj_file), str(obj_file)

# === UI with Custom CSS ===
with gr.Blocks(css="""
    #generate-btn .gr-button {
        background-color: #28a745 !important;
        color: white !important;
    }

    #fcstd-download .gr-button,
    #obj-download .gr-button {
        background-color: #fd7e14 !important;
        color: white !important;
    }

    .footer-text {
        text-align: center;
        font-size: 0.85rem;
        margin-top: 2em;
        color: #888;
    }

    .footer-text a {
        color: #fd7e14;
        text-decoration: none;
    }

    .footer-text a:hover {
        text-decoration: underline;
    }
""") as demo:

    gr.Markdown("<h1 style='text-align: center;'> CADomatic - FreeCAD Script Generator</h1>")
    gr.Markdown("Generate 3D models by describing them in plain English. Powered by FreeCAD and LLMs.")

    input_text = gr.Textbox(
        label="📝 Describe your FreeCAD part",
        lines=3,
        placeholder="e.g., Create a 10mm thick cylinder with radius 5mm..."
    )

    generate_btn = gr.Button("Generate", elem_id="generate-btn")

    model_preview = gr.Model3D(label="🔍 3D Preview", height=400)

    with gr.Row():
        fcstd_download = gr.DownloadButton("Download .FCStd file", elem_id="fcstd-download")
        obj_download = gr.DownloadButton("Download .obj file", elem_id="obj-download")

    generate_btn.click(
        fn=prepare_outputs,
        inputs=input_text,
        outputs=[fcstd_download, obj_download, model_preview]
    )

    gr.HTML("""
        <div class='footer-text'>
            <strong>Note:</strong> CADomatic is still under development and still needs to be refined. For best results, run it locally. Toggle to view all in downloaded .FCStd file to see the generated part<br>
            Please refresh and run if there is no preview<br>
            View the source on <a href="https://github.com/yas1nsyed/CADomatic" target="_blank">GitHub</a>.
        </div>
    """)

if __name__ == "__main__":
    demo.launch()
