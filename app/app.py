import gradio as gr
from pathlib import Path
from process import generate_script_and_run

# Folder where FreeCAD outputs the actual files
generated_dir = Path(__file__).parent / "generated"
fcstd_file = generated_dir / "model.FCStd"
obj_file = generated_dir / "model.obj"

# Optionally remove stale broken files (copies)
for file in ["generated_model.FCStd", "generated_model.obj"]:
    fpath = generated_dir / file
    if fpath.exists():
        fpath.unlink()

def prepare_outputs(description):
    # Run FreeCAD pipeline
    generate_script_and_run(description)

    # Return paths to the real output files directly
    return str(fcstd_file), str(obj_file), str(obj_file)  # model.obj for preview

with gr.Blocks() as demo:
    gr.Markdown("# 🛠️ CADomatic - FreeCAD Script Generator")
    gr.Markdown("Enter a CAD description to generate your 3D model:")

    input_text = gr.Textbox(
        label="Describe your FreeCAD part",
        lines=3,
        placeholder="e.g., Create a 10mm thick cylinder with radius 5mm..."
    )

    generate_btn = gr.Button("Generate", variant="primary")

    model_preview = gr.Model3D(label="3D Preview", height=400)

    with gr.Row():
        fcstd_download_btn = gr.DownloadButton(label="Download .FCStd", variant="secondary")
        obj_download_btn = gr.DownloadButton(label="Download .obj", variant="secondary")

    generate_btn.click(
        fn=prepare_outputs,
        inputs=input_text,
        outputs=[fcstd_download_btn, obj_download_btn, model_preview]
    )

if __name__ == "__main__":
    demo.launch()
