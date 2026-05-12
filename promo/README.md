# Promo video (Remotion)

A 60-second, 9:16 (1080×1920) YouTube Shorts promo for Blur Faces Free, built with [Remotion](https://www.remotion.dev/).

## Scenes

| Time | Scene | What it does |
|---|---|---|
| 0:00 – 0:03 | **Hook** | Pulsing "face" → blur ramp → CENSORED stamp slams in → "blurring faces shouldn't suck." |
| 0:03 – 0:08 | **Pain** | Quick-cut pain points (subscriptions, cloud uploads, watermarks) slashed with red |
| 0:08 – 0:13 | **Reveal** | Brand drop: **blur faces.** + tagline `free. local. no cap.` |
| 0:13 – 0:30 | **Demo** | Mock app window: drop-zone, MP4 file flies in, progress bar fills, before/after face reveal |
| 0:30 – 0:42 | **Features** | Six benefit cards spring in: 100% local · GPU fast · batch mode · Win + Mac · free forever · drag & drop |
| 0:42 – 0:50 | **Install** | Three-step install (Python → install script → drag a vid) |
| 0:50 – 1:00 | **CTA** | `github.com/Teylersf/blurfacefree` pulse-glows + `freefaceblur.com` Pro callout |

## Build it yourself

```bash
cd promo
npm install
npm run build         # renders to out/promo.mp4
# or
npm run dev           # opens the Remotion Studio for live editing
```

Output: `out/promo.mp4` (H.264, 1080×1920, 30fps, ~60s).

## Editing scenes

All scenes live in `src/Promo.tsx`. Theme colors and font stacks are in `src/theme.ts`. Each scene is a normal React component; the timing constants at the top of `Promo.tsx` (`T_HOOK`, `T_PAIN`, etc.) control when each scene starts.

For a live preview while editing:

```bash
npm run dev
```

This opens the Remotion Studio in your browser with hot reload.

## Suggested YouTube Shorts metadata

**Title (60 char limit):**
> Free Face Blur for Videos — Local, Offline, No Watermark (Win + Mac)

**Description:**
```
Blur Faces Free — drag, drop, anonymize.
100% local. No upload. No watermark. No subscription. Forever free.

⬇️ GitHub: https://github.com/Teylersf/blurfacefree
🌐 Pro / cloud: https://freefaceblur.com

Works on Windows + macOS. Powered by deface + ONNX.

#faceblur #anonymize #privacy #videoediting #opensource #python #shorts
```

**Tags:** face blur, blur faces in video, anonymize video, free face blur, privacy, GDPR, video privacy, open source, Windows, macOS, no watermark, offline
