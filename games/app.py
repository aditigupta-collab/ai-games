import streamlit as st
from openai import OpenAI
import base64
from PIL import Image, ImageDraw, ImageChops
import io
import requests
from streamlit_image_coordinates import streamlit_image_coordinates
import json
from datetime import datetime

client = OpenAI()

st.set_page_config(layout="wide") 
st.title("Spot the Difference 🎯")

# --- 1. GAME STATE ---
if 'base_image_bytes' not in st.session_state:
    st.session_state.base_image_bytes = None
if 'alt_image_bytes' not in st.session_state:
    st.session_state.alt_image_bytes = None
if 'found_diffs' not in st.session_state:
    st.session_state.found_diffs = {} 
# UPGRADE: Track all incorrect clicks for evaluation data
if 'missed_clicks' not in st.session_state:
    st.session_state.missed_clicks = []
if 'last_click' not in st.session_state:
    st.session_state.last_click = None 

# The 5 regions on the raw 1024x1024 image
MASK_ZONES = [
    (100, 100, 250, 250), 
    (774, 100, 924, 250), 
    (437, 437, 587, 587), 
    (100, 774, 250, 924), 
    (774, 774, 924, 924)  
]

st.sidebar.title("Scoreboard 🏆")
st.sidebar.header(f"{len(st.session_state.found_diffs)} / 5 Found")
if st.sidebar.button("Reset Game"):
    st.session_state.clear()
    st.rerun()

# --- 2. THE SINGLE-BUTTON AGENT WORKFLOW ---
st.write("Generate a level to play!")
scene_prompt = st.text_input("Theme:", value="A highly detailed, colorful cartoon illustration of a busy city playground.")

if st.button("Generate Level (Takes ~15s)"):
    with st.spinner("Generating base scene and weaving in 5 hidden differences..."):
        try:
            base_resp = client.images.generate(
                model="gpt-image-2.5-flare",
                prompt=scene_prompt,
                size="1024x1024",
                quality="low",
                n=1,
            )
            
            if base_resp.data[0].b64_json:
                base_bytes = base64.b64decode(base_resp.data[0].b64_json)
            else:
                base_bytes = requests.get(base_resp.data[0].url).content
            
            base_img = Image.open(io.BytesIO(base_bytes)).convert("RGBA")
            mask = Image.new("RGBA", base_img.size, (255, 255, 255, 255))
            draw = ImageDraw.Draw(mask)
            for zone in MASK_ZONES:
                draw.rectangle(zone, fill=(255, 255, 255, 0))
                
            mask_bytes = io.BytesIO()
            mask.save(mask_bytes, format="PNG")
            img_bytes = io.BytesIO()
            base_img.save(img_bytes, format="PNG")
            
            edit_resp = client.images.edit(
                model="gpt-image-2.5-flare",
                image=("image.png", img_bytes.getvalue()),
                mask=("mask.png", mask_bytes.getvalue()),
                prompt="Keep the exact same scene, but change minor details in the transparent areas (like a different color, a new small object, or a missing item).",
                n=1
            )
            
            if edit_resp.data[0].b64_json:
                alt_bytes = base64.b64decode(edit_resp.data[0].b64_json)
            else:
                alt_bytes = requests.get(edit_resp.data[0].url).content
            
            st.session_state.base_image_bytes = base_bytes
            st.session_state.alt_image_bytes = alt_bytes
            st.session_state.found_diffs = {} 
            st.session_state.missed_clicks = [] # Reset miss tracker for the new game
            st.session_state.last_click = None 
            st.rerun()
            
        except Exception as e:
            st.error(f"Generation failed: {e}")

# --- 3. THE GAME BOARD ---
if st.session_state.alt_image_bytes:
    st.divider()
    st.write("Click the **5 differences** on the RIGHT image!")
    
    col1, col2 = st.columns(2)
    display_size = (450, 450)
    
    # Load clean base and altered images
    base_display = Image.open(io.BytesIO(st.session_state.base_image_bytes)).convert("RGB").resize(display_size)
    alt_display_clean = Image.open(io.BytesIO(st.session_state.alt_image_bytes)).convert("RGB").resize(display_size)
    
    # Generate the computer vision heatmap from the CLEAN images
    heatmap = ImageChops.difference(base_display, alt_display_clean).convert("L")
    
    # Draw tracking dots on a copy of the image for the UI
    alt_display_ui = alt_display_clean.copy()
    ui_draw = ImageDraw.Draw(alt_display_ui)
    
    # Draw SUCCESS dots (Neon Green)
    for dot_x, dot_y in st.session_state.found_diffs.values():
        r = 10 
        ui_draw.ellipse([dot_x - r, dot_y - r, dot_x + r, dot_y + r], fill="#39FF14", outline="darkgreen", width=2)
        
    # Draw MISS dots (Bright Red)
    for miss_x, miss_y in st.session_state.missed_clicks:
        r = 8 # Slightly smaller so it doesn't overpower the image
        ui_draw.ellipse([miss_x - r, miss_y - r, miss_x + r, miss_y + r], fill="#FF0000", outline="darkred", width=2)
    
    with col1:
        st.markdown("### Original")
        streamlit_image_coordinates(base_display, key="base_board")
        
    with col2:
        st.markdown("### Spot the Difference!")
        # Render the UI version with both green and red dots painted
        click_data = streamlit_image_coordinates(alt_display_ui, key="game_board")
        
        # Hit detection logic using Computer Vision
        if click_data is not None:
            click_id = f"{click_data['x']}_{click_data['y']}"
            
            if st.session_state.last_click != click_id:
                st.session_state.last_click = click_id
                
                x, y = click_data['x'], click_data['y']
                hit = False
                
                radius = 10
                left = max(0, x - radius)
                top = max(0, y - radius)
                right = min(display_size[0], x + radius)
                bottom = min(display_size[1], y + radius)
                
                click_region = heatmap.crop((left, top, right, bottom))
                extrema = click_region.getextrema() 
                
                if extrema is not None and extrema[1] > 20:
                    scale = 450 / 1024 
                    PADDING = 150 
                    
                    for i, (x1, y1, x2, y2) in enumerate(MASK_ZONES):
                        target_x1 = (x1 - PADDING) * scale
                        target_y1 = (y1 - PADDING) * scale
                        target_x2 = (x2 + PADDING) * scale
                        target_y2 = (y2 + PADDING) * scale
                        
                        if target_x1 <= x <= target_x2 and target_y1 <= y <= target_y2:
                            if i not in st.session_state.found_diffs:
                                st.session_state.found_diffs[i] = (x, y) 
                                hit = True
                                break 
                                
                if not hit:
                    # Save the missed coordinate to our tracking array
                    st.session_state.missed_clicks.append((x, y))
                    st.toast("Miss! Keep looking.")
                
                st.rerun()
                
    # --- 4. VICTORY STATE & EVAL LOGGING ---
    if len(st.session_state.found_diffs) == 5:
        st.balloons() 
        st.success("🎉 You found all 5 differences!")
        
        if 'logged_eval' not in st.session_state:
            from datetime import datetime
            import json
            
            # Create unique filenames using the current time
            timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_filename = f"base_{timestamp_str}.png"
            alt_filename = f"alt_{timestamp_str}.png"
            
            # Save the raw image bytes to disk as PNGs
            with open(base_filename, "wb") as f:
                f.write(st.session_state.base_image_bytes)
            with open(alt_filename, "wb") as f:
                f.write(st.session_state.alt_image_bytes)
            
            eval_data = {
                "timestamp": timestamp_str,
                "prompt": scene_prompt,
                "total_misses": len(st.session_state.missed_clicks),
                "miss_coordinates": st.session_state.missed_clicks,
                "hit_coordinates": [coords for coords in st.session_state.found_diffs.values()],
                "difficulty_ratio": len(st.session_state.missed_clicks) / 5.0,
                "base_image_file": base_filename,
                "alt_image_file": alt_filename
            }
            
            try:
                with open("eval_logs.json", "r") as f:
                    logs = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                logs = []
                
            logs.append(eval_data)
            
            with open("eval_logs.json", "w") as f:
                json.dump(logs, f, indent=4)
                
            st.session_state.logged_eval = True 
            
        colA, colB, colC = st.columns([1, 2, 1])
        with colB:
            st.image("https://media.tenor.com/7sPnhgKHKj8AAAAi/trophy-winner.gif", use_container_width=True)