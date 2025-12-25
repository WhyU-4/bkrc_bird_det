"""
Setup script for Bird Detection and Tracking System
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="bkrc_bird_det",
    version="1.0.0",
    author="WhyU-4",
    description="Bird detection and tracking system with YOLO11 and ONVIF PTZ control for RK3588S",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/WhyU-4/bkrc_bird_det",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Image Recognition",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "bird-tracker=main:main",
        ],
    },
)
