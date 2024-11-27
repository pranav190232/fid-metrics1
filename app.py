import os
import shutil
import subprocess
import gradio as gr

# 1. Setting up the environment
def setup_environment():
    # Setting up the directory where the FID metrics code is located
    # Users should set the 'FID_METRICS_PATH' environment variable to the path where the FID metrics code is located
    fid_path = os.getenv('FID_METRICS_PATH', './fid-metrics')
    os.environ['PYTHONPATH'] = f"{fid_path};{os.environ.get('PYTHONPATH', '')}"
    return "Environment setup complete."

# 2. File path validation and upload handling
def handle_upload(file1, file2):
    if not os.path.exists(file1):
        return None, None, f"File1 '{file1}' does not exist."
    if not os.path.exists(file2):
        return None, None, f"File2 '{file2}' does not exist."
    return file1, file2, "Files uploaded successfully."

# 3. Running metric calculation
def run_metric_calculation(path1, path2):
    try:
        # Update the command to use the correct paths for VS Code
        # Users should ensure that the 'FID_METRICS_PATH' environment variable is set correctly
        fid_main_script = os.path.join(os.getenv('FID_METRICS_PATH', './fid-metrics'), 'fid_metrics', 'main.py')
        command = f"python {fid_main_script} paths=[\"{path1}\",\"{path2}\"]"
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            return f"Error running metrics calculation: {result.stderr}"
        return f"Metrics calculation complete: {result.stdout}"
    except Exception as e:
        return f"Error: {e}"

# 4. Cleaning up
def clean_up():
    # Temporary uploads directory (update if necessary)
    # Users should ensure that the 'FID_METRICS_PATH' environment variable is set correctly
    temp_path = os.path.join(os.getenv('FID_METRICS_PATH', './fid-metrics'), 'uploads')
    try:
        if os.path.exists(temp_path):
            shutil.rmtree(temp_path)
        return f"Cleaned up temporary files at {temp_path}."
    except Exception as e:
        return f"Error cleaning up: {e}"

# Gradio Interface Function
def fid_workflow(file1, file2):
    # Step 1: Setup environment
    setup_message = setup_environment()

    # Step 2: Handle file upload
    path1, path2, upload_message = handle_upload(file1, file2)
    if not path1 or not path2:
        return setup_message, upload_message, "", ""

    # Step 3: Run metric calculation
    metric_message = run_metric_calculation(path1, path2)
    if "Error" in metric_message:
        return setup_message, upload_message, metric_message, ""

    # Step 4: Cleanup
    cleanup_message = clean_up()

    return setup_message, upload_message, metric_message, cleanup_message

# Gradio UI setup with drag-and-drop
interface = gr.Interface(
    fn=fid_workflow,
    inputs=[
        gr.File(label="Drag and Drop Video 1", type="filepath"),
        gr.File(label="Drag and Drop Video 2", type="filepath")
    ],
    outputs=[
        gr.Textbox(label="Environment Setup Status"),
        gr.Textbox(label="Upload Status"),
        gr.Textbox(label="Metric Calculation Status"),
        gr.Textbox(label="Cleanup Status")
    ],
    title="FID Metric Calculator with Drag-and-Drop",
    description="Drag and drop two video files to calculate FID/FVD metrics."
)

# Launch the Gradio app
interface.launch()
