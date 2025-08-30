# app.py

import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageOps
import io

# --- PAGE CONFIGURATION & META TAGS ---
st.set_page_config(
    page_title="Imprint Generator",
    page_icon="🖼️",
    layout="centered",
    initial_sidebar_state="auto"
)

def set_page_head():
    """
    Injects custom CSS for styling and meta tags for rich link previews.
    """
    
    # --- YOUR PREVIEW DETAILS ---
    app_url = "https://your-streamlit-app-url.com"  # Replace with your app's URL
    image_url = "https://raw.githubusercontent.com/GathaiMundia/imprint/main/Attending%202025.png" 
    # --- END OF YOUR DETAILS ---

    meta_tags = f"""
        <meta property="og:title" content="Imprint Generator | YPG Conference">
        <meta property="og:description" content="Create your personalized poster for the PSK-YPG 2025 Annual Conference.">
        <meta property="og:image" content="{image_url}">
        <meta property="og:url" content="{app_url}">
        <meta name="twitter:card" content="summary_large_image">
    """

    css_styles = """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap');
        
        html, body, [class*="st-"], .st-emotion-cache-16txtl3 {
            font-family: 'Lexend Deca', sans-serif;
        }
        .st-emotion-cache-1j6s6b6, .st-emotion-cache-1x0xh3b {
            background-color: #ECF2FF;
            border-radius: 8px;
        }
        .st-emotion-cache-1j6s6b6 input, .st-emotion-cache-1x0xh3b input {
            color: #040D12 !important;
            -webkit-text-fill-color: #040D12 !important;
        }
        .stDownloadButton > button {
            background-color: #00A9FF;
            color: #FFFFFF;
            font-weight: bold;
            border: 2px solid #00A9FF;
            border-radius: 8px;
            padding: 0.75rem 1.5rem;
            width: 100%;
            transition: all 0.3s ease-in-out;
            box-shadow: 0 4px 15px rgba(0, 169, 255, 0.3);
        }
        .stDownloadButton > button:hover {
            background-color: #FFFFFF;
            color: #00A9FF;
            box-shadow: 0 6px 20px rgba(0, 169, 255, 0.5);
            transform: translateY(-2px);
        }
        </style>
    """
    
    st.markdown(meta_tags + css_styles, unsafe_allow_html=True)

# Apply the styling and meta tags at the start of the app
set_page_head()

# --- FILE AND CONFIGURATION CONSTANTS ---
POSTER_PATH = "YPG_Conference_Template.png"  # Make sure to have this file in the same directory

# --- CORE IMAGE PROCESSING FUNCTION ---
def create_poster(user_image_file, user_name, user_role, photo_scale, photo_pos_x, photo_pos_y, photo_rotation, name_font_size, role_font_size):
    try:
        poster_template = Image.open(POSTER_PATH).convert("RGBA")
    except FileNotFoundError:
        st.error("The poster template image was not found. Please make sure 'YPG_Conference_Template.png' is in the same directory as the app.py file.")
        return None

    user_photo = Image.open(user_image_file)
    user_photo = ImageOps.exif_transpose(user_photo)
    user_photo = user_photo.convert("RGBA")
    
    # Create a circular mask for the photo
    mask = Image.new('L', (500, 500), 0)
    draw_mask = ImageDraw.Draw(mask) 
    draw_mask.ellipse((0, 0, 500, 500), fill=255)

    # Apply the circular mask
    user_photo = user_photo.resize(mask.size, Image.Resampling.LANCZOS)
    
    canvas = Image.new("RGBA", poster_template.size)
    
    if photo_rotation != 0:
        user_photo = user_photo.rotate(photo_rotation, resample=Image.Resampling.BICUBIC, expand=True)
    
    base_photo_width = 350 # Adjusted for the new template
    aspect_ratio = user_photo.height / user_photo.width
    new_width = int(base_photo_width * photo_scale)
    new_height = int(new_width * aspect_ratio)
    user_photo = user_photo.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    # Create a new circular mask for the resized photo
    mask = Image.new('L', (new_width, new_height), 0)
    draw_mask = ImageDraw.Draw(mask)
    draw_mask.ellipse((0, 0, new_width, new_height), fill=255)

    photo_paste_x = (canvas.width // 2) - (new_width // 2) + photo_pos_x
    photo_paste_y = 300 - (new_height // 2) + photo_pos_y # Adjusted for the new template
    
    # Paste the photo with the circular mask
    canvas.paste(user_photo, (photo_paste_x, photo_paste_y), mask)
    canvas.paste(poster_template, (0, 0), poster_template)

    draw = ImageDraw.Draw(canvas)
    
    try:
        # Using a default font that is likely to be available. 
        # For better results, you can upload a specific .ttf font file and provide its path.
        name_font = ImageFont.truetype("arial.ttf", name_font_size)
        role_font = ImageFont.truetype("arial.ttf", role_font_size)
    except IOError:
        st.warning("Arial font not found. Using default.")
        name_font = ImageFont.load_default(size=60)
        role_font = ImageFont.load_default(size=40)
    
    # Coordinates are adjusted for the new template
    draw.text((poster_template.width/2, 530), user_name.upper(), font=name_font, fill="#FFFFFF", anchor="ms")
    draw.text((poster_template.width/2, 570), user_role, font=role_font, fill="#FFFFFF", anchor="ms")
    
    return canvas

# --- STREAMLIT APP LAYOUT ---
st.title("Imprint Generator")
st.write("Create your personalized event poster in seconds.")

# --- SIDEBAR CONTROLS ---
with st.sidebar:
    st.header("1. Your Details")
    user_upload = st.file_uploader("Upload Your Headshot")
    user_name = st.text_input("Enter Your Name", "Your Name")
    user_role = st.text_input("Enter Your Role", "Your Role")


    st.header("2. Photo Controls")
    photo_scale = st.number_input("Zoom Photo", min_value=0.5, max_value=4.0, value=1.0, step=0.1)
    photo_pos_x = st.number_input("Move Photo Left/Right", min_value=-400, max_value=400, value=0, step=10)
    photo_pos_y = st.number_input("Move Photo Up/Down", min_value=-400, max_value=400, value=0, step=10)
    photo_rotation = st.number_input("Rotate Photo (°)", min_value=0, max_value=360, value=0, step=5)

    st.header("3. Text Controls")
    name_font_size = st.number_input("Name Font Size", min_value=20, max_value=150, value=60, step=2)
    role_font_size = st.number_input("Role Font Size", min_value=15, max_value=100, value=40, step=2)


# --- MAIN PANEL LOGIC ---
if user_upload and user_name:
    final_poster = create_poster(
        user_image_file=user_upload,
        user_name=user_name,
        user_role=user_role,
        photo_scale=photo_scale,
        photo_pos_x=photo_pos_x,
        photo_pos_y=photo_pos_y,
        photo_rotation=photo_rotation,
        name_font_size=name_font_size,
        role_font_size=role_font_size
    )
    
    if final_poster:
        st.image(final_poster, caption="Looking great! You can now download your poster.", use_container_width=True)
        
        buf = io.BytesIO()
        final_poster.save(buf, format="PNG")
        byte_im = buf.getvalue()
        
        st.download_button(
            label="📥 Download Poster",
            data=byte_im,
            file_name=f"YPG_Conference_{user_name.replace(' ', '_')}.png",
            mime="image/png"
        )
else:
    st.info("⬅️ Start by uploading your photo, name and role in the sidebar.")
    try:
        st.image(POSTER_PATH, caption="Poster Template", use_container_width=True)
    except FileNotFoundError:
        st.error("The poster template image was not found. Please make sure 'YPG_Conference_Template.png' is in the same directory as the app.py file.")
