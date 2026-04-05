import json
import streamlit.components.v1 as components
import streamlit as st
import cadquery as cq
import math
import tempfile

st.set_page_config(page_title="Luxel Master Pro", layout="wide")

# ==========================================
# INDUSTRIAL DESIGN UI (CSS INJECTION)
# ==========================================
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        
        /* Base Theme */
        html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
            background-color: #EBEBEB !important;
            font-family: 'Inter', sans-serif !important;
        }

        /* Sidebar - The Flat Console */
        [data-testid="stSidebar"] {
            background-color: #FFFFFF !important;
            border-right: 1px solid #CCCCCC !important;
            padding-top: 1rem !important;
        }

        /* Typography */
        h1, h2, h3, p, span, div {
            font-family: 'Inter', sans-serif;
            color: #222222 !important;
        }
        
        label, .stRadio label {
            font-size: 10px !important;
            text-transform: uppercase;
            letter-spacing: 1.5px !important;
            font-weight: 600 !important;
            color: #666666 !important;
        }

        /* The Braun Section Headers */
        .braun-header {
            font-size: 11px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 2px;
            color: #222222;
            border-bottom: 1px solid #EBEBEB;
            padding-bottom: 8px;
            margin-top: 24px;
            margin-bottom: 12px;
        }

        /* Sliders - Dark Track, Orange Thumb */
        .stSlider [data-baseweb="slider"] [role="slider"] {
            background-color: #FF4500 !important;
            border: none !important;
            border-radius: 0px !important;
            width: 14px !important;
            height: 14px !important;
        }
        .stSlider [data-baseweb="slider"] div[data-testid="stTickBar"] {
            display: none;
        }

        /* Buttons - Outlined, Orange on Hover */
        .stButton > button {
            background-color: transparent !important;
            color: #222222 !important;
            border-radius: 0px !important;
            border: 1px solid #222222 !important;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            font-size: 11px;
            font-weight: 600;
            width: 100%;
            transition: all 0.2s ease-in-out;
            margin-top: 10px;
        }
        .stButton > button:hover {
            background-color: #FF4500 !important;
            border-color: #FF4500 !important;
            color: #FFFFFF !important;
        }
        
        /* Hide Streamlit Branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

st.sidebar.markdown("<h2 style='text-transform:uppercase; letter-spacing:2px; font-size:16px; margin-bottom: 0;'>Luxel Console</h2>", unsafe_allow_html=True)

# ==========================================
# 1. STYLE & HARDWARE
# ==========================================
st.sidebar.markdown("<div class='braun-header'>1. Foundation</div>", unsafe_allow_html=True)
design_path = st.sidebar.radio("Design Methodology", ["Path A: Geometric & Textured", "Path B: Sculpted Flower"])
is_path_b = (design_path == "Path B: Sculpted Flower")

hardware = st.sidebar.radio("Hardware Mount", ["E27 Socket", "USB LED Disk", "Tea Light", "Solid"])

# DYNAMIC HARDWARE LOCKS
if hardware == "E27 Socket":
    h_rad = 20.5
    min_base = 60
elif hardware == "USB LED Disk":
    h_rad = 30.0   
    min_base = 70  
elif hardware == "Tea Light":
    h_rad = 19.5
    min_base = 55
else:
    h_rad = 0
    min_base = 20
    
h_height = st.sidebar.slider("Shade Total Height", 100, 400, 220)

# ==========================================
# 2. SHADE UI (PATH A & B)
# ==========================================
if not is_path_b:
    st.sidebar.markdown("<div class='braun-header'>2. The 3-Plane Profile</div>", unsafe_allow_html=True)
    col1, col2, col3 = st.sidebar.columns(3)
    bot_w = col1.slider("Btm W", min_base, 250, max(80, min_base))
    bel_w = col2.slider("Mid W", 30, 250, 80)
    top_w = col3.slider("Top W", 20, 200, 60)
        
    st.sidebar.markdown("<div class='braun-header'>3. Base Shape</div>", unsafe_allow_html=True)
    core_profile = st.sidebar.radio("Profile Type", ["Polygon", "Star"])
    sides = st.sidebar.slider("Sides / Points", 3, 12, 4)
    pinch = st.sidebar.slider("Star Pinch (%)", 0, 80, 40) / 100.0 if core_profile == "Star" else 0
    aspect = st.sidebar.slider("Aspect Ratio", 0.5, 3.0, 1.0) if sides == 4 else 1.0
    
    st.sidebar.markdown("<div class='braun-header'>4. Modifiers</div>", unsafe_allow_html=True)
    twist = st.sidebar.slider("Twist (Deg)", 0, 360, 0)
    texture = st.sidebar.radio("Texture", ["Smooth", "Waves", "Flutes"])
    if texture != "Smooth":
        st.sidebar.warning("Texture Active: Fillet locked to 0.")
        f_count = st.sidebar.slider("Ridges/side", 1, 20, 10)
        f_depth = st.sidebar.slider("Depth (mm)", 0.0, 10.0, 3.0)
        fillet_val = 0
    else:
        f_count, f_depth = 0, 0
        f_max = 0 if twist > 45 else (5 if twist > 0 else 20)
        fillet_val = st.sidebar.slider("Fillet (mm)", 0, f_max, 0) if f_max > 0 else 0
else:
    st.sidebar.markdown("<div class='braun-header'>2. Silhouette Sculptor</div>", unsafe_allow_html=True)
    bot_w = st.sidebar.slider("Base Width", min_base, 250, max(100, min_base))
    pts = [st.sidebar.slider(f"Curve Pt {i+1}", -40, 80, 0) for i in range(6)]
    bel_w, top_w, twist, texture, sides, aspect, fillet_val, f_depth, core_profile, f_count, pinch = bot_w, bot_w, 0, "Smooth", 36, 1.0, 0, 0, "Polygon", 0, 0

# ==========================================
# 3. STAND UI
# ==========================================
st.sidebar.markdown("<div class='braun-header'>5. Base Stand Design</div>", unsafe_allow_html=True)
st_style = st.sidebar.radio("Stand Type", ["Cylindrical", "Conical", "Circular 3-Legged"])
st_ht = st.sidebar.slider("Stand Height", 5, 100, 30)
st_bot = st.sidebar.slider("Floor Width", 60, 250, bot_w + 20) if st_style == "Conical" else bot_w
st_ribs = st.sidebar.slider("Stand Ribs", 0, 60, 0) if st_style != "Circular 3-Legged" else 0
st_rib_depth = st.sidebar.slider("Rib Depth", 0.0, 5.0, 1.0) if st_ribs > 0 else 0

# ==========================================
# 4. SHARED POINT ENGINE
# ==========================================
def get_outline_master(w, p_idx, is_lip=False):
    target = (w - 1.6) if is_lip else w
    p_list = []
    res = 288 
    for i in range(res):
        th = (i / res) * 2 * math.pi
        if is_path_b:
            fade = 1.0 if p_idx < 0.95 else (1.0 - p_idx) / 0.05
            r = (target/2) * (1.0 - (0.04 * fade * (0.5 * math.sin(36 * th) + 0.5)))
        else:
            step = (2 * math.pi) / sides
            alpha = (th % step) - (step / 2)
            r = (target/2) * (math.cos(step/2) / math.cos(alpha))
            if core_profile == "Star":
                r *= (1.0 - (pinch * abs((th % step) / step * 2 - 1)))
            bx, by = r * aspect * math.cos(th), r * math.sin(th)
            if texture != "Smooth":
                raw = math.sin(th * sides * f_count)
                val = (1.0 if raw > 0.3 else -1.0 if raw < -0.3 else 0) if texture == "Flutes" else raw
                d = math.sqrt(bx**2 + by**2) + 0.001
                bx += (bx / d) * val * f_depth
                by += (by / d) * val * f_depth
            return (bx, by) if i == 0 else (bx, by)
        p_list.append((r * math.cos(th), r * math.sin(th)))
    return p_list

def get_pts_stable(w, is_lip=False):
    target = (w - 1.6) if is_lip else w
    pts_list = []
    res = 288 
    for i in range(res):
        th = (i / res) * 2 * math.pi
        step = (2 * math.pi) / sides
        alpha = (th % step) - (step / 2)
        r = (target/2) * (math.cos(step/2) / math.cos(alpha))
        if core_profile == "Star": r *= (1.0 - (pinch * abs((th % step) / step * 2 - 1)))
        bx, by = r * aspect * math.cos(th), r * math.sin(th)
        if texture != "Smooth":
            raw = math.sin(th * sides * f_count)
            val = (1.0 if raw > 0.3 else -1.0 if raw < -0.3 else 0) if texture == "Flutes" else raw
            d_vec = math.sqrt(bx**2 + by**2) + 0.001
            bx += (bx / d_vec) * val * f_depth
            by += (by / d_vec) * val * f_depth
        pts_list.append((bx, by))
    return pts_list

# ==========================================
# 5. GENERATORS
# ==========================================
def build_shade():
    try:
        sections = []
        c_bez = 2 * bel_w - (0.5 * bot_w) - (0.5 * top_w)
        def b6(t): return ((1-t)**5*pts[0] + 5*(1-t)**4*t*pts[1] + 10*(1-t)**3*t**2*pts[2] + 10*(1-t)**2*t**3*pts[3] + 5*(1-t)*t**4*pts[4] + t**5*pts[5]) if is_path_b else 0
        
        for i in range(41):
            p = i / 40
            curr_w = ((1-p)**2 * bot_w + 2*(1-p)*p * c_bez + p**2 * top_w) + (b6(p)*2)
            
            safe_min = (h_rad * 2) + 5 if h_rad > 0 else 5
            curr_w = max(curr_w, safe_min)

            if is_path_b:
                target_r = curr_w / 2
                p_list = []
                for idx in range(288):
                    th = (idx / 288) * 2 * math.pi
                    fade = 1.0 if p < 0.95 else (1.0 - p) / 0.05
                    r = target_r * (1.0 - (0.04 * fade * (0.5 * math.sin(36 * th) + 0.5)))
                    p_list.append((r * math.cos(th), r * math.sin(th)))
            else:
                p_list = get_pts_stable(curr_w)
            
            wire = cq.Workplane("XY", origin=(0,0,p*h_height)).polyline(p_list + [p_list[0]]).close()
            if not is_path_b and texture == "Smooth" and fillet_val > 0:
                wire = wire.vertices().fillet(fillet_val * (curr_w / bot_w))
            sections.append(wire.val().rotate((0,0,0),(0,0,1), p * twist))
        
        shade_solid = cq.Solid.makeLoft(sections, ruled=False)
        if h_rad > 0:
            hole_cutter = cq.Workplane("XY").circle(h_rad + 0.5).extrude(10)
            shade_solid = cq.Workplane(obj=shade_solid).cut(hole_cutter).val()
        return shade_solid
    except Exception as e:
        st.error(f"Shade Error: {e}"); return None

def build_stand():
    try:
        r_top, r_bot = bot_w/2, st_bot/2
        def rib_w(r, z):
            pts_rib = [((r + (math.sin((i/120)*2*math.pi*st_ribs)*st_rib_depth if st_ribs>0 else 0)) * math.cos((i/120)*2*math.pi), (r + (math.sin((i/120)*2*math.pi*st_ribs)*st_rib_depth if st_ribs>0 else 0)) * math.sin((i/120)*2*math.pi)) for i in range(120)]
            return cq.Workplane("XY", origin=(0,0,z)).polyline(pts_rib + [pts_rib[0]]).close().val()

        if st_style == "Circular 3-Legged":
            base = cq.Workplane("XY", origin=(0,0,st_ht-5)).circle(r_top).extrude(5)
            for i in range(3):
                a = math.radians(i*120); d = r_top-8
                base = base.union(cq.Workplane("XY").center(d*math.cos(a), d*math.sin(a)).circle(5).extrude(st_ht))
        else:
            base = cq.Workplane(obj=cq.Solid.makeLoft([rib_w(r_bot, 0), rib_w(r_top, st_ht)], True))
        
        if is_path_b:
            target_r = (bot_w - 1.6) / 2
            lip_pts = [((target_r * (1.0 - (0.04 * (0.5 * math.sin(36 * (idx/288)*2*math.pi) + 0.5)))) * math.cos((idx/288)*2*math.pi), (target_r * (1.0 - (0.04 * (0.5 * math.sin(36 * (idx/288)*2*math.pi) + 0.5)))) * math.sin((idx/288)*2*math.pi)) for idx in range(288)]
        else:
            lip_pts = get_pts_stable(bot_w, is_lip=True)
            
        lip = cq.Workplane("XY", origin=(0,0,st_ht)).polyline(lip_pts + [lip_pts[0]]).close().extrude(12)
        final = base.union(lip)
        if h_rad > 0: final = final.cut(cq.Workplane("XY").circle(h_rad).extrude(st_ht + 25))
        return final
    except Exception as e:
        st.error(f"Stand Error: {e}"); return None

# ==========================================
# 6. EXECUTE (Moved to the bottom of the sidebar)
# ==========================================
st.sidebar.markdown("<div class='braun-header'>Execute</div>", unsafe_allow_html=True)

if st.sidebar.button("Generate Shade STL"):
    with st.spinner("Compiling Geometry..."):
        m = build_shade()
        if m:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".stl") as t:
                cq.exporters.export(m, t.name)
                with open(t.name, "rb") as f:
                    st.sidebar.download_button("Save Shade", f, "luxel_shade.stl", key="btn_shade")

if st.sidebar.button("Generate Stand STL"):
    with st.spinner("Compiling Geometry..."):
        m = build_stand()
        if m:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".stl") as t:
                cq.exporters.export(m.val() if hasattr(m, 'val') else m, t.name)
                with open(t.name, "rb") as f:
                    st.sidebar.download_button("Save Stand", f, "luxel_stand.stl", key="btn_stand")

# ==========================================
# 7. LIVE 3D PREVIEW
# ==========================================
preview_data = {
    "design_path": "Path B" if is_path_b else "Path A",
    "h_rad": h_rad,
    "h_height": h_height,
    "bot_w": bot_w,
    "bel_w": bel_w,
    "top_w": top_w,
    "sides": sides,
    "aspect": aspect,
    "pinch": pinch,
    "twist": twist,
    "texture": texture,
    "f_count": f_count,
    "f_depth": f_depth,
    "core_profile": core_profile,
    "st_style": st_style,
    "st_ht": st_ht,
    "st_bot": st_bot,
    "st_ribs": st_ribs,
    "st_rib_depth": st_rib_depth
}

if is_path_b:
    preview_data["pts"] = pts

try:
    with open("preview.html", "r") as f:
        html_content = f.read()

    injection_script = f"""
    <script>
        setTimeout(() => {{
            if (window.updateFromStreamlit) {{
                window.updateFromStreamlit({json.dumps(preview_data)});
            }}
        }}, 150);
    </script>
    """
    html_content = html_content.replace("</body>", f"{injection_script}</body>")
    components.html(html_content, height=750)

except FileNotFoundError:
    st.error("⚠️ preview.html not found! Make sure it is in the same folder as this Python script.")