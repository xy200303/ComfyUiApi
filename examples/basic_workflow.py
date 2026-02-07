import json
import random
from comfyui_api import ComfyUiClient

def main():
    # 1. Initialize Client
    # Replace with your server address
    client = ComfyUiClient(server_address="127.0.0.1:8188")
    
    # 2. Define a simple workflow (Text to Image)
    # This is a simplified example. In practice, load this from a JSON file.
    workflow = {
        "3": {
            "class_type": "KSampler",
            "inputs": {
                "seed": random.randint(1, 1000000000),
                "steps": 20,
                "cfg": 8,
                "sampler_name": "euler",
                "scheduler": "normal",
                "denoise": 1,
                "model": ["4", 0],
                "positive": ["6", 0],
                "negative": ["7", 0],
                "latent_image": ["5", 0]
            }
        },
        "4": {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {"ckpt_name": "v1-5-pruned-emaonly.ckpt"}
        },
        "5": {
            "class_type": "EmptyLatentImage",
            "inputs": {"width": 512, "height": 512, "batch_size": 1}
        },
        "6": {
            "class_type": "CLIPTextEncode",
            "inputs": {"text": "a beautiful scenery nature glass bottle landscape, purple galaxy bottle,", "clip": ["4", 1]}
        },
        "7": {
            "class_type": "CLIPTextEncode",
            "inputs": {"text": "text, watermark", "clip": ["4", 1]}
        },
        "8": {
            "class_type": "VAEDecode",
            "inputs": {"samples": ["3", 0], "vae": ["4", 2]}
        },
        "9": {
            "class_type": "SaveImage",
            "inputs": {"filename_prefix": "ComfyUI", "images": ["8", 0]}
        }
    }

    print("Queueing workflow...")
    
    # 3. Process Workflow
    results = client.process_workflow(workflow)

    # 4. Save Results
    for i, result in enumerate(results):
        filename = f"output_basic_{i}.png"
        print(f"Saving {filename}...")
        result.save(filename)
        
        if result.file_type == "image":
            result.show()

if __name__ == "__main__":
    main()
