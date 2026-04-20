import streamlit as st

# --- RAMP CALCULATION ENGINE ---
class RampCalculator:
    def __init__(self, code_standard="SBC"):
        self.code_standard = code_standard

    def calculate_car_ramp_length(self, height, slope_percent):
        slope = slope_percent / 100
        if slope <= 0: return None
        if slope == 0.12:
            f_len, f_h = 3.6, (3.6 * 0.06) * 2
            ramp_length = (f_len * 2) + ((height - f_h) / slope)
        elif slope > 0.15:
            f_len, f_h = 5, (5 * 0.15) * 2
            ramp_length = (f_len * 2) + ((height - f_h) / 0.18)
        elif slope == 0.08:
            f_len, f_h = 4, (4 * 0.04) * 2
            ramp_length = (f_len * 2) + ((height - f_h) / slope)
        else:
            ramp_length = height / slope
        return round(ramp_length, 2)

    def calculate_car_ramp_height(self, length, slope_percent):
        slope = slope_percent / 100
        if length <= 0: return None
        if slope == 0.12:
            f_len, f_h = 3.6 * 2, (3.6 * 0.06) * 2
            ramp_height = f_h + (length - f_len) * 0.12
        elif slope > 0.15:
            f_len, f_h = 5 * 2, (5 * 0.15) * 2
            ramp_height = f_h + (length - f_len) * 0.18
        elif slope == 0.08:
            f_len, f_h = 4 * 2, (4 * 0.04) * 2
            ramp_height = f_h + (length - f_len) * 0.08
        else:
            ramp_height = length * slope
        return round(ramp_height, 2)

    def calculate_ada_ramp_length(self, height, slope_percent=8.33, max_run=9.0, landing=1.2):
        slope = slope_percent / 100
        if slope <= 0 or slope > 0.12: return None
        base_length = height / slope
        num_landings = int(base_length // max_run) if base_length > max_run else 0
        total_length = base_length + (num_landings * landing)
        return {"total_length": round(total_length, 2), "landings_count": num_landings}

    def calculate_clear_height(self, current_point_height, ceiling_elevation, slab_thickness):
        net_clearance = ceiling_elevation - current_point_height - slab_thickness
        return round(net_clearance, 2)

# --- STREAMLIT UI ---
st.set_page_config(page_title="BIM Ramp Pro", page_icon="📐")

st.title("📐 BIM Ramp Master Pro")
st.caption("Professional Tool for Car & ADA Ramps | Developed by Lead BIM Engineer")

calc = RampCalculator()
tabs = st.tabs(["🚗 Car Ramp Length", "📊 Car Ramp Height", "♿ ADA Ramp"])

with tabs[0]:
    st.header("Calculate Length")
    h = st.number_input("Total Height / Rise (m)", value=3.0, step=0.1, key="h1")
    s = st.selectbox("Design Slope (%)", [8, 12, 15, 18, 20], index=1, key="s1")
    res_l = calc.calculate_car_ramp_length(h, s)
    st.success(f"**Required Length: {res_l} m**")
    
    st.divider()
    st.subheader("Headroom Check")
    ceil = st.number_input("Ceiling Elevation (m)", value=3.5)
    slab = st.number_input("Slab Thickness (m)", value=0.3)
    cl = calc.calculate_clear_height(0, ceil, slab)
    if cl < 2.2: st.error(f"Critical Clearance: {cl}m")
    else: st.info(f"Clearance OK: {cl}m")

with tabs[1]:
    st.header("Calculate Height")
    l_in = st.number_input("Available Length (m)", value=10.0, key="l2")
    s_in = st.selectbox("Design Slope (%)", [8, 12, 15, 18, 20], index=1, key="s2")
    res_h = calc.calculate_car_ramp_height(l_in, s_in)
    st.success(f"**Achieved Height: {res_h} m**")

with tabs[2]:
    st.header("ADA Ramp (Landings included)")
    h_ada = st.number_input("Total Rise (m)", value=0.5)
    res_ada = calc.calculate_ada_ramp_length(h_ada)
    st.metric("Total Length", f"{res_ada['total_length']} m")
    st.metric("Landings Count", res_ada['landings_count'])