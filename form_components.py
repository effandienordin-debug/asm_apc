import streamlit as st
from database_utils import get_radio_index

def render_apc_evaluation_form(prev_responses, rev_metadata, disabled=False):
    st.subheader("📋 360 Degree Evaluation (APC-ASM)")
    st.info("Please provide a score (1 - 5) based on the core competency criteria below. The score will be calculated automatically.")
    
    def get_val(key, default=1):
        val = prev_responses.get(key, default)
        try:
            return int(val)
        except:
            return 1
            
    # --- RUBRIC DEFINITION ---
    options = [
        "1 - Unsatisfactory",
        "2 - Needs Improvement",
        "3 - Meets Expectations",
        "4 - Exceeds Expectations",
        "5 - Excellent"
    ]
    
    def get_index_from_val(val):
        if 1 <= val <= 5:
            return val - 1
        return 0
        
    def val_from_option(opt):
        return int(opt.split(" - ")[0])

    st.divider()
    
    # 1. Leadership
    st.markdown("### 1. Leadership")
    st.caption("Able to lead in a positive, constructive manner and provide direction in accordance with the organization's policies, procedures, and job descriptions.")
    kepimpinan_opt = st.radio("Leadership Score", options, index=get_index_from_val(get_val('kepimpinan', 1)), disabled=disabled, horizontal=True, key="kepimpinan")
    kepimpinan_val = val_from_option(kepimpinan_opt)
    
    st.divider()
    
    # 2. Teamwork
    st.markdown("### 2. Teamwork")
    st.caption("Able to work in groups and carry out tasks cooperatively to achieve goals and complete tasks within a team.")
    pasukan_opt = st.radio("Teamwork Score", options, index=get_index_from_val(get_val('pasukan', 1)), disabled=disabled, horizontal=True, key="pasukan")
    pasukan_val = val_from_option(pasukan_opt)
    
    st.divider()
    
    # 3. Interpersonal Skills
    st.markdown("### 3. Interpersonal Skills")
    st.caption("Able to interact with a positive attitude and behavior, including effective communication, good problem solving, and effective negotiation skills.")
    interpersonal_opt = st.radio("Interpersonal Skills Score", options, index=get_index_from_val(get_val('interpersonal', 1)), disabled=disabled, horizontal=True, key="interpersonal")
    interpersonal_val = val_from_option(interpersonal_opt)
    
    st.divider()
    
    # 4. Accountability
    st.markdown("### 4. Accountability")
    st.caption("Responsible for the tasks and decisions made, and ready to accept the consequences and implications of their actions.")
    akauntabiliti_opt = st.radio("Accountability Score", options, index=get_index_from_val(get_val('akauntabiliti', 1)), disabled=disabled, horizontal=True, key="akauntabiliti")
    akauntabiliti_val = val_from_option(akauntabiliti_opt)
    
    st.divider()
    
    # 5. Innovation
    st.markdown("### 5. Innovation")
    st.caption("Able to be creative and show initiative to generate innovations or improvements for the organization.")
    inovatif_opt = st.radio("Innovation Score", options, index=get_index_from_val(get_val('inovatif', 1)), disabled=disabled, horizontal=True, key="inovatif")
    inovatif_val = val_from_option(inovatif_opt)
    
    # --- SCORE CALCULATION ---
    total_score = kepimpinan_val + pasukan_val + interpersonal_val + akauntabiliti_val + inovatif_val
    
    st.divider()
    st.markdown(f"""
        <div style="background-color:#e1f5fe; padding:20px; border-radius:10px; border-left: 8px solid #0288d1; text-align:center;">
            <p style="margin:0; font-size:16px; color:#01579b;">Total Score</p>
            <h1 style="margin:0; color:#01579b;">{total_score} / 25</h1>
        </div>
    """, unsafe_allow_html=True)
    st.divider()
    
    # --- RECOMMENDATION & REMARKS ---
    st.subheader("💡 Support & Final Comments")
    prev_rec = rev_metadata.get('final_recommendation')
    rec_index = 0 if prev_rec == "SUPPORT" else 1 if prev_rec == "DO NOT SUPPORT" else None
    
    rec_val = st.radio("Do you support this nomination for APC?", options=["SUPPORT", "DO NOT SUPPORT"], index=rec_index, disabled=disabled, horizontal=True)
    
    prev_remark = rev_metadata.get('overall_justification', "")
    remark_val = st.text_area("Remarks / Comments (Required)", value=prev_remark, height=150, disabled=disabled, placeholder="Please provide your comments regarding this applicant...")
    
    return {
        "responses": {
            "kepimpinan": kepimpinan_val,
            "pasukan": pasukan_val,
            "interpersonal": interpersonal_val,
            "akauntabiliti": akauntabiliti_val,
            "inovatif": inovatif_val,
            "total_score": total_score
        },
        "recommendation": rec_val,
        "justification": remark_val
    }
