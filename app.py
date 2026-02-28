import sys
import os
import re
import sqlite3
import datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

import hdate
import streamlit as st
from workflows.parasha_workflow import torah_workflow, torah_daily_workflow

DB_FILE = "parasha_history.db"

PARSHA_MAP = {
    "בראשית": "Bereishit", "נח": "Noach", "לך לך": "Lech Lecha",
    "וירא": "Vayera", "חיי שרה": "Chayei Sarah", "תולדות": "Toldot",
    "ויצא": "Vayetzei", "וישלח": "Vayishlach", "וישב": "Vayeshev",
    "מקץ": "Miketz", "ויגש": "Vayigash", "ויחי": "Vayechi",
    "שמות": "Shemot", "וארא": "Vaera", "בא": "Bo",
    "בשלח": "Beshalach", "יתרו": "Yitro", "משפטים": "Mishpatim",
    "תרומה": "Terumah", "תצוה": "Tetzaveh", "כי תשא": "Ki Tisa",
    "ויקהל": "Vayakhel", "פקודי": "Pekudei", "ויקרא": "Vayikra",
    "צו": "Tzav", "שמיני": "Shemini", "תזריע": "Tazria",
    "מצורע": "Metzora", "אחרי מות": "Acharei Mot", "קדושים": "Kedoshim",
    "אמור": "Emor", "בהר": "Behar", "בחוקותי": "Bechukotai",
    "במדבר": "Bamidbar", "נשא": "Naso", "בהעלותך": "Beha'alotcha",
    "שלח": "Shelach", "קרח": "Korach", "חקת": "Chukat",
    "בלק": "Balak", "פינחס": "Pinchas", "מטות": "Matot",
    "מסעי": "Masei", "דברים": "Devarim", "ואתחנן": "Vaetchanan",
    "עקב": "Eikev", "ראה": "Re'eh", "שופטים": "Shoftim",
    "כי תצא": "Ki Teitzei", "כי תבוא": "Ki Tavo", "נצבים": "Nitzavim",
    "וילך": "Vayeilech", "האזינו": "Haazinu", "וזאת הברכה": "Vezot Habracha"
}

def get_current_parsha() -> str:
    today = datetime.date.today()
    h = hdate.HDateInfo(today)
    hebrew_name = str(h.parasha).strip()
    return PARSHA_MAP.get(hebrew_name, hebrew_name)

# --- Database ---

def init_db():
    conn = sqlite3.connect(DB_FILE)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            entry_type TEXT NOT NULL DEFAULT 'weekly',
            parasha TEXT NOT NULL,
            theme TEXT,
            summary TEXT,
            research TEXT,
            commentary TEXT,
            script TEXT,
            dailies TEXT,
            dvar_torah TEXT
        )
    """)
    for col in ["entry_type TEXT NOT NULL DEFAULT 'weekly'", "dailies TEXT", "dvar_torah TEXT"]:
        try:
            conn.execute(f"ALTER TABLE entries ADD COLUMN {col}")
        except Exception:
            pass
    conn.commit()
    conn.close()

def save_entry(parasha, entry_type, theme, research, commentary,
               script="", dailies="", dvar_torah=""):
    summary = commentary[:300].strip().replace("\n", " ") + "..." if commentary else ""
    conn = sqlite3.connect(DB_FILE)
    conn.execute(
        """INSERT INTO entries
           (created_at, entry_type, parasha, theme, summary, research, commentary, script, dailies, dvar_torah)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (datetime.datetime.now().isoformat(), entry_type, parasha, theme,
         summary, research, commentary, script, dailies, dvar_torah)
    )
    conn.commit()
    conn.close()

def load_all_entries():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT id, created_at, entry_type, parasha, theme, summary FROM entries ORDER BY created_at DESC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def load_entry(entry_id):
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT * FROM entries WHERE id = ?", (entry_id,)).fetchone()
    conn.close()
    return dict(row) if row else None

def delete_entry(entry_id):
    conn = sqlite3.connect(DB_FILE)
    conn.execute("DELETE FROM entries WHERE id = ?", (entry_id,))
    conn.commit()
    conn.close()

def load_latest_entry_id():
    conn = sqlite3.connect(DB_FILE)
    row = conn.execute("SELECT id FROM entries ORDER BY created_at DESC LIMIT 1").fetchone()
    conn.close()
    return row[0] if row else None

# --- Init ---
init_db()

st.set_page_config(page_title="📖 Weekly Parasha Agent", layout="wide")

# --- Custom CSS for anchor nav and day cards ---
st.markdown("""
<style>
.section-anchor { padding-top: 60px; margin-top: -60px; }
.day-card {
    border-left: 4px solid #7c6af7;
    border-radius: 4px;
    padding: 16px 20px;
    margin-bottom: 16px;
}
.nav-bar {
    position: sticky;
    top: 0;
    background: #0e1117;
    padding: 8px 0;
    z-index: 999;
    border-bottom: 1px solid #333;
    margin-bottom: 16px;
}
</style>
""", unsafe_allow_html=True)

st.title("📖 Weekly Parasha Study")

if "content" not in st.session_state:
    st.session_state.content = None
if "view" not in st.session_state:
    st.session_state.view = "generate"

# --- Top navigation ---
col_nav1, col_nav2 = st.columns([1, 1])
with col_nav1:
    if st.button("⚡ Generate", use_container_width=True,
                 type="primary" if st.session_state.view == "generate" else "secondary"):
        st.session_state.view = "generate"
        st.session_state.content = None
        st.rerun()
with col_nav2:
    if st.button("📚 History", use_container_width=True,
                 type="primary" if st.session_state.view == "history" else "secondary"):
        st.session_state.view = "history"
        st.rerun()

st.divider()

# =====================
# HISTORY VIEW
# =====================
if st.session_state.view == "history":
    st.subheader("📚 All Parasha Entries")
    entries = load_all_entries()

    if not entries:
        st.info("No entries yet.")
    else:
        hcol1, hcol2, hcol3, hcol4, hcol5, hcol6, hcol7 = st.columns([2, 2, 1, 2, 4, 1, 1])
        hcol1.markdown("**Date**")
        hcol2.markdown("**Parasha**")
        hcol3.markdown("**Type**")
        hcol4.markdown("**Theme**")
        hcol5.markdown("**Summary**")
        hcol6.markdown("**View**")
        hcol7.markdown("**Delete**")
        st.divider()

        for entry in entries:
            col1, col2, col3, col4, col5, col6, col7 = st.columns([2, 2, 1, 2, 4, 1, 1])
            col1.write(entry["created_at"][:10])
            col2.write(entry["parasha"])
            etype = entry.get("entry_type", "weekly")
            col3.write("📅" if etype == "daily" else "📖")
            col4.write(entry.get("theme") or "—")
            col5.write(entry["summary"])
            with col6:
                if st.button("View", key=f"view_{entry['id']}"):
                    st.session_state.content = load_entry(entry["id"])
                    st.session_state.view = "generate"
                    st.rerun()
            with col7:
                if st.button("🗑️", key=f"delete_{entry['id']}", help="Delete this entry"):
                    delete_entry(entry["id"])
                    if st.session_state.content and st.session_state.content.get("id") == entry["id"]:
                        st.session_state.content = None
                    st.rerun()
            st.divider()

# =====================
# GENERATE / VIEW
# =====================
elif st.session_state.view == "generate":

    entries = load_all_entries()

    # --- Entry selector ---
    col_select, col_btn = st.columns([4, 1])
    with col_select:
        options = ["— Generate new entry —"] + [
            f"{e['created_at'][:10]} · {e['parasha']} · "
            f"{'Daily' if e.get('entry_type') == 'daily' else 'Weekly'}"
            + (f" · {e['theme']}" if e.get("theme") else "")
            for e in entries
        ]
        entry_ids = [None] + [e["id"] for e in entries]
        selected = st.selectbox("Select entry", options, label_visibility="collapsed")
        selected_idx = options.index(selected)
        selected_id = entry_ids[selected_idx]

    with col_btn:
        if selected_id is not None:
            if st.button("📂 Load", type="primary", use_container_width=True):
                st.session_state.content = load_entry(selected_id)
                st.rerun()

    if selected_id is not None and (
        st.session_state.content is None or
        st.session_state.content.get("id") != selected_id
    ):
        st.session_state.content = load_entry(selected_id)
        st.rerun()

    # --- Generate buttons ---
    if selected_id is None:
        gcol1, gcol2 = st.columns(2)
        with gcol1:
            gen_weekly = st.button(
                "📖 Generate Weekly Study + Podcast",
                type="primary", use_container_width=True
            )
        with gcol2:
            gen_daily = st.button(
                "📅 Generate Daily Reflections + Dvar Torah",
                type="primary", use_container_width=True
            )

        if gen_weekly:
            with st.spinner("Generating weekly study — 2-3 minutes..."):
                result = torah_workflow.run(input="general themes")
                step_map = {s.step_name: s.content for s in result.step_results}
                parsha_name = get_current_parsha()
                save_entry(
                    parasha=parsha_name, entry_type="weekly", theme="",
                    research=step_map.get("research", ""),
                    commentary=step_map.get("commentary", ""),
                    script=step_map.get("script", result.content or ""),
                )
                st.session_state.content = load_entry(load_latest_entry_id())
                st.rerun()

        if gen_daily:
            with st.spinner("Generating daily reflections + Dvar Torah — 3-4 minutes..."):
                result = torah_daily_workflow.run(input="general themes")
                step_map = {s.step_name: s.content for s in result.step_results}
                parsha_name = get_current_parsha()
                save_entry(
                    parasha=parsha_name, entry_type="daily", theme="",
                    research=step_map.get("research", ""),
                    commentary=step_map.get("commentary", ""),
                    dailies=step_map.get("dailies", ""),
                    dvar_torah=step_map.get("dvar_torah", result.content or ""),
                )
                st.session_state.content = load_entry(load_latest_entry_id())
                st.rerun()

    # =====================
    # CONTENT DISPLAY
    # =====================
    if st.session_state.content:
        content = st.session_state.content
        parsha = content.get("parasha", "Weekly Parasha")
        entry_type = content.get("entry_type", "weekly")

        st.subheader(f"🕍 Parashat {parsha}")
        st.caption(
            f"{'📅 Daily Reflections' if entry_type == 'daily' else '📖 Weekly Study'}"
            f" · {content.get('created_at', '')[:10]}"
        )

        # --- Section jump links ---
        if entry_type == "weekly":
            st.markdown(
                "**Jump to:** &nbsp;"
                "[📚 Research](#research) &nbsp;|&nbsp; "
                "[✍️ Commentary](#commentary) &nbsp;|&nbsp; "
                "[🎙️ Podcast Script](#podcast-script) &nbsp;|&nbsp; "
                "[📄 Full Document](#full-document)",
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                "**Jump to:** &nbsp;"
                "[📚 Research](#research) &nbsp;|&nbsp; "
                "[✍️ Commentary](#commentary) &nbsp;|&nbsp; "
                "[☀️ Sun](#day-1-sunday) &nbsp;|&nbsp; "
                "[☀️ Mon](#day-2-monday) &nbsp;|&nbsp; "
                "[☀️ Tue](#day-3-tuesday) &nbsp;|&nbsp; "
                "[☀️ Wed](#day-4-wednesday) &nbsp;|&nbsp; "
                "[☀️ Thu](#day-5-thursday) &nbsp;|&nbsp; "
                "[🕯️ Erev Shabbat](#day-6-erev-shabbat) &nbsp;|&nbsp; "
                "[🕯️ Dvar Torah](#dvar-torah) &nbsp;|&nbsp; "
                "[📄 Full Document](#full-document)",
                unsafe_allow_html=True
            )

        st.divider()

        def section(anchor_id, label, text):
            st.markdown(f'<div class="section-anchor" id="{anchor_id}"></div>', unsafe_allow_html=True)
            st.subheader(label)
            st.markdown(text)
            with st.expander("📋 Copy to clipboard"):
                st.code(text, language=None)
                st.caption("Cmd+A, Cmd+C, paste into Google Docs")
            st.divider()

        # --- Weekly layout ---
        if entry_type == "weekly":
            section("research", "📚 Research", content.get("research", ""))
            section("commentary", "✍️ Commentary", content.get("commentary", ""))
            section("podcast-script", "🎙️ Podcast Script", content.get("script", ""))

        # --- Daily layout ---
        elif entry_type == "daily":
            section("research", "📚 Research", content.get("research", ""))
            section("commentary", "✍️ Commentary", content.get("commentary", ""))

            # Parse and display each day individually
            st.markdown('<div class="section-anchor" id="daily-reflections"></div>', unsafe_allow_html=True)
            st.subheader("📅 Daily Reflections")
            st.caption("Five reflections building toward Shabbat")
            st.divider()

            dailies_text = content.get("dailies", "")
            day_labels = [
                ("day-1-sunday", "☀️ Day 1 — Sunday"),
                ("day-2-monday", "☀️ Day 2 — Monday"),
                ("day-3-tuesday", "☀️ Day 3 — Tuesday"),
                ("day-4-wednesday", "☀️ Day 4 — Wednesday"),
                ("day-5-thursday", "☀️ Day 5 — Thursday"),
                ("day-6-erev-shabbat", "🕯️ Day 6 — Erev Shabbat (Friday)"),
            ]

            if dailies_text:
                days = [d.strip() for d in re.split(r"(?=\*\*Day [1-5])", dailies_text) if d.strip() and re.match(r"\*\*Day [1-5]", d.strip())]
                for i, day_text in enumerate(days[:6]):
                    anchor_id, label = day_labels[i]
                    st.markdown(f'<div class="section-anchor" id="{anchor_id}"></div>', unsafe_allow_html=True)
                    st.markdown(f"### {label}")
                    st.markdown(day_text)
                    with st.expander("📋 Copy this day"):
                        st.code(day_text, language=None)
                    st.divider()

            with st.expander("📋 Copy all 5 reflections"):
                st.code(dailies_text, language=None)

            st.divider()
            section("dvar-torah", "🕯️ Dvar Torah", content.get("dvar_torah", ""))

        # --- Full document export ---
        st.markdown('<div class="section-anchor" id="full-document"></div>', unsafe_allow_html=True)
        with st.expander("📄 Copy full document for Google Docs"):
            if entry_type == "weekly":
                full_text = (
                    f"TORAH STUDY — Parashat {parsha}\n\n{'='*50}\n\n"
                    f"RESEARCH\n\n{content.get('research', '')}\n\n{'='*50}\n\n"
                    f"COMMENTARY\n\n{content.get('commentary', '')}\n\n{'='*50}\n\n"
                    f"PODCAST SCRIPT\n\n{content.get('script', '')}\n"
                )
            else:
                full_text = (
                    f"TORAH STUDY — Parashat {parsha}\n\n{'='*50}\n\n"
                    f"RESEARCH\n\n{content.get('research', '')}\n\n{'='*50}\n\n"
                    f"COMMENTARY\n\n{content.get('commentary', '')}\n\n{'='*50}\n\n"
                    f"DAILY REFLECTIONS\n\n{content.get('dailies', '')}\n\n{'='*50}\n\n"
                    f"DVAR TORAH\n\n{content.get('dvar_torah', '')}\n"
                )
            st.code(full_text, language=None)
            st.caption("Cmd+A, Cmd+C, paste into a blank Google Doc")

    else:
        if not entries:
            st.info("No entries yet. Choose a generation mode above to get started.")
        else:
            st.info("Select an entry from the dropdown or generate a new one.")