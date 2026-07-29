import streamlit as st
import pandas as pd
import os
import time
import base64
import json
from sqlalchemy import text

# --- 1. SETUP & UTILS ---
PHOTO_DIR = "evaluator_photos"
os.makedirs(PHOTO_DIR, exist_ok=True)

def get_local_image_base64(username):
    file_path = os.path.join(PHOTO_DIR, f"{username.replace(' ', '_')}.png")
    if os.path.exists(file_path):
        with open(file_path, "rb") as img_file:
            b64 = base64.b64encode(img_file.read()).decode()
            return f"data:image/png;base64,{b64}"
    return "https://cdn-icons-png.flaticon.com/512/149/149071.png"

# --- 2. DIALOGS (APPLICANTS & REVIEWERS) ---

@st.dialog("➕ Tambah Calon Baru (Beserta Maklumat Kad Laporan)", width="large")
def add_applicant_dialog(engine):
    with st.form("add_app_form"):
        st.subheader("Maklumat Asas")
        new_photo = st.file_uploader("Gambar", type=['jpg', 'jpeg', 'png'])
        c1, c2 = st.columns(2)
        new_id = c1.text_input("No ID ASM")
        new_name = c2.text_input("Nama Calon*")
        c3, c4, c5 = st.columns(3)
        new_inst = c3.text_input("Jawatan")
        new_gred = c4.text_input("Gred")
        new_bahagian = c5.text_input("Bahagian / Unit")
        
        st.divider()
        st.subheader("Maklumat Report Card (Syarat Kelayakan)")
        rc1, rc2 = st.columns(2)
        r_tahun = rc1.text_input("Tahun Penilaian")
        r_kump = rc2.text_input("Kumpulan Perkhidmatan")
        
        rc3, rc4 = st.columns(2)
        r_tarikh = rc3.text_input("Tarikh Bermula Berkhidmat")
        r_tempoh = rc4.text_input("Tempoh Berkhidmat (Tahun pada 31 Disember)")
        r_rekod = st.text_input("Rekod Penerimaan APC", value="Tiada")
        
        st.markdown("**Semakan Syarat (Tanda jika Ya)**")
        s1 = st.checkbox("Kakitangan bertaraf Tetap / Contract of Service (CoS)")
        s2 = st.checkbox("Kakitangan adalah di Gred 14 dan ke bawah")
        s3 = st.checkbox("Telah berkhidmat sekurang-kurangnya satu (1) tahun pada tahun penilaian")
        s4 = st.checkbox("Bebas daripada tindakan disiplin / tatatertib")
        
        sc1, sc2 = st.columns(2)
        s5 = sc1.checkbox("Markah LNPT (Tahun Penilaian) >= 85%")
        m5 = sc1.text_input("Catatan / Markah LNPT Tahun Penilaian")
        s6 = sc2.checkbox("Markah LNPT (Tahun Sebelum) >= 85%")
        m6 = sc2.text_input("Catatan / Markah LNPT Tahun Sebelum")
        
        if st.form_submit_button("Simpan Calon", type="primary"):
            if new_name:
                add_info = json.dumps({
                    "tahun_penilaian": r_tahun, "kump_perkhidmatan": r_kump, "tarikh_mula": r_tarikh,
                    "tempoh_khidmat": r_tempoh, "rekod_apc": r_rekod, "s_tetap": s1, "s_gred14": s2,
                    "s_setahun": s3, "s_disiplin": s4, "s_lnpt_semasa": s5, "m_lnpt_semasa": m5,
                    "s_lnpt_sebelum": s6, "m_lnpt_sebelum": m6
                })
                with engine.begin() as conn:
                    conn.execute(text("INSERT INTO applicants (name, proposal_title, institution, info_link, remarks, photo, additional_info) VALUES (:n, :t, :i, :l, :r, :p, :ai)"), 
                                 {"n":new_name, "t":new_id, "i":new_inst, "l":new_gred, "r":new_bahagian, "p":new_photo.read() if new_photo else None, "ai":add_info})
                st.cache_resource.clear(); st.success("✅ Telah Ditambah!"); time.sleep(1); st.rerun()
            else:
                st.error("Nama Calon adalah wajib.")

@st.dialog("📝 Sunting Calon (Beserta Maklumat Kad Laporan)", width="large")
def edit_applicant_dialog(engine, app_data):
    info = {}
    if app_data.get('additional_info'):
        try:
            info = json.loads(app_data['additional_info'])
        except: pass
        
    with st.form("edit_app_form"):
        st.subheader("Maklumat Asas")
        new_photo = st.file_uploader("Gambar (Sila abaikan jika tiada perubahan)", type=['jpg', 'jpeg', 'png'])
        c1, c2 = st.columns(2)
        new_id = c1.text_input("No ID ASM", value=app_data.get('proposal_title', ''))
        new_name = c2.text_input("Nama Calon", value=app_data['name'])
        c3, c4, c5 = st.columns(3)
        new_inst = c3.text_input("Jawatan", value=app_data.get('institution', ''))
        new_gred = c4.text_input("Gred", value=app_data.get('info_link', ''))
        new_bahagian = c5.text_input("Bahagian / Unit", value=app_data.get('remarks', ''))
        
        st.divider()
        st.subheader("Maklumat Report Card (Syarat Kelayakan)")
        rc1, rc2 = st.columns(2)
        r_tahun = rc1.text_input("Tahun Penilaian", value=info.get("tahun_penilaian", ""))
        r_kump = rc2.text_input("Kumpulan Perkhidmatan", value=info.get("kump_perkhidmatan", ""))
        
        rc3, rc4 = st.columns(2)
        r_tarikh = rc3.text_input("Tarikh Bermula Berkhidmat", value=info.get("tarikh_mula", ""))
        r_tempoh = rc4.text_input("Tempoh Berkhidmat (Tahun pada 31 Disember)", value=info.get("tempoh_khidmat", ""))
        r_rekod = st.text_input("Rekod Penerimaan APC", value=info.get("rekod_apc", "Tiada"))
        
        st.markdown("**Semakan Syarat (Tanda jika Ya)**")
        s1 = st.checkbox("Kakitangan bertaraf Tetap / Contract of Service (CoS)", value=info.get("s_tetap", False))
        s2 = st.checkbox("Kakitangan adalah di Gred 14 dan ke bawah", value=info.get("s_gred14", False))
        s3 = st.checkbox("Telah berkhidmat sekurang-kurangnya satu (1) tahun pada tahun penilaian", value=info.get("s_setahun", False))
        s4 = st.checkbox("Bebas daripada tindakan disiplin / tatatertib", value=info.get("s_disiplin", False))
        
        sc1, sc2 = st.columns(2)
        s5 = sc1.checkbox("Markah LNPT (Tahun Penilaian) >= 85%", value=info.get("s_lnpt_semasa", False))
        m5 = sc1.text_input("Catatan / Markah LNPT Tahun Penilaian", value=info.get("m_lnpt_semasa", ""))
        s6 = sc2.checkbox("Markah LNPT (Tahun Sebelum) >= 85%", value=info.get("s_lnpt_sebelum", False))
        m6 = sc2.text_input("Catatan / Markah LNPT Tahun Sebelum", value=info.get("m_lnpt_sebelum", ""))
        
        if st.form_submit_button("Kemaskini Calon & Syarat", type="primary"):
            add_info = json.dumps({
                "tahun_penilaian": r_tahun, "kump_perkhidmatan": r_kump, "tarikh_mula": r_tarikh,
                "tempoh_khidmat": r_tempoh, "rekod_apc": r_rekod, "s_tetap": s1, "s_gred14": s2,
                "s_setahun": s3, "s_disiplin": s4, "s_lnpt_semasa": s5, "m_lnpt_semasa": m5,
                "s_lnpt_sebelum": s6, "m_lnpt_sebelum": m6
            })
            with engine.begin() as conn:
                if new_photo:
                    conn.execute(text("UPDATE applicants SET name=:n, proposal_title=:t, institution=:i, info_link=:l, remarks=:r, photo=:p, additional_info=:ai WHERE id=:id"),
                                 {"n":new_name, "t":new_id, "i":new_inst, "l":new_gred, "r":new_bahagian, "p":new_photo.read(), "ai":add_info, "id":app_data['id']})
                else:
                    conn.execute(text("UPDATE applicants SET name=:n, proposal_title=:t, institution=:i, info_link=:l, remarks=:r, additional_info=:ai WHERE id=:id"),
                                 {"n":new_name, "t":new_id, "i":new_inst, "l":new_gred, "r":new_bahagian, "ai":add_info, "id":app_data['id']})
            st.cache_resource.clear(); st.success("✅ Telah Dikemas kini!"); time.sleep(1); st.rerun()

@st.dialog("📝 Sunting Penilai")
def edit_reviewer_dialog(engine, rev_data, hash_password):
    kump_options = ["", "FELO ASM", "KETUA PEGAWAI EKSEKUTIF", "KETUA PEGAWAI OPERASI", "KETUA PEGAWAI STRATEGIK", "KETUA PEGAWAI Hal Ehwal Antarabangsa & Komunikasi", "PENGURUSAN DAN PROFESIONAL", "PELAKSANA"]
    curr_kump = rev_data.get('kumpulan_pegawai', '')
    k_idx = kump_options.index(curr_kump) if curr_kump in kump_options else 0
    with st.form("edit_rev_form"):
        new_name = st.text_input("Nama Penuh", value=rev_data['full_name'])
        new_user = st.text_input("Nama Pengguna (Username)", value=rev_data['username'], disabled=True) 
        new_kump = st.selectbox("Kumpulan Pegawai", kump_options, index=k_idx)
        new_pass = st.text_input("Kata Laluan Baru (Biarkan kosong jika tiada perubahan)", type="password")
        if st.form_submit_button("Kemaskini Penilai", type="primary"):
            with engine.begin() as conn:
                if new_pass.strip():
                    conn.execute(text("UPDATE reviewers SET full_name=:n, kumpulan_pegawai=:k, password_hash=:p WHERE id=:id"),
                                 {"n":new_name, "k":new_kump, "p":hash_password(new_pass), "id":rev_data['id']})
                else:
                    conn.execute(text("UPDATE reviewers SET full_name=:n, kumpulan_pegawai=:k WHERE id=:id"),
                                 {"n":new_name, "k":new_kump, "id":rev_data['id']})
            st.cache_resource.clear(); st.success("✅ Telah Dikemas kini!"); time.sleep(1); st.rerun()

@st.dialog("📚 Tambah Calon Berkelompok")
def bulk_add_applicants_dialog(engine):
    st.markdown("**Format:** `No ID ASM, Nama Calon, Jawatan, Gred, Bahagian/Unit` (Satu baris untuk setiap calon)")
    raw_data = st.text_area("Tampal senarai calon di sini", height=200)
    if st.button("Import Calon", type="primary"):
        lines = [line.strip() for line in raw_data.split('\n') if line.strip()]
        with engine.begin() as conn:
            for line in lines:
                parts = [p.strip() for p in line.split(',')]
                if len(parts) >= 2:
                    conn.execute(text("INSERT INTO applicants (proposal_title, name, institution, info_link, remarks) VALUES (:t, :n, :i, :l, :r) ON CONFLICT (name) DO NOTHING"), 
                                 {"t":parts[0], "n":parts[1], "i":parts[2] if len(parts)>2 else "", "l":parts[3] if len(parts)>3 else "", "r":parts[4] if len(parts)>4 else ""})
        st.cache_resource.clear(); st.success("✅ Selesai!"); time.sleep(1); st.rerun()

@st.dialog("📚 Tambah Penilai Berkelompok")
def bulk_add_reviewers_dialog(engine, hash_password):
    raw_data = st.text_area("Format: Nama Penuh, Nama Pengguna, Kata Laluan", height=200)
    if st.button("Import Penilai", type="primary"):
        lines = [line.strip() for line in raw_data.split('\n') if line.strip()]
        with engine.begin() as conn:
            for line in lines:
                parts = [p.strip() for p in line.split(',')]
                if len(parts) >= 3:
                    conn.execute(text("INSERT INTO reviewers (username, full_name, password_hash) VALUES (:u, :n, :p) ON CONFLICT (username) DO NOTHING"), 
                                 {"u":parts[1].strip(), "n":parts[0].strip(), "p":hash_password(parts[2].strip())})
        st.cache_resource.clear(); st.success("✅ Selesai!"); time.sleep(1); st.rerun()


@st.dialog("📦 Arkib Data (Archive)")
def archive_data_dialog(engine):
    st.warning("Fungsi ini akan menyimpan salinan semua data semasa (Calon, Tugasan, Keputusan Penilaian) ke dalam pangkalan data arkib.")
    archive_name = st.text_input("Nama Arkib (Contoh: Penilaian APC 2024)", value=f"Arkib {time.strftime('%Y-%m-%d')}")
    if st.button("Simpan ke Arkib", type="primary"):
        with engine.begin() as conn:
            import json
            import pandas as pd
            import base64
            # fetch data
            apps = pd.read_sql("SELECT * FROM applicants", conn).to_dict(orient="records")
            assigns = pd.read_sql("SELECT * FROM applicant_assignments", conn).to_dict(orient="records")
            revs = pd.read_sql("SELECT * FROM reviews", conn).to_dict(orient="records")
            
            for a in apps:
                if 'photo' in a and a['photo']:
                    try:
                        a['photo'] = base64.b64encode(a['photo']).decode('utf-8')
                    except:
                        a['photo'] = None
                else:
                    a['photo'] = None
            
            archive_data = json.dumps({
                "applicants": apps,
                "applicant_assignments": assigns,
                "reviews": revs
            }, default=str)
            
            conn.execute(text("INSERT INTO archives (archive_name, archive_date, archive_data) VALUES (:n, :d, :data)"), 
                         {"n": archive_name, "d": time.strftime("%Y-%m-%d %H:%M:%S"), "data": archive_data})
        st.success("✅ Data berjaya diarkibkan!")
        time.sleep(1)
        st.rerun()

@st.dialog("⚠️ Reset Data (Kosongkan)")
def reset_data_dialog(engine):
    st.error("AMARAN: Tindakan ini akan MEMADAM semua data calon, tugasan penilai, dan keputusan penilaian semasa.")
    st.warning("Pastikan anda telah membuat Arkib (Archive) terlebih dahulu sebelum meneruskan tindakan ini.")
    confirm = st.text_input("Taip 'RESET' untuk mengesahkan tindakan ini:")
    if st.button("Padam Semua Data Semasa", type="primary"):
        if confirm == 'RESET':
            with engine.begin() as conn:
                conn.execute(text("DELETE FROM reviews"))
                conn.execute(text("DELETE FROM applicant_assignments"))
                conn.execute(text("DELETE FROM applicants"))
            st.cache_resource.clear()
            st.success("✅ Data semasa telah berjaya dipadam!")
            time.sleep(1)
            st.rerun()
        else:
            st.error("Sila taip 'RESET' dengan betul untuk pengesahan.")

def render_dashboard(engine):
    if st.session_state.get('report_card_app'):
        render_report_card(engine, st.session_state.report_card_app)
        return

    st.header("📊 Data Penilaian Semasa")
    
    col1, col2, col3 = st.columns(3)
    if col1.button("🔄 Kemaskini Papan Pemuka", use_container_width=True):
        st.cache_resource.clear()
        st.rerun()
    if col2.button("📦 Arkib Data Lama", use_container_width=True):
        archive_data_dialog(engine)
    if col3.button("🗑️ Reset Data Semasa", use_container_width=True):
        reset_data_dialog(engine)
        
    query_p1 = text("""
        SELECT 
            r.username, 
            r.full_name,
            (SELECT COUNT(*) FROM applicant_assignments aa 
             WHERE TRIM(LOWER(aa.reviewer_username)) = TRIM(LOWER(r.username))) as assigned,
            (SELECT COUNT(*) FROM reviews rev 
             WHERE TRIM(LOWER(rev.reviewer_username)) = TRIM(LOWER(r.username))) as done
        FROM reviewers r
        ORDER BY r.full_name ASC
    """)
    
    try:
        stats_p1 = pd.read_sql(query_p1, engine)
        
        st.subheader("📋 Status Penilaian")
        if stats_p1.empty:
            st.info("Tiada penilai dijumpai dalam pangkalan data.")
        else:
            cols = st.columns(4)
            for i, row in stats_p1.iterrows():
                f = row['full_name']
                assigned = row['assigned']
                done = row['done']
                
                bg = "#E6FFFA" if (done >= assigned and assigned > 0) else "#FFFBEB"
                
                with cols[i % 4]:
                    st.markdown(f"""
                        <div style='background-color:{bg}; padding:15px; border-radius:8px; border:1px solid #cbd5e0; margin-bottom:10px; text-align:center;'>
                            <strong style='color: #1a202c; font-size:14px; display: block; margin-bottom: 5px;'>{f}</strong>
                            <span style='color: #2d3748; font-size:20px; font-weight: bold;'>{done} / {assigned}</span><br>
                            <small style='color: #4a5568; font-weight: 500;'>Selesai</small>
                        </div>
                    """, unsafe_allow_html=True)

        st.divider()
        st.subheader("🖼️ Galeri Kad Laporan Calon")
        
        apps_df = pd.read_sql("SELECT name, proposal_title, institution, photo FROM applicants ORDER BY name ASC", engine)
        
        if not apps_df.empty:
            cols = st.columns(3)
            for i, row in apps_df.iterrows():
                app_name = row['name']
                
                photo_html = ""
                try:
                    if pd.notna(row['photo']):
                        b64_img = base64.b64encode(row['photo']).decode("utf-8")
                        photo_html = f"<img src='data:image/jpeg;base64,{b64_img}' style='width:100%; height:180px; object-fit:cover; border-radius:6px; margin-bottom:15px;'/>"
                except:
                    pass
                
                if not photo_html:
                    photo_html = "<div style='width:100%; height:180px; background-color:#E2E8F0; border-radius:6px; margin-bottom:15px; display:flex; align-items:center; justify-content:center; color:#94A3B8; font-size:12px;'>Tiada Gambar</div>"
                
                with cols[i % 3]:
                    st.markdown(f"""
                        <div style='background-color:#F8FAFC; padding:15px; border-radius:8px; border:1px solid #E2E8F0; margin-bottom:15px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); text-align:center;'>
                            {photo_html}
                            <h4 style='color:#1E293B; margin-top:0; margin-bottom:10px; font-size:16px;'>{app_name}</h4>
                            <p style='color:#475569; font-size:13px; margin-bottom:5px;'>ID: {row['proposal_title'] or 'Tiada'}</p>
                            <p style='color:#475569; font-size:13px; margin-bottom:15px;'>Jawatan: {row['institution'] or 'Tiada'}</p>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button("📄 Lihat Kad Laporan", key=f"btn_rc_dash_{i}", use_container_width=True):
                        st.session_state.report_card_app = app_name
                        st.rerun()
        else:
            st.info("Tiada calon didaftarkan.")

    except Exception as e:
        st.error(f"🚨 Ralat Papan Pemuka: {str(e)}")

def render_report_card(engine, app_name):
    app_data = pd.read_sql(text("SELECT * FROM applicants WHERE name=:n"), engine, params={"n":app_name})
    if app_data.empty:
        st.error("Calon tidak dijumpai.")
        if st.button("⬅️ Kembali"): st.session_state.report_card_app = None; st.rerun()
        return
        
    app_row = app_data.iloc[0]
    info = {}
    try:
        info = json.loads(app_row['additional_info']) if app_row['additional_info'] else {}
    except: pass
    
    if st.button("⬅️ Kembali"): st.session_state.report_card_app = None; st.rerun()
    st.divider()

    # HTML Report Generation for Print (Inside iframe)
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Kad Laporan APC - {app_row['name']}</title>
<style>
    body {{ font-family: Arial, sans-serif; color: black; background: white; padding: 10px; font-size: 12px; }}
    h3 {{ font-size: 14px; margin-bottom: 10px; }}
    h4 {{ font-size: 13px; margin-top: 15px; margin-bottom: 5px; }}
    table {{ width: 100%; border-collapse: collapse; margin-bottom: 10px; font-size: 11px; }}
    th, td {{ border: 1px solid black; padding: 4px 6px; text-align: left; }}
    th {{ background-color: #f2f2f2; }}
    .center-text {{ text-align: center; }}
    .print-btn {{
        background-color: #FF4B4B; color: white; padding: 8px 16px; border: none;
        border-radius: 4px; font-size: 14px; cursor: pointer; font-weight: bold;
        margin-bottom: 10px;
    }}
    .print-btn:hover {{ background-color: #ff3333; }}
    @media print {{
        @page {{ size: A4; margin: 10mm; }}
        body {{ padding: 0; }}
        .no-print {{ display: none !important; }}
    }}
</style>
</head>
<body>
<div class="no-print" style="text-align: right;">
    <button class="print-btn" onclick="window.print()">🖨️ Cetak Kad Laporan (PDF)</button>
</div>
<h3 class="center-text">PENILAIAN ANUGERAH PERKHIDMATAN CEMERLANG, AKADEMI SAINS MALAYSIA (APC-ASM)</h3>
<br>
<table>
<tr><td width="40%">Tahun Penilaian</td><td>: {info.get('tahun_penilaian', '')}</td></tr>
<tr><td>Kumpulan Perkhidmatan</td><td>: {info.get('kump_perkhidmatan', '')}</td></tr>
<tr><td>Nama Kakitangan</td><td>: {app_row['name']}</td></tr>
<tr><td>No. Pekerja (ID ASM)</td><td>: {app_row['proposal_title']}</td></tr>
<tr><td>Tarikh Bermula Berkhidmat</td><td>: {info.get('tarikh_mula', '')}</td></tr>
<tr><td>Tempoh Berkhidmat pada 31 Disember</td><td>: {info.get('tempoh_khidmat', '')}</td></tr>
<tr><td>Rekod Penerimaan APC</td><td>: {info.get('rekod_apc', 'Tiada')}</td></tr>
</table>
<br>
<h4>SYARAT KELAYAKAN APC-ASM</h4>
<table>
<tr><th>Syarat</th><th>YA</th><th>TIDAK</th><th>CATATAN</th></tr>
<tr><td>Kakitangan bertaraf Tetap / Contract of Service (CoS)</td><td class="center-text">{'✔' if info.get('s_tetap') else ''}</td><td class="center-text">{'✔' if not info.get('s_tetap') else ''}</td><td></td></tr>
<tr><td>Kakitangan adalah di Gred 14 dan ke bawah</td><td class="center-text">{'✔' if info.get('s_gred14') else ''}</td><td class="center-text">{'✔' if not info.get('s_gred14') else ''}</td><td>{app_row['info_link']}</td></tr>
<tr><td>Telah berkhidmat sekurang-kurangnya satu (1) tahun pada tahun penilaian</td><td class="center-text">{'✔' if info.get('s_setahun') else ''}</td><td class="center-text">{'✔' if not info.get('s_setahun') else ''}</td><td></td></tr>
<tr><td>Bebas daripada tindakan disiplin / tatatertib pada tahun penilaian</td><td class="center-text">{'✔' if info.get('s_disiplin') else ''}</td><td class="center-text">{'✔' if not info.get('s_disiplin') else ''}</td><td></td></tr>
<tr><td>Markah Penilaian Prestasi Tahunan (LNPT) adalah 85% dan ke atas pada tahun penilaian</td><td class="center-text">{'✔' if info.get('s_lnpt_semasa') else ''}</td><td class="center-text">{'✔' if not info.get('s_lnpt_semasa') else ''}</td><td>{info.get('m_lnpt_semasa', '')}</td></tr>
<tr><td>Memperoleh markah LNPT 85% dan ke atas untuk tahun sebelum tahun penilaian</td><td class="center-text">{'✔' if info.get('s_lnpt_sebelum') else ''}</td><td class="center-text">{'✔' if not info.get('s_lnpt_sebelum') else ''}</td><td>{info.get('m_lnpt_sebelum', '')}</td></tr>
</table>
<br>
<h4>PENILAIAN 360 DARJAH APC-ASM</h4>
<table>
<tr><th>No</th><th>Kumpulan Pegawai</th><th>Pegawai Penilai</th><th>Markah</th></tr>
"""
    
    revs = pd.read_sql(text("SELECT r.reviewer_username, rev.full_name, r.responses, rev.kumpulan_pegawai FROM reviews r LEFT JOIN reviewers rev ON r.reviewer_username = rev.username WHERE r.applicant_name=:n"), engine, params={"n":app_name})
    
    total_score = 0
    max_score = 0
    for idx, r_row in revs.iterrows():
        try:
            res = json.loads(r_row['responses'])
            score = int(res.get('total_score', 0))
        except: score = 0
        
        total_score += score
        max_score += 25
        
        kump = r_row.get('kumpulan_pegawai')
        display_kump = kump if kump else 'PENILAI'
        
        html_content += f"<tr><td>{idx+1}</td><td>{display_kump}</td><td>{r_row['full_name']}</td><td class='center-text'>{score} / 25</td></tr>\n"
        
    html_content += f"""
<tr><th colspan="3" style="text-align:right;">Jumlah Markah Penilaian 360 Darjah</th><th class="center-text">{total_score} / {max_score if max_score > 0 else 100}</th></tr>
</table>
<br><br><br>
<table style="border:none;">
<tr style="border:none;">
<td style="border:none; width:50%;">Disediakan oleh:<br><br><br><br>___________________________<br>NAMA<br>JAWATAN<br>URUS SETIA PROGRAM PENGIKTIRAFAN PEGAWAI</td>
<td style="border:none; width:50%;">Disahkan oleh:<br><br><br><br>___________________________<br>NAMA<br>JAWATAN<br>URUS SETIA PROGRAM PENGIKTIRAFAN PEGAWAI</td>
</tr>
</table>
</body>
</html>
"""
    
    # Render the entire HTML (preview + print logic) cleanly inside an iframe
    st.components.v1.html(html_content, height=1000, scrolling=True)



# --- 4. RENDER MANAGEMENT ---
def render_management(menu, engine, hash_password, delete_item):
    if st.session_state.get('report_card_app'):
        render_report_card(engine, st.session_state.report_card_app)
        return

    if menu == "Pengurusan Penilaian":
        apps_df = pd.read_sql("SELECT * FROM applicants ORDER BY id ASC", engine)
        st.header(f"📋 Pengurusan Penilaian (Jumlah: {len(apps_df)})")
        
        c1, c2 = st.columns(2)
        if c1.button("📚 Tambah Calon Berkelompok", use_container_width=True): bulk_add_applicants_dialog(engine)
        
        if st.button("➕ Tambah Calon Baru", use_container_width=True):
            add_applicant_dialog(engine)

        revs_df = pd.read_sql("SELECT username, full_name FROM reviewers", engine)
        assign_df = pd.read_sql("SELECT * FROM applicant_assignments", engine)
        rev_map = dict(zip(revs_df['username'], revs_df['full_name']))

        for idx, row in apps_df.iterrows():
            with st.container(border=True):
                ca, cb, cc = st.columns([0.1, 2.2, 2.3])
                ca.write(f"{idx+1}")
                asm_id_str = row['proposal_title'] if row['proposal_title'] else 'Tiada ID'
                cb.write(f"**{row['name']}** ({asm_id_str})")
                cb.caption(f"💼 Jawatan: {row['institution'] or 'N/A'} | Gred: {row['info_link'] or 'N/A'} | Bahagian: {row['remarks'] or 'N/A'}")
                
                ced1, ced2, ced3 = cc.columns([1, 1.4, 1])
                if ced1.button("📝 Sunting", key=f"ed_ap_{row['id']}", help="Sunting Calon & Syarat"): edit_applicant_dialog(engine, row)
                if ced2.button("📄 Kad Laporan", key=f"rc_ap_{row['id']}", help="Lihat Kad Laporan"):
                    st.session_state.report_card_app = row['name']
                    st.rerun()
                if ced3.button("🗑️ Padam", key=f"del_ap_{row['id']}", help="Padam Calon"): delete_item("applicants", row['id'])
                
                curr = assign_df[assign_df['applicant_name'] == row['name']]['reviewer_username'].tolist()
                sel = st.multiselect("Tugaskan Penilai:", options=list(rev_map.keys()), default=curr, format_func=lambda x: rev_map.get(x), key=f"p1_sel_{row['id']}")
                if st.button("💾 Simpan Tugasan", key=f"p1_sv_{row['id']}"):
                    with engine.begin() as conn:
                        conn.execute(text("DELETE FROM applicant_assignments WHERE applicant_name = :a"), {"a":row['name']})
                        for r in sel:
                            conn.execute(text("INSERT INTO applicant_assignments (applicant_name, reviewer_username) VALUES (:a, :r)"), {"a":row['name'], "r":r})
                    st.success("✅ Telah Disimpan!"); time.sleep(0.5); st.rerun()

    elif menu == "Pengurusan Penilai":
        st.header("👤 Pengurusan Penilai")
        
        with st.expander("🔐 Tukar Kata Laluan Admin"):
            with st.form("change_admin_pass"):
                new_admin_pass = st.text_input("Kata Laluan Admin Baru", type="password")
                if st.form_submit_button("Kemaskini Kata Laluan Admin", type="primary"):
                    if new_admin_pass.strip():
                        with engine.begin() as conn:
                            # Update kata laluan untuk user yang sedang login (Admin)
                            conn.execute(text("UPDATE users SET password_hash=:p WHERE username=:u"), 
                                         {"p": hash_password(new_admin_pass), "u": st.session_state.username})
                        st.success("✅ Kata laluan Admin telah berjaya dikemaskini!")
                        time.sleep(1)
                        st.rerun()

        st.divider()
        st.subheader("👥 Senarai Penilai")
        
        with st.expander("✉️ Templat Emel Arahan (Untuk dihantar kepada Penilai)"):
            st.markdown("Sila salin templat di bawah dan kemas kini butiran (Pautan, Nama Pengguna, Kata Laluan) sebelum menghantarnya kepada Pegawai Penilai yang telah didaftarkan:")
            st.code("""Tajuk: Jemputan Sebagai Pegawai Penilai untuk Anugerah Perkhidmatan Cemerlang (APC) ASM 2025

YBhg. Prof./Datuk/Dato'/Dr./Tuan/Puan,

Dengan segala hormatnya perkara di atas adalah dirujuk.

Dimaklumkan bahawa anda telah dilantik sebagai Pegawai Penilai bagi Penilaian 360 Darjah untuk Anugerah Perkhidmatan Cemerlang (APC) ASM 2025. 

Sila log masuk ke dalam Sistem Penilaian APC-ASM menggunakan butiran berikut untuk memulakan sesi penilaian:

Pautan Sistem: [Sila masukkan pautan URL sistem]
Nama Pengguna: [Username Penilai]
Kata Laluan: [Kata Laluan Penilai]

Kerjasama dan perhatian YBhg. Prof./Datuk/Dato'/Dr./Tuan/Puan amatlah dihargai.

Sekian, terima kasih.

Urus Setia Program Pengiktirafan Pegawai
Akademi Sains Malaysia""", language="text")
        
        if st.button("📚 Tambah Penilai Berkelompok", use_container_width=True): bulk_add_reviewers_dialog(engine, hash_password)
        
        with st.expander("➕ Tambah Penilai Individu"):
            with st.form("add_rev_form", clear_on_submit=True):
                n = st.text_input("Nama Penuh")
                u = st.text_input("Nama Pengguna (Username)")
                kump_options = ["", "FELO ASM", "KETUA PEGAWAI EKSEKUTIF", "KETUA PEGAWAI OPERASI", "KETUA PEGAWAI STRATEGIK", "KETUA PEGAWAI Hal Ehwal Antarabangsa & Komunikasi", "PENGURUSAN DAN PROFESIONAL", "PELAKSANA"]
                kump = st.selectbox("Kumpulan Pegawai", kump_options)
                p = st.text_input("Kata Laluan", type="password")
                if st.form_submit_button("Simpan Penilai"):
                    if n and u and p:
                        with engine.begin() as conn:
                            conn.execute(text("INSERT INTO reviewers (username, full_name, password_hash, kumpulan_pegawai) VALUES (:u, :n, :p, :k) ON CONFLICT DO NOTHING"), {"u":u.strip(), "n":n.strip(), "p":hash_password(p), "k":kump})
                        st.cache_resource.clear(); st.success("✅ Telah Ditambah!"); time.sleep(1); st.rerun()

        revs = pd.read_sql("SELECT * FROM reviewers ORDER BY id ASC", engine)
        for _, r in revs.iterrows():
            with st.container(border=True):
                ca, cb = st.columns([3.5, 1.5])
                ca.write(f"**{r['full_name']}** ({r['username']})")
                
                # Check if reviewer has locked forms
                locked_count = pd.read_sql(text("SELECT COUNT(*) FROM reviews WHERE reviewer_username = :u AND is_final = TRUE"), engine, params={"u": r['username']}).iloc[0,0]
                if locked_count > 0:
                    ca.caption(f"🔒 {locked_count} borang penilaian telah dikunci (Final)")
                
                # --- BUTANG UNTUK REVIEWER ---
                ced1, ced2, ced3 = cb.columns(3)
                if ced1.button("📝", key=f"ed_rev_{r['id']}", help="Sunting Penilai"): edit_reviewer_dialog(engine, r, hash_password)
                if ced2.button("🗑️", key=f"del_rev_{r['id']}", help="Padam Penilai"): delete_item("reviewers", r['id'])
                
                if locked_count > 0:
                    if ced3.button("🔓", key=f"unl_rev_{r['id']}", help="Buka Kunci Borang (Unlock)"):
                        with engine.begin() as conn:
                            conn.execute(text("UPDATE reviews SET is_final = FALSE WHERE reviewer_username = :u"), {"u": r['username']})
                        st.cache_resource.clear()
                        st.success("✅ Borang telah dibuka kunci!"); time.sleep(1); st.rerun()
