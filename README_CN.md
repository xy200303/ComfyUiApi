# ComfyUI API Client

[English](README.md) | [中文](README_CN.md)

一个用于与 [ComfyUI](https://github.com/comfyanonymous/ComfyUI) API 交互的 Python 客户端库。
该库提供了一个便捷的包装器，可以通过编程方式排队工作流、上传图像/遮罩以及检索生成结果（图像、视频、音频等）。

## 特性

- **工作流管理**：轻松排队工作流并等待结果。
- **文件管理**：直接将输入图像和遮罩上传到 ComfyUI。
- **通用输出处理**：自动处理各种输出类型（图像、视频/GIF、音频）。
- **执行控制**：中断运行中的任务、检查队列状态和查看历史记录。
- **节点信息**：检索 ComfyUI 节点的定义。

## 安装

```bash
pip install comfyui_xy
```

## 如何获取工作流 JSON

要使用此 API，你需要 **API 格式** 的工作流，这与 ComfyUI 默认保存的 JSON 不同。

1. **开启开发者模式**：
   - 在 ComfyUI 网页界面中，点击菜单中的 **设置**（齿轮图标）。
   - 勾选 **"Enable Dev mode Options"**（开启开发者模式选项）。

2. **保存为 API 格式**：
   - 开启开发者模式后，菜单中会出现一个新按钮：**"Save (API Format)"**。
   - 点击该按钮将工作流保存为 JSON 文件（例如 `workflow_api.json`）。
   - 将此 JSON 文件用于 `ComfyUiClient`。

## 快速开始

```python
import json
from comfyui_api import ComfyUiClient

# 1. 初始化客户端
client = ComfyUiClient(url="http://127.0.0.1:8188")

# 2. 加载工作流
# 你应该从 ComfyUI 中导出 "API 格式" 的工作流
with open("workflow_api.json", "r", encoding="utf-8") as f:
    workflow = json.load(f)

# 3. 修改参数（可选）
# 例如，修改 KSampler（节点 ID "3"）中的随机种子
import random
workflow["3"]["inputs"]["seed"] = random.randint(1, 1000000000)

# 4. 运行工作流
print("正在排队工作流...")
results = client.process_workflow(workflow)

# 5. 处理结果
for i, result in enumerate(results):
    print(f"收到文件: {result.filename} ({result.file_type})")
    
    # 保存到磁盘
    result.save(f"output_{i}_{result.filename}")
    
    # 如果是图像，则显示
    if result.file_type == "image":
        result.show()
```

## 详细用法

### 1. 初始化

```python
from comfyui_api import ComfyUiClient

# 默认本地服务器 (http://127.0.0.1:8188)
client = ComfyUiClient() 

# 指定 URL
client = ComfyUiClient(url="http://127.0.0.1:8188")

# 远程 HTTPS 服务器
client = ComfyUiClient(url="https://my-comfyui-server.com:8188")
```

### 2. 上传文件

在运行工作流之前，你可以上传图像或遮罩。这些文件将保存在 ComfyUI 的 `input` 目录中。

```python
# 上传图像
# 返回 ComfyUI 使用的文件名（用于设置节点输入）
image_name = client.upload_image("path/to/my_image.png")

# 上传遮罩
mask_name = client.upload_mask("path/to/my_mask.png")

# 示例：在 LoadImage 节点（例如节点 ID "10"）中设置上传的图像
workflow["10"]["inputs"]["image"] = image_name
```

### 3. 处理工作流

`process_workflow` 方法是一个高级助手，它执行以下操作：
1. 排队提示词。
2. 等待执行完成。
3. 下载所有生成的文件。

```python
results = client.process_workflow(workflow)
```

**返回值：**
它返回一个 `ComfyResponse` 对象列表。

### 4. 处理响应 (`ComfyResponse`)

`ComfyResponse` 对象封装了 ComfyUI 返回的原始数据。

- **属性**:
  - `data`: 文件的原始字节数据。
  - `filename`: 服务器上的原始文件名。
  - `file_type`: 文件类型（例如 'image', 'video', 'audio'）。
  - `image`: 一个 `PIL.Image` 对象（如果文件是有效图像）。

- **方法**:
  - `save(path=None)`: 将文件保存到磁盘。如果 `path` 为 None，则使用 `filename`。
  - `show()`: 在默认查看器中打开图像（仅适用于图像）。

### 5. 高级控制

**中断执行：**
```python
client.interrupt()
```

**获取系统状态：**
```python
# 获取队列状态（待处理/运行中的任务）
queue_info = client.get_queue()

# 获取完整历史记录
history = client.get_history_all()

# 获取节点信息
node_info = client.get_object_info("KSampler")
```

## 示例

查看 [examples/](examples/) 目录以获取更完整的脚本：
- `basic_workflow.py`: 简单的文生图生成。
- `image_to_image.py`: 上传图像并进行处理。
- `advanced_control.py`: 检查队列和系统信息。

## 许可证

MIT
