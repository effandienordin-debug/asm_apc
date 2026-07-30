import streamlit as st
from database_utils import get_radio_index

def render_apc_evaluation_form(prev_responses, rev_metadata, disabled=False):
    # --- CSS UNTUK BESARKAN & STANDARDKAN FONT SIZE ---
    st.markdown("""
        <style>
        /* Tajuk dan Subtajuk */
        div[data-testid="stMarkdownContainer"] h3 {
            font-size: 24px !important;
            font-weight: 700 !important;
        }
        /* Teks biasa, info, dan caption */
        div[data-testid="stMarkdownContainer"] p {
            font-size: 18px !important;
            line-height: 1.6 !important;
        }
        /* Penerangan Soalan (Caption) digelapkan */
        div[data-testid="stCaptionContainer"] p {
            font-size: 18px !important;
            line-height: 1.6 !important;
            color: #1c1c1c !important; /* Warna teks digelapkan */
            font-weight: 500 !important; /* Sikit tebal / semi-bold */
        }
        /* Label soalan (Radio utama) */
        div[data-testid="stWidgetLabel"] p {
            font-size: 20px !important;
            font-weight: 600 !important;
        }
        /* Pilihan jawapan (Radio options) */
        div[role="radiogroup"] label p {
            font-size: 18px !important;
            font-weight: 400 !important;
        }
        /* Jadual Rubrik Berwarna */
        table {
            width: 100% !important;
            margin-bottom: 20px !important;
            border-collapse: collapse !important;
            border: 1px solid #81d4fa !important;
        }
        table th {
            background-color: #0288d1 !important;
            color: white !important;
            font-size: 16px !important;
            padding: 10px !important;
            text-align: left !important;
        }
        table td {
            font-size: 16px !important;
            padding: 10px !important;
            background-color: #e1f5fe !important;
            color: #01579b !important;
            border-bottom: 1px solid #b3e5fc !important;
        }
        table tr:nth-child(even) td {
            background-color: #b3e5fc !important;
        }
        </style>
    """, unsafe_allow_html=True)

    st.subheader("📋 Penilaian 360 Darjah untuk calon APC-2025")
    st.info("Sila berikan markah (1 - 5) berdasarkan kriteria kecekapan utama di bawah. Markah akan dikira secara automatik.")
    
    def get_val(key, default=1):
        val = prev_responses.get(key, default)
        try:
            return int(val)
        except:
            return 1
            
    # --- RUBRIC DEFINITION ---
    options = [
        "1 - Tidak Memuaskan",
        "2 - Memerlukan Penambahbaikan",
        "3 - Memenuhi Jangkaan",
        "4 - Melebihi Jangkaan",
        "5 - Cemerlang"
    ]
    
    def get_index_from_val(val):
        if 1 <= val <= 5:
            return val - 1
        return 0
        
    def val_from_option(opt):
        return int(opt.split(" - ")[0])

    st.divider()
    
    # 1. Daya Kepimpinan
    st.markdown("### 1. Daya Kepimpinan")
    st.caption("Pegawai berkebolehan memimpin dengan cara yang positif, membina dan memberi arahan mengikut polisi, tatacara dan deskripsi kerja organisasi.")
    st.markdown("""
**📖 Rubrik Terperinci:**
| Skala | Keterangan |
|---|---|
| **1 - Tidak Memuaskan** | Sedikit atau tiada daya kepimpinan dalam menyelesaikan atau menangani konflik dalam pasukan. |
| **2 - Memerlukan Penambahbaikan** | Berusaha memimpin pasukan tetapi tidak memberikan arahan dan pemahaman yang jelas untuk tugasan yang perlu dilaksanakan. |
| **3 - Memenuhi Jangkaan** | Berkebolehan memimpin pasukan dan konsisten memberikan arahan dan pemahaman yang jelas untuk tugasan yang perlu dilaksanakan. |
| **4 - Melebihi Jangkaan** | Berkebolehan memimpin pasukan dan menjangkakan cabaran yang akan dihadapi dan bersedia dengan pelan luar jangkaan. |
| **5 - Cemerlang** | Berkebolehan memimpin, menjadi mentor dan rujukan dalam pasukan. |
    """)
    kepimpinan_opt = st.radio("Markah Daya Kepimpinan", options, index=get_index_from_val(get_val('kepimpinan', 1)), disabled=disabled, horizontal=True, key="kepimpinan")
    kepimpinan_val = val_from_option(kepimpinan_opt)
    
    st.divider()
    
    # 2. Semangat Berpasukan
    st.markdown("### 2. Semangat Berpasukan")
    st.caption("Pegawai berkeupayaan untuk bekerja secara berkumpulan dan menjalankan tugas secara bekerjasama bagi mencapai matlamat dan menyelesaikan tugas dalam satu pasukan.")
    st.markdown("""
**📖 Rubrik Terperinci:**
| Skala | Keterangan |
|---|---|
| **1 - Tidak Memuaskan** | Tidak menunjukkan minat atau tidak mengambil bahagian dalam kerja berpasukan. |
| **2 - Memerlukan Penambahbaikan** | Mengambil bahagian dalam kerja berpasukan untuk tugasan tertentu. |
| **3 - Memenuhi Jangkaan** | Mengambil bahagian secara aktif bagi mencapai matlamat dan menyelesaikan tugas dalam satu pasukan. |
| **4 - Melebihi Jangkaan** | Berkebolehan mewujudkan suasana kerja berpasukan yang harmoni dan mempunyai semangat berpasukan yang tinggi. |
| **5 - Cemerlang** | Memberikan kerjasama yang proaktif kepada kumpulan pengurusan dalam mencari penyelesaian yang tepat untuk organisasi. |
    """)
    pasukan_opt = st.radio("Markah Semangat Berpasukan", options, index=get_index_from_val(get_val('pasukan', 1)), disabled=disabled, horizontal=True, key="pasukan")
    pasukan_val = val_from_option(pasukan_opt)
    
    st.divider()
    
    # 3. Kemahiran Interpersonal
    st.markdown("### 3. Kemahiran Interpersonal")
    st.caption("Pegawai berkeupayaan untuk berinteraksi dengan sikap dan tingkah laku yang positif termasuk cara berkomunikasi yang efektif, penyelesaian masalah yang baik dan kemahiran rundingan yang berkesan.")
    st.markdown("""
**📖 Rubrik Terperinci:**
| Skala | Keterangan |
|---|---|
| **1 - Tidak Memuaskan** | Tidak berkeupayaan untuk berinteraksi dengan sikap dan tingkah laku yang positif. |
| **2 - Memerlukan Penambahbaikan** | Berkeupayaan untuk berinteraksi dengan sikap dan tingkah laku yang positif namun, memerlukan bimbingan untuk berinteraksi dengan jelas. |
| **3 - Memenuhi Jangkaan** | Berkomunikasi dengan meyakinkan serta menggunakan nada, kaedah, saluran dan kandungan yang jelas. |
| **4 - Melebihi Jangkaan** | Berkomunikasi secara jelas, mendengar dan menerima pendapat dan menggalakkan komunikasi terbuka. |
| **5 - Cemerlang** | Berkebolehan mempengaruhi orang lain berdasarkan pemahaman terperinci mengenai tugasan sambil mengekalkan sikap saling menghormati. |
    """)
    interpersonal_opt = st.radio("Markah Kemahiran Interpersonal", options, index=get_index_from_val(get_val('interpersonal', 1)), disabled=disabled, horizontal=True, key="interpersonal")
    interpersonal_val = val_from_option(interpersonal_opt)
    
    st.divider()
    
    # 4. Akauntabiliti
    st.markdown("### 4. Akauntabiliti")
    st.caption("Pegawai bertanggungjawab ke atas tugasan atau keputusan yang dilakukan dan bersedia untuk menerima kesan dan implikasi dari suatu perbuatan atas tindakan yang dilakukannya.")
    st.markdown("""
**📖 Rubrik Terperinci:**
| Skala | Keterangan |
|---|---|
| **1 - Tidak Memuaskan** | Tidak bertanggungjawab ke atas tugasan atau keputusan yang dilakukan dan memerlukan penyeliaan yang berterusan. |
| **2 - Memerlukan Penambahbaikan** | Memenuhi tanggungjawab atau tugasan tetapi masih memerlukan penyeliaan dan arahan yang kerap. |
| **3 - Memenuhi Jangkaan** | Bertanggungjawab ke atas tugasan yang diberikan dengan penyeliaan yang minimal dan memahami kesan daripada sebarang tindakan yang dilakukan. |
| **4 - Melebihi Jangkaan** | Memenuhi tanggungjawab atau tugasan melebihi jangkaan yang ditetapkan dan menerima secara terbuka hasil kerja yang positif atau negatif. |
| **5 - Cemerlang** | Berkebolehan memenuhi tanggungjawab atau tugasan dan bersedia menerima implikasi dari setiap keputusan serta mengekalkan profesionalisme. |
    """)
    akauntabiliti_opt = st.radio("Markah Akauntabiliti", options, index=get_index_from_val(get_val('akauntabiliti', 1)), disabled=disabled, horizontal=True, key="akauntabiliti")
    akauntabiliti_val = val_from_option(akauntabiliti_opt)
    
    st.divider()
    
    # 5. Inovatif
    st.markdown("### 5. Inovatif")
    st.caption("Pegawai berkeupayaan dan berkebolehan menjadi kreatif dan menunjukkan inisiatif untuk menjana pembaharuan atau penambahbaikan organisasi.")
    st.markdown("""
**📖 Rubrik Terperinci:**
| Skala | Keterangan |
|---|---|
| **1 - Tidak Memuaskan** | Tiada inisiatif dan penjanaan idea serta penambahbaikan baru dalam tugas. |
| **2 - Memerlukan Penambahbaikan** | Berkebolehan mengutarakan idea dan inisiatif untuk penambahbaikan namun masih memerlukan bimbingan, panduan dan sokongan. |
| **3 - Memenuhi Jangkaan** | Kreatif dan proaktif dalam penjanaan idea dengan pemantauan yang minimal. |
| **4 - Melebihi Jangkaan** | Berkemampuan menggabungkan dan menambahbaik idea-idea baru untuk digunapakai dalam organisasi. |
| **5 - Cemerlang** | Berkebolehan memimpin, menyelaras dan mengutamakan penerokaan idea baru selaras dengan matlamat organisasi. |
    """)
    inovatif_opt = st.radio("Markah Inovatif", options, index=get_index_from_val(get_val('inovatif', 1)), disabled=disabled, horizontal=True, key="inovatif")
    inovatif_val = val_from_option(inovatif_opt)
    
    # --- SCORE CALCULATION ---
    total_score = kepimpinan_val + pasukan_val + interpersonal_val + akauntabiliti_val + inovatif_val
    
    st.divider()
    st.markdown(f"""
        <div style="background-color:#e1f5fe; padding:20px; border-radius:10px; border-left: 8px solid #0288d1; text-align:center;">
            <p style="margin:0; font-size:16px; color:#01579b;">Jumlah Markah</p>
            <h1 style="margin:0; color:#01579b;">{total_score} / 25</h1>
        </div>
    """, unsafe_allow_html=True)
    st.divider()
    
    # --- REMARKS ---
    # Ulasan / Komen removed as requested.
    
    return {
        "responses": {
            "kepimpinan": kepimpinan_val,
            "pasukan": pasukan_val,
            "interpersonal": interpersonal_val,
            "akauntabiliti": akauntabiliti_val,
            "inovatif": inovatif_val,
            "total_score": total_score
        },
        "recommendation": "SUPPORT", # Defaulting to SUPPORT in DB since we removed it from UI
        "justification": "" # Defaulting to empty string since we removed it from UI
    }
