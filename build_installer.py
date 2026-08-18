import os
import sys
import shutil
import subprocess
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VENV_PYTHON = os.path.join(BASE_DIR, ".venv", "Scripts", "python.exe")
PYINSTALLER_EXE = os.path.join(BASE_DIR, ".venv", "Scripts", "pyinstaller.exe")

def clean_dir(path):
    if os.path.exists(path):
        for _ in range(5):
            try:
                shutil.rmtree(path, ignore_errors=True)
                if not os.path.exists(path):
                    break
            except Exception:
                time.sleep(0.5)

def get_package_path(package_name):
    script = f"import {package_name}; print({package_name}.__path__[0])"
    try:
        res = subprocess.check_output([VENV_PYTHON, "-c", script], text=True).strip()
        return res
    except Exception as e:
        print(f"Could not locate package {package_name}: {e}")
        return None

def build():
    print("=== Building EZ-Game-Chat Standalone Executable ===")

    dist_dir = os.path.join(BASE_DIR, "dist")
    build_dir = os.path.join(BASE_DIR, "build")

    clean_dir(os.path.join(dist_dir, "EZ-Game-Chat"))
    clean_dir(build_dir)
    
    ctk_path = get_package_path("customtkinter")
    dnd_path = get_package_path("tkinterdnd2")

    add_data_args = []

    # CustomTkinter assets
    if ctk_path and os.path.exists(ctk_path):
        add_data_args.extend(["--add-data", f"{ctk_path};customtkinter"])
        print(f"Added CustomTkinter assets from {ctk_path}")

    # TkinterDnD2 assets
    if dnd_path and os.path.exists(dnd_path):
        add_data_args.extend(["--add-data", f"{dnd_path};tkinterdnd2"])
        print(f"Added TkinterDnD2 assets from {dnd_path}")

    # Project assets
    quotes_file = os.path.join(BASE_DIR, "quotes.json")
    settings_file = os.path.join(BASE_DIR, "settings.json")
    changelog_file = os.path.join(BASE_DIR, "CHANGELOG.md")
    uninstaller_file = os.path.join(BASE_DIR, "uninstaller.bat")
    icons_dir = os.path.join(BASE_DIR, "icons")

    if os.path.exists(quotes_file):
        add_data_args.extend(["--add-data", f"{quotes_file};."])
    if os.path.exists(settings_file):
        add_data_args.extend(["--add-data", f"{settings_file};."])
    if os.path.exists(changelog_file):
        add_data_args.extend(["--add-data", f"{changelog_file};."])
    if os.path.exists(uninstaller_file):
        add_data_args.extend(["--add-data", f"{uninstaller_file};."])
    if os.path.exists(icons_dir):
        add_data_args.extend(["--add-data", f"{icons_dir};icons"])

    # Output icon
    icon_ico = os.path.join(icons_dir, "icon.ico")
    icon_png = os.path.join(icons_dir, "icon.png")
    app_icon = icon_ico if os.path.exists(icon_ico) else (icon_png if os.path.exists(icon_png) else None)
    icon_arg = []
    if app_icon:
        icon_arg = ["--icon", app_icon]

    cmd = [
        PYINSTALLER_EXE,
        "--noconfirm",
        "--clean",
        "--onedir",
        "--windowed",
        "--name", "EZ-Game-Chat",
        "--uac-admin",
        "--collect-all", "PIL",
        "--collect-all", "customtkinter",
        "--collect-all", "tkinterdnd2",
        "--hidden-import", "PIL._imaging",
        *icon_arg,
        *add_data_args,
        os.path.join(BASE_DIR, "main.py")
    ]

    print("Running PyInstaller command...")
    res = subprocess.run(cmd, cwd=BASE_DIR)
    if res.returncode == 0:
        print("\n=== Build Completed Successfully! ===")
        print(f"Executable output folder: {os.path.join(BASE_DIR, 'dist', 'EZ-Game-Chat')}")
    else:
        print(f"\nBuild failed with exit code {res.returncode}")

if __name__ == "__main__":
    build()
