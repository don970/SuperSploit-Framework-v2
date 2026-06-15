from setuptools import setup, find_packages
import os

setup(
    name="SuperSploit",
    version="6.0.0",
    author="Donald Ford",
    description="An advanced, multi-platform offensive security framework.",
    packages=find_packages(where="source"),
    package_dir={"": "source"},
    include_package_data=True,
    install_requires=[
        "cryptography",
        "pyfiglet",
        "pure-python-adb",
        "scapy",
        "requests",
        "PyYAML",
        "phonenumbers",
        "fpdf",
        "sqlitedict",
        "prompt-toolkit",
        "buildozer",
        "kivy",
        "PyPDF2",
        "python-docx",
        "openpyxl",
        "python-pptx",
        "Pillow",
        "pyserial",
        "psutil",
        "colorama",
        "tabulate"
    ],
    entry_points={
        'console_scripts': [
            'supersploit-native=main:main',
        ],
    },
    python_requires='>=3.10',
)
