# Media Assets

This directory contains visual assets for the ML-MLOps Portfolio documentation.

## 📺 Main Demo Video

[![YouTube Demo](https://img.shields.io/badge/YouTube-Watch%20Demo-red?style=for-the-badge&logo=youtube)](https://youtu.be/qmw9VlgUcn8)

**Full Portfolio Walkthrough**: [https://youtu.be/qmw9VlgUcn8](https://youtu.be/qmw9VlgUcn8)

---

## Directory Structure

```
media/
├── gifs/                           # Animated demonstrations
│   ├── portfolio-demo.gif          # ✅ Full portfolio overview (time-lapse)
│   ├── bankchurn-preview.gif       # ✅ BankChurn API demo
│   ├── carvision-preview.gif       # ✅ CarVision API demo
│   ├── streamlit-carvision.gif     # ✅ CarVision Streamlit dashboard
│   ├── telecom-preview.gif         # ✅ TelecomAI API demo
│   └── mlflow-demo.gif             # ✅ MLflow experiment tracking
│
├── screenshots/                    # Static screenshots
│   ├── github-actions-ci.PNG       # ✅ CI/CD pipeline passing
│   ├── mlflow-experiments.PNG      # ✅ MLflow experiments view
│   ├── mlflow-metrics.PNG          # ✅ MLflow metrics comparison
│   ├── streamlit-dashboard.PNG     # ✅ CarVision Streamlit UI
│   ├── streamlit-prediction.PNG    # ✅ Price prediction result
│   ├── swagger-bankchurn.PNG       # ✅ BankChurn API docs
│   ├── swagger-carvision.PNG       # ✅ CarVision API docs
│   └── swagger-telecom.PNG         # ✅ TelecomAI API docs
│
├── videos/                         # Source video files
│   ├── portfolio-demo.mp4          # Main portfolio demo
│   ├── bankchurn-preview.mp4       # BankChurn recording
│   ├── carvision-preview.mp4       # CarVision API recording
│   ├── streamlit-carvision.mp4     # Streamlit recording
│   ├── telecom-preview.mp4         # TelecomAI recording
│   └── mlflow-demo.mp4             # MLflow recording
│
└── thumbnails/                     # Video thumbnails (optional)
```

---

## GIF Assets (All Complete ✅)

| GIF | Description | Duration | Used In |
|-----|-------------|----------|---------|
| `portfolio-demo.gif` | Full stack overview (time-lapse) | ~22s | Main README |
| `bankchurn-preview.gif` | BankChurn API prediction | ~9s | BankChurn README |
| `carvision-preview.gif` | CarVision API prediction | ~9s | CarVision README |
| `streamlit-carvision.gif` | Streamlit dashboard tour | ~13s | CarVision README |
| `telecom-preview.gif` | TelecomAI API prediction | ~8s | TelecomAI README |
| `mlflow-demo.gif` | MLflow experiment tracking | ~11s | Main README |

### GIF Generation

GIFs were generated from MP4 source videos using ffmpeg:

```bash
# Time-lapse style (covers full video at 3x speed)
ffmpeg -i video.mp4 \
  -vf "fps=12,setpts=PTS/3,scale=800:600:force_original_aspect_ratio=decrease,pad=800:600:(ow-iw)/2:(oh-ih)/2" \
  output.gif
```

---

## Screenshot Assets (All Complete ✅)

| Screenshot | Description | Used In |
|------------|-------------|---------|
| `github-actions-ci.PNG` | CI/CD pipeline passing | Main README |
| `mlflow-experiments.PNG` | MLflow experiments list | Main README, Project READMEs |
| `mlflow-metrics.PNG` | Metrics comparison view | Documentation |
| `streamlit-dashboard.PNG` | CarVision dashboard overview | CarVision README |
| `streamlit-prediction.PNG` | Price prediction result | CarVision README |
| `swagger-bankchurn.PNG` | BankChurn Swagger UI | BankChurn README |
| `swagger-carvision.PNG` | CarVision Swagger UI | CarVision README |
| `swagger-telecom.PNG` | TelecomAI Swagger UI | TelecomAI README |

---

## Video Assets

Source MP4 files used to generate the GIFs above. These are not committed to Git (use Git LFS or external hosting for large files).

### Main Demo Video

The full portfolio demonstration is hosted on YouTube:

- **Title**: ML/MLOps Portfolio – Production-Ready End-to-End Demo
- **URL**: [https://youtu.be/qmw9VlgUcn8](https://youtu.be/qmw9VlgUcn8)
- **Duration**: ~3 minutes
- **Content**:
  1. Architecture overview
  2. MLflow experiments (9 runs across 3 projects)
  3. BankChurn API demo
  4. CarVision API + Streamlit dashboard
  5. TelecomAI API demo
  6. Docker Compose stack

---

## Usage in Documentation

### Embedding GIFs in README

```markdown
![Portfolio Demo](media/gifs/portfolio-demo.gif)
```

### Embedding Screenshots

```markdown
![MLflow Experiments](media/screenshots/mlflow-experiments.PNG)
```

### Collapsible Demo Section

```markdown
<details>
<summary>🎬 Click to expand demo</summary>

![Demo GIF](media/gifs/bankchurn-preview.gif)

</details>
```

### YouTube Badge

```markdown
[![YouTube Demo](https://img.shields.io/badge/YouTube-Watch%20Demo-red?style=for-the-badge&logo=youtube)](https://youtu.be/qmw9VlgUcn8)
```
