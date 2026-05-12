"""Drag-and-drop GUI wrapper for deface. Dark-mode redesign."""
import os
import queue
import re
import shutil
import subprocess
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import (
    BooleanVar, DoubleVar, StringVar, Tk,
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

WIN_TITLE = "blur faces - free, local, no cap"

# theme
BG = "#0b0b14"
CARD = "#161624"
CARD_HI = "#1f1f30"
BORDER = "#2a2a40"
TEXT = "#f5f5fa"
DIM = "#8a8aa3"
ACCENT = "#a78bfa"
ACCENT_HOT = "#c4a8ff"
PINK = "#ec4899"
GREEN = "#34d399"
YELLOW = "#fbbf24"
RED = "#f87171"

F_TITLE = ("Segoe UI Variable Display", 24, "bold")
F_SUB = ("Segoe UI Variable", 11)
F_HEAD = ("Segoe UI Variable Display", 11, "bold")
F_BODY = ("Segoe UI Variable", 11)
F_BTN = ("Segoe UI Variable Display", 11, "bold")
F_BIG_BTN = ("Segoe UI Variable Display", 13, "bold")
F_MONO = ("Cascadia Mono", 10)
F_DROP = ("Segoe UI Variable Display", 14, "bold")


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


def make_card(parent, **kw):
    return tk.Frame(parent, bg=CARD, highlightthickness=1,
                    highlightbackground=BORDER, highlightcolor=BORDER, **kw)


def make_btn(parent, text, command, *, kind="primary", **kw):
    colors = {
        "primary": (ACCENT, "#0b0b14", ACCENT_HOT),
        "ghost":   (CARD_HI, TEXT, BORDER),
        "danger":  (RED, "#0b0b14", "#fca5a5"),
        "ok":      (GREEN, "#0b0b14", "#6ee7b7"),
    }[kind]
    bg_c, fg_c, hover = colors
    btn = tk.Button(
        parent, text=text, command=command,
        bg=bg_c, fg=fg_c, activebackground=hover, activeforeground=fg_c,
        relief="flat", bd=0, padx=18, pady=9, cursor="hand2",
        font=kw.pop("font", F_BTN), **kw,
    )
    btn.bind("<Enter>", lambda _e: btn.configure(bg=hover))
    btn.bind("<Leave>", lambda _e: btn.configure(bg=bg_c))
    btn._base_bg = bg_c
    return btn


class App:
    def __init__(self, root):
        self.root = root
        root.title(WIN_TITLE)
        root.configure(bg=BG)
        root.geometry("820x960")
        root.minsize(700, 720)

        style = ttk.Style()
        try:
            style.theme_use("clam")
        except Exception:
            pass
        style.configure("Dark.Horizontal.TProgressbar",
                        background=ACCENT, troughcolor=CARD_HI,
                        bordercolor=BORDER, lightcolor=ACCENT, darkcolor=ACCENT)
        style.configure("Dark.Horizontal.TScale",
                        background=CARD, troughcolor=CARD_HI,
                        bordercolor=BORDER, lightcolor=ACCENT, darkcolor=ACCENT)
        style.map("Dark.Horizontal.TScale",
                  background=[("active", ACCENT_HOT)])

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
        root = self.root

        # ── header ──
        header = tk.Frame(root, bg=BG)
        header.pack(fill="x", padx=22, pady=(20, 8))
        tk.Label(header, text="blur faces.", bg=BG, fg=TEXT,
                 font=F_TITLE).pack(side="left")
        tk.Label(header, text="  free  •  offline  •  no upload",
                 bg=BG, fg=ACCENT, font=F_HEAD).pack(side="left", pady=(14, 0))

        tk.Label(root, text="drag a video. blur every face. that's it.",
                 bg=BG, fg=DIM, font=F_SUB).pack(anchor="w", padx=24, pady=(0, 14))

        # ── drop zone ──
        drop_outer = tk.Frame(root, bg=ACCENT, padx=2, pady=2)
        drop_outer.pack(fill="x", padx=22, pady=(0, 10))
        drop = tk.Frame(drop_outer, bg=CARD)
        drop.pack(fill="both", expand=True)
        self.drop_label = tk.Label(
            drop,
            text=("drop ur vids here\n— or click 'add files' below —"
                  if DND_AVAILABLE else
                  "drag-drop unavailable — use 'add files' below"),
            bg=CARD, fg=TEXT, font=F_DROP,
            anchor="center", justify="center", pady=34,
        )
        self.drop_label.pack(fill="both", expand=True)
        if DND_AVAILABLE:
            for w in (drop, self.drop_label, drop_outer):
                w.drop_target_register(DND_FILES)
                w.dnd_bind("<<Drop>>", self._on_drop)

        # ── queue card ──
        q_card = make_card(root)
        q_card.pack(fill="x", padx=22, pady=8)
        tk.Label(q_card, text="queue", bg=CARD, fg=PINK,
                 font=F_HEAD).pack(anchor="w", padx=14, pady=(10, 4))
        self.listbox = ScrolledText(
            q_card, height=4, wrap="none",
            bg=CARD_HI, fg=TEXT, insertbackground=TEXT,
            relief="flat", bd=0, font=F_MONO,
            highlightthickness=1, highlightbackground=BORDER,
        )
        self.listbox.pack(fill="x", padx=14, pady=(0, 8))
        self.listbox.configure(state=DISABLED)

        qbtn = tk.Frame(q_card, bg=CARD)
        qbtn.pack(fill="x", padx=12, pady=(0, 12))
        make_btn(qbtn, "+ add files", self._pick_files, kind="ghost").pack(side="left", padx=4)
        make_btn(qbtn, "clear", self._clear_queue, kind="ghost").pack(side="left", padx=4)

        # ── options card ──
        opts = make_card(root)
        opts.pack(fill="x", padx=22, pady=8)
        tk.Label(opts, text="vibe check", bg=CARD, fg=PINK,
                 font=F_HEAD).pack(anchor="w", padx=14, pady=(10, 6))

        # mode pills
        modes = tk.Frame(opts, bg=CARD)
        modes.pack(fill="x", padx=12, pady=(0, 8))
        tk.Label(modes, text="mode:", bg=CARD, fg=DIM, font=F_BODY).pack(side="left", padx=(4, 8))
        for v, label in (("blur", "🫧 blur"), ("mosaic", "🟪 mosaic"),
                         ("solid", "⬛ solid"), ("none", "👀 detect")):
            rb = tk.Radiobutton(
                modes, text=label, variable=self.mode, value=v,
                indicatoron=False, bd=0, padx=14, pady=7,
                bg=CARD_HI, fg=TEXT,
                selectcolor=ACCENT,
                activebackground=ACCENT_HOT, activeforeground="#0b0b14",
                font=F_BTN, relief="flat", cursor="hand2",
                tristatevalue="x_unused",
            )
            rb.pack(side="left", padx=3)

        # toggles
        toggles = tk.Frame(opts, bg=CARD)
        toggles.pack(fill="x", padx=12, pady=4)
        for var, label in (
            (self.keep_audio, "🔊 keep audio"),
            (self.use_boxes, "▭ box masks"),
        ):
            cb = tk.Checkbutton(
                toggles, text=label, variable=var,
                bg=CARD, fg=TEXT, selectcolor=CARD_HI,
                activebackground=CARD, activeforeground=ACCENT,
                font=F_BODY, bd=0, relief="flat", cursor="hand2",
            )
            cb.pack(side="left", padx=8)

        # sliders
        for label, var, lo, hi, fmt in (
            ("face detection sensitivity", self.thresh, 0.05, 0.6, "{:.2f}"),
            ("blur cushion (how much around the face)", self.mask_scale, 1.0, 2.5, "{:.2f}"),
        ):
            row = tk.Frame(opts, bg=CARD)
            row.pack(fill="x", padx=14, pady=4)
            tk.Label(row, text=label, bg=CARD, fg=DIM, font=F_BODY).pack(side="left")
            value_lbl = tk.Label(row, text=fmt.format(var.get()), width=6,
                                 bg=CARD, fg=ACCENT, font=F_HEAD)
            value_lbl.pack(side="right")
            ttk.Scale(row, from_=lo, to=hi, variable=var, orient="horizontal",
                      length=220, style="Dark.Horizontal.TScale").pack(side="right", padx=10)
            var.trace_add("write", lambda *_x, lbl=value_lbl, v=var, f=fmt: lbl.config(text=f.format(v.get())))

        # mosaic size + output folder
        misc = tk.Frame(opts, bg=CARD)
        misc.pack(fill="x", padx=14, pady=(8, 4))
        tk.Label(misc, text="mosaic block size:", bg=CARD, fg=DIM, font=F_BODY).pack(side="left")
        tk.Entry(misc, textvariable=self.mosaic_size, width=5,
                 bg=CARD_HI, fg=TEXT, insertbackground=TEXT,
                 relief="flat", font=F_BODY,
                 highlightthickness=1, highlightbackground=BORDER,
                 highlightcolor=ACCENT).pack(side="left", padx=8)

        outrow = tk.Frame(opts, bg=CARD)
        outrow.pack(fill="x", padx=14, pady=(6, 14))
        tk.Label(outrow, text="output folder:", bg=CARD, fg=DIM,
                 font=F_BODY).pack(side="left")
        tk.Entry(outrow, textvariable=self.output_dir,
                 bg=CARD_HI, fg=TEXT, insertbackground=TEXT,
                 relief="flat", font=F_BODY,
                 highlightthickness=1, highlightbackground=BORDER,
                 highlightcolor=ACCENT).pack(side="left", fill="x", expand=True, padx=8)
        make_btn(outrow, "browse", self._pick_outdir, kind="ghost").pack(side="left")

        # ── action bar ──
        action = tk.Frame(root, bg=BG)
        action.pack(fill="x", padx=22, pady=(6, 4))
        self.start_btn = make_btn(action, "✨  blur it  ✨", self._start,
                                  kind="primary", font=F_BIG_BTN)
        self.start_btn.pack(side="left")
        self.stop_btn = make_btn(action, "stop", self._stop, kind="danger")
        self.stop_btn.pack(side="left", padx=8)
        self.stop_btn.configure(state=DISABLED)
        make_btn(action, "open output", self._open_outdir, kind="ghost").pack(side="left", padx=4)
        self.status = tk.Label(action, text="idle. drop a vid 👇", bg=BG, fg=DIM, font=F_BODY)
        self.status.pack(side="right")

        # progress
        self.progress = ttk.Progressbar(root, mode="determinate", maximum=100,
                                        style="Dark.Horizontal.TProgressbar")
        self.progress.pack(fill="x", padx=22, pady=(4, 8))

        # log
        log_card = make_card(root)
        log_card.pack(fill="both", expand=True, padx=22, pady=(4, 18))
        tk.Label(log_card, text="what's happening", bg=CARD, fg=PINK,
                 font=F_HEAD).pack(anchor="w", padx=14, pady=(10, 4))
        self.log = ScrolledText(
            log_card, height=10, wrap="word",
            bg=CARD_HI, fg=TEXT, insertbackground=TEXT,
            relief="flat", bd=0, font=F_MONO,
            highlightthickness=1, highlightbackground=BORDER,
        )
        self.log.pack(fill="both", expand=True, padx=14, pady=(0, 12))
        self.log.configure(state=DISABLED)

    # ── interactions ──
    def _on_drop(self, event):
        for p in parse_dropped(event.data):
            self._add_path(Path(p))
        self._refresh_queue()

    def _pick_files(self):
        paths = filedialog.askopenfilenames(
            title="pick a video",
            filetypes=[("videos", " ".join(f"*{e}" for e in sorted(VIDEO_EXTS))), ("all files", "*.*")],
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
        os.startfile(str(d))  # noqa: S606

    def _add_path(self, p: Path):
        if p.is_dir():
            for child in p.iterdir():
                if child.suffix.lower() in VIDEO_EXTS:
                    self.files.append(child)
        elif p.suffix.lower() in VIDEO_EXTS:
            self.files.append(p)
        else:
            self._log(f"skipped (not a video): {p}")

    def _clear_queue(self):
        self.files.clear()
        self._refresh_queue()

    def _refresh_queue(self):
        self.listbox.config(state=NORMAL)
        self.listbox.delete("1.0", END)
        for f in self.files:
            self.listbox.insert(END, f"{f}\n")
        self.listbox.config(state=DISABLED)
        self.status.config(text=f"{len(self.files)} in queue" if self.files else "idle. drop a vid 👇")

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
            messagebox.showinfo("nothing here", "add at least one video first ✨")
            return
        outdir = Path(self.output_dir.get())
        outdir.mkdir(parents=True, exist_ok=True)
        self.stop_flag.clear()
        self.start_btn.config(state=DISABLED)
        self.stop_btn.config(state=NORMAL)
        self.progress["value"] = 0
        self.worker = threading.Thread(target=self._run_jobs,
                                       args=(list(self.files), outdir), daemon=True)
        self.worker.start()

    def _stop(self):
        self.stop_flag.set()
        if self.current_proc and self.current_proc.poll() is None:
            try:
                self.current_proc.terminate()
            except Exception:
                pass
        self._log("stop requested.")
        self.status.config(text="stopping...")

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
                            self.status.config(text=f"cooking [{i}/{total}] {name}"))
            self._log(f"\n=== [{i}/{total}] {f}")
            self._log(" ".join(f'"{a}"' if " " in a else a for a in args))
            rc = self._run_one(args)
            if rc == 0:
                self._log(f"ok -> {out}")
            elif self.stop_flag.is_set():
                self._log("stopped.")
                break
            else:
                self._log(f"failed (exit {rc})")
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
            self._log(f"could not launch deface: {e}")
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
        self.status.config(text="done ✨")
        self.progress["value"] = 100


def main():
    if DND_AVAILABLE:
        root = TkinterDnD.Tk()
    else:
        root = Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
