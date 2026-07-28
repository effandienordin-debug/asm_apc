import streamlit as st
import pandas as pd
import json
from sqlalchemy import text

# --- 1. CACHED DATA FETCHING ---
@st.cache_resource(ttl=60)
def get_assigned_applicants(_engine, username):
    table_assign = "applicant_assignments"
    query = text(f"""
        SELECT a.* FROM applicants a
        JOIN {table_assign} aa ON a.name = aa.applicant_name
        WHERE aa.reviewer_username = :u
    """)
    df = pd.read_sql(query, _engine, params={"u": username})
    return df

# --- 2. RENDER REVIEW FORM & GALLERY ---
def render_review_form(engine, get_malaysia_time, render_apc_evaluation_form):
    table_reviews = "reviews"
    phase_name = "Penilaian 360 Darjah untuk calon APC-2025"

    st.markdown(f"## 📋 {phase_name}")
    st.divider()

    with st.container(border=True):
        col_icon, col_greet = st.columns([1, 10])
        col_icon.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=65)
        col_greet.markdown(f"### Selamat kembali, {st.session_state.full_name}!")
        col_greet.caption(f"🔬 Log masuk sebagai: {st.session_state.username} | Peranan: Penilai | {phase_name}")

    st.warning("""**Berikut nota penting yang perlu diambil perhatian bagi setiap penilai:**
• Sila isi ruang kosong dengan SATU NOMBOR berdasarkan skala 1 hingga 5 (tidak memuaskan-cemerlang) dan terdapat lima (5) aspek yang akan dinilai.
• Tidak berkongsi apa-apa maklumat berkaitan Penilaian 360° (APC-ASM) ini kepada mana-mana kakitangan/individu. Penilaian perlu dilakukan secara sulit supaya proses penilaian dapat dilaksanakan dengan lebih objektif, fokus dan teliti.""")

    is_locked = pd.read_sql(text(f"SELECT COUNT(*) FROM {table_reviews} WHERE reviewer_username = :u AND is_final = TRUE"),
                            engine, params={"u": st.session_state.username}).iloc[0,0] > 0

    if st.session_state.get('active_review_app'):
        # --- INDIVIDUAL REVIEW PAGE ---
        name = st.session_state.active_review_app
        app = pd.read_sql(text("SELECT * FROM applicants WHERE name = :n"), engine, params={"n": name}).iloc[0]
        rev = pd.read_sql(text(f"SELECT * FROM {table_reviews} WHERE reviewer_username = :u AND applicant_name = :a"),
                          engine, params={"u": st.session_state.username, "a": name})

        prev_resp = {}
        if not rev.empty and rev.iloc[0]['responses']:
            try: prev_resp = json.loads(rev.iloc[0]['responses'])
            except: pass

        with st.container(border=True):
            col_img, col_txt = st.columns([1, 4])
            if app['photo']: col_img.image(bytes(app['photo']), width=150)

            col_txt.subheader(name)
            col_txt.markdown(f"**Jawatan:** {app['institution'] if app['institution'] else 'N/A'}")

        # --- EVALUATION FORM ---
        res = render_apc_evaluation_form(prev_resp, rev.iloc[0].to_dict() if not rev.empty else {}, disabled=is_locked)

        # BUTTONS (Extracted from form for flexibility)
        if not is_locked:
            if st.button("💾 Simpan Draf", use_container_width=True, type="primary"):
                is_incomplete = False
                if is_incomplete:
                    st.error("🚨 Sila isikan markah sebelum menyimpan.")
                else:
                    with engine.begin() as conn:
                        if not rev.empty:
                            conn.execute(text(f"UPDATE {table_reviews} SET responses=:r, final_recommendation=:fr, overall_justification=:oj, updated_at=:t WHERE id=:id"),
                                         {"r":json.dumps(res["responses"]), "fr":res["recommendation"], "oj":res["justification"], "t":get_malaysia_time(), "id":int(rev.iloc[0]['id'])})
                        else:
                            conn.execute(text(f"INSERT INTO {table_reviews} (reviewer_username, applicant_name, responses, final_recommendation, overall_justification, submitted_at, updated_at) VALUES (:u, :a, :r, :fr, :oj, :t, :t)"),
                                         {"u":st.session_state.username, "a":name, "r":json.dumps(res["responses"]), "fr":res["recommendation"], "oj":res["justification"], "t":get_malaysia_time()})
                    
                    st.cache_resource.clear()
                    st.toast("✅ Draf disimpan!")
                    st.success("Draf dikemas kini. Anda boleh teruskan suntingan atau kembali ke senarai.")
                    st.rerun() # Stay on the page

            if st.button("🚀 Hantar Penilaian Akhir", use_container_width=True, type="secondary"):
                is_incomplete = False
                if is_incomplete:
                    st.error("🚨 Sila isikan markah sebelum menghantar.")
                else:
                    with engine.begin() as conn:
                        if not rev.empty:
                            conn.execute(text(f"UPDATE {table_reviews} SET responses=:r, final_recommendation=:fr, overall_justification=:oj, updated_at=:t, is_final=TRUE WHERE id=:id"),
                                         {"r":json.dumps(res["responses"]), "fr":res["recommendation"], "oj":res["justification"], "t":get_malaysia_time(), "id":int(rev.iloc[0]['id'])})
                        else:
                            conn.execute(text(f"INSERT INTO {table_reviews} (reviewer_username, applicant_name, responses, final_recommendation, overall_justification, submitted_at, updated_at, is_final) VALUES (:u, :a, :r, :fr, :oj, :t, :t, TRUE)"),
                                         {"u":st.session_state.username, "a":name, "r":json.dumps(res["responses"]), "fr":res["recommendation"], "oj":res["justification"], "t":get_malaysia_time()})
                    st.cache_resource.clear()
                    st.toast("✅ Penilaian Dihantar!")
                    st.session_state.active_review_app = None
                    st.rerun()

        if st.button("⬅️ Kembali ke Senarai Calon", use_container_width=True):
            st.session_state.active_review_app = None
            st.rerun()
            
    else:
        # --- GALLERY VIEW ---
        apps = get_assigned_applicants(engine, st.session_state.username)

        if apps.empty:
            st.info(f"You currently have no applicants assigned to you for {phase_name}.")
        else:
            rev_records = pd.read_sql(text(f"SELECT applicant_name, responses, final_recommendation, overall_justification FROM {table_reviews} WHERE reviewer_username = :u"),
                                      engine, params={"u": st.session_state.username})
            reviews_lookup = rev_records.set_index('applicant_name').to_dict('index')

            st.subheader(f"Galeri Calon yang Ditugaskan ({phase_name})")
            for i in range(0, len(apps), 4):
                cols = st.columns(4)
                for j in range(4):
                    if i+j < len(apps):
                        row = apps.iloc[i+j]
                        with cols[j]:
                            with st.container(border=True):
                                if row['photo']: st.image(bytes(row['photo']), use_container_width=True)
                                else: st.image("https://cdn-icons-png.flaticon.com/512/149/149071.png", use_container_width=True)

                                st.write(f"**{row['name']}**")
                                st.caption(f"💼 Jawatan: {row['institution'] if row['institution'] else 'N/A'}")

                                if row['name'] in reviews_lookup:
                                    r_data = reviews_lookup[row['name']]
                                    st.markdown(f"**Status:** :green[✅ Selesai]")
                                    
                                    # --- Papar Markah ---
                                    try:
                                        res_data = json.loads(r_data.get('responses', '{}'))
                                        total = res_data.get('total_score', 0)
                                        st.markdown(f"**Jumlah Markah:** {total} / 25")
                                    except: pass

                                    # Removed justification/remarks display
                                else:
                                    st.markdown("**Status:** :orange[⏳ Menunggu Penilaian]")

                                if st.button("Nilai/Sunting", key=f"go_{row['id']}", use_container_width=True, disabled=is_locked):
                                    st.session_state.active_review_app = row['name']
                                    st.rerun()

            if not is_locked and len(reviews_lookup) >= len(apps) > 0:
                st.divider()
                if st.button(f"🚀 KUNCI KESEMUA PENILAIAN ({phase_name})", type="primary", use_container_width=True):
                    with engine.begin() as conn:
                        conn.execute(text(f"UPDATE {table_reviews} SET is_final = TRUE WHERE reviewer_username = :u"), {"u": st.session_state.username})
                    st.cache_resource.clear(); st.balloons(); st.rerun()
