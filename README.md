# File Date Prefix Naming Tool

## Introduction

The File Date Prefix Naming Tool is an efficient and user-friendly file management utility designed to help users quickly add creation or modification date prefixes to files in a folder, making file naming more standardized and easier to manage. Through a simple graphical user interface, users can select a target folder, specify the time type (creation or modification), and initiate batch renaming. The program automatically handles filename conflicts, checks filename formats, and provides detailed processing logs and progress feedback to ensure transparency and safety.

**English** | [中文](https://github.com/AISophon/FileRenamer/edit/main/README_cn.md)

## Features

- **Folder Selection**: Intuitive folder browser for selecting the target folder.
- **Time Type Selection**: Choose between file creation time or modification time for renaming.
- **Core Renaming Functionality**: Adds date prefixes in "YYYY-MM-DD " format.
- **Filename Legality Check**: Automatically cleans illegal characters from filenames.
- **Conflict Handling**: Automatically appends numbers to distinguish conflicting filenames.
- **Duplicate File Detection**: Identifies and handles duplicate files using size and hash comparisons.
- **Logging**: Records processing details for later review.
- **Progress Feedback**: Real-time progress bar and processing information.
- **Name Restoration**: Removes "YYYY-MM-DD " prefixes to restore original filenames.

## Installation Guide

### System Requirements

- Operating System: Windows 7+, macOS 10.12+, Linux (mainstream distributions)
- Python Version: 3.6+
- Memory: At least 2GB
- Disk Space: At least 50MB

### Installation Steps

1. Ensure Python 3.6 or higher is installed on your system.
2. Clone or download this project to your local machine.
3. Open a terminal or command prompt and navigate to the project directory.
4. Run the following command to install dependencies:
   ```
   pip install pyqt5
   ```
5. After installation, launch the program with:
   ```
   python main.py
   ```

## Usage Instructions

### Interface Overview

The main interface consists of:

- **Folder Selection Area**: Shows the selected folder path with a folder selection button.
- **Time Type Selection**: Choose between creation time or modification time.
- **Operation Mode Selection**: Choose between adding date prefixes or restoring original names.
- **Progress Bar**: Displays processing progress.
- **Log Display Area**: Shows processing logs.
- **Start Button**: Initiates batch renaming.

### Operating Steps

1. Click the "Select Folder" button to choose the folder to process.
2. Select the time type (creation or modification).
3. Choose the operation mode (add prefix or restore name).
4. Click "Start Processing" to begin.
5. View progress and results in the log display area.

## Update Log

### Version 1.0.0 - 2024-12-18

- **New Features**
  - Folder selection
  - Time type selection
  - Core file renaming
  - Filename legality checks
  - Conflict handling
  - Duplicate file detection
  - Logging
  - Progress feedback
  - Name restoration

- **Optimizations**
  - Fixed creation time accuracy issues on certain file systems
  - Improved file traversal and processing algorithms
  - Fixed special character handling in filenames

## Contribution Guidelines

To contribute to this project:

1. Fork this repository to your GitHub account.
2. Clone your fork locally.
3. Create a new branch for your improvements.
4. Make changes and ensure all tests pass.
5. Submit a pull request to the main branch of this project.

## License

This project is licensed under the MIT License. See the LICENSE file for details.
