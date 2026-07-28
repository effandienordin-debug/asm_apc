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
    
    if 'responses' in df.columns:
        def parse_responses(resp_str):
            try:
                return json.loads(resp_str) if resp_str else {}
            except:
                return {}
                
        parsed = df['responses'].apply(parse_responses)
        
        df['Daya Kepimpinan'] = parsed.apply(lambda x: int(x.get('kepimpinan', 0)))
        df['Semangat Berpasukan'] = parsed.apply(lambda x: int(x.get('pasukan', 0)))
        df['Kemahiran Interpersonal'] = parsed.apply(lambda x: int(x.get('interpersonal', 0)))
        df['Akauntabiliti'] = parsed.apply(lambda x: int(x.get('akauntabiliti', 0)))
        df['Inovatif'] = parsed.apply(lambda x: int(x.get('inovatif', 0)))
        df['Jumlah Markah'] = parsed.apply(lambda x: int(x.get('total_score', 0)))
        
        df = df.drop(columns=['responses'])
        
    return df

def render_reporting(engine):

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

    # --- 4. EXPORT BUTTONS ---
    st.divider()
    st.download_button(
        label="📊 Muat Turun Data (CSV)",
        data=filtered_df.to_csv(index=False),
        file_name="ASM_APC_Evaluation_Data_Export.csv",
        mime="text/csv",
        use_container_width=True,
        type="primary"
    )

    # --- 5. DATA PREVIEW ---
    st.subheader("📋 Ringkasan Data")
    st.dataframe(filtered_df, use_container_width=True, hide_index=True)
