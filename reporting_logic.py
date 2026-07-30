import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import text

@st.cache_resource(ttl=60)
def get_report_data(_engine):
    query = """
        SELECT 
            COALESCE(rev.full_name, r.reviewer_username) as reviewer_name,
            rev.kumpulan_pegawai,
            rev.has_consented,
            rev.consented_at,
            r.applicant_name,
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
        
        df = df.rename(columns={
            'reviewer_name': 'Nama Penilai',
            'kumpulan_pegawai': 'Kumpulan Pegawai',
            'has_consented': 'Telah Bersetuju (Kerahsiaan)',
            'consented_at': 'Tarikh Persetujuan',
            'applicant_name': 'Menilai Siapa'
        })
        
        if 'Telah Bersetuju (Kerahsiaan)' in df.columns:
            df['Telah Bersetuju (Kerahsiaan)'] = df['Telah Bersetuju (Kerahsiaan)'].apply(lambda x: 'Ya' if x is True or str(x).lower() == 'true' else 'Belum')
            
        
        df['Daya Kepimpinan'] = parsed.apply(lambda x: int(x.get('kepimpinan', 0)))
        df['Semangat Berpasukan'] = parsed.apply(lambda x: int(x.get('pasukan', 0)))
        df['Kemahiran Interpersonal'] = parsed.apply(lambda x: int(x.get('interpersonal', 0)))
        df['Akauntabiliti'] = parsed.apply(lambda x: int(x.get('akauntabiliti', 0)))
        df['Inovatif'] = parsed.apply(lambda x: int(x.get('inovatif', 0)))
        df['Jumlah Markah'] = parsed.apply(lambda x: int(x.get('total_score', 0)))
        
        df = df.drop(columns=['responses'])
        
        # Susun semula lajur (Reorder columns)
        cols = ['Nama Penilai', 'Kumpulan Pegawai', 'Telah Bersetuju (Kerahsiaan)', 'Tarikh Persetujuan', 'Menilai Siapa', 'Daya Kepimpinan', 'Semangat Berpasukan', 'Kemahiran Interpersonal', 'Akauntabiliti', 'Inovatif', 'Jumlah Markah']
        df = df[[c for c in cols if c in df.columns]]
        
    return df

def render_reporting(engine):

    st.header("📄 Laporan Penilaian APC")
    df = get_report_data(engine)

    if df.empty:
        st.info("Tiada data setakat ini.")
        return

    # --- 2. FILTERS (Hides in Print automatically due to .stButton/expander logic) ---
    with st.expander("🔍 Tapis Keputusan"):
        col1, col2 = st.columns(2)
        with col1:
            f_rev = st.multiselect("Penilai", df['Nama Penilai'].unique(), default=df['Nama Penilai'].unique())
        with col2:
            # Handle null/None values for Kumpulan Pegawai
            kp_options = df['Kumpulan Pegawai'].fillna('Tiada Kumpulan').unique()
            f_kp = st.multiselect("Kumpulan Pegawai", kp_options, default=kp_options)
    
    # Fill NaN so that filter works smoothly
    filtered_df = df.copy()
    filtered_df['Kumpulan Pegawai'] = filtered_df['Kumpulan Pegawai'].fillna('Tiada Kumpulan')
    
    filtered_df = filtered_df[
        (filtered_df['Nama Penilai'].isin(f_rev)) & 
        (filtered_df['Kumpulan Pegawai'].isin(f_kp))
    ]

    # --- 3. VISUALS ---
    review_counts = filtered_df.groupby('Menilai Siapa').size().reset_index(name='count')
    fig2 = px.bar(review_counts, x='Menilai Siapa', y='count', title="Jumlah Penilaian (Reviews) Diterima", text_auto=True)

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
    st.subheader("📋 Ringkasan Data Mengikut Penilai")
    
    if filtered_df.empty:
        st.info("Tiada data ditemui.")
    else:
        grouped = filtered_df.groupby('Nama Penilai')
        for penilai, group_df in grouped:
            # Dapatkan info kumpulan pegawai jika ada
            kump = group_df['Kumpulan Pegawai'].iloc[0] if 'Kumpulan Pegawai' in group_df.columns else ''
            kump_str = f" ({kump})" if pd.notna(kump) and kump != 'Tiada Kumpulan' and kump != '' else ""
            
            with st.expander(f"👤 Penilai: {penilai}{kump_str} - {len(group_df)} Calon Dinilai", expanded=False):
                # Buang lajur Nama Penilai dari dataframe kecil ini sebab ia sudah ada pada tajuk
                display_df = group_df.drop(columns=['Nama Penilai'])
                st.dataframe(display_df, use_container_width=True, hide_index=True)
