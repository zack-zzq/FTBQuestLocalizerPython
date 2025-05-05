from setuptools import setup, find_packages

setup(
    name="ftb_quest_localizer",
    version="1.0.0",
    description="FTB Quest Localization Helper",
    author="Zack Zhu",
    license="MIT",
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