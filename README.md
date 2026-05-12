# Blur Faces Free — Easy Drag-and-Drop Face Blur for Videos

> **Free, offline, local face-blur app for Windows.** Drag a video in, get the same video back with every face automatically blurred. No upload, no cloud, no watermark, no signup.

Automatically detect and blur faces in MP4, MOV, MKV, AVI, WEBM and more — right on your own computer. Powered by the open-source [deface](https://github.com/ORB-HD/deface) face-detection engine, wrapped in a friendly drag-and-drop GUI so anyone can use it.

![Made with Python](https://img.shields.io/badge/Made%20with-Python%203.10%2B-3776AB?logo=python&logoColor=white)
![Platform: Windows](https://img.shields.io/badge/Platform-Windows-blue)
![License: MIT](https://img.shields.io/badge/License-MIT-green)
![Offline](https://img.shields.io/badge/Runs-100%25%20offline-brightgreen)

---

## Why use it

- **Privacy-friendly** — videos never leave your PC. No upload, no account, no tracking.
- **Free forever** — open source, MIT licensed, zero cost, no watermark.
- **Automatic** — no clicking on faces frame-by-frame. The AI finds them for you.
- **Fast** — uses your GPU when available (Intel / AMD / NVIDIA via DirectML).
- **Batch friendly** — drop in 50 videos at once, get 50 blurred videos out.
- **Tunable** — sliders for sensitivity and coverage; choose blur, mosaic/pixelate, or solid block.
- **Audio preserved** — keep-audio is on by default.

Great for: **YouTube creators**, **TikTok / Reels / Shorts**, **journalists**, **researchers**, **GDPR / privacy compliance**, **bodycam footage**, **protest videos**, **classroom recordings**, **dashcam clips**, **real-estate walkthroughs**, anything where you need to anonymize people.

---

## Quick start (3 steps)

### 1. Install Python (one time)

Download Python 3.10 or newer from **[python.org/downloads](https://www.python.org/downloads/)**.

> **Important:** during install, tick **"Add Python to PATH"** on the first screen. If you forget, just re-run the installer and choose *Modify → Add to PATH*.

### 2. Download this app

- Click the green **Code → Download ZIP** button at the top of this page
- Right-click the ZIP → **Extract All**

(Or `git clone https://github.com/Teylersf/blurfacefree.git` if you use git.)

### 3. Run the installer, then open the app

- Double-click **`install.bat`** — installs the face-detection engine. Takes ~1 minute.
- Double-click **`Blur Faces.bat`** — opens the drag-and-drop window.

That's it. Drag a video onto the big drop zone, click **Blur faces**, find the result in the `output\` folder.

---

## How to use

1. Drag one or more videos onto the drop zone (or click **Add files...**).
2. Pick a mode:
   - **blur** — smooth Gaussian blur over each face (default)
   - **mosaic** — pixelated / mosaic censor
   - **solid** — solid black box
   - **none** — just draw detection ellipses (debug)
3. Adjust sliders if needed:
   - **Detection threshold** — lower = more aggressive (catches more faces, more false positives)
   - **Mask size** — bigger = more coverage around each face
4. Click **Blur faces**. Watch the log + progress bar.
5. Open the **output** folder to grab your anonymized videos.

### Supported video formats

`.mp4`  `.mov`  `.mkv`  `.avi`  `.webm`  `.m4v`  `.mpg`  `.mpeg`  `.wmv`  `.flv`

Output is always `.mp4` H.264 by default (works everywhere — YouTube, Premiere, Resolve, browsers).

---

## All options explained

| Option | What it does | When to change |
|---|---|---|
| **Mode** | Blur, mosaic, solid black, or none | Mosaic = TV-news censor look. Solid = strongest anonymization. |
| **Detection threshold** | How confident the AI must be before calling something a face. Default 0.2 | Lower to 0.1 if it's missing small / angled / blurry faces. Raise to 0.3+ if random objects get blurred. |
| **Mask size** | How much the blur extends around the detected face. Default 1.3× | Raise to 1.6–2.0 if hair / ears / chin keep peeking through. |
| **Keep audio** | Copy the original audio track through unchanged. **On by default.** | Turn off only if you want a silent output. |
| **Use rectangles** | Use a box mask instead of an ellipse | Boxes look more "official redaction"; ellipses look more natural. |
| **Mosaic block size** | Pixel size of mosaic squares | Bigger = chunkier pixels (more censored look). |
| **Output folder** | Where the blurred videos are written | Anywhere you like. Defaults to `.\output\`. |

---

## Command line (power users)

The GUI is a wrapper around the excellent [`deface`](https://github.com/ORB-HD/deface) CLI. After `install.bat` you can also run it from PowerShell:

```powershell
deface "C:\path\to\video.mp4" --keep-audio
```

Live webcam demo:

```powershell
deface cam
```

Full options: `deface --help`.

The `blur.bat` script in this repo is a simple drag-onto-it CLI shortcut; `blur-folder.bat` processes everything in the `input\` folder.

---

## Troubleshooting

<details>
<summary><b>"Python is not recognized" when I run install.bat</b></summary>

Python isn't on your PATH. Re-run the Python installer from python.org and tick **"Add Python to PATH"** on the first screen, or use the *Modify* button to add it after the fact.
</details>

<details>
<summary><b>The GUI opens but the drop zone says "Drag-drop unavailable"</b></summary>

The `tkinterdnd2` package didn't install correctly. In PowerShell:

```powershell
python -m pip install --upgrade tkinterdnd2
```

You can still use the **Add files...** button in the meantime.
</details>

<details>
<summary><b>It misses faces (small, blurry, side-profile, sunglasses)</b></summary>

Lower the detection threshold to **0.10** and raise the mask size to **1.7–2.0**. If you still see issues, switch to **mosaic** mode with a larger block size — pixelation forgives small detection errors.
</details>

<details>
<summary><b>Random non-face things are getting blurred</b></summary>

Raise the detection threshold to **0.30–0.40**.
</details>

<details>
<summary><b>It's slow on my machine</b></summary>

- Make sure GPU acceleration installed (`install.bat` does this automatically — look for `onnxruntime-directml` in the log).
- Try lowering the resolution the detector sees: command-line option `--scale 640x360` makes detection much faster with minimal accuracy loss on HD/4K videos.
- Close other GPU-heavy apps.
</details>

<details>
<summary><b>The first run is downloading something — is that OK?</b></summary>

Yes. On the very first run, deface downloads a ~2 MB face-detection model (CenterFace). After that, everything is 100% offline.
</details>

<details>
<summary><b>Can I run this on Mac or Linux?</b></summary>

The underlying engine ([deface](https://github.com/ORB-HD/deface)) is cross-platform. The Python GUI script also works on Mac/Linux — but the `.bat` launchers are Windows-only. On Mac/Linux you can run `python blur_gui.pyw` directly after `pip install -r requirements.txt`.
</details>

---

## How it works (short version)

1. The app launches the [deface](https://github.com/ORB-HD/deface) command on each video you drop in.
2. deface runs the **CenterFace** neural network (a tiny ~2 MB ONNX model) on every frame.
3. Each detected face region gets blurred / mosaiced / blacked-out.
4. Frames are re-encoded with ffmpeg, audio is muxed back in, and you get a new MP4.

No data leaves your machine. No telemetry. No accounts.

---

## Credits

This project is a friendly GUI wrapper. **All the heavy lifting is done by these excellent open-source projects:**

- **[deface](https://github.com/ORB-HD/deface)** by [ORB-HD](https://github.com/ORB-HD) — the actual face-detection-and-anonymization engine. Please star their repo too.
- **[CenterFace](https://github.com/Star-Clouds/CenterFace)** — the underlying face-detection model.
- **[ONNX Runtime](https://onnxruntime.ai/)** — fast neural-network inference.
- **[ffmpeg](https://ffmpeg.org/)** — video encoding/decoding (via [imageio-ffmpeg](https://github.com/imageio/imageio-ffmpeg)).
- **[tkinterdnd2](https://github.com/pmgagne/tkinterdnd2)** — drag-and-drop in Tkinter.

If you use this for anything serious, please support those upstream projects.

---

## License

[MIT](LICENSE) — do whatever you want with it, just don't sue me. The underlying [deface](https://github.com/ORB-HD/deface) is also MIT licensed.

---

## Keywords

*Free face blur for video. Blur faces in video Windows. Automatic face blur. Anonymize video faces. Hide faces in video free. Face blur software open source. Pixelate faces in video. Censor faces in video. GDPR video anonymization. Privacy face blur tool. Offline face blur. Face blur AI free. YouTube face blur free. Video redaction tool free. Best free face blur software. Blur faces without watermark. Local face blur app. Drag and drop face blur.*
