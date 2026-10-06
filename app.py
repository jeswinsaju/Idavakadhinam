import streamlit as st
import pandas as pd
import re
from datetime import datetime, date
import gspread
from google.oauth2.service_account import Credentials

# =============================================================
# PAGE CONFIG
# =============================================================
st.set_page_config(
    page_title="St. George Parish Day Portal v2.0",
    page_icon="⛪",
    layout="wide",
)

# =============================================================
# CONSTANTS
# =============================================================
SHEET_INDIVIDUAL = "Individual_Data"
SHEET_GROUP = "Group_Data"

UNITS_BY_ZONE = {
    "ST MATHEW ZONE": [
        "ALL SAINTS", "ST. ALPHONSA", "DON BOSCO", "ST MARYS", "LOURDMATHA",
        "ST ANTONYS", "ST VICENT DE PAUL", "MARIA GORETHI", "SACRES HEART",
        "ST JOSEPH", "ST MICHEAL",
    ],
    "ST MARKOSE ZONE": [
        "MADONA", "HOLY FAMILY", "ST AUGUSTIN", "ST.CHAVARA KURIAKOSE",
        "ASSISSI", "ST.REETHA", "ST.PAUL", "ST PETER", "ST BENEDICT",
    ],
    "ST LUKE ZONE": [
        "LITTLE FLOWER", "ST. THOMAS", "ST. RAPHEAL", "JOHN PAUL",
        "ST.MARIAM THRESIA", "ST.CARLO", "ST.ANNES", "HOLY SPIRIT",
        "ST SEBASTIAN",
    ],
    "ST JOHN ZONE": [
        "MOTHER THERESA", "ST.JUDE", "ST.JAMES", "JOHN MARIA VIYYANI",
        "CHRISTURAJ", "ST.ALOYSIUS", "HOLY ANGELS", "ST FRANCIS XAVIER",
        "ST.DOMINIC SAVIO", "ST. CLARE", "INFANT JESUS",
    ],
}

ALL_UNITS = [u for units in UNITS_BY_ZONE.values() for u in units]

ARTS_INDIVIDUAL = {
    "പ്രച്ഛന്നവേഷം (FANCY DRESS)": ["Kiddies", "Sub Junior", "Junior"],
    "നാടോടിനൃത്തം (FOLK DANCE)": ["Kiddies", "Sub Junior", "Junior", "Youth"],
    "ലളിത ഗാനം (LIGHT MUSIC)": ["Sub Junior", "Junior", "Youth", "Senior", "Super Senior"],
    "ഏകാഭിനയം (MONO ACT)": ["Sub Junior", "Junior", "Youth"],
    "നിമിഷ പ്രസംഗം (MINUTE SPEECH)": ["Sub Junior", "Junior", "Youth"],
    "പുത്തൻ പാന": ["Youth", "Senior", "Super Senior"],
}

SPORTS_INDIVIDUAL = {
    "50 Mtr. Race": ["Kiddies"],
    "Spoon Race": ["Kiddies"],
    "Cricket Ball Throw": ["Kiddies"],
    "1500 MTR Walking": ["Super Senior"],
    "Penalty Shootout": ["Kiddies", "Sub Junior", "Junior", "Youth", "Senior", "Super Senior"],
    "Basket Ball Throw": ["Sub Junior", "Junior", "Youth", "Senior", "Super Senior"],
    "100 Mtr. Race": ["Sub Junior", "Junior", "Youth", "Senior"],
    "200 Mtr. Race": ["Sub Junior", "Junior", "Youth", "Senior"],
    "400 Mtr. Race": ["Sub Junior", "Junior", "Youth", "Senior"],
    "Long Jump": ["Sub Junior", "Junior", "Youth", "Senior"],
    "Shot Put": ["Sub Junior", "Junior", "Youth", "Senior", "Super Senior"],
}

LITERARY_INDIVIDUAL = ["ഉപന്യാസം", "കഥ രചന", "കവിത രചന", "ക്വിസ്", "ചിത്രാങ്കനം"]

ARTS_GROUP = [
    "സംഘ നൃത്തം (GROUP DANCE - KIDDIES)",
    "സംഘ നൃത്തം (GROUP DANCE - SUB JUNIOR)",
    "സംഘ നൃത്തം (GROUP DANCE - JUNIOR)",
    "സംഘ നൃത്തം (GROUP DANCE - YOUTH)",
    "മൂകാഭിനയം (MIME - SUB JUNIOR)",
    "മൂകാഭിനയം (MIME - JUNIOR)",
    "മൂകാഭിനയം (MIME - YOUTH)",
    "സംഘ ഗാനം (GROUP SONG - JUNIOR)",
    "സംഘ ഗാനം (GROUP SONG - YOUTH)",
    "സംഘ ഗാനം (GROUP SONG - SENIOR)",
    "സംഘ ഗാനം (GROUP SONG - SUPER SENIOR)",
    "മാർഗംകളി (NO SPECIFIC AGE GROUP)",
]

SPORTS_GROUP = [
    "4 X 100 Relay (SUB JUNIOR - BOYS)",
    "4 X 100 Relay (SUB JUNIOR - GIRLS)",
    "4 X 100 Relay (JUNIOR - BOYS)",
    "4 X 100 Relay (JUNIOR - GIRLS)",
    "4 X 100 Relay (YOUTH - BOYS)",
    "4 X 100 Relay (YOUTH - GIRLS)",
    "4 X 100 Relay (SENIOR - MEN)",
    "4 X 100 Relay (SENIOR - WOMEN)",
    "Badminton Doubles (BOYS)",
    "Badminton Doubles (GIRLS)",
    "Men's Football 5s (Maximum 7 Players)",
    "Men's Cricket 6s (Maximum 7 Players)",
]

# =============================================================
# GOOGLE SHEETS
# =============================================================
def get_gsheets_secrets():
    """Support both [connections.gsheets] and [gsheets] secret layouts."""
    try:
        if "connections" in st.secrets and "gsheets" in st.secrets["connections"]:
            return st.secrets["connections"]["gsheets"]
        if "gsheets" in st.secrets:
            return st.secrets["gsheets"]
    except Exception:
        pass
    raise RuntimeError(
        "Google Sheets secrets not found. Configure [connections.gsheets] "
        "in .streamlit/secrets.toml."
    )


def get_gspread_client():
    secrets = get_gsheets_secrets()

    required = [
        "type", "project_id", "private_key_id",
        "private_key", "client_email", "client_id",
    ]
    missing = [k for k in required if not secrets.get(k)]
    if missing:
        raise RuntimeError("Missing Google credential fields: " + ", ".join(missing))

    private_key = str(secrets["private_key"]).replace("\\n", "\n")

    creds_dict = {
        "type": secrets["type"],
        "project_id": secrets["project_id"],
        "private_key_id": secrets["private_key_id"],
        "private_key": private_key,
        "client_email": secrets["client_email"],
        "client_id": secrets["client_id"],
        "token_uri": secrets.get(
            "token_uri", "https://oauth2.googleapis.com/token"
        ),
    }

    creds = Credentials.from_service_account_info(
        creds_dict,
        scopes=[
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ],
    )
    return gspread.authorize(creds)


def get_spreadsheet():
    secrets = get_gsheets_secrets()
    spreadsheet_url = secrets.get("spreadsheet") or secrets.get("spreadsheet_url")

    if not spreadsheet_url:
        raise RuntimeError(
            "Spreadsheet URL is missing. Add 'spreadsheet' = 'https://docs.google.com/...'"
        )

    client = get_gspread_client()
    return client.open_by_url(spreadsheet_url)


def get_worksheet(worksheet_name, create_if_missing=False):
    sh = get_spreadsheet()

    try:
        return sh.worksheet(worksheet_name)
    except gspread.WorksheetNotFound:
        if create_if_missing:
            return sh.add_worksheet(title=worksheet_name, rows=1000, cols=30)
        raise RuntimeError(
            f"Worksheet '{worksheet_name}' was not found in the Google Sheet."
        )


def fetch_live_data(worksheet_name):
    """Return dataframe and a human-readable error message."""
    try:
        ws = get_worksheet(worksheet_name)
        records = ws.get_all_records()

        if not records:
            return pd.DataFrame(), None

        df = pd.DataFrame(records)
        df.columns = [str(c).strip() for c in df.columns]
        return df, None

    except Exception as exc:
        return pd.DataFrame(), str(exc)


def append_rows(worksheet_name, list_of_dicts):
    if not list_of_dicts:
        return

    ws = get_worksheet(worksheet_name, create_if_missing=True)

    # If a newly-created/empty worksheet has no header, create one.
    existing_values = ws.get_all_values()
    if not existing_values:
        headers = list(list_of_dicts[0].keys())
        ws.append_row(headers, value_input_option="USER_ENTERED")

    headers = ws.row_values(1)
    if not headers:
        headers = list(list_of_dicts[0].keys())
        ws.append_row(headers, value_input_option="USER_ENTERED")

    # Write values according to the actual header order.
    rows = []
    for item in list_of_dicts:
        rows.append([item.get(h, "") for h in headers])

    ws.append_rows(rows, value_input_option="USER_ENTERED")


def test_google_connection():
    try:
        sh = get_spreadsheet()
        return True, sh.title
    except Exception as exc:
        return False, str(exc)


# =============================================================
# HELPERS
# =============================================================
def clean_text(value):
    if value is None:
        return ""
    return re.sub(r"[^a-zA-Z0-9]", "", str(value)).lower()


def find_column(df, possible_names):
    if df.empty:
        return None

    for col in df.columns:
        col_clean = clean_text(col)
        for possible in possible_names:
            if clean_text(possible) in col_clean:
                return col
    return None


def get_zone_for_unit(unit_name):
    for zone, units in UNITS_BY_ZONE.items():
        if unit_name in units:
            return zone
    return "ST MATHEW ZONE"


def get_age_category(dob):
    today = date.today()
    age = today.year - dob.year - (
        (today.month, today.day) < (dob.month, dob.day)
    )

    if age <= 5:
        return "Kiddies", age
    if age <= 10:
        return "Sub Junior", age
    if age <= 15:
        return "Junior", age
    if age <= 35:
        return "Youth", age
    if age <= 55:
        return "Senior", age
    return "Super Senior", age


def show_connection_status():
    st.caption("✅ Dashboard v2.0 • Corrected Google Sheets + Live Central Dashboard")
    with st.sidebar:
        st.markdown("### 🔧 System Status")

        if st.button("🔌 Test Google Sheets Connection", use_container_width=True):
            ok, result = test_google_connection()
            if ok:
                st.success(f"Connected: {result}")
            else:
                st.error("Connection failed")
                st.code(result)

        st.caption("If dashboard data is empty, use the test button above.")


# =============================================================
# HEADER / NAVIGATION
# =============================================================
st.title("⛪ സെന്റ് ജോർജ്ജസ് ചർച്ച്, മുക്കാട്ടുകര")
st.subheader("ഇടവക ദിന മത്സര രജിസ്ട്രേഷൻ പോർട്ടൽ • Dashboard v2.0")

show_connection_status()

nav_choice = st.radio(
    "📌 പേജ് തിരഞ്ഞെടുക്കുക:",
    [
        "✍️ പുതിയ രജിസ്ട്രേഷൻ (Single / Group)",
        "📊 ലൈവ് റിപ്പോർട്ട് & ഡാഷ്‌ബോർഡ്",
    ],
    horizontal=True,
)

st.markdown("---")

# =============================================================
# REGISTRATION PAGE
# =============================================================
if nav_choice == "✍️ പുതിയ രജിസ്ട്രേഷൻ (Single / Group)":

    st.header("📝 പുതിയ അപേക്ഷ സമർപ്പിക്കുക")

    unit = st.selectbox(
        "🏘️ കുടുംബ യൂണിറ്റ് തിരഞ്ഞെടുക്കുക *",
        ALL_UNITS,
    )
    detected_zone = get_zone_for_unit(unit)
    st.info(f"📍 തിരഞ്ഞെടുത്ത യൂണിറ്റിന്റെ മേഖല (Zone): **{detected_zone}**")

    c_m1, c_m2 = st.columns(2)
    with c_m1:
        tm_name = st.text_input("👤 ടീം മാനേജരുടെ പേര് *")
        tm_phone = st.text_input("📞 ടീം മാനേജരുടെ ഫോൺ നമ്പർ *")
    with c_m2:
        atm_name = st.text_input("👤 അസിസ്റ്റന്റ് ടീം മാനേജരുടെ പേര് *")
        atm_phone = st.text_input("📞 അസിസ്റ്റന്റ് ടീം മാനേജരുടെ ഫോൺ നമ്പർ *")

    st.markdown("---")

    entry_type = st.radio(
        "രജിസ്ട്രേഷൻ ടൈപ്പ്:",
        [
            "👤 വ്യക്തിഗത മത്സരങ്ങൾ (Multiple Participants)",
            "👥 ഗ്രൂപ്പ് മത്സരങ്ങൾ",
        ],
        horizontal=True,
    )

    # ---------------------------------------------------------
    # INDIVIDUAL
    # ---------------------------------------------------------
    if entry_type == "👤 വ്യക്തിഗത മത്സരങ്ങൾ (Multiple Participants)":

        st.subheader("👤 വ്യക്തിഗത മത്സരങ്ങളുടെ എൻട്രി")
        num_participants = st.number_input(
            "എത്ര മത്സരാർത്ഥികളെ ചേർക്കണം?",
            min_value=1,
            max_value=20,
            value=1,
            step=1,
        )

        participants_data = []

        with st.form("bulk_individual_form"):

            for i in range(int(num_participants)):
                st.markdown(f"#### 🎭 മത്സരാർത്ഥി #{i + 1}")

                c1, c2, c3, c4 = st.columns([2, 1.2, 1.8, 3])

                with c1:
                    name = st.text_input("പേര് *", key=f"name_{i}")

                with c2:
                    gender = st.selectbox(
                        "ലിംഗം",
                        ["Male", "Female"],
                        key=f"gender_{i}",
                    )

                with c3:
                    dob = st.date_input(
                        "ജനന തീയതി (DOB) *",
                        value=date(2010, 1, 1),
                        min_value=date(1910, 1, 1),
                        max_value=date.today(),
                        key=f"dob_{i}",
                    )

                age_cat, age = get_age_category(dob)

                with c4:
                    cat_type = st.selectbox(
                        "മത്സര വിഭാഗം",
                        ["കലാമത്സരം", "കായിക മത്സരം", "സാഹിത്യമത്സരം"],
                        key=f"cattype_{i}",
                    )

                    if cat_type == "കലാമത്സരം":
                        eligible = [
                            k for k, v in ARTS_INDIVIDUAL.items()
                            if age_cat in v
                        ]
                    elif cat_type == "കായിക മത്സരം":
                        eligible = [
                            k for k, v in SPORTS_INDIVIDUAL.items()
                            if age_cat in v
                        ]
                    else:
                        eligible = LITERARY_INDIVIDUAL

                    selected_events = st.multiselect(
                        f"ഇനങ്ങൾ ({age_cat} - വയസ്സ്: {age}) *",
                        eligible,
                        max_selections=3,
                        key=f"events_{i}",
                    )

                participants_data.append({
                    "വിഭാഗം": cat_type,
                    "മേഖല": detected_zone,
                    "യൂണിറ്റ്": unit,
                    "പേര്": name.strip(),
                    "DOB": str(dob),
                    "വയസ്സ്": age,
                    "ഏജ് കാറ്റഗറി": age_cat,
                    "ലിംഗം": gender,
                    "തിരഞ്ഞെടുത്ത ഇനങ്ങൾ": ", ".join(selected_events),
                    "ടീം മാനേജർ": (
                        f"{tm_name.strip()} ({tm_phone.strip()})"
                        if tm_name.strip() else ""
                    ),
                    "അസിസ്റ്റന്റ് മാനേജർ": (
                        f"{atm_name.strip()} ({atm_phone.strip()})"
                        if atm_name.strip() else ""
                    ),
                    "രജിസ്റ്റർ ചെയ്ത സമയം": datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),
                    "_valid": bool(name.strip() and selected_events),
                })

                st.markdown("---")

            submit_bulk = st.form_submit_button(
                "🚀 വ്യക്തിഗത എൻട്രികൾ ഒന്നായി സേവ് ചെയ്യുക",
                use_container_width=True,
            )

        if submit_bulk:
            if not tm_name.strip() or not tm_phone.strip() or not atm_name.strip() or not atm_phone.strip():
                st.error(
                    "⚠️ മാനേജരുടെയും അസിസ്റ്റന്റ് മാനേജരുടെയും പേരും ഫോൺ നമ്പറും നിർബന്ധമാണ്."
                )
            else:
                valid_entries = [p for p in participants_data if p["_valid"]]

                if len(valid_entries) != len(participants_data):
                    st.error(
                        "⚠️ എല്ലാ മത്സരാർത്ഥികളുടെയും പേരും കുറഞ്ഞത് ഒരു മത്സര ഇനവും നൽകുക."
                    )
                else:
                    for item in valid_entries:
                        item.pop("_valid", None)

                    try:
                        append_rows(SHEET_INDIVIDUAL, valid_entries)
                        st.success(
                            f"🎉 {len(valid_entries)} അപേക്ഷകൾ Google Sheets-ൽ വിജയകരമായി സേവ് ചെയ്തു."
                        )
                        st.cache_data.clear()
                    except Exception as exc:
                        st.error(f"❌ Google Sheets-ലേക്ക് സേവ് ചെയ്യാൻ കഴിഞ്ഞില്ല: {exc}")
                        with st.expander("🔍 Technical error"):
                            st.exception(exc)

    # ---------------------------------------------------------
    # GROUP
    # ---------------------------------------------------------
    else:
        st.subheader("👥 ഗ്രൂപ്പ് മത്സരങ്ങളുടെ എൻട്രി")

        g_type = st.selectbox(
            "മത്സര വിഭാഗം തിരഞ്ഞെടുക്കുക",
            ["കലാമത്സരം", "കായിക മത്സരം"],
            key="group_cat_select",
        )

        available_group_events = (
            ARTS_GROUP if g_type == "കലാമത്സരം" else SPORTS_GROUP
        )

        with st.form("group_form_single"):
            col1, col2 = st.columns(2)

            with col1:
                st.info(f"തിരഞ്ഞെടുത്ത വിഭാഗം: **{g_type}**")
                g_event = st.selectbox(
                    "ഇനത്തിന്റെ പേര് *",
                    available_group_events,
                    key="group_event_select",
                )

            with col2:
                st.text_input(
                    "മേഖല (Zone)",
                    value=detected_zone,
                    disabled=True,
                )
                cluster_units = st.multiselect(
                    "ക്ലസ്റ്റർ യൂണിറ്റുകൾ (ഉണ്ടെങ്കിൽ)",
                    [u for u in ALL_UNITS if u != unit],
                )

            submit_group = st.form_submit_button(
                "🚀 ഗ്രൂപ്പ് എൻട്രി സേവ് ചെയ്യുക",
                use_container_width=True,
            )

        if submit_group:
            if not tm_name.strip() or not tm_phone.strip() or not atm_name.strip() or not atm_phone.strip():
                st.error(
                    "⚠️ മാനേജരുടെയും അസിസ്റ്റന്റ് മാനേജരുടെയും പേരും ഫോൺ നമ്പറും നിർബന്ധമാണ്."
                )
            else:
                g_entry = [{
                    "വിഭാഗം": g_type,
                    "മേഖല": detected_zone,
                    "പ്രധാന യൂണിറ്റ്": unit,
                    "ഇനത്തിന്റെ പേര്": g_event,
                    "ക്ലസ്റ്റർ യൂണിറ്റുകൾ": (
                        ", ".join(cluster_units) if cluster_units else "-"
                    ),
                    "ടീം മാനേജർ": f"{tm_name.strip()} ({tm_phone.strip()})",
                    "അസിസ്റ്റന്റ് മാനേജർ": f"{atm_name.strip()} ({atm_phone.strip()})",
                    "രജിസ്റ്റർ ചെയ്ത സമയം": datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),
                }]

                try:
                    append_rows(SHEET_GROUP, g_entry)
                    st.success(
                        f"🎉 ഗ്രൂപ്പ് മത്സരം ({g_event}) വിജയകരമായി രജിസ്റ്റർ ചെയ്തു."
                    )
                    st.cache_data.clear()
                except Exception as exc:
                    st.error(f"❌ Google Sheets-ലേക്ക് സേവ് ചെയ്യാൻ കഴിഞ്ഞില്ല: {exc}")
                    with st.expander("🔍 Technical error"):
                        st.exception(exc)


# =============================================================
# DASHBOARD
# =============================================================
else:
    st.header("📊 സമഗ്ര ലൈവ് ഡാഷ്‌ബോർഡ്")

    c1, c2 = st.columns([1, 5])
    with c1:
        if st.button("🔄 ഡാറ്റ പുതുക്കുക", use_container_width=True):
            st.rerun()

    # Always show connection/data status rather than silently hiding errors.
    with st.spinner("Google Sheets-ൽ നിന്ന് ലൈവ് വിവരങ്ങൾ ശേഖരിക്കുന്നു..."):
        df_ind, ind_error = fetch_live_data(SHEET_INDIVIDUAL)
        df_grp, grp_error = fetch_live_data(SHEET_GROUP)

    if ind_error:
        st.error("❌ Individual_Data വായിക്കാൻ കഴിഞ്ഞില്ല.")
        with st.expander("Individual_Data error details"):
            st.code(ind_error)

    if grp_error:
        st.error("❌ Group_Data വായിക്കാൻ കഴിഞ്ഞില്ല.")
        with st.expander("Group_Data error details"):
            st.code(grp_error)

    # Helpful setup message when sheets exist but contain no rows.
    if not ind_error and df_ind.empty:
        st.info(
            f"ℹ️ '{SHEET_INDIVIDUAL}' sheet-ൽ ഇപ്പോൾ രജിസ്ട്രേഷൻ ഡാറ്റ ഇല്ല."
        )

    if not grp_error and df_grp.empty:
        st.info(
            f"ℹ️ '{SHEET_GROUP}' sheet-ൽ ഇപ്പോൾ രജിസ്ട്രേഷൻ ഡാറ്റ ഇല്ല."
        )

    unit_col_ind = find_column(df_ind, ["യൂണിറ്റ്", "unit"])
    events_col_ind = find_column(
        df_ind, ["തിരഞ്ഞെടുത്ത ഇനങ്ങൾ", "events", "ഇനങ്ങൾ"]
    )

    unit_col_grp = find_column(
        df_grp,
        [
            "പ്രധാന യൂണിറ്റ്",
            "പ്രധാന യൂണിറ്റ് പേര്",
            "യൂണിറ്റ്",
            "unit",
            "main unit",
            "main_unit",
        ],
    )
    events_col_grp = find_column(
        df_grp, ["ഇനത്തിന്റെ പേര്", "event", "ഇനം"]
    )

    with st.expander("🔎 Data Diagnostics", expanded=False):
        st.write(f"Individual_Data rows loaded: **{len(df_ind)}**")
        st.write(f"Group_Data rows loaded: **{len(df_grp)}**")
        if not df_ind.empty:
            st.write("Individual_Data columns:", list(df_ind.columns))
        if not df_grp.empty:
            st.write("Group_Data columns:", list(df_grp.columns))

    tab1, tab2, tab3 = st.tabs([
        "📌 സെൻട്രൽ ഡാഷ്‌ബോർഡ്",
        "👤 വ്യക്തിഗത റിപ്പോർട്ട്",
        "👥 ഗ്രൂപ്പ് റിപ്പോർട്ട്",
    ])

    # ---------------------------------------------------------
    # CENTRAL DASHBOARD
    # ---------------------------------------------------------
    with tab1:
        m1, m2, m3, m4 = st.columns(4)

        m1.metric(
            "ആകെ വ്യക്തിഗത എൻട്രികൾ",
            len(df_ind),
        )
        m2.metric(
            "ആകെ ഗ്രൂപ്പ് എൻട്രികൾ",
            len(df_grp),
        )

        counts_dict = {}
        if not df_ind.empty and unit_col_ind:
            cleaned_series = df_ind[unit_col_ind].fillna("").apply(clean_text)
            counts_dict = cleaned_series.value_counts().to_dict()

        registered_units_count = sum(
            1 for unit in ALL_UNITS
            if counts_dict.get(clean_text(unit), 0) > 0
        )

        m3.metric(
            "രജിസ്റ്റർ ചെയ്ത യൂണിറ്റുകൾ",
            f"{registered_units_count} / {len(ALL_UNITS)}",
        )

        total_registrations = len(df_ind) + len(df_grp)
        m4.metric("ആകെ രജിസ്ട്രേഷനുകൾ", total_registrations)

        st.markdown("---")

        # -----------------------------------------------------
        # Zone summary
        # -----------------------------------------------------
        st.subheader("🗺️ Zone-wise Summary")

        zone_counts = {z: 0 for z in UNITS_BY_ZONE}

        if not df_ind.empty:
            zone_col_ind = find_column(df_ind, ["മേഖല", "zone"])
            if zone_col_ind:
                for value in df_ind[zone_col_ind].fillna(""):
                    if str(value).strip() in zone_counts:
                        zone_counts[str(value).strip()] += 1

        if not df_grp.empty:
            zone_col_grp = find_column(df_grp, ["മേഖല", "zone"])
            if zone_col_grp:
                for value in df_grp[zone_col_grp].fillna(""):
                    if str(value).strip() in zone_counts:
                        zone_counts[str(value).strip()] += 1

        zone_df = pd.DataFrame(
            list(zone_counts.items()),
            columns=["Zone", "Registrations"],
        )
        st.dataframe(
            zone_df,
            use_container_width=True,
            hide_index=True,
        )

        st.markdown("---")

        # -----------------------------------------------------
        # Event summary
        # -----------------------------------------------------
        st.subheader(
            "🎯 ഓരോ മത്സര ഇനങ്ങളുടെയും മൊത്തം എൻട്രികൾ"
        )

        event_counts = {}

        if not df_ind.empty and events_col_ind:
            for ev_list in df_ind[events_col_ind].dropna():
                for ev in str(ev_list).split(","):
                    ev_clean = ev.strip()
                    if ev_clean:
                        event_counts[ev_clean] = (
                            event_counts.get(ev_clean, 0) + 1
                        )

        if not df_grp.empty and events_col_grp:
            for ev in df_grp[events_col_grp].dropna():
                ev_clean = str(ev).strip()
                if ev_clean:
                    key = f"[Group] {ev_clean}"
                    event_counts[key] = event_counts.get(key, 0) + 1

        if event_counts:
            df_event_summary = pd.DataFrame(
                list(event_counts.items()),
                columns=["മത്സര ഇനം (Event)", "ആകെ രജിസ്ട്രേഷനുകൾ"],
            ).sort_values(
                by="ആകെ രജിസ്ട്രേഷനുകൾ",
                ascending=False,
            )

            st.dataframe(
                df_event_summary,
                use_container_width=True,
                hide_index=True,
            )

            st.bar_chart(
                df_event_summary.set_index("മത്സര ഇനം (Event)")
                .head(15)["ആകെ രജിസ്ട്രേഷനുകൾ"]
            )
        else:
            st.info("ഇതുവരെ മത്സര ഇനങ്ങളിൽ എൻട്രികൾ ലഭിച്ചിട്ടില്ല.")

        st.markdown("---")

        # -----------------------------------------------------
        # Unit-wise detail
        # -----------------------------------------------------
        st.subheader("🏘️ കുടുംബ യൂണിറ്റ് തിരിച്ചു എൻട്രി ലിസ്റ്റ് നോക്കുക")

        selected_unit_view = st.selectbox(
            "വിവരങ്ങൾ കാണേണ്ട യൂണിറ്റ് തിരഞ്ഞെടുക്കുക:",
            ["-- Select Unit --"] + ALL_UNITS,
        )

        if selected_unit_view != "-- Select Unit --":
            u_clean = clean_text(selected_unit_view)

            st.markdown(
                f"#### 👤 {selected_unit_view} - വ്യക്തിഗത എൻട്രികൾ"
            )

            # ---------------- INDIVIDUAL ----------------
            if df_ind.empty:
                st.info(
                    f"ℹ️ Individual_Data sheet-ൽ ഇപ്പോൾ ഡാറ്റ ഇല്ല."
                )
            elif not unit_col_ind:
                st.warning(
                    "⚠️ Individual_Data-ൽ യൂണിറ്റ് column കണ്ടെത്താനായില്ല."
                )
                st.caption(
                    "ലഭ്യമായ columns: " + ", ".join(map(str, df_ind.columns))
                )
                st.dataframe(
                    df_ind,
                    use_container_width=True,
                    hide_index=True,
                )
            else:
                matched_ind = df_ind[
                    df_ind[unit_col_ind]
                    .fillna("")
                    .apply(clean_text)
                    .eq(u_clean)
                ]

                if not matched_ind.empty:
                    st.dataframe(
                        matched_ind,
                        use_container_width=True,
                        hide_index=True,
                    )
                else:
                    st.info(
                        f"ℹ️ {selected_unit_view} യൂണിറ്റിൽ "
                        "വ്യക്തിഗത രജിസ്ട്രേഷൻ ഒന്നുമില്ല."
                    )

            st.markdown(
                f"#### 👥 {selected_unit_view} - ഗ്രൂപ്പ് എൻട്രികൾ"
            )

            # IMPORTANT:
            # Never call an existing Group_Data sheet "empty" merely
            # because the unit column was not detected.
            if df_grp.empty:
                st.info(
                    "ℹ️ Group_Data sheet-ൽ ഇപ്പോൾ ഡാറ്റ ഇല്ല."
                )
            elif not unit_col_grp:
                st.warning(
                    "⚠️ Group_Data-ൽ യൂണിറ്റ് column കണ്ടെത്താനായില്ല."
                )
                st.caption(
                    "ലഭ്യമായ Group_Data columns: "
                    + ", ".join(map(str, df_grp.columns))
                )
                st.dataframe(
                    df_grp,
                    use_container_width=True,
                    hide_index=True,
                )
            else:
                matched_grp = df_grp[
                    df_grp[unit_col_grp]
                    .fillna("")
                    .apply(clean_text)
                    .eq(u_clean)
                ]

                if not matched_grp.empty:
                    st.dataframe(
                        matched_grp,
                        use_container_width=True,
                        hide_index=True,
                    )
                else:
                    st.info(
                        f"ℹ️ {selected_unit_view} യൂണിറ്റിൽ "
                        "ഗ്രൂപ്പ് രജിസ്ട്രേഷൻ ഒന്നുമില്ല."
                    )

    # ---------------------------------------------------------
    # INDIVIDUAL REPORT
    # ---------------------------------------------------------
    with tab2:
        st.subheader("👤 എല്ലാ വ്യക്തിഗത അപേക്ഷകളുടെയും ലിസ്റ്റ്")

        if not df_ind.empty:
            st.dataframe(
                df_ind,
                use_container_width=True,
                hide_index=True,
            )

            csv = df_ind.to_csv(index=False).encode("utf-8-sig")
            st.download_button(
                "📥 CSV ആയി ഡൗൺലോഡ് ചെയ്യുക",
                csv,
                "all_individual_reports.csv",
                "text/csv",
                use_container_width=True,
            )
        else:
            st.info("വ്യക്തിഗത രജിസ്ട്രേഷനുകൾ ഒന്നും കണ്ടെത്തിയിട്ടില്ല.")

    # ---------------------------------------------------------
    # GROUP REPORT
    # ---------------------------------------------------------
    with tab3:
        st.subheader("👥 എല്ലാ ഗ്രൂപ്പ് അപേക്ഷകളുടെയും ലിസ്റ്റ്")

        if not df_grp.empty:
            st.dataframe(
                df_grp,
                use_container_width=True,
                hide_index=True,
            )

            csv_grp = df_grp.to_csv(index=False).encode("utf-8-sig")
            st.download_button(
                "📥 CSV ആയി ഡൗൺലോഡ് ചെയ്യുക",
                csv_grp,
                "all_group_reports.csv",
                "text/csv",
                use_container_width=True,
            )
        else:
            st.info("ഗ്രൂപ്പ് രജിസ്ട്രേഷനുകൾ ഒന്നും കണ്ടെത്തിയിട്ടില്ല.")
