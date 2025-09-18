#!/usr/bin/env python3
"""Simple Tkinter GUI for running backgroundremover on still images."""
from __future__ import annotations

import io
import subprocess
import tempfile
import threading
from pathlib import Path
from typing import Optional

try:  # Pillow is required for applying the DPI metadata
    from PIL import Image
except ImportError as exc:  # pragma: no cover - handled at runtime in the UI
    raise SystemExit(
        "Pillow is required to run this GUI. Install it with 'pip install pillow'."
    ) from exc

try:
    import tkinter as tk
    from tkinter import filedialog, messagebox
except ImportError as exc:  # pragma: no cover - Tkinter should be available on CPython
    raise SystemExit("Tkinter is not available in this Python installation") from exc

DEFAULT_PPI = 300


class BackgroundRemoverGUI:
    """Tkinter based GUI for removing backgrounds and updating DPI metadata."""

    def __init__(self, master: tk.Tk) -> None:
        self.master = master
        master.title("BackgroundRemover DPI Helper")
        master.resizable(False, False)

        self.input_var = tk.StringVar()
        self.output_var = tk.StringVar()
        self.ppi_var = tk.StringVar(value=str(DEFAULT_PPI))
        self.status_var = tk.StringVar(value="Ready")

        self._build_layout()

    # --- UI construction -------------------------------------------------
    def _build_layout(self) -> None:
        padding = {"padx": 10, "pady": 5}

        tk.Label(self.master, text="Input image").grid(row=0, column=0, sticky="w", **padding)
        input_entry = tk.Entry(self.master, textvariable=self.input_var, width=40)
        input_entry.grid(row=0, column=1, sticky="we", **padding)
        tk.Button(self.master, text="Browse", command=self._choose_input).grid(row=0, column=2, **padding)

        tk.Label(self.master, text="Output image").grid(row=1, column=0, sticky="w", **padding)
        output_entry = tk.Entry(self.master, textvariable=self.output_var, width=40)
        output_entry.grid(row=1, column=1, sticky="we", **padding)
        tk.Button(self.master, text="Browse", command=self._choose_output).grid(row=1, column=2, **padding)

        tk.Label(self.master, text="Desired PPI").grid(row=2, column=0, sticky="w", **padding)
        tk.Entry(self.master, textvariable=self.ppi_var, width=10).grid(row=2, column=1, sticky="w", **padding)

        self.run_button = tk.Button(self.master, text="Remove background", command=self._start_processing)
        self.run_button.grid(row=3, column=0, columnspan=3, pady=(10, 5))

        self.status_label = tk.Label(self.master, textvariable=self.status_var, anchor="w", fg="grey")
        self.status_label.grid(row=4, column=0, columnspan=3, sticky="we", padx=10, pady=(0, 10))

        for i in range(3):
            self.master.grid_columnconfigure(i, weight=1)

    # --- UI helpers ------------------------------------------------------
    def _choose_input(self) -> None:
        path = filedialog.askopenfilename(
            title="Select input image",
            filetypes=[("Images", "*.png *.jpg *.jpeg"), ("All files", "*.*")],
        )
        if path:
            self.input_var.set(path)
            if not self.output_var.get():
                suggested = _suggest_output_path(Path(path))
                self.output_var.set(str(suggested))

    def _choose_output(self) -> None:
        initialfile = Path(self.output_var.get()).name if self.output_var.get() else None
        path = filedialog.asksaveasfilename(
            title="Select output image",
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg"), ("All files", "*.*")],
            initialfile=initialfile,
        )
        if path:
            self.output_var.set(path)

    def _set_status(self, message: str, *, error: bool = False) -> None:
        def updater() -> None:
            self.status_var.set(message)
            self.status_label.config(fg="red" if error else "green" if message.startswith("Done") else "grey")

        self.master.after(0, updater)

    def _start_processing(self) -> None:
        thread = threading.Thread(target=self._process_image, daemon=True)
        self.run_button.config(state=tk.DISABLED)
        self._set_status("Processing...")
        thread.start()

    # --- Background processing ------------------------------------------
    def _process_image(self) -> None:
        try:
            input_path = Path(self.input_var.get()).expanduser()
            if not input_path.is_file():
                raise ValueError("Please select a valid input image file.")

            output_path = self.output_var.get().strip()
            if output_path:
                output_path = Path(output_path).expanduser()
            else:
                output_path = _suggest_output_path(input_path)
                self.output_var.set(str(output_path))

            try:
                ppi_value = float(self.ppi_var.get())
            except ValueError as exc:  # pragma: no cover - validated at runtime
                raise ValueError("The PPI value must be a number.") from exc
            if ppi_value <= 0:
                raise ValueError("The PPI value must be greater than zero.")

            result_bytes = _remove_background(input_path)
            _save_with_ppi(result_bytes, output_path, ppi_value)
        except Exception as exc:  # pragma: no cover - runtime feedback
            self._set_status(f"Error: {exc}", error=True)
            self.master.after(0, lambda: messagebox.showerror("BackgroundRemover", str(exc)))
        else:
            self._set_status("Done! Image saved.")
        finally:
            self.master.after(0, lambda: self.run_button.config(state=tk.NORMAL))


# --- Helper functions ----------------------------------------------------
def _suggest_output_path(input_path: Path) -> Path:
    suffix = input_path.suffix.lower() or ".png"
    if suffix not in {".png", ".jpg", ".jpeg"}:
        suffix = ".png"
    return input_path.with_name(f"{input_path.stem}_no_bg{suffix}")


def _remove_background(input_path: Path) -> bytes:
    """Try to use the Python API, fall back to the CLI if unavailable."""
    try:
        from backgroundremover.bg import remove  # type: ignore import-not-found
    except Exception:  # pragma: no cover - fallback path
        return _remove_background_cli(input_path)

    with input_path.open("rb") as source:
        data = source.read()
    return remove(data)  # type: ignore[call-arg]


def _remove_background_cli(input_path: Path) -> bytes:
    cli_name = "backgroundremover"
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_output = Path(tmpdir, input_path.name)
        cmd = [cli_name, "-i", str(input_path), "-o", str(tmp_output)]
        try:
            subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except FileNotFoundError as exc:  # pragma: no cover - runtime feedback
            raise RuntimeError(
                "Neither the Python module nor the 'backgroundremover' CLI is available."
            ) from exc
        except subprocess.CalledProcessError as exc:  # pragma: no cover
            stderr = exc.stderr.decode(errors="ignore") if exc.stderr else ""
            raise RuntimeError(f"backgroundremover CLI failed: {stderr.strip() or exc}") from exc

        with tmp_output.open("rb") as result:
            return result.read()


def _save_with_ppi(image_bytes: bytes, output_path: Path, ppi: float) -> None:
    with Image.open(io.BytesIO(image_bytes)) as image:
        format_name: Optional[str] = image.format
        save_kwargs = {"dpi": (ppi, ppi)}
        if format_name:
            save_kwargs["format"] = format_name
        output_path.parent.mkdir(parents=True, exist_ok=True)
        image.save(output_path, **save_kwargs)


def main() -> None:
    root = tk.Tk()
    gui = BackgroundRemoverGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
