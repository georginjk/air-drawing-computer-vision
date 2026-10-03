# 🎨 Air Drawing Using Hand Gesture and Computer Vision

An interactive, touchless computer vision application built with **Python**, **OpenCV**, and Google's **MediaPipe**. Draw, erase, select colors, and export high-resolution digital artwork directly into Windows Photos in real time using intuitive physical hand gestures captured via your webcam.

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
* **On-Screen Heads-Up Display (HUD):** Real-time feedback showing active mode, selected tool, brush size, and transient notifications.

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
├── src/
│   ├── config.py           # Centralized configuration (constants, colors, paths)
│   ├── hand_tracking.py    # HandDetector class (MediaPipe & vector math)
│   ├── toolbar.py          # Toolbar class (rendering & hit-testing)
│   ├── drawing_canvas.py   # CanvasManager class (persistent canvas, eraser, export)
│   └── main.py             # Application entry point & orchestration
│
├── assets/                 # Backup exported drawings and repository assets
├── screenshots/            # Screenshots and GIFs for project showcase
├── requirements.txt        # Pinned project dependencies
├── .gitignore              # Git ignore rules for virtual environments
├── README.md               # Complete project documentation
└── LICENSE                 # MIT Open-Source License
```

---

## ⚙️ Installation & Setup

### 1. Prerequisites
* Python 3.10 or 3.11 installed
* Git installed
* Built-in or USB webcam

### 2. Clone the Repository
```bash
git clone https://github.com/<your-username>/air-drawing-computer-vision.git
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
| **Touch [SAVE] / 's'** | Save Artwork | Exports drawing to Windows `Pictures/AirDrawing` folder. |
| **Touch [CLR] / 'c'** | Clear Canvas | Wipes canvas clean. |
| **'q'** | Exit | Safely releases webcam hardware and closes window. |

---

## 🎓 Technical & Viva Highlights

* **Why OpenCV uses BGR:** Historical compatibility with Sony and early camera hardware image framebuffers.
* **Why RGB Conversion is needed for MediaPipe:** MediaPipe's deep convolutional models were trained on standard RGB datasets.
* **Why Persistent Canvas is required:** Video feeds refresh 30 times a second; painting on a separate NumPy buffer prevents frames from wiping previous strokes.
* **Vector Cosine Finger Detection:** Measures angle alignment between proximal and distal phalanges:
  $$\cos(\theta) = \frac{\vec{v_1} \cdot \vec{v_2}}{\|\vec{v_1}\| \|\vec{v_2}\|}$$
  Provides rotation-invariant detection across all 360 degrees.
* **2D Pixel Masking:** Evaluates `np.any(canvas > 0, axis=-1)` to prevent individual zero-channels in BGR from turning white when exported.

---

## 📜 License
This project is open-source and licensed under the [MIT License](LICENSE).
