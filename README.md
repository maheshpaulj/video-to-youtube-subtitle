<p align="center">
  <img src="icon.png" width="96" alt="App Icon" />

  <h1>YouTube Subtitle Video Player 🎬📝</h1>

  <p><strong>A small GUI tool that converts video frames into stylized ASCII-like subtitles (YouTube Timed Text `.ytt`).</strong></p>

  <p>
    <img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License" />
    <img src="https://img.shields.io/badge/python-3.10%2B-blue.svg" alt="Python" />
    <img src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg" alt="PRs welcome" />
    <img src="https://img.shields.io/badge/contributions-welcome-blueviolet.svg" alt="Contributions welcome" />
  </p>
</p>

---

## Features ✅

- Generates `.ytt` subtitles from a video by converting frames into ASCII or block visuals.
- Supports color, grayscale, and pure B&W modes.
- Adjustable resolution width, FPS limit, compression, and color depth.
- Lightweight GUI based on `customtkinter`.

## Quick Start ⚡

### Requirements

- Python 3.10+
- pip packages:
  - customtkinter
  - opencv-python
  - pillow
  - numpy

Install dependencies:

```bash
pip install customtkinter opencv-python pillow numpy
```

### Run

```bash
python main.py
```

1. Click **Select Video** and choose a video file (mp4/avi/mov/mkv).
2. Adjust controls (Resolution Width, FPS limit, Compression, Color Depth, Visual Style).
3. Click **GENERATE SUBTITLE FILE** and save the resulting `.ytt` file.

> Tip: The GUI shows progress and number of pens (colors) while processing.

## Project Structure 🔧

- `main.py` — Main application and conversion logic
- `inputs/` — Example/fixture subtitle files and outputs

## Troubleshooting ⚠️

- If you see import errors, ensure all dependencies are installed with `pip`.
- On Windows, make sure OpenCV can access your video codecs.

## Contributing 🤝

We welcome contributions! Please follow these steps if you'd like to help:

1. **Fork** the repository and create a branch (e.g., `feature/your-feature`).
2. **Open an issue** to discuss larger or design-heavy changes first.
3. Make small, focused commits and open a **pull request (PR)**.
4. Ensure code follows style, add tests if applicable, and update documentation.

If you're new, look for issues labeled `good first issue`. If you'd like, I can add a `CONTRIBUTING.md` and issue/PR templates to make contributions easier.

## License

MIT

---

Made by **Mahesh Paul J** — enjoy converting your videos into subtitle art! ✨
