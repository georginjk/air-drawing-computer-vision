# 🎨 Air Drawing Using Hand Gesture and Computer Vision

[![Live Demo](https://img.shields.io/badge/Live_Demo-Try_in_Browser-brightgreen?style=for-the-badge&logo=googlechrome)](https://georginjk.github.io/air-drawing-computer-vision/)
[![Python 3.11](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![OpenCV](https://img.shields.io/badge/OpenCV-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white)](https://opencv.org/)
[![MediaPipe](https://img.shields.io/badge/MediaPipe-Google-00897B?style=for-the-badge)](https://mediapipe.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

An interactive, touchless computer vision application built with **Python**, **OpenCV**, and Google's **MediaPipe**. Draw, erase, select colors, and export high-resolution digital artwork in real time using intuitive physical hand gestures captured via your webcam.

### 🌐 **[Click Here to Launch the Live Web App (No Installation Needed!)](https://georginjk.github.io/air-drawing-computer-vision/)**

---

## 🌟 Key Features

* **Touchless Air Drawing:** Draw continuous, smooth strokes in 3D physical space using your index finger.
* **Smart Gesture Control (Pen Up / Pen Down):**
  * ☝️ **1 Finger Extended (Index):** `DRAW MODE` / `ERASE MODE`
  * ✌️ **2 Fingers Extended (Index + Middle):** `HOVER / PEN UP MODE` (Reposition cursor or select tools without leaving marks)
  * ✊ **Fist / Relaxed Hand:** `STANDBY MODE` (Paused)
* **360° Orientation-Invariant Finger Detection:** Employs Euclidean vector dot-product and cosine angle mathematics to reliably track finger states at any angle, curvature, or distance.
* **Anti-Jitter & Debounced Smoothing:** Built-in Exponential Moving Average (EMA) and 3-frame hysteresis buffer eliminate camera sensor tremors and prevent broken dashed lines.
* **Interactive Dynamic Toolbar:** Touch on-screen buttons to choose from 6 vibrant colors (**Red, Green, Blue, Yellow, Purple, Orange**).
* **Smart Eraser Engine:** Circular stamp eraser that cleanly clears canvas strokes without tearing video feed pixels.
* **Dynamic Brush Sizing:** Cycle between 4 brush thicknesses (`4px`, `8px`, `14px`, `22px`) on the fly.
* **Direct Windows Photos Integration:** Exports finished artwork onto crisp white digital paper directly into your Windows **Pictures/AirDrawing** folder with automated timestamping.
* **Live Web Edition:** Zero-install client-side edition running seamlessly on GitHub Pages via WebGL & WebAssembly.

---

## 🧠 System Architecture & Data Pipeline

```
┌──────────────┐     ┌──────────────┐     ┌────────────────┐
│   Webcam     │ ──> │ OpenCV BGR   │ ──> │ Convert to RGB │
│ Video Stream │     │ Frame Capture│     │ (for MediaPipe)│
└──────────────┘     └──────────────┘     └────────────────┘
                                                   │
                                                   ▼
┌──────────────────┐     ┌────────────────┐     ┌────────────────┐
│ Persistent 2D    │ <── │ 360° Vector    │ <── │ MediaPipe 21   │
│ Canvas Rendering │     │ Angle Math     │     │ Hand Landmarks │
└──────────────────┘     └────────────────┘     └────────────────┘
         │
         ▼
┌──────────────────┐     ┌────────────────┐
│ 2D Pixel Masking │ ──> │ Final Window   │
│ Composite Merging│     │ & HUD Display  │
└──────────────────┘     └────────────────┘
```

---

## 📂 Project Directory Structure

```text
Air-Drawing/
│
├── index.html              # Zero-install web edition for GitHub Pages
├── DOCUMENTATION.md        # Formal B.Tech CSE Academic Project Report
├── requirements.txt        # Pinned project dependencies
├── .gitignore              # Git ignore rules for virtual environments
├── README.md               # Complete project documentation
├── LICENSE                 # MIT Open-Source License
│
├── src/
│   ├── config.py           # Centralized configuration (constants, colors, paths)
│   ├── hand_tracking.py    # HandDetector class (MediaPipe & vector math)
│   ├── toolbar.py          # Toolbar class (rendering & hit-testing)
│   ├── drawing_canvas.py   # CanvasManager class (persistent canvas, eraser, export)
│   └── main.py             # Application entry point & orchestration
│
├── assets/                 # Backup exported drawings and repository assets
└── screenshots/            # Screenshots and GIFs for project showcase
```

---

## ⚙️ Installation & Setup (Desktop App)

### 1. Prerequisites
* Python 3.10 or 3.11 installed
* Git installed
* Built-in or USB webcam

### 2. Clone the Repository
```bash
git clone https://github.com/georginjk/air-drawing-computer-vision.git
cd air-drawing-computer-vision
```

### 3. Create & Activate Virtual Environment
```powershell
# Windows PowerShell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Run the Application
```bash
python src/main.py
```

---

## 🕹️ Controls Cheat-Sheet

| Gesture / Key | Mode | Description |
| :---: | :---: | :--- |
| ☝️ **Index Finger** | `DRAWING` / `ERASING` | Leaves a smooth brush stroke on the canvas. |
| ✌️ **Index + Middle** | `HOVER (PEN UP)` | Lifts the pen; move pointer freely or touch buttons. |
| ✊ **Fist** | `STANDBY` | Pauses tracking. |
| **Touch [SIZE]** | Size Toggle | Cycles brush thickness (4px $\rightarrow$ 8px $\rightarrow$ 14px $\rightarrow$ 22px). |
| **Touch [SAVE] / 's'** | Save Artwork | Exports drawing to Windows `Pictures/AirDrawing` folder (or downloads in web app). |
| **Touch [CLR] / 'c'** | Clear Canvas | Wipes canvas clean. |
| **'q'** | Exit | Safely releases webcam hardware and closes window. |

---

## 📚 Formal Academic Documentation
The full, formal **B.Tech CSE Project Report** (including Abstract, Objectives, Mathematical Formulations, Experimental Benchmarks, and References) is available in [DOCUMENTATION.md](DOCUMENTATION.md).

---

## 📜 License
This project is open-source and licensed under the [MIT License](LICENSE).

**Author:** Georgin J.K.  
*B.Tech Computer Science & Engineering*
