# 🔍 Spot the Difference: AI Game & Closed-Loop Evaluation Framework

A self-auditing AI application built with **Streamlit**, **OpenAI**, and **Pillow**, featuring a closed-loop evaluation workflow, automated telemetry logging, an algorithmic auto-grader, and an interactive evaluation dashboard.

Designed from an **Eval PM perspective**, this project bridges the gap between raw player interaction and system improvement by auditing hit-detection accuracy and measuring player friction in real-time.

---

## 🚀 Key Features

* **AI-Generated Levels:** Dynamically generates base and altered images using OpenAI APIs based on custom text prompts.
* **Closed-Loop Telemetry Logging:** Automatically captures player interactions—tracking successful finds (hits) and incorrect clicks (misses) into `eval_logs.json`.
* **Automated Auto-Grader Agent (`auto_grader.py`):** Programmatically computes a normalized **Playability Score (0-100)** and diagnoses system health based on player friction.
* **Hit-Detection Accuracy Auditing:** Cross-references click coordinates against a computer vision difference heatmap (`ImageChops.difference`) to isolate **False Negatives (Code Errors)** from **True Misses (User Errors)**.
* **Interactive Streamlit Eval Dashboard (`eval_dashboard.py`):** Provides a visual session review with high-contrast coordinate overlays, historical trend analysis, and actionable agent recommendations.

---

## 📂 Project Architecture

```text
games/
├── app.py              # Main Streamlit gameplay loop & telemetry recorder
├── auto_grader.py      # Backend evaluation engine & accuracy auditor
├── eval_dashboard.py   # Streamlit evaluation dashboard & visual audit tool
└── eval_logs.json      # Structured session telemetry database

📊 Evaluation Metrics Explained
Playability Score (0-100): Calculated using a friction ratio (Misses / Target Diffs). It measures how frustrating or balanced a level design is for the player.

Hit-Detection Accuracy (%): Evaluates code precision by determining whether a miss was a true user error or a code failure (bounding box too tight / False Negative).

System Health Status: Automatically categorizes system performance into Healthy, Moderate Friction, or High Friction, outputting concrete tuning actions for wrappers and prompts.

⚙️ Getting Started & Running Locally
1. Prerequisites
Make sure you have Python installed along with the required packages:

Bash
pip install streamlit openai pandas pillow
2. Set Your OpenAI API Key
Export your OpenAI API key in your terminal session:

Bash
export OPENAI_API_KEY="your-actual-api-key-here"
3. Run the Game (app.py)
Launch the gameplay application to generate levels and record telemetry:

Bash
streamlit run app.py
4. Run the Evaluation Dashboard (eval_dashboard.py)
Launch the dashboard in a separate terminal window to audit past sessions, view accuracy metrics, and check system recommendations:

Bash
streamlit run eval_dashboard.py
🛠️ The Evaluation Loop
Play: User plays the game, generating telemetry logs (eval_logs.json).

Audit: The auto-grader ingests logs and runs computer vision heatmaps to check for code vs. user errors.

Inspect: The Eval PM reviews session heatmaps and metric trends via the Streamlit dashboard.

Iterate: Actionable recommendations drive adjustments to code parameters (hitbox padding) or prompt engineering strategies.

## 📸 App Preview & Evaluation Workflow

### 1. The Gameplay Interface (`app.py`)
Players interact with side-by-side AI-generated images, clicking differences while telemetry tracks hits and misses in real-time[cite: 1].
![Spot the Difference Gameplay Interface](assets/gameplay.png)

---

### 2. The Evaluation Dashboard (`eval_dashboard.py`)
An overview of session health, playability scores, and agent improvement recommendations[cite: 2].
![Eval Dashboard Metrics and Recommendations](assets/dashboard-metrics.png)

---

### 3. Visual Session Review & Accuracy Audit
The auto-grader cross-references click telemetry against computer vision difference heatmaps to isolate code errors (false negatives) from user errors[cite: 3].
![Visual Audit and Hit-Detection Accuracy](assets/dashboard-audit.png)
