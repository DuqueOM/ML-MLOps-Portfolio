# Media Assets Directory

This directory contains all visual assets for the portfolio documentation.

## Directory Structure

```
media/
├── videos/                    # Demo videos (MP4, WebM)
│   ├── bankchurn-demo.mp4
│   ├── carvision-demo.mp4
│   └── telecom-demo.mp4
├── gifs/                      # Animated GIFs for README embeds
│   ├── bankchurn-preview.gif
│   ├── carvision-preview.gif
│   └── telecom-preview.gif
├── screenshots/               # Static screenshots
│   ├── ci-pipeline-passing.png
│   ├── mlflow-dashboard.png
│   └── ...
└── thumbnails/                # Video thumbnails
    ├── bankchurn-thumb.png
    ├── carvision-thumb.png
    └── telecom-thumb.png
```

---

## 🎬 VIDEO CREATION GUIDE

### Recommended Video Specs
- **Resolution**: 1920x1080 (1080p)
- **Duration**: 2-3 minutes per project
- **Format**: MP4 (H.264) for best compatibility
- **Audio**: Clear narration, minimal background music

### Video Script Template (per project)

```
[0:00 - 0:07] INTRO
- Show: Project title slide with logo
- Say: "This is [Project Name] — [one-liner problem statement]"

[0:07 - 0:25] ARCHITECTURE (30 seconds)
- Show: Architecture diagram (from docs/)
- Say: "Data flows from [source] through [ETL] to [model] to [endpoint]"

[0:25 - 0:55] CI/CD IN ACTION
- Show: GitHub Actions workflow running
- Highlight: Green checkmarks, test coverage badge
- Say: "Every commit triggers automated tests and security scans"

[0:55 - 1:35] LIVE DEMO
- Show: API call (Swagger UI or curl)
- Show: Response with prediction
- Show: Dashboard/UI if applicable
- Say: "Here's a real prediction with [X ms] latency"

[1:35 - 2:00] RESULTS & VALUE
- Show: Metrics table (AUC, RMSE, etc.)
- Say: "This translates to [business impact]"

[2:00 - 2:15] CALL TO ACTION
- Show: GitHub repo link, contact info
- Say: "Clone the repo and try: docker-compose up"
```

---

## 🎞️ GIF CREATION GUIDE

### Recommended GIF Specs
- **Duration**: 6-8 seconds (loop smoothly)
- **Resolution**: 800x450 (16:9 aspect ratio)
- **File size**: < 5MB for fast loading
- **Frame rate**: 15-20 fps

### What to Capture for Each GIF

| Project | Key Action to Record |
|---------|----------------------|
| BankChurn | API prediction call → response with churn probability |
| CarVision | Streamlit dashboard → price prediction with gauge |
| TelecomAI | API call → plan recommendation response |

### Tools for GIF Creation
- **macOS**: `brew install gifski` (high quality)
- **Linux**: `ffmpeg -i video.mp4 -vf "fps=15,scale=800:-1" output.gif`
- **Cross-platform**: [Kap](https://getkap.co/), [ScreenToGif](https://www.screentogif.com/)

---

## 📸 SCREENSHOT GUIDE

### Required Screenshots

1. **CI Pipeline Passing**
   - File: `screenshots/ci-pipeline-passing.png`
   - Content: GitHub Actions workflow with all green checkmarks

2. **Coverage Report**
   - File: `screenshots/coverage-report.png`
   - Content: pytest-cov output showing >70% coverage

3. **MLflow Dashboard**
   - File: `screenshots/mlflow-dashboard.png`
   - Content: Experiment tracking with runs and metrics

4. **Docker Build**
   - File: `screenshots/docker-build-success.png`
   - Content: Terminal showing successful image build

5. **API Swagger UI**
   - Files: `screenshots/bankchurn-api.png`, `screenshots/carvision-api.png`, `screenshots/telecom-api.png`
   - Content: FastAPI auto-generated docs

6. **Dashboard UI** (CarVision)
   - File: `screenshots/carvision-dashboard.png`
   - Content: Streamlit dashboard with charts and predictions

---

## 🖼️ THUMBNAIL GUIDE

### Specs
- **Size**: 1280x720 (YouTube standard)
- **Format**: PNG or JPG

### Design Elements
- Project name prominently displayed
- Key tech logos (Python, Docker, MLflow)
- A preview of the main interface/output

---

## 📁 FILE NAMING CONVENTION

```
[project-name]-[asset-type].[ext]

Examples:
- bankchurn-demo.mp4
- bankchurn-preview.gif
- bankchurn-api-screenshot.png
- bankchurn-thumb.png
```

---

## ⬆️ UPLOAD ALTERNATIVES

If files are too large for GitHub:

1. **YouTube** (Unlisted)
   - Upload to YouTube as unlisted
   - Embed link in README

2. **Google Drive**
   - Set sharing to "Anyone with link"
   - Use format: `https://drive.google.com/file/d/FILE_ID/preview`

3. **GitHub Releases**
   - Create a release and attach video files
   - Link to release page in README

---

## 📝 TODO: Assets to Create

- [ ] `videos/bankchurn-demo.mp4` — **[RECORD AND UPLOAD]**
- [ ] `videos/carvision-demo.mp4` — **[RECORD AND UPLOAD]**
- [ ] `videos/telecom-demo.mp4` — **[RECORD AND UPLOAD]**
- [ ] `gifs/bankchurn-preview.gif` — **[CREATE FROM VIDEO]**
- [ ] `gifs/carvision-preview.gif` — **[CREATE FROM VIDEO]**
- [ ] `gifs/telecom-preview.gif` — **[CREATE FROM VIDEO]**
- [ ] `screenshots/ci-pipeline-passing.png` — **[CAPTURE FROM GITHUB ACTIONS]**
- [ ] `screenshots/coverage-report.png` — **[CAPTURE AFTER RUNNING TESTS]**
- [ ] `screenshots/mlflow-dashboard.png` — **[CAPTURE AFTER TRAINING RUN]**
- [ ] `thumbnails/bankchurn-thumb.png` — **[DESIGN OR CAPTURE]**
- [ ] `thumbnails/carvision-thumb.png` — **[DESIGN OR CAPTURE]**
- [ ] `thumbnails/telecom-thumb.png` — **[DESIGN OR CAPTURE]**
