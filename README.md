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
