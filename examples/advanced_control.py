import time
from comfyui_xy import ComfyUiClient

def main():
    client = ComfyUiClient(url="http://127.0.0.1:8188")

    # 1. Get System Stats
    print("Getting queue info...")
    queue = client.get_queue()
    print(f"Pending: {queue.get('queue_pending', 0)}, Running: {queue.get('queue_running', 0)}")

    # 2. Get Object Info (Node Definitions)
    print("\nGetting info for KSampler...")
    info = client.get_object_info("KSampler")
    if info:
        print(f"KSampler input types: {list(info.get('KSampler', {}).get('input', {}).get('required', {}).keys())}")

    # 3. Get History
    print("\nGetting history...")
    history = client.get_history_all()
    print(f"Total history items: {len(history)}")

    # 4. Interrupt (Demonstration)
    # print("\nInterrupting current execution...")
    # if client.interrupt():
    #     print("Interrupted successfully.")
    # else:
    #     print("Failed to interrupt.")

if __name__ == "__main__":
    main()
