# FTB Quest Localizer

[![PyPI version](https://img.shields.io/pypi/v/ftb-quest-localizer.svg)](https://pypi.org/project/ftb-quest-localizer/)
[![Python Version](https://img.shields.io/pypi/pyversions/ftb-quest-localizer.svg)](https://pypi.org/project/ftb-quest-localizer/)
[![License](https://img.shields.io/github/license/zack-zzq/FTBQuestLocalizerPython)](LICENSE)

[English](README.md) | 中文

FTB Quest Localizer 是一个用于提取和管理 FTB Quests 本地化字符串的工具。同时支持**新格式**（1.20+，带 `lang/` 目录）和**旧格式**（1.20 以下，字符串直接内嵌在章节文件中）。

## 安装

从 PyPI 安装：
```bash
pip install ftb-quest-localizer
```

从源码安装（使用 [uv](https://docs.astral.sh/uv/)）：
```bash
git clone https://github.com/zack-zzq/FTBQuestLocalizerPython
cd FTBQuestLocalizerPython
uv sync
```

## 使用方法

工具提供三个命令：`split`、`extract` 和 `merge`。

### `split` — 新格式（1.20+）

将 `lang/en_us/` 下的 SNBT 语言文件拆分为按章节分组的 JSON 文件，方便翻译：

```bash
ftb-quest-localizer split -i <ftbquests/quests路径> -o <输出目录>
```

读取 `lang/en_us/` 目录，为每个章节生成一个 JSON 文件，章节组、奖励表等也有对应的独立文件。

### `extract` — 旧格式（1.20 以下）

从章节 SNBT 文件中直接提取可翻译字符串：

```bash
ftb-quest-localizer extract -i <ftbquests/quests路径> -o <输出目录> -m <整合包名称>
```

将内嵌的字符串替换为翻译键，并生成 `en_us.json` 语言文件。

### `merge` — 合并翻译

将翻译后的 JSON 文件合并回 SNBT 语言目录结构：

```bash
ftb-quest-localizer merge -i <JSON目录> -o <输出lang目录>
```

还原与 `lang/en_us/` 相同的目录结构（`chapter.snbt`、`chapter_group.snbt`、`chapters/*.snbt` 等），可直接放入整合包使用。

### 作为 Python 库使用

```python
from ftb_quest_localizer.splitter import split_lang_files
from ftb_quest_localizer.extractor import extract_quest_strings
from ftb_quest_localizer.merger import merge_json_to_lang_dir

# 新格式：拆分 SNBT 语言文件为 JSON
split_lang_files("path/to/ftbquests/quests", "output/")

# 旧格式：从章节文件提取字符串
extract_quest_strings("path/to/ftbquests/quests", "output/", "modpack_name")

# 合并翻译后的 JSON 回 SNBT
merge_json_to_lang_dir("translated_json/", "lang/zh_cn/")
```

## 工作原理

### 新格式（1.20+）
1. 读取 `lang/en_us/` 下的 SNBT 语言文件（章节、任务、子任务、奖励等条目）
2. 将多行描述展平为带数字后缀的键
3. 按章节分组输出 JSON 文件
4. 合并时从翻译后的 JSON 重建原始目录结构

### 旧格式（1.20 以下）
1. 使用 `snbtlib` 解析章节 SNBT 文件
2. 提取 `title`、`subtitle`、`description`、`text` 和悬停文本等字段
3. 将原始文本替换为翻译键
4. 生成包含原始文本的 JSON 语言文件