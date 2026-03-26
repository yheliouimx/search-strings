"""Setup configuration for search-strings package."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="search-strings",
    version="2.1.0",
    author="Youssef HELIOUI",
    description="High-performance recursive pattern search tool with multi-format reporting",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yheliouimx/search-strings",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Archiving :: Mirroring",
        "Topic :: Utilities",
    ],
    python_requires=">=3.7",
    install_requires=[
        "tqdm>=4.50.0",
        "colorama>=0.4.3",
        "pandas>=1.0.0",
        "openpyxl>=3.0.0",
        "rich>=10.0.0",
    ],
    entry_points={
        "console_scripts": [
            "search-strings=search_strings.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
