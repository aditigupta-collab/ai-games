import streamlit as st
import json
import pandas as pd
from PIL import Image, ImageDraw
from auto_grader import audit_and_grade_logs, audit_hit_detection_accuracy

st.set_page_config(layout="wide", page_title="AI Eval Dashboard")
st.title("Spot the Difference: Eval Framework & Auto-Grader 📊")

# Run the Auto-Grader Agent
eval_report = audit_and_grade_logs()

if "status" in eval_report:
    st.warning("No evaluation logs found yet. Play a game in app.py to generate data!")
    st.stop()

# --- TOP-LEVEL EVAL METRICS ---
st.divider()
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Sessions", eval_report["total_sessions"])
with col2:
    st.metric("Playability Score", f"{eval_report['average_playability_score']}/100")
with col3:
    st.metric("Avg Misses / Game", eval_report["average_misses"])
with col4:
    status = eval_report["system_status"]
    color_emoji = "🟢" if status == "HEALTHY" else "🟡" if "MODERATE" in status else "DR"
    st.metric("System Health", f"{color_emoji} {status}")

# --- AGENT RECOMMENDATIONS ---
st.divider()
st.subheader("🤖 Agent Improvement Loop & Recommendations")
st.info(f"**Suggested System Action:** {eval_report['recommendation']}")

with st.expander("View Historical Playability Trend"):
    trend_df = pd.DataFrame(eval_report["historical_trend"])
    st.line_chart(trend_df.set_index('timestamp')['playability_score'])

# --- HISTORICAL SESSION REVIEW & ACCURACY AUDIT ---
st.divider()
st.subheader("Visual Session Review & Hit-Detection Accuracy Audit")

try:
    with open("eval_logs.json", "r") as f:
        logs = json.load(f)
        
    if not logs:
        st.warning("Logs file is empty.")
        st.stop()

    session_options = {f"[{log['timestamp']}] {log['prompt']} (Misses: {log['total_misses']})": log for log in logs}
    
    selected_label = st.selectbox("Select a game session to inspect:", list(session_options.keys()))
    selected_session = session_options[selected_label]
    
    # Run the accuracy audit on this specific session
    accuracy_results = audit_hit_detection_accuracy(selected_session)

    # Display Session Accuracy Sub-Metrics
    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric("Hit-Detection Accuracy", f"{accuracy_results['hit_detection_accuracy']}%", help="Percentage of clicks correctly classified by the code.")
    with m2:
        st.metric("False Negatives (Code Errors)", accuracy_results['false_negatives'], help="Red dots placed because the code missed a real change the user clicked.")
    with m3:
        st.metric("True Misses (User Errors)", accuracy_results['true_misses'], help="Red dots placed because the user clicked empty space.")

    st.write(f"**Selected Prompt:** `{selected_session['prompt']}`")

    # Legend for the auditor
    st.markdown("""
    * 🟢 **Neon Green Circles:** Valid Hits (Successfully verified differences)
    * 🔴 **Bright Red Circles (Yellow Border):** User Misses / Friction Points
    """)

    colA, colB = st.columns(2)

    base_img = Image.open(selected_session["base_image_file"]).convert("RGB").resize((450, 450))
    alt_img = Image.open(selected_session["alt_image_file"]).convert("RGB").resize((450, 450))
    
    eval_draw = ImageDraw.Draw(alt_img)
    
    # Paint Green Hits
    for x, y in selected_session["hit_coordinates"]:
        eval_draw.ellipse([x - 12, y - 12, x + 12, y + 12], fill="#39FF14", outline="black", width=2)
        
    # Paint Red Misses
    for x, y in selected_session["miss_coordinates"]:
        eval_draw.ellipse([x - 10, y - 10, x + 10, y + 10], fill="#FF0000", outline="yellow", width=3)

    with colA:
        st.markdown("**Original Scene**")
        st.image(base_img)
    with colB:
        st.markdown("**Audited Gameplay (Accuracy Map)**")
        st.image(alt_img)
        
except Exception as e:
    st.error(f"Could not load visual session data: {e}")