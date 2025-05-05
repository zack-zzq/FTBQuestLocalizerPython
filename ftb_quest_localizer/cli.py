"""Command-line interface module"""

import re
import os
import argparse
import sys

from prompt_toolkit import prompt
from prompt_toolkit.validation import Validator, ValidationError

from .localizer import run


class ModpackNameValidator(Validator):
    """Modpack name validator"""
    def validate(self, document):
        text = document.text
        if not text:
            raise ValidationError(message="Modpack name cannot be empty")
        
        # Remove invalid characters
        invalid_chars = r'[`~!@#$%^&*()_|+\-=?;:\'",.<>\{\}\[\]\\\/ ]'
        if re.search(invalid_chars, text):
            raise ValidationError(
                message="Modpack name contains invalid characters",
                cursor_position=len(text)
            )


class PathValidator(Validator):
    """Path validator"""
    def validate(self, document):
        text = document.text
        if not text:
            raise ValidationError(message="Path cannot be empty")
        
        if not os.path.exists(text):
            raise ValidationError(
                message="Path does not exist",
                cursor_position=len(text)
            )


def interactive_mode():
    """Interactive mode to get user input"""
    print("FTB Quest Localization Tool")
    print("Output will be created in the output directory")
    
    modpack_name = prompt(
        "Enter modpack name (used for JSON keys): ",
        validator=ModpackNameValidator()
    )
    
    # Remove invalid characters
    invalid_chars = r'[`~!@#$%^&*()_|+\-=?;:\'",.<>\{\}\[\]\\\/ ]'
    modpack_name = re.sub(invalid_chars, "", modpack_name)
    
    ftbquests_path = prompt(
        "Enter path to ftbquests directory: ",
        validator=PathValidator()
    )
    
    return modpack_name, ftbquests_path


def main():
    """Main function, handles command-line arguments"""
    parser = argparse.ArgumentParser(
        description="FTB Quest Localization Tool - Extract quest strings for easy localization"
    )
    parser.add_argument(
        "--modpack", "-m",
        help="Modpack name (used for JSON keys)",
        type=str
    )
    parser.add_argument(
        "--path", "-p",
        help="Path to ftbquests directory",
        type=str
    )
    
    args = parser.parse_args()
    
    # If both arguments are provided, use them; otherwise enter interactive mode
    if args.modpack and args.path:
        # Validate and clean modpack name
        invalid_chars = r'[`~!@#$%^&*()_|+\-=?;:\'",.<>\{\}\[\]\\\/ ]'
        modpack_name = re.sub(invalid_chars, "", args.modpack)
        if not modpack_name:
            print("Error: Invalid modpack name")
            sys.exit(1)
        
        # Validate path
        ftbquests_path = args.path
        if not os.path.exists(ftbquests_path):
            print(f"Error: Path '{ftbquests_path}' does not exist")
            sys.exit(1)
    else:
        modpack_name, ftbquests_path = interactive_mode()
    
    # Run localization processing
    success = run(modpack_name, ftbquests_path)
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()