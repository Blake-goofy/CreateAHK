#create_ahk.py

import os
import shutil
import sys
import tkinter as tk
from tkinter import messagebox, filedialog
import configparser
import subprocess
import json

BASE_DIR = os.path.dirname(os.path.abspath(sys.argv[0]))
TEMPLATE_DIR = os.path.join(BASE_DIR, "ahk_template")
INI_PATH = os.path.join(BASE_DIR, "settings.ini")

config = configparser.ConfigParser()
if os.path.exists(INI_PATH):
    config.read(INI_PATH)
    last_dir = config.get("Options", "last_dir", fallback=BASE_DIR)
    last_ahk_dir = config.get("Options", "last_ahk_dir", fallback=BASE_DIR)
else:
    last_dir = BASE_DIR
    last_ahk_dir = BASE_DIR

def browse_dir():
    dir_selected = filedialog.askdirectory(initialdir=last_dir)
    if dir_selected:
        entry_dir.delete(0, tk.END)
        entry_dir.insert(0, os.path.normpath(dir_selected))

def save_last_dir(path):
    config["Options"] = {"last_dir": path}
    with open(INI_PATH, "w") as configfile:
        config.write(configfile)

def browse_ahk_exe():
    exe_selected = filedialog.askopenfilename(
        initialdir=last_ahk_dir,
        title="Select AutoHotkey64.exe",
        filetypes=[("AutoHotkey Executable", "AutoHotkey64.exe"), ("All Files", "*.*")]
    )
    if exe_selected:
        entry_ahk_exe.delete(0, tk.END)
        entry_ahk_exe.insert(0, os.path.normpath(exe_selected))

def save_last_ahk_dir(path):
    config["Options"]["last_ahk_dir"] = path
    with open(INI_PATH, "w") as configfile:
        config.write(configfile)

def create_project():
    project_name = entry_project.get().strip()
    script_name = entry_script.get().strip()
    dest_parent = entry_dir.get().strip()
    ahk_exe_path = entry_ahk_exe.get().strip()

    ensure_ahk_task_keybinding()

    if not project_name or not script_name or not dest_parent or not ahk_exe_path:
        messagebox.showerror("Error", "All fields are required.")
        return

    dest_dir = os.path.join(dest_parent, project_name)
    if os.path.exists(dest_dir):
        messagebox.showerror("Error", f"Project already exists:\n{dest_dir}")
        return

    ahk_dir = os.path.dirname(ahk_exe_path)
    bat_path = os.path.join(ahk_dir, "toggle_ahk.bat")
    template_bat_path = os.path.join(TEMPLATE_DIR, ".vscode", "toggle_ahk.bat")

    try:
        # Copy everything except .vscode/toggle_ahk.bat
        shutil.copytree(TEMPLATE_DIR, dest_dir, ignore=shutil.ignore_patterns('toggle_ahk.bat'))
        old_script = os.path.join(dest_dir, "template.ahk")
        new_script = os.path.join(dest_dir, f"{script_name}.ahk")
        os.rename(old_script, new_script)
        save_last_dir(dest_parent)
        save_last_ahk_dir(ahk_dir)

        # Only copy toggle_ahk.bat to the ahk_dir if it doesn't exist
        if not os.path.exists(bat_path):
            with open(template_bat_path, "r", encoding="utf-8") as f:
                bat_content = f.read()
            bat_content = bat_content.replace(
                'start "" "dir\\AutoHotkey64.exe" "%SCRIPT%"',
                f'start "" "{ahk_dir}\\AutoHotkey64.exe" "%SCRIPT%"'
            )
            with open(bat_path, "w", encoding="utf-8") as f:
                f.write(bat_content)

        # Update tasks.json in the new project to point to the correct bat file
        tasks_path = os.path.join(dest_dir, ".vscode", "tasks.json")
        if os.path.exists(tasks_path):
            with open(tasks_path, "r", encoding="utf-8") as f:
                content = f.read()
            bat_path_json = bat_path.replace("\\", "\\\\")  # Escape for JSON
            content = content.replace(
                '"command": "dir\\\\ahk_template\\\\.vscode\\\\toggle_ahk.bat"',
                f'"command": "{bat_path_json}"'
            )
            with open(tasks_path, "w", encoding="utf-8") as f:
                f.write(content)

    except Exception as e:
        messagebox.showerror("Error", f"Failed to create project:\n{e}")
        root.destroy()
        return

    # Open the folder in VS Code
    try:
        subprocess.Popen(["code.cmd", dest_dir])
        root.destroy()
    except Exception as e:
        messagebox.showinfo("Success", f"Project created at:\n{dest_dir}\nBut could not open in VS Code:\n{e}")
        root.destroy()

def ensure_ahk_task_keybinding():
    user_dir = os.path.expanduser(r"~\AppData\Roaming\Code\User")
    keybindings_path = os.path.join(user_dir, "keybindings.json")
    entry = {
        "command": "workbench.action.tasks.runTask",
        "args": "Toggle AHK Script",
        "when": "editorLangId == ahk2"
    }

    # Read existing keybindings
    if os.path.exists(keybindings_path):
        with open(keybindings_path, "r", encoding="utf-8") as f:
            try:
                keybindings = json.load(f)
            except Exception:
                keybindings = []
    else:
        keybindings = []

    # Check if entry exists (ignoring "key")
    exists = any(
        kb.get("command") == entry["command"] and
        kb.get("args") == entry["args"] and
        kb.get("when") == entry["when"]
        for kb in keybindings
    )

    # If not, add with default key "f5"
    if not exists:
        entry["key"] = "f5"
        keybindings.append(entry)
        with open(keybindings_path, "w", encoding="utf-8") as f:
            json.dump(keybindings, f, indent=2)

# GUI Setup
root = tk.Tk()
root.title("AHK Project Generator")
root.geometry("500x220")

tk.Label(root, text="Project name:").place(x=20, y=20)
entry_project = tk.Entry(root, width=50)
entry_project.place(x=140, y=20)

tk.Label(root, text=".ahk name:").place(x=20, y=60)
entry_script = tk.Entry(root, width=50)
entry_script.place(x=140, y=60)

tk.Label(root, text="Repo folder:").place(x=20, y=100)
entry_dir = tk.Entry(root, width=40)
entry_dir.place(x=140, y=100)
entry_dir.insert(0, last_dir)
btn_browse = tk.Button(root, text="Browse", command=browse_dir)
btn_browse.place(x=400, y=97)

tk.Label(root, text="AutoHotkey64.exe:").place(x=20, y=140)
entry_ahk_exe = tk.Entry(root, width=40)
entry_ahk_exe.place(x=140, y=140)
entry_ahk_exe.insert(0, os.path.join(last_ahk_dir, "AutoHotkey64.exe"))
btn_browse_ahk = tk.Button(root, text="Browse", command=browse_ahk_exe)
btn_browse_ahk.place(x=400, y=137)

btn = tk.Button(root, text="Create Project", command=create_project, width=20)
btn.place(x=180, y=180)

root.mainloop()