# 🍉 FINGER NINJA 3D
### ✨ Slice Fruits. Control the Game. No Touch Required.

<p align="center">
  <strong>An AI-powered, webcam-controlled fruit slicing game built with Python, OpenCV, MediaPipe and Pygame.</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/OpenCV-Computer%20Vision-green?logo=opencv" />
  <img src="https://img.shields.io/badge/MediaPipe-Hand%20Tracking-orange" />
  <img src="https://img.shields.io/badge/Pygame-Game%20Engine-yellow" />
  <img src="https://img.shields.io/badge/Status-Under%20Development-brightgreen" />
</p>

---

## 🎮 About The Project

**Finger Ninja 3D** is an interactive computer vision gaming project that transforms your hand into a virtual sword!

Using your laptop's webcam, the system detects and tracks your index finger in real time. Move your finger through flying fruits to slice them, earn points and beat your high score.

No controller. No touchscreen. No keyboard required during gameplay.

Just your hand and your imagination! 🚀

## ✨ Features

- 🖐️ **AI Hand Tracking** – Real-time finger detection using MediaPipe.
- ⚔️ **Virtual Sword** – Control your blade using index finger movements.
- 🍉 **Fruit Slicing** – Slice flying fruits using gesture-based collision detection.
- 💥 **Particle Effects** – Visual effects when fruits are sliced.
- 🎨 **3D-Inspired Graphics** – Gradient backgrounds, glossy fruit shading and animations.
- ❤️ **Lives System** – Avoid missing fruits.
- 💣 **Bomb Detection** – Avoid bombs or face game over.
- 🏆 **Live Scoreboard** – Earn points for every successful slice.

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| Python | Core programming |
| OpenCV | Webcam processing |
| MediaPipe | AI hand landmark detection |
| Pygame | Game development and rendering |
| NumPy | Image processing and numerical operations |

## ⚙️ How It Works

1. Webcam captures live video.
2. MediaPipe detects hand landmarks.
3. The index fingertip position is tracked.
4. Finger movement is mapped to game coordinates.
5. Collision detection identifies fruit slicing.
6. Pygame renders animations, effects and scores.

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/MahiVTech/Finger-Ninja-3D.git
```

### 2. Open the project

```bash
cd Finger-Ninja-3D
```

### 3. Create a virtual environment

```bash
python -m venv venv
```

Activate on Windows:

```bash
venv\Scripts\activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Run the game

```bash
python finger_ninja_3d.py
```

**Note:** Allow webcam access when prompted.

## 🕹️ Controls

| Action | Control |
|---|---|
| Activate virtual blade | Extend index finger |
| Slice fruits | Move index finger |
| Pause / Resume | `P` |
| Restart game | `R` |
| Exit game | `ESC` |

## 📸 Screenshots & Demo

*Screenshots and gameplay demonstration coming soon.*

## 🔮 Future Improvements

- [ ] Realistic 3D fruit models.
- [ ] Advanced fruit-cutting animations.
- [ ] Realistic slicing sound effects.
- [ ] Multiple difficulty levels.
- [ ] Combo and bonus scoring.
- [ ] Global high-score leaderboard.
- [ ] Improved gesture recognition.
- [ ] Multiplayer gameplay.

## 👩‍💻 Developer

**Mahi Varshney**

B.Tech CSE – Artificial Intelligence

GitHub: [@MahiVTech](https://github.com/MahiVTech)

---

<p align="center">
  ⭐ If you like this project, consider giving it a star!
</p>

<p align="center">
  <strong>Built with Python, AI and creativity ❤️</strong>
</p>
