# FTB Quest Localizer

[English](README.md) | 中文

FTB Quest Localizer 是一个将 Minecraft 模组包中的任务字符串提取到 JSON 文件中以方便本地化的工具。

**注意：仅适用于 Minecraft 1.15+ 模组包**

### 安装

从源码安装：
```
git clone https://github.com/your-username/FTB-Quest-Localizer
cd FTB-Quest-Localizer
pip install -e .
```

### 使用方法

该工具需要访问 FTB quests 目录。

#### 命令行使用
```
ftb-quest-localizer --modpack <模组包名称> --path <ftbquests路径>
```

选项：
- `--modpack`, `-m`：模组包名称（用于 JSON 键）
- `--path`, `-p`：ftbquests 目录的路径
- `--help`, `-h`：显示帮助信息

#### 作为 Python 库使用
```python
from ftb_quest_localizer.localizer import run

# 使用模组包名称和 ftbquests 路径运行本地化处理
run("模组包名称", "ftbquests的路径")
```

### 工作原理
该工具会：
1. 扫描并提取 ftbquests/quests/chapters 目录中的任务文件
2. 提取标题、副标题和描述字段
3. 将原始文本替换为翻译键
4. 生成包含原始文本的 JSON 语言文件