"""Drag-and-drop GUI wrapper for deface."""
import os
import queue
import re
import shutil
import subprocess
import sys
import threading
from pathlib import Path
from tkinter import (
    BooleanVar, DoubleVar, StringVar, Tk, Toplevel,
    filedialog, messagebox, ttk, END, NORMAL, DISABLED,
)
from tkinter.scrolledtext import ScrolledText

try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    DND_AVAILABLE = True
except Exception:
    DND_AVAILABLE = False

VIDEO_EXTS = {".mp4", ".mov", ".mkv", ".avi", ".webm", ".m4v", ".mpg", ".mpeg", ".wmv", ".flv"}
HERE = Path(__file__).resolve().parent
DEFAULT_OUTPUT = HERE / "output"
SCRIPTS_DIR = Path(os.environ.get("APPDATA", "")) / "Python" / "Python313" / "Scripts"


def find_deface():
    exe = shutil.which("deface")
    if exe:
        return [exe]
    candidate = SCRIPTS_DIR / "deface.exe"
    if candidate.exists():
        return [str(candidate)]
    return [sys.executable, "-m", "deface"]


def parse_dropped(data: str):
    paths, buf, in_brace = [], "", False
    for ch in data:
        if ch == "{":
            in_brace = True
            continue
        if ch == "}":
            in_brace = False
            if buf:
                paths.append(buf); buf = ""
            continue
        if ch == " " and not in_brace:
            if buf:
                paths.append(buf); buf = ""
            continue
        buf += ch
    if buf:
        paths.append(buf)
    return [p for p in paths if p]


class App:
    def __init__(self, root):
        self.root = root
        root.title("Blur Faces - local + free (deface)")
        root.geometry("760x640")
        root.minsize(620, 540)

        self.files: list[Path] = []
        self.output_dir = StringVar(value=str(DEFAULT_OUTPUT))
        self.keep_audio = BooleanVar(value=True)
        self.thresh = DoubleVar(value=0.2)
        self.mask_scale = DoubleVar(value=1.3)
        self.mode = StringVar(value="blur")
        self.use_boxes = BooleanVar(value=False)
        self.mosaic_size = StringVar(value="20")
        self.log_q: queue.Queue = queue.Queue()
        self.worker: threading.Thread | None = None
        self.stop_flag = threading.Event()
        self.current_proc: subprocess.Popen | None = None

        self._build_ui()
        self.root.after(80, self._drain_log)

    def _build_ui(self):
        pad = {"padx": 10, "pady": 6}

        drop = ttk.Frame(self.root, relief="ridge", borderwidth=2)
        drop.pack(fill="x", padx=12, pady=(12, 6))
        self.drop_label = ttk.Label(
            drop,
            text=("Drop video files here\n(or click 'Add files...')"
                  if DND_AVAILABLE else
                  "Drag-drop unavailable - click 'Add files...' below"),
            anchor="center", justify="center", font=("Segoe UI", 12),
        )
        self.drop_label.pack(fill="x", ipady=28)
        if DND_AVAILABLE:
            drop.drop_target_register(DND_FILES)
            drop.dnd_bind("<<Drop>>", self._on_drop)
            self.drop_label.drop_target_register(DND_FILES)
            self.drop_label.dnd_bind("<<Drop>>", self._on_drop)

        list_frame = ttk.LabelFrame(self.root, text="Queue")
        list_frame.pack(fill="both", expand=False, padx=12, pady=6)
        self.listbox = ScrolledText(list_frame, height=5, state=DISABLED, wrap="none")
        self.listbox.pack(fill="x", padx=6, pady=6)

        btn_row = ttk.Frame(self.root)
        btn_row.pack(fill="x", padx=12)
        ttk.Button(btn_row, text="Add files...", command=self._pick_files).pack(side="left")
        ttk.Button(btn_row, text="Clear queue", command=self._clear_queue).pack(side="left", padx=6)

        opts = ttk.LabelFrame(self.root, text="Options")
        opts.pack(fill="x", padx=12, pady=8)

        row1 = ttk.Frame(opts); row1.pack(fill="x", **pad)
        ttk.Label(row1, text="Mode:").pack(side="left")
        for v in ("blur", "mosaic", "solid", "none"):
            ttk.Radiobutton(row1, text=v, variable=self.mode, value=v).pack(side="left", padx=4)
        ttk.Checkbutton(row1, text="Keep audio", variable=self.keep_audio).pack(side="right")

        row2 = ttk.Frame(opts); row2.pack(fill="x", **pad)
        ttk.Label(row2, text="Detection threshold (lower=more aggressive):").pack(side="left")
        ttk.Scale(row2, from_=0.05, to=0.6, variable=self.thresh, orient="horizontal", length=200).pack(side="left", padx=8)
        self.thresh_lbl = ttk.Label(row2, width=5, text="0.20")
        self.thresh_lbl.pack(side="left")
        self.thresh.trace_add("write", lambda *_: self.thresh_lbl.config(text=f"{self.thresh.get():.2f}"))

        row3 = ttk.Frame(opts); row3.pack(fill="x", **pad)
        ttk.Label(row3, text="Mask size (bigger = more coverage):").pack(side="left")
        ttk.Scale(row3, from_=1.0, to=2.5, variable=self.mask_scale, orient="horizontal", length=200).pack(side="left", padx=8)
        self.mask_lbl = ttk.Label(row3, width=5, text="1.30")
        self.mask_lbl.pack(side="left")
        self.mask_scale.trace_add("write", lambda *_: self.mask_lbl.config(text=f"{self.mask_scale.get():.2f}"))

        row4 = ttk.Frame(opts); row4.pack(fill="x", **pad)
        ttk.Checkbutton(row4, text="Use rectangles (instead of ellipse)", variable=self.use_boxes).pack(side="left")
        ttk.Label(row4, text="   Mosaic block size:").pack(side="left")
        ttk.Entry(row4, textvariable=self.mosaic_size, width=5).pack(side="left", padx=4)

        row5 = ttk.Frame(opts); row5.pack(fill="x", **pad)
        ttk.Label(row5, text="Output folder:").pack(side="left")
        ttk.Entry(row5, textvariable=self.output_dir).pack(side="left", fill="x", expand=True, padx=6)
        ttk.Button(row5, text="Browse...", command=self._pick_outdir).pack(side="left")

        action = ttk.Frame(self.root); action.pack(fill="x", padx=12, pady=(4, 6))
        self.start_btn = ttk.Button(action, text="Blur faces", command=self._start)
        self.start_btn.pack(side="left")
        self.stop_btn = ttk.Button(action, text="Stop", command=self._stop, state=DISABLED)
        self.stop_btn.pack(side="left", padx=6)
        ttk.Button(action, text="Open output folder", command=self._open_outdir).pack(side="left", padx=6)
        self.status = ttk.Label(action, text="Idle.", foreground="#444")
        self.status.pack(side="right")

        self.progress = ttk.Progressbar(self.root, mode="determinate", maximum=100)
        self.progress.pack(fill="x", padx=12, pady=(0, 6))

        log_frame = ttk.LabelFrame(self.root, text="Log")
        log_frame.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        self.log = ScrolledText(log_frame, height=10, state=DISABLED, wrap="word")
        self.log.pack(fill="both", expand=True, padx=6, pady=6)

    def _on_drop(self, event):
        for p in parse_dropped(event.data):
            self._add_path(Path(p))
        self._refresh_queue()

    def _pick_files(self):
        paths = filedialog.askopenfilenames(
            title="Pick video file(s)",
            filetypes=[("Videos", " ".join(f"*{e}" for e in sorted(VIDEO_EXTS))), ("All files", "*.*")],
        )
        for p in paths:
            self._add_path(Path(p))
        self._refresh_queue()

    def _pick_outdir(self):
        d = filedialog.askdirectory(initialdir=self.output_dir.get() or str(HERE))
        if d:
            self.output_dir.set(d)

    def _open_outdir(self):
        d = Path(self.output_dir.get())
        d.mkdir(parents=True, exist_ok=True)
        os.startfile(str(d))  # noqa: S606  (Windows-only by design)

    def _add_path(self, p: Path):
        if p.is_dir():
            for child in p.iterdir():
                if child.suffix.lower() in VIDEO_EXTS:
                    self.files.append(child)
        elif p.suffix.lower() in VIDEO_EXTS:
            self.files.append(p)
        else:
            self._log(f"Skipped (not a video): {p}")

    def _clear_queue(self):
        self.files.clear()
        self._refresh_queue()

    def _refresh_queue(self):
        self.listbox.config(state=NORMAL)
        self.listbox.delete("1.0", END)
        for f in self.files:
            self.listbox.insert(END, f"{f}\n")
        self.listbox.config(state=DISABLED)

    def _log(self, msg: str):
        self.log_q.put(msg)

    def _drain_log(self):
        try:
            while True:
                msg = self.log_q.get_nowait()
                self.log.config(state=NORMAL)
                self.log.insert(END, msg.rstrip() + "\n")
                self.log.see(END)
                self.log.config(state=DISABLED)
        except queue.Empty:
            pass
        self.root.after(80, self._drain_log)

    def _start(self):
        if not self.files:
            messagebox.showinfo("Nothing to do", "Add at least one video first.")
            return
        outdir = Path(self.output_dir.get())
        outdir.mkdir(parents=True, exist_ok=True)
        self.stop_flag.clear()
        self.start_btn.config(state=DISABLED)
        self.stop_btn.config(state=NORMAL)
        self.progress["value"] = 0
        self.worker = threading.Thread(target=self._run_jobs, args=(list(self.files), outdir), daemon=True)
        self.worker.start()

    def _stop(self):
        self.stop_flag.set()
        if self.current_proc and self.current_proc.poll() is None:
            try:
                self.current_proc.terminate()
            except Exception:
                pass
        self._log("Stop requested.")
        self.status.config(text="Stopping...")

    def _run_jobs(self, files: list[Path], outdir: Path):
        deface_cmd = find_deface()
        total = len(files)
        for i, f in enumerate(files, 1):
            if self.stop_flag.is_set():
                break
            out = outdir / f"{f.stem}_anonymized{f.suffix}"
            args = list(deface_cmd) + [
                "--thresh", f"{self.thresh.get():.3f}",
                "--mask-scale", f"{self.mask_scale.get():.3f}",
                "--replacewith", self.mode.get(),
                "-o", str(out),
            ]
            if self.keep_audio.get():
                args.append("--keep-audio")
            if self.use_boxes.get():
                args.append("--boxes")
            if self.mode.get() == "mosaic":
                try:
                    int(self.mosaic_size.get())
                    args += ["--mosaicsize", self.mosaic_size.get()]
                except ValueError:
                    pass
            args.append(str(f))

            self.root.after(0, lambda i=i, total=total, name=f.name:
                            self.status.config(text=f"[{i}/{total}] {name}"))
            self._log(f"\n=== [{i}/{total}] {f}")
            self._log(" ".join(f'"{a}"' if " " in a else a for a in args))
            rc = self._run_one(args)
            if rc == 0:
                self._log(f"OK -> {out}")
            elif self.stop_flag.is_set():
                self._log("Stopped.")
                break
            else:
                self._log(f"FAILED (exit {rc})")
            self.root.after(0, lambda v=(i / total) * 100: self.progress.configure(value=v))

        self.root.after(0, self._jobs_done)

    def _run_one(self, args) -> int:
        try:
            self.current_proc = subprocess.Popen(
                args,
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, bufsize=1,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
        except FileNotFoundError as e:
            self._log(f"Could not launch deface: {e}")
            return -1
        assert self.current_proc.stdout is not None
        pct_re = re.compile(r"(\d{1,3})%")
        for line in self.current_proc.stdout:
            line = line.rstrip()
            if not line:
                continue
            self._log(line)
            m = pct_re.search(line)
            if m:
                try:
                    pct = int(m.group(1))
                    self.root.after(0, lambda v=pct: self.progress.configure(value=v))
                except ValueError:
                    pass
        return self.current_proc.wait()

    def _jobs_done(self):
        self.start_btn.config(state=NORMAL)
        self.stop_btn.config(state=DISABLED)
        self.status.config(text="Done.")
        self.progress["value"] = 100


def main():
    if DND_AVAILABLE:
        root = TkinterDnD.Tk()
    else:
        root = Tk()
    try:
        ttk.Style().theme_use("vista")
    except Exception:
        pass
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
