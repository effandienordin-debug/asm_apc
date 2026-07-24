import streamlit as st
from database_utils import get_radio_index

def render_apc_evaluation_form(prev_responses, rev_metadata, disabled=False):
    st.subheader("📋 Penilaian 360 Darjah (APC-ASM)")
    st.info("Sila berikan markah (1 - 5) berdasarkan kriteria kecekapan utama di bawah. Markah akan dikira secara automatik.")
    
    def get_val(key, default=1):
        val = prev_responses.get(key, default)
        try:
            return int(val)
        except:
            return 1
            
    # --- DEFINISI RUBRIK ---
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
    st.caption("Berkebolehan memimpin dengan cara yang positif, membina dan memberi arahan mengikut polisi, tatacara dan deskripsi kerja organisasi.")
    kepimpinan_opt = st.radio("Markah Daya Kepimpinan", options, index=get_index_from_val(get_val('kepimpinan', 1)), disabled=disabled, horizontal=True, key="kepimpinan")
    kepimpinan_val = val_from_option(kepimpinan_opt)
    
    st.divider()
    
    # 2. Semangat Berpasukan
    st.markdown("### 2. Semangat Berpasukan")
    st.caption("Berkebolehan untuk bekerja secara berkumpulan dan menjalankan tugas secara bekerjasama bagi mencapai matlamat dan menyelesaikan tugas dalam satu pasukan.")
    pasukan_opt = st.radio("Markah Semangat Berpasukan", options, index=get_index_from_val(get_val('pasukan', 1)), disabled=disabled, horizontal=True, key="pasukan")
    pasukan_val = val_from_option(pasukan_opt)
    
    st.divider()
    
    # 3. Kemahiran Interpersonal
    st.markdown("### 3. Kemahiran Interpersonal")
    st.caption("Berkebolehan untuk berinteraksi dengan sikap dan tingkah laku yang positif termasuk cara berkomunikasi yang efektif, penyelesaian masalah yang baik dan kemahiran rundingan yang berkesan.")
    interpersonal_opt = st.radio("Markah Kemahiran Interpersonal", options, index=get_index_from_val(get_val('interpersonal', 1)), disabled=disabled, horizontal=True, key="interpersonal")
    interpersonal_val = val_from_option(interpersonal_opt)
    
    st.divider()
    
    # 4. Akauntabiliti
    st.markdown("### 4. Akauntabiliti")
    st.caption("Bertanggungjawab ke atas tugas dan keputusan yang dilakukan dan bersedia untuk menerima kesan dan implikasi dari suatu perbuatan atas tindakan yang dilakukannya.")
    akauntabiliti_opt = st.radio("Markah Akauntabiliti", options, index=get_index_from_val(get_val('akauntabiliti', 1)), disabled=disabled, horizontal=True, key="akauntabiliti")
    akauntabiliti_val = val_from_option(akauntabiliti_opt)
    
    st.divider()
    
    # 5. Inovatif
    st.markdown("### 5. Inovatif")
    st.caption("Berkebolehan menjadi kreatif dan menunjukkan inisiatif untuk menjana pembaharuan atau penambahbaikan organisasi.")
    inovatif_opt = st.radio("Markah Inovatif", options, index=get_index_from_val(get_val('inovatif', 1)), disabled=disabled, horizontal=True, key="inovatif")
    inovatif_val = val_from_option(inovatif_opt)
    
    # --- PENGIRAAN MARKAH ---
    total_score = kepimpinan_val + pasukan_val + interpersonal_val + akauntabiliti_val + inovatif_val
    
    st.divider()
    st.markdown(f"""
        <div style="background-color:#e1f5fe; padding:20px; border-radius:10px; border-left: 8px solid #0288d1; text-align:center;">
            <p style="margin:0; font-size:16px; color:#01579b;">Jumlah Markah</p>
            <h1 style="margin:0; color:#01579b;">{total_score} / 25</h1>
        </div>
    """, unsafe_allow_html=True)
    st.divider()
    
    # --- REKOMENDASI & ULASAN ---
    st.subheader("💡 Sokongan & Ulasan Akhir")
    prev_rec = rev_metadata.get('final_recommendation')
    rec_index = 0 if prev_rec == "SOKONG" else 1 if prev_rec == "TIDAK SOKONG" else None
    
    rec_val = st.radio("Adakah anda menyokong pencalonan ini untuk APC?", options=["SOKONG", "TIDAK SOKONG"], index=rec_index, disabled=disabled, horizontal=True)
    
    prev_remark = rev_metadata.get('overall_justification', "")
    remark_val = st.text_area("Ulasan / Komen (Wajib)", value=prev_remark, height=150, disabled=disabled, placeholder="Sila berikan ulasan anda mengenai calon ini...")
    
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
