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

@st.dialog("📝 Sunting Calon")
def edit_applicant_dialog(engine, app_data):
    with st.form("edit_app_form"):
        new_name = st.text_input("Nama Penuh", value=app_data['name'])
        new_inst = st.text_input("Jawatan", value=app_data['institution'])
        
        # Keep old values for hidden fields to avoid DB constraint issues
        new_title = app_data.get('proposal_title', '')
        new_link = app_data.get('info_link', '')
        new_rem = app_data.get('remarks', '')
        
        if st.form_submit_button("Kemaskini Calon", type="primary"):
            with engine.begin() as conn:
                conn.execute(text("UPDATE applicants SET name=:n, proposal_title=:t, institution=:i, info_link=:l, remarks=:r WHERE id=:id"),
                             {"n":new_name, "t":new_title, "i":new_inst, "l":new_link, "r":new_rem, "id":app_data['id']})
            st.cache_resource.clear(); st.success("✅ Telah Dikemas kini!"); time.sleep(1); st.rerun()

@st.dialog("📝 Sunting Penilai")
def edit_reviewer_dialog(engine, rev_data, hash_password):
    with st.form("edit_rev_form"):
        new_name = st.text_input("Nama Penuh", value=rev_data['full_name'])
        new_user = st.text_input("Nama Pengguna (Username)", value=rev_data['username'], disabled=True) 
        new_pass = st.text_input("Kata Laluan Baru (Biarkan kosong jika tiada perubahan)", type="password")
        if st.form_submit_button("Kemaskini Penilai", type="primary"):
            with engine.begin() as conn:
                if new_pass.strip():
                    conn.execute(text("UPDATE reviewers SET full_name=:n, password_hash=:p WHERE id=:id"),
                                 {"n":new_name, "p":hash_password(new_pass), "id":rev_data['id']})
                else:
                    conn.execute(text("UPDATE reviewers SET full_name=:n WHERE id=:id"),
                                 {"n":new_name, "id":rev_data['id']})
            st.cache_resource.clear(); st.success("✅ Telah Dikemas kini!"); time.sleep(1); st.rerun()

@st.dialog("📚 Tambah Calon Berkelompok")
def bulk_add_applicants_dialog(engine):
    st.markdown("**Format:** `Nama Calon, Jawatan` (Satu baris untuk setiap calon)")
    raw_data = st.text_area("Tampal senarai calon di sini", height=200)
    if st.button("Import Calon", type="primary"):
        lines = [line.strip() for line in raw_data.split('\n') if line.strip()]
        with engine.begin() as conn:
            for line in lines:
                parts = [p.strip() for p in line.split(',')]
                if len(parts) >= 1:
                    conn.execute(text("INSERT INTO applicants (name, proposal_title, institution, info_link, remarks) VALUES (:n, :t, :i, :l, :r) ON CONFLICT (name) DO NOTHING"), 
                                 {"n":parts[0], "t":"", "i":parts[1] if len(parts)>1 else "", "l":"", "r":""})
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


def render_dashboard(engine):
    st.header("📊 Penjejak Penilaian Semasa")
    if st.button("🔄 Segerakkan Data Papan Pemuka"):
        st.cache_resource.clear()
        st.rerun()
        
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
        st.subheader("🏁 Papan Pendahulu (Kedudukan)")
        p2_reviews = pd.read_sql("SELECT applicant_name, responses FROM reviews", engine)
        
        if not p2_reviews.empty:
            leaderboard_data = []
            for _, r_row in p2_reviews.iterrows():
                try:
                    res = json.loads(r_row['responses'])
                    leaderboard_data.append({
                        "Calon": r_row['applicant_name'], 
                        "Markah": int(res.get('total_score', 0))
                    })
                except: continue
            
            if leaderboard_data:
                ld_df = pd.DataFrame(leaderboard_data)
                final_ld = ld_df.groupby("Calon")["Markah"].mean().sort_values(ascending=False).reset_index()
                final_ld.index += 1
                st.table(final_ld)
            else: st.info("Belum ada markah dikira.")
        else: st.info("Menunggu penghantaran...")

    except Exception as e:
        st.error(f"🚨 Ralat Papan Pemuka: {str(e)}")

# --- 4. RENDER MANAGEMENT ---
def render_management(menu, engine, hash_password, delete_item):
    if menu == "Pengurusan Penilaian":
        apps_df = pd.read_sql("SELECT * FROM applicants ORDER BY id ASC", engine)
        st.header(f"📋 Pengurusan Penilaian (Jumlah: {len(apps_df)})")
        
        c1, c2 = st.columns(2)
        if c1.button("📚 Tambah Calon Berkelompok", use_container_width=True): bulk_add_applicants_dialog(engine)
        
        with st.expander("➕ Tambah Calon Baru"):
            with st.form("add_app_single", clear_on_submit=True):
                n = st.text_input("Nama Calon*")
                i = st.text_input("Jawatan")
                if st.form_submit_button("Simpan Calon", type="primary"):
                    if n:
                        with engine.begin() as conn:
                            conn.execute(text("INSERT INTO applicants (name, proposal_title, institution, info_link, remarks) VALUES (:n, :t, :i, :l, :r)"), {"n":n, "t":"", "i":i, "l":"", "r":""})
                        st.cache_resource.clear(); st.success("✅ Telah Ditambah!"); time.sleep(1); st.rerun()

        revs_df = pd.read_sql("SELECT username, full_name FROM reviewers", engine)
        assign_df = pd.read_sql("SELECT * FROM applicant_assignments", engine)
        rev_map = dict(zip(revs_df['username'], revs_df['full_name']))

        for idx, row in apps_df.iterrows():
            with st.container(border=True):
                ca, cb, cc = st.columns([0.1, 3, 1.2])
                ca.write(f"{idx+1}")
                cb.write(f"**{row['name']}**")
                cb.caption(f"💼 Jawatan: {row['institution'] if row['institution'] else 'N/A'}")
                
                ced1, ced2 = cc.columns(2)
                if ced1.button("📝 Sunting", key=f"ed_ap_{row['id']}"): edit_applicant_dialog(engine, row)
                if ced2.button("🗑️", key=f"del_ap_{row['id']}"): delete_item("applicants", row['id'])
                
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
        
        if st.button("📚 Tambah Penilai Berkelompok", use_container_width=True): bulk_add_reviewers_dialog(engine, hash_password)
        
        with st.expander("➕ Tambah Penilai Individu"):
            with st.form("add_rev_form", clear_on_submit=True):
                n = st.text_input("Nama Penuh")
                u = st.text_input("Nama Pengguna (Username)")
                p = st.text_input("Kata Laluan", type="password")
                if st.form_submit_button("Simpan Penilai"):
                    if n and u and p:
                        with engine.begin() as conn:
                            conn.execute(text("INSERT INTO reviewers (username, full_name, password_hash) VALUES (:u, :n, :p) ON CONFLICT DO NOTHING"), {"u":u.strip(), "n":n.strip(), "p":hash_password(p)})
                        st.cache_resource.clear(); st.success("✅ Telah Ditambah!"); time.sleep(1); st.rerun()

        revs = pd.read_sql("SELECT * FROM reviewers ORDER BY id ASC", engine)
        for _, r in revs.iterrows():
            with st.container(border=True):
                ca, cb = st.columns([4, 1.2])
                ca.write(f"**{r['full_name']}** ({r['username']})")
                
                # --- BUTANG EDIT UNTUK REVIEWER ---
                ced1, ced2 = cb.columns(2)
                if ced1.button("📝", key=f"ed_rev_{r['id']}"): edit_reviewer_dialog(engine, r, hash_password)
                if ced2.button("🗑️", key=f"del_rev_{r['id']}"): delete_item("reviewers", r['id'])
