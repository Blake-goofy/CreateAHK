# AHK Project Generator (Python GUI)

This is a simple GUI tool to generate AutoHotkey v2 project folders with everything wired up to toggle the script using **F5 in VS Code**.

## Features

- Creates a new folder based on a project name
- Copies a template `.ahk` script and renames it
- Generates a `.vscode/tasks.json` that runs your script with a `toggle_ahk.bat` file
- Sets up a `keybindings.json` entry in VS Code so you can press `F5` to toggle AHK
- Opens the project folder in VS Code automatically

## Requirements

- Python 3.6+
- AutoHotkey v2 installed (must locate `AutoHotkey64.exe`)
- VS Code with the AutoHotkey extension

## How to Use

1. **Clone this repo:**

    ```bash
    git clone https://github.com/yourusername/create_ahk_project.git
    cd create_ahk_project
    ```

2. **Run the script:**

    ```bash
    python create_ahk.py
    ```

3. **Fill out the form:**
   - Project Name
   - Script Name (your `.ahk` file)
   - Destination Folder
   - Browse to your `AutoHotkey64.exe`

4. **Click "Create Project"** — The script will:
   - Create your new AHK project folder
   - Copy template files
   - Wire up F5 to run/stop the script in VS Code
   - Open the project in VS Code

## Template

Edit the `ahk_template/` folder to change what files are copied into new projects.
Make sure you preserve the structure, especially the `.vscode` folder.

## Notes

- The script saves your last used directories in `settings.ini`.
- The `.bat` file is only copied once to avoid overwriting your global runner.
- Make sure `"code"` is on your system path (or change `subprocess.Popen(["code.cmd", ...])` if needed).
