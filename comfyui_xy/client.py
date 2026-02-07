import requests
import time
import io
import random
import asyncio
import aiohttp
from PIL import Image

class ComfyResponse:
    def __init__(self, data, filename, source_type):
        self.data = data
        self.filename = filename
        self.source_type = source_type # 'output', 'temp', etc.
        self.file_type = self._determine_file_type()
        self.image = None
        
        if self.file_type == 'image':
            try:
                self.image = Image.open(io.BytesIO(data))
            except Exception:
                pass

    def _determine_file_type(self):
        """Determine file type based on extension."""
        if not self.filename:
            return 'unknown'
            
        ext = self.filename.split('.')[-1].lower()
        if ext in ['png', 'jpg', 'jpeg', 'webp', 'bmp', 'tiff']:
            return 'image'
        elif ext in ['mp4', 'mkv', 'webm', 'gif', 'avi', 'mov']:
            return 'video'
        elif ext in ['mp3', 'wav', 'flac', 'ogg']:
            return 'audio'
        return 'unknown'

    def save(self, path=None):
        """
        Save the file to disk.
        
        Args:
            path (str, optional): The path to save to. Defaults to the original filename.
        """
        if path is None:
            path = self.filename
        with open(path, 'wb') as f:
            f.write(self.data)
            
    def show(self):
        """
        Show the image if it is one.
        """
        if self.image:
            self.image.show()
        else:
            print(f"Cannot show non-image file: {self.filename}")

class ComfyUiClient:
    def __init__(self, url="http://127.0.0.1:8188", server_address=None, https=False):
        """
        Initialize the ComfyUI client.
        
        Args:
            url (str): The full URL of the ComfyUI server (e.g., "http://127.0.0.1:8188").
            server_address (str, optional): Deprecated. Use `url` instead.
            https (bool, optional): Deprecated. Use `url` instead.
        """
        if server_address:
            # Backward compatibility
            self.url_prefix = "https://" if https else "http://"
            self.base_url = f"{self.url_prefix}{server_address}"
        else:
            # New URL handling
            if not url.startswith("http"):
                # Assume http if protocol is missing but user passed "127.0.0.1:8188"
                url = f"http://{url}"
            self.base_url = url.rstrip("/")

    def upload_image(self, image_path, overwrite=True):
        """
        Upload an image to the ComfyUI server.
        
        Args:
            image_path (str): Path to the image file.
            overwrite (bool): Whether to overwrite existing files.
            
        Returns:
            str: The name of the uploaded file on the server, or None if failed.
        """
        url = f"{self.base_url}/upload/image"
        try:
            with open(image_path, 'rb') as f:
                files = {'image': f}
                data = {'type': 'input', 'overwrite': str(overwrite).lower()}
                response = requests.post(url, files=files, data=data)
                
            if response.status_code == 200:
                result = response.json()
                return result.get('name')
            else:
                print(f"Failed to upload image: {response.status_code} {response.text}")
                return None
        except Exception as e:
            print(f"Error uploading image: {e}")
            return None

    def upload_mask(self, mask_path, overwrite=True):
        """
        Upload a mask to the ComfyUI server.
        
        Args:
            mask_path (str): Path to the mask file.
            overwrite (bool): Whether to overwrite existing files.
            
        Returns:
            str: The name of the uploaded mask file on the server, or None if failed.
        """
        url = f"{self.base_url}/upload/mask"
        try:
            with open(mask_path, 'rb') as f:
                files = {'image': f}
                data = {'type': 'input', 'overwrite': str(overwrite).lower()}
                response = requests.post(url, files=files, data=data)
                
            if response.status_code == 200:
                result = response.json()
                return result.get('name')
            else:
                print(f"Failed to upload mask: {response.status_code} {response.text}")
                return None
        except Exception as e:
            print(f"Error uploading mask: {e}")
            return None

    def interrupt(self):
        """
        Interrupt the current execution.
        
        Returns:
            bool: True if successful, False otherwise.
        """
        url = f"{self.base_url}/interrupt"
        try:
            response = requests.post(url)
            return response.status_code == 200
        except Exception as e:
            print(f"Error interrupting execution: {e}")
            return False

    def get_object_info(self, node_class):
        """
        Get information about a specific node class.
        
        Args:
            node_class (str): The node class name.
            
        Returns:
            dict: The object info, or None if failed.
        """
        url = f"{self.base_url}/object_info/{node_class}"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Failed to get object info: {response.status_code} {response.text}")
                return None
        except Exception as e:
            print(f"Error getting object info: {e}")
            return None

    def get_history_all(self):
        """
        Get the entire history.
        
        Returns:
            dict: The history data.
        """
        url = f"{self.base_url}/history"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return response.json()
            return {}
        except Exception as e:
            print(f"Error getting history: {e}")
            return {}

    def get_queue(self):
        """
        Get the current queue status.
        
        Returns:
            dict: The queue data.
        """
        url = f"{self.base_url}/queue"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return response.json()
            return {}
        except Exception as e:
            print(f"Error getting queue: {e}")
            return {}


    def queue_prompt(self, workflow):
        """
        Queue a workflow for execution.
        
        Args:
            workflow (dict): The workflow JSON object.
            
        Returns:
            str: The prompt ID, or None if failed.
        """
        url = f"{self.base_url}/prompt"
        data = {"prompt": workflow}
        try:
            response = requests.post(url, json=data)
            if response.status_code == 200:
                result = response.json()
                return result.get('prompt_id')
            else:
                print(f"Failed to queue prompt: {response.status_code} {response.text}")
                return None
        except Exception as e:
            print(f"Error queuing prompt: {e}")
            return None

    def get_history(self, prompt_id):
        """
        Get the history of a specific prompt execution.
        
        Args:
            prompt_id (str): The prompt ID.
            
        Returns:
            dict: The history data.
        """
        url = f"{self.base_url}/history/{prompt_id}"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return response.json()
            return {}
        except Exception as e:
            print(f"Error getting history: {e}")
            return {}

    def get_view(self, filename, subfolder, folder_type):
        """
        Download a file from the server (view endpoint).
        
        Args:
            filename (str): The filename.
            subfolder (str): The subfolder.
            folder_type (str): The folder type (e.g., "output").
            
        Returns:
            bytes: The file data.
        """
        url = f"{self.base_url}/view"
        params = {
            "filename": filename,
            "subfolder": subfolder,
            "type": folder_type
        }
        try:
            response = requests.get(url, params=params)
            return response.content
        except Exception as e:
            print(f"Error getting file: {e}")
            return None

    def get_image(self, filename, subfolder, folder_type):
        """
        Alias for get_view.
        """
        return self.get_view(filename, subfolder, folder_type)

    def wait_for_execution(self, prompt_id, check_interval=1):
        """
        Wait for a prompt execution to complete.
        
        Args:
            prompt_id (str): The prompt ID.
            check_interval (int): Seconds to wait between checks.
            
        Returns:
            dict: The output data from history.
        """
        while True:
            history = self.get_history(prompt_id)
            if prompt_id in history:
                return history[prompt_id].get('outputs', {})
            time.sleep(check_interval)

    def process_workflow(self, workflow):
        """
        High-level helper to process a workflow.
        Assumes the workflow is already configured with necessary inputs.
        
        Args:
            workflow (dict): The workflow JSON.
            
        Returns:
            list[ComfyResponse]: List of generated outputs (images, videos, etc.).
        """
        # 1. Queue Prompt
        prompt_id = self.queue_prompt(workflow)
        if not prompt_id:
            return []

        # 2. Wait for Execution
        outputs = self.wait_for_execution(prompt_id)

        # 3. Retrieve Files
        generated_files = []
        for node_id, node_output in outputs.items():
            # Iterate over all output types (images, gifs, videos, etc.)
            for output_type, output_list in node_output.items():
                if isinstance(output_list, list):
                    for item in output_list:
                        if isinstance(item, dict) and 'filename' in item and 'subfolder' in item and 'type' in item:
                            file_data = self.get_view(item['filename'], item['subfolder'], item['type'])
                            if file_data:
                                response = ComfyResponse(file_data, item['filename'], item['type'])
                                generated_files.append(response)
        
        return generated_files



class AsyncComfyUiClient:
    def __init__(self, url="http://127.0.0.1:8188", server_address=None, https=False):
        """
        Initialize the Async ComfyUI client.
        
        Args:
            url (str): The full URL of the ComfyUI server (e.g., "http://127.0.0.1:8188").
            server_address (str, optional): Deprecated. Use `url` instead.
            https (bool, optional): Deprecated. Use `url` instead.
        """
        if server_address:
            # Backward compatibility
            self.url_prefix = "https://" if https else "http://"
            self.base_url = f"{self.url_prefix}{server_address}"
        else:
            # New URL handling
            if not url.startswith("http"):
                # Assume http if protocol is missing but user passed "127.0.0.1:8188"
                url = f"http://{url}"
            self.base_url = url.rstrip("/")
        
        self._session = None

    async def _get_session(self):
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def upload_image(self, image_path, overwrite=True):
        """
        Upload an image to the ComfyUI server.
        
        Args:
            image_path (str): Path to the image file.
            overwrite (bool): Whether to overwrite existing files.
            
        Returns:
            str: The name of the uploaded file on the server, or None if failed.
        """
        url = f"{self.base_url}/upload/image"
        try:
            session = await self._get_session()
            with open(image_path, 'rb') as f:
                file_data = f.read()
            
            data = aiohttp.FormData()
            data.add_field('image', file_data, filename=image_path.split('/')[-1].split('\\')[-1])
            data.add_field('type', 'input')
            data.add_field('overwrite', str(overwrite).lower())
            
            async with session.post(url, data=data) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get('name')
                else:
                    text = await response.text()
                    print(f"Failed to upload image: {response.status} {text}")
                    return None
        except Exception as e:
            print(f"Error uploading image: {e}")
            return None

    async def upload_mask(self, mask_path, overwrite=True):
        """
        Upload a mask to the ComfyUI server.
        
        Args:
            mask_path (str): Path to the mask file.
            overwrite (bool): Whether to overwrite existing files.
            
        Returns:
            str: The name of the uploaded mask file on the server, or None if failed.
        """
        url = f"{self.base_url}/upload/mask"
        try:
            session = await self._get_session()
            with open(mask_path, 'rb') as f:
                file_data = f.read()
                
            data = aiohttp.FormData()
            data.add_field('image', file_data, filename=mask_path.split('/')[-1].split('\\')[-1])
            data.add_field('type', 'input')
            data.add_field('overwrite', str(overwrite).lower())
            
            async with session.post(url, data=data) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get('name')
                else:
                    text = await response.text()
                    print(f"Failed to upload mask: {response.status} {text}")
                    return None
        except Exception as e:
            print(f"Error uploading mask: {e}")
            return None

    async def interrupt(self):
        """
        Interrupt the current execution.
        
        Returns:
            bool: True if successful, False otherwise.
        """
        url = f"{self.base_url}/interrupt"
        try:
            session = await self._get_session()
            async with session.post(url) as response:
                return response.status == 200
        except Exception as e:
            print(f"Error interrupting execution: {e}")
            return False

    async def get_object_info(self, node_class):
        """
        Get information about a specific node class.
        
        Args:
            node_class (str): The node class name.
            
        Returns:
            dict: The object info, or None if failed.
        """
        url = f"{self.base_url}/object_info/{node_class}"
        try:
            session = await self._get_session()
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    text = await response.text()
                    print(f"Failed to get object info: {response.status} {text}")
                    return None
        except Exception as e:
            print(f"Error getting object info: {e}")
            return None

    async def get_history_all(self):
        """
        Get the entire history.
        
        Returns:
            dict: The history data.
        """
        url = f"{self.base_url}/history"
        try:
            session = await self._get_session()
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                return {}
        except Exception as e:
            print(f"Error getting history: {e}")
            return {}

    async def get_queue(self):
        """
        Get the current queue status.
        
        Returns:
            dict: The queue data.
        """
        url = f"{self.base_url}/queue"
        try:
            session = await self._get_session()
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                return {}
        except Exception as e:
            print(f"Error getting queue: {e}")
            return {}

    async def queue_prompt(self, workflow):
        """
        Queue a workflow for execution.
        
        Args:
            workflow (dict): The workflow JSON object.
            
        Returns:
            str: The prompt ID, or None if failed.
        """
        url = f"{self.base_url}/prompt"
        data = {"prompt": workflow}
        try:
            session = await self._get_session()
            async with session.post(url, json=data) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get('prompt_id')
                else:
                    text = await response.text()
                    print(f"Failed to queue prompt: {response.status} {text}")
                    return None
        except Exception as e:
            print(f"Error queuing prompt: {e}")
            return None

    async def get_history(self, prompt_id):
        """
        Get the history of a specific prompt execution.
        
        Args:
            prompt_id (str): The prompt ID.
            
        Returns:
            dict: The history data.
        """
        url = f"{self.base_url}/history/{prompt_id}"
        try:
            session = await self._get_session()
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                return {}
        except Exception as e:
            print(f"Error getting history: {e}")
            return {}

    async def get_view(self, filename, subfolder, folder_type):
        """
        Download a file from the server (view endpoint).
        
        Args:
            filename (str): The filename.
            subfolder (str): The subfolder.
            folder_type (str): The folder type (e.g., "output").
            
        Returns:
            bytes: The file data.
        """
        url = f"{self.base_url}/view"
        params = {
            "filename": filename,
            "subfolder": subfolder,
            "type": folder_type
        }
        try:
            session = await self._get_session()
            async with session.get(url, params=params) as response:
                return await response.read()
        except Exception as e:
            print(f"Error getting file: {e}")
            return None

    async def get_image(self, filename, subfolder, folder_type):
        """
        Alias for get_view.
        """
        return await self.get_view(filename, subfolder, folder_type)

    async def wait_for_execution(self, prompt_id, check_interval=1):
        """
        Wait for a prompt execution to complete.
        
        Args:
            prompt_id (str): The prompt ID.
            check_interval (int): Seconds to wait between checks.
            
        Returns:
            dict: The output data from history.
        """
        while True:
            history = await self.get_history(prompt_id)
            if prompt_id in history:
                return history[prompt_id].get('outputs', {})
            await asyncio.sleep(check_interval)

    async def process_workflow(self, workflow):
        """
        High-level helper to process a workflow.
        Assumes the workflow is already configured with necessary inputs.
        
        Args:
            workflow (dict): The workflow JSON.
            
        Returns:
            list[ComfyResponse]: List of generated outputs (images, videos, etc.).
        """
        # 1. Queue Prompt
        prompt_id = await self.queue_prompt(workflow)
        if not prompt_id:
            return []

        # 2. Wait for Execution
        outputs = await self.wait_for_execution(prompt_id)

        # 3. Retrieve Files
        generated_files = []
        for node_id, node_output in outputs.items():
            # Iterate over all output types (images, gifs, videos, etc.)
            for output_type, output_list in node_output.items():
                if isinstance(output_list, list):
                    for item in output_list:
                        if isinstance(item, dict) and 'filename' in item and 'subfolder' in item and 'type' in item:
                            file_data = await self.get_view(item['filename'], item['subfolder'], item['type'])
                            if file_data:
                                response = ComfyResponse(file_data, item['filename'], item['type'])
                                generated_files.append(response)
        
        return generated_files
