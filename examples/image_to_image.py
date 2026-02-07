import json
import random
import os
from comfyui_api import ComfyUiClient

def main():
    client = ComfyUiClient(server_address="127.0.0.1:8188")
    
    # 1. Prepare Image
    image_path = "test_input.png"
    if not os.path.exists(image_path):
        print(f"Please create a dummy {image_path} for testing.")
        return

    # 2. Upload Image
    print(f"Uploading {image_path}...")
    uploaded_name = client.upload_image(image_path)
    if not uploaded_name:
        print("Upload failed.")
        return

    # 3. Load Workflow (Load from file in real usage)
    # This example assumes a workflow that has a LoadImage node (id "10")
    workflow = {
        # ... (other nodes) ...
        "10": {
            "class_type": "LoadImage",
            "inputs": {
                "image": uploaded_name  # Use the uploaded filename
            }
        },
        # ... (processing nodes) ...
    }
    
    # In a real scenario, you would load a full JSON file:
    # with open("img2img_workflow.json", "r") as f:
    #     workflow = json.load(f)
    # workflow["10"]["inputs"]["image"] = uploaded_name

    print("Workflow configured. (Note: This is a partial example, it won't run without a full workflow)")
    
    # Uncomment to run if you have a full workflow
    # results = client.process_workflow(workflow)
    # for result in results:
    #     result.save()

if __name__ == "__main__":
    main()
