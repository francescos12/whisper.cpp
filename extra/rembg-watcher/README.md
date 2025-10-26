# rembg watcher setup

This directory contains a PowerShell helper script that prepares a simple "watcher" workspace for background removal tasks on Windows. Running the script

```
powershell -ExecutionPolicy Bypass -File .\setup-rembg-watcher.ps1
```

will, by default, create the workspace under `<UserProfile>\rembg-watcher`. You can target a different location by providing the optional `-BasePath` parameter.

The script performs the following steps:

1. Creates `input` and `output` folders inside the chosen workspace.
2. Installs the Python dependencies required by the `backgroundremover` command line tool (including PyTorch, Pillow, OpenCV, and media utilities).
3. Generates three convenience scripts in the workspace:
   * `Processa_Soft.ps1` &mdash; uses the `isnet-general-use` model.
   * `Processa_Medium.ps1` &mdash; uses the `u2net` model.
   * `Processa_Hard.ps1` &mdash; uses the `u2netp` model.

To process images, drop them into the `input` folder and then run the desired processing script. The outputs will be saved to the `output` folder with suffixes that match the chosen strength profile (soft, medium, hard).
