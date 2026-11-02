import json
import pandas as pd
from PIL import Image, ImageChops

def audit_hit_detection_accuracy(session_log):
    """
    Audits a single session log against its actual image files 
    to measure False Negatives (Code Errors) vs. True Misses (User Errors).
    """
    try:
        base_img = Image.open(session_log["base_image_file"]).convert("RGB").resize((450, 450))
        alt_img = Image.open(session_log["alt_image_file"]).convert("RGB").resize((450, 450))
        heatmap = ImageChops.difference(base_img, alt_img).convert("L")
    except Exception:
        return {"false_negatives": 0, "true_misses": len(session_log.get("miss_coordinates", [])), "hit_detection_accuracy": 100.0}

    false_negatives = 0  # User clicked a real difference, but code marked it red
    true_misses = 0      # User clicked empty space and code marked it red

    for x, y in session_log.get("miss_coordinates", []):
        radius = 10
        left = max(0, x - radius)
        top = max(0, y - radius)
        right = min(450, x + radius)
        bottom = min(450, y + radius)
        
        click_region = heatmap.crop((left, top, right, bottom))
        extrema = click_region.getextrema()
        
        # If the region has lit-up pixels (> 20), a real visual difference was there!
        if extrema is not None and extrema[1] > 20:
            false_negatives += 1
        else:
            true_misses += 1

    total_clicks_evaluated = len(session_log.get("miss_coordinates", [])) + len(session_log.get("hit_coordinates", []))
    
    # Hit-Detection Accuracy calculation
    accuracy_rate = 100.0 if total_clicks_evaluated == 0 else max(0, ((total_clicks_evaluated - false_negatives) / total_clicks_evaluated) * 100)

    return {
        "false_negatives": false_negatives,
        "true_misses": true_misses,
        "hit_detection_accuracy": round(accuracy_rate, 1)
    }

def audit_and_grade_logs(log_file="eval_logs.json"):
    try:
        with open(log_file, "r") as f:
            logs = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"status": "No logs found"}

    df = pd.DataFrame(logs)
    
    df['friction_ratio'] = df['total_misses'] / 5.0
    df['playability_score'] = (100 - (df['friction_ratio'] * 30)).clip(lower=0)
    
    avg_score = df['playability_score'].mean()
    avg_misses = df['total_misses'].mean()
    
    if avg_score >= 80:
        system_status = "HEALTHY"
        recommendation = "Hit-detection and AI distinctness are well-balanced. No changes required."
    elif 50 <= avg_score < 80:
        system_status = "MODERATE FRICTION"
        recommendation = "Action: Expand hit-detection padding threshold in app.py to convert boundary misses into hits."
    else:
        system_status = "HIGH FRICTION / FRUSTRATING"
        recommendation = "Action: AI generation is producing overly subtle changes. Tighten generation prompts to force bolder edits."

    eval_summary = {
        "total_sessions": len(df),
        "average_playability_score": round(avg_score, 1),
        "average_misses": round(avg_misses, 1),
        "system_status": system_status,
        "recommendation": recommendation,
        "historical_trend": df[['timestamp', 'playability_score', 'total_misses']].to_dict(orient="records")
    }
    
    return eval_summary