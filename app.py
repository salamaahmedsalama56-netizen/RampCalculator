import streamlit as st

# --- RAMP CALCULATION ENGINE ---
class RampCalculator:
    def __init__(self, code_standard="SBC"):
        self.code_standard = code_standard

    def calculate_car_ramp_length(self, height, slope_percent):
        slope = slope_percent / 100
        if slope <= 0: return 0.0
        
        # Specific cases for Transition Zones based on your logic
        if slope == 0.12:
            f_len, f_h = 3.6, (3.6 * 0.06) * 2
            remaining_height = height - f_h
            ramp_length = (f_len * 2) + (remaining_height / slope)
        elif slope >= 0.15:
            f_len, f_h = 5.0, (5.0 * 0.15) * 2
            remaining_height = height - f_h
            # Using 18% for the main part in this specific case as per your logic
            ramp_length = (f_len * 2) + (remaining_height / 0.18)
        elif slope == 0.08:
            f_len, f_h = 4.0, (4.0 * 0.04) * 2
            remaining_height = height - f_h
            ramp_length = (f_len * 2) + (remaining_height / slope)
        else:
            # General case for any manual slope input
            ramp_length = height / slope
            
        return round(max(ramp_length, 0.0), 2)

    def calculate_car_ramp_height(self, length, slope_percent):
        slope = slope_percent / 100
        if length <= 0: return 0.0
        
        if slope == 0.12:
            f_len, f_h = 3.6 * 2, (3.6 * 0.06) * 2
            ramp_height = f_h + (length - f_len) * 0.12
        elif slope >= 0.15:
            f_len, f_h = 5.0 * 2, (5.0 * 0.15) * 2
            ramp_height = f_h + (length - f_len) * 0.18
        elif slope == 0.01:
            f_len, f_h = 3.0 * 2, (3.0 * 0.05) * 2
            ramp_height = f_h + (length - f_len) * 0.01
        elif slope == 0.08:
            f_len, f_h = 2.4 * 2, (2.4 * 0.04) * 2
            ramp_height = f_h + (length - f_len) * 0.08
        else:
            ramp_height = length * slope
            
        return round(max(ramp_height, 0.0), 2)

    def calculate_ada_ramp_length(self, height, slope_percent, max_run=9.0, landing=1.2):
        slope = slope_percent / 100
        if slope <= 0: return {"total_length": 0.0, "landings_count": 0}
        
        base_length = height / slope
        num_landings = int(base_length // max_run) if base_length > max_run else 0
        total_length = base_length + (num_landings * landing)
        return {"total_length": round(total_length, 2), "landings_count": num_landings}

# --- STREAMLIT UI ---
import streamlit as st
st.set_page_config(page_title="BIM Ramp Master Pro", page_icon="📐", layout="centered")

# Custom CSS for Professional Look
st.markdown("""
    <style>
    .main { text-align: left; }
    .stMetric { background-color: #f0f2f6; padding: 10px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("📐 BIM Ramp Master Pro")
st.caption("Advanced Calculation Tool | Developed by SALAMA AHMED")

calc = RampCalculator()
tabs = st.tabs(["🚗 Car Ramp (Length)", "📊 Car Ramp (Height)", "♿ ADA/Pedestrian"])

# --- TAB 1: Length Calculation ---
with tabs[0]:
    st.header("Calculate Total Length")
    col1, col2 = st.columns(2)
    with col1:
        h = st.number_input("Target Height (m)", value=3.0, step=0.1, key="h1")
    with col2:
        # Manual entry enabled
        s1 = st.number_input("Design Slope (%)", value=12.0, step=0.1, key="s1")
    
    res_l = calc.calculate_car_ramp_length(h, s1)
    st.success(f"**Total Required Length: {res_l} m**")
    
# --- Section Header ---
st.divider()
st.subheader("Headroom/Clear Height Verification")

# --- Inputs ---
col1, col2 = st.columns(2)

with col1:
    ceil_elev = st.number_input("Ceiling Level (Bottom of Slab) [m]", value=4.00)
    start_ramp_elev = st.number_input("Start Ramp Floor Level [m]", value=0.00)

with col2:
    slab_thk = st.number_input("Upper Slab Thickness [m]", value=0.30)
    slope_pct = st.number_input("Ramp Slope [%]", value=15.0)

# Convert percentage to decimal (e.g., 15% -> 0.15)
slope = slope_pct / 100

# --- 1. Initial Clearance Check ---
# Net height = (Ceiling elevation) - (Floor elevation) - (Slab thickness of the roof above)
net_clearance = round(ceil_elev - start_ramp_elev - slab_thk, 2)

if net_clearance < 2.50:
    st.error(f"⚠️ Critical Clearance Alert: {net_clearance}m (Minimum required: 2.50m)")
else:
    st.success(f"✅ Safe Clearance: {net_clearance}m")

# --- 2. Transition Zones & Required Length Logic ---
target_h = 2.50 # The standard minimum clear height

if slope <= 0:
    st.warning("Slope must be greater than 0%")
else:
    # Logic for Transition Zones (Standard practice for parking ramps)
    if slope == 0.12:
        f_len = 3.6
        # Transition slope is usually half of the main slope
        transition_h = f_len * (slope / 2) 
        needed_remaining_h = target_h - transition_h
        ramp_len_req = f_len + (needed_remaining_h / slope)
        
    elif slope >= 0.15:
        f_len = 5.0
        transition_h = f_len * (0.05) # Specific case for 15% slope
        needed_remaining_h = target_h - transition_h
        ramp_len_req = f_len + (needed_remaining_h / slope)
        
    elif slope == 0.08:
        f_len = 4.0
        transition_h = f_len * (0.04)
        needed_remaining_h = target_h - transition_h
        ramp_len_req = f_len + (needed_remaining_h / slope)
        
    else:
        # General simple calculation without specific transition rules
        ramp_len_req = target_h / slope

    st.info(f"**Required Horizontal Distance to reach 2.5m clearance:** {round(ramp_len_req, 2)} meters")

# --- TAB 2: Height Calculation ---
with tabs[1]:
    st.header("Calculate Achieved Height")
    col3, col4 = st.columns(2)
    with col3:
        l_in = st.number_input("Available Length (m)", value=10.0, step=0.1, key="l2")
    with col4:
        s2 = st.number_input("Design Slope (%)", value=12.0, step=0.1, key="s2")
    
    res_h = calc.calculate_car_ramp_height(l_in, s2)
    st.success(f"**Achieved Rise: {res_h} m**")

# --- TAB 3: ADA Ramp ---
with tabs[2]:
    st.header("ADA Ramp (Accessible Design)")
    h_ada = st.number_input("Total Rise (m)", value=0.50, step=0.05, key="h_ada")
    s_ada = st.number_input("ADA Slope (%)", value=8.33, step=0.01, key="s_ada")
    
    res_ada = calc.calculate_ada_ramp_length(h_ada, s_ada)
    
    c1, c2 = st.columns(2)
    c1.metric("Total Length (Inc. Landings)", f"{res_ada['total_length']} m")
    c2.metric("Landings Count", res_ada['landings_count'])

st.divider()
st.caption("SBC Compliant Logic | 2026 Professional Edition")
