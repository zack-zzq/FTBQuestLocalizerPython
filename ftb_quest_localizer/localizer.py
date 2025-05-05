"""FTB Quest Localization main functionality module"""

import os
import json
import re
from pathlib import Path


def quest_extract(chapter_file, modpack_name, ftbquests_path):
    """
    Extract quest strings from chapter file and generate localization files
    
    Args:
        chapter_file (str): Chapter file name
        modpack_name (str): Modpack name
        ftbquests_path (str): Path to ftbquests directory
    """
    chapter = chapter_file.replace(".snbt", "")
    
    # Read chapter file
    chapter_file_path = os.path.join(ftbquests_path, "quests", "chapters", chapter_file)
    with open(chapter_file_path, "r", encoding="utf-8") as f:
        quest_chapter = f.read().replace('\\"', "'")
    
    # Create output directory
    output_path = Path(f"./output/{modpack_name}/chapters")
    output_path.mkdir(parents=True, exist_ok=True)
    
    rewrite_chapter = quest_chapter
    lang = {}
    
    # Regex patterns for titles, subtitles and descriptions
    title_regex = re.compile(r'\btitle: \"[\s\S.]*?\"', re.MULTILINE)
    subtitle_regex = re.compile(r'\bsubtitle: \[?\"[\s\S.]*?\"\]?', re.MULTILINE)
    desc_regex = re.compile(r'\bdescription: \[[\s\S.]*?\]', re.MULTILINE)
    image_regex = re.compile(r'^{image:[0-9a-zA-Z]*:.*}$', re.MULTILINE)
    color_code_regex = re.compile(r'&[0-9A-FK-OR]', re.IGNORECASE)
    
    # Match text
    titles = title_regex.findall(quest_chapter)
    subtitles = subtitle_regex.findall(quest_chapter)
    descriptions = desc_regex.findall(quest_chapter)
    
    if not any([titles, subtitles, descriptions]):
        return
    
    def get_string(text, part):
        """Extract strings from text"""
        string_regex = re.compile(r'(?<=("))(?:(?=(\\?))\2.)*?(?=\1)')
        cleaned_text = text.replace(f"{part}: ", "").replace('""', "")
        return string_regex.findall(cleaned_text)
    
    def remove_empty(array):
        """Remove empty elements"""
        return [e for e in array if e]
    
    def add_quotes(match):
        """Add quotes to match"""
        return '"' + match.group(0) + '"'
    
    def convert(array, part):
        """Extract strings and convert to localization format"""
        source_strings = remove_empty(
            [item for sublist in [get_string(el, f"{part}") for el in array] for item in sublist]
        )
        
        nonlocal rewrite_chapter, lang
        
        for i, source_string in enumerate(source_strings):
            key = f"{modpack_name}.{chapter}.{part}{i}"
            
            # Skip if string matches image format
            if not image_regex.match(source_string):
                # Replace color codes
                source_string_with_color = color_code_regex.sub(
                    lambda m: add_quotes(m), source_string)
                
                # Replace original text with localization key
                rewrite_chapter = rewrite_chapter.replace(
                    f'"{source_string}"', f'"{{{key}}}"')
                
                # Save to language file
                lang[key] = source_string
        
        return rewrite_chapter, lang
    
    # Process various text types
    if titles:
        rewrite_chapter, lang = convert(titles, "title")
    if subtitles:
        rewrite_chapter, lang = convert(subtitles, "subtitle")
    if descriptions:
        rewrite_chapter, lang = convert(descriptions, "description")
    
    # Save modified chapter file
    with open(f"./output/{modpack_name}/chapters/{chapter_file}", "w", encoding="utf-8") as f:
        f.write(rewrite_chapter)
    
    # Save or update language file
    lang_file_path = f"./output/{modpack_name}/en_us.json"
    if os.path.exists(lang_file_path):
        with open(lang_file_path, "r", encoding="utf-8") as f:
            existing_lang = json.load(f)
        lang = {**existing_lang, **lang}
    
    with open(lang_file_path, "w", encoding="utf-8") as f:
        json.dump(lang, f, indent=2, ensure_ascii=False)
    
    print(f"{chapter_file} processed successfully")


def run(modpack_name, ftbquests_path):
    """
    Run localization processing
    
    Args:
        modpack_name (str): Modpack name
        ftbquests_path (str): Path to ftbquests directory
        
    Returns:
        bool: True if successful, False otherwise
    """
    chapters_path = os.path.join(ftbquests_path, "quests", "chapters")
    try:
        for file in os.listdir(chapters_path):
            quest_extract(file, modpack_name, ftbquests_path)
    except FileNotFoundError:
        print(f"Error: '{chapters_path}' directory not found")
        return False
    return True