# FTB Quest Localizer

[![PyPI version](https://img.shields.io/pypi/v/ftb-quest-localizer.svg)](https://pypi.org/project/ftb-quest-localizer/)
[![Python Version](https://img.shields.io/pypi/pyversions/ftb-quest-localizer.svg)](https://pypi.org/project/ftb-quest-localizer/)
[![License](https://img.shields.io/github/license/kressety/FTBQuestLocalizerPython)](LICENSE)

English | [中文](README_zh.md)

FTB Quest Localizer is a tool for extracting quest strings from Minecraft modpacks into JSON files for easy localization.

**Note: Works only with Minecraft 1.15+ modpacks**

### Installation

From Pypi:
```
pip install ftb-quest-localizer
```

From source:
```
git clone https://github.com/your-username/FTB-Quest-Localizer
cd FTB-Quest-Localizer
pip install -e .
```

### Usage

The tool requires access to a FTB quests directory.

#### Command Line Usage
```
ftb-quest-localizer --modpack <modpack_name> --path <ftbquests_path>
```

Options:
- `--modpack`, `-m`: Modpack name (used for JSON keys)
- `--path`, `-p`: Path to the ftbquests directory
- `--help`, `-h`: Show help message

#### As a Python Library
```python
from ftb_quest_localizer.localizer import run

# Run localization with modpack name and path to ftbquests
run("modpack_name", "path/to/ftbquests")
```

### How It Works
The tool:
1. Scans and extracts quest files from the ftbquests/quests/chapters directory
2. Extracts title, subtitle, and description fields
3. Replaces original text with translation keys
4. Generates JSON language files containing the original text
