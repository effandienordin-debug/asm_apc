import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import text

@st.cache_resource(ttl=60)
def get_report_data(_engine):
    query = """
        SELECT 
            r.applicant_name,
            COALESCE(rev.full_name, r.reviewer_username) as reviewer_name,
            r.responses
        FROM reviews r
        LEFT JOIN reviewers rev ON r.reviewer_username = rev.username
    """
    import json
    df = pd.read_sql(text(query), _engine)
    
    # Extract total_score from responses json
    def get_score(resp_str):
        try:
            return int(json.loads(resp_str).get('total_score', 0))
        except:
            return 0
            
    if 'responses' in df.columns:
        df['total_score'] = df['responses'].apply(get_score)
        df = df.drop(columns=['responses'])
        
    return df

def render_reporting(engine):
    # --- 1. CSS PRINT HACK (Updated to hide toasts and align layout) ---
    st.markdown("""
        <style>
        @media print {
            /* Hide Sidebar, Header, Footer, and Navigation */
            [data-testid="stSidebar"], header, footer, #MainMenu {
                display: none !important;
            }
            /* HIDE TOAST NOTIFICATIONS (Prevents overlap with title) */
            [data-testid="stToast"] {
                display: none !important;
            }
            /* Hide all buttons during print */
            .stButton {
                display: none !important;
            }
            /* Adjust margins for a clean PDF layout */
            .main .block-container {
                padding-top: 1rem !important;
                max-width: 100% !important;
            }
        }
        </style>
    """, unsafe_allow_html=True)

    st.header("📄 Laporan Penilaian APC")
    df = get_report_data(engine)

    if df.empty:
        st.info("Tiada data setakat ini.")
        return

    # --- 2. FILTERS (Hides in Print automatically due to .stButton/expander logic) ---
    with st.expander("🔍 Tapis Keputusan"):
        f_rev = st.multiselect("Penilai", df['reviewer_name'].unique(), default=df['reviewer_name'].unique())
    
    filtered_df = df[df['reviewer_name'].isin(f_rev)]

    # --- 3. VISUALS ---
    review_counts = filtered_df.groupby('applicant_name').size().reset_index(name='count')
    fig2 = px.bar(review_counts, x='applicant_name', y='count', title="Jumlah Penilaian (Reviews) Diterima", text_auto=True)

    st.plotly_chart(fig2, use_container_width=True)

    # --- 4. ALIGNED EXPORT BUTTONS ---
    st.divider()
    btn_col1, btn_col2 = st.columns(2)

    # Print Button
    if btn_col1.button("🖨️ Jana PDF Profesional", use_container_width=True, type="primary"):
        # parent.print() escapes the iframe to print the full page
        st.components.v1.html("""
            <script>
                window.parent.print();
            </script>
        """, height=0)
        st.toast("Membuka tetapan cetakan... Pilih 'Save as PDF'.")

    # CSV Button (Aligned perfectly next to Print)
    btn_col2.download_button(
        label="📊 Muat Turun Data (CSV)",
        data=filtered_df.to_csv(index=False),
        file_name="ASM_APC_Evaluation_Data_Export.csv",
        mime="text/csv",
        use_container_width=True
    )

    # --- 5. DATA PREVIEW ---
    st.subheader("📋 Ringkasan Data")
    st.dataframe(filtered_df, use_container_width=True, hide_index=True)
