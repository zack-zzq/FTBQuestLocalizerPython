from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ftb-quest-localizer",
    version="1.0.1",
    description="FTB Quest Localization Helper",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Zack Zhu",
    license="MIT",
    url="https://github.com/zack-zzq/FTBQuestLocalizerPython",
    project_urls={
        "Bug Tracker": "https://github.com/zack-zzq/FTBQuestLocalizerPython/issues",
    },
    packages=find_packages(),
    install_requires=[
        "prompt_toolkit>=3.0.0",
    ],
    entry_points={
        'console_scripts': [
            'ftb-quest-localizer=ftb_quest_localizer.cli:main',
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)