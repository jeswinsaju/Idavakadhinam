import streamlit as st
import pandas as pd
from datetime import datetime, date
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="സെന്റ് ജോർജ്ജസ് ചർച്ച് - ഇടവക ദിന മത്സരങ്ങൾ", layout="wide")

# -------------------------------------------------------------
# Google Sheets Connection Helper
# -------------------------------------------------------------
def get_gspread_client():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    secrets = st.secrets["connections"]["gsheets"]
    creds_dict = {
        "type": secrets["type"],
        "project_id": secrets["project_id"],
        "private_key_id": secrets["private_key_id"],
        "private_key": secrets["private_key"].replace('\\n', '\n'),
        "client_email": secrets["client_email"],
        "client_id": secrets["client_id"],
        "token_uri": secrets.get("token_uri", "https://oauth2.googleapis.com/token"),
    }
    creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    client = gspread.authorize(creds)
    sheet_url = secrets["spreadsheet"]
    return client.open_by_url(sheet_url)

def fetch_live_data(worksheet_name):
    try:
        sh = get_gspread_client()
        ws = sh.worksheet(worksheet_name)
        records = ws.get_all_records()
        return pd.DataFrame(records)
    except Exception as e:
        return pd.DataFrame()

def append_rows(worksheet_name, list_of_dicts):
    sh = get_gspread_client()
    ws = sh.worksheet(worksheet_name)
    existing_records = ws.get_all_values()
    
    if not list_of_dicts:
        return
        
    if not existing_records:
        ws.append_row(list(list_of_dicts[0].keys()))
        
    rows_to_append = [list(d.values()) for d in list_of_dicts]
    ws.append_rows(rows_to_append)

# -------------------------------------------------------------
# 1. 40 കുടുംബ യൂണിറ്റുകളുടെ ലിസ്റ്റ് (4 Zones)
# -------------------------------------------------------------
UNITS_BY_ZONE = {
    "ST MATHEW ZONE": [
        "ALL SAINTS", "ST. ALPHONSA", "DON BOSCO", "ST MARYS", "LOURDMATHA",
        "ST ANTONYS", "ST VICENT DE PAUL", "MARIA GORETHI", "SACRES HEART",
        "ST JOSEPH", "ST MICHEAL"
    ],
    "ST MARKOSE ZONE": [
        "MADONA", "HOLY FAMILY", "ST AUGUSTIN", "ST.CHAVARA KURIAKOSE",
        "ASSISSI", "ST.REETHA", "ST.PAUL", "ST PETER", "ST BENEDICT"
    ],
    "ST LUKE ZONE": [
        "LITTLE FLOWER", "ST. THOMAS", "ST. RAPHEAL", "JOHN PAUL",
        "ST.MARIAM THRESIA", "ST.CARLO", "ST.ANNES", "HOLY SPIRIT", "ST SEBASTIAN"
    ],
    "ST JOHN ZONE": [
        "MOTHER THERESA", "ST.JUDE", "ST.JAMES", "JOHN MARIA VIYYANI",
        "CHRISTURAJ", "ST.ALOYSIUS", "HOLY ANGELS", "ST FRANCIS XAVIER",
        "ST.DOMINIC SAVIO", "ST. CLARE", "INFANT JESUS"
    ]
}

ALL_UNITS = [unit for units in UNITS_BY_ZONE.values() for unit in units]

# -------------------------------------------------------------
# 2. മാപ്പിംഗ് & റൂളുകൾ
# -------------------------------------------------------------
ARTS_INDIVIDUAL = {
    "പ്രച്ഛന്നവേഷം (FANCY DRESS)": ["Kiddies", "Sub Junior", "Junior"],
    "നാടോടിനൃത്തം (FOLK DANCE)": ["Kiddies", "Sub Junior", "Junior", "Youth"],
    "ലളിത ഗാനം (LIGHT MUSIC)": ["Sub Junior", "Junior", "Youth", "Senior", "Super Senior"],
    "ഏകാഭിനയം (MONO ACT)": ["Sub Junior", "Junior", "Youth"],
    "നിമിഷ പ്രസംഗം (MINUTE SPEECH)": ["Sub Junior", "Junior", "Youth"],
    "പുത്തൻ പാന": ["Youth", "Senior", "Super Senior"]
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
    "Shot Put": ["Sub Junior", "Junior", "Youth", "Senior", "Super Senior"]
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
    "മാർഗംകളി (NO SPECIFIC AGE GROUP)"
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
    "Men's Cricket 6s (Maximum 7 Players)"
]

def get_age_category(dob):
    today = date.today()
    age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    if age <= 5:
        return "Kiddies", age
    elif 6 <= age <= 10:
        return "Sub Junior", age
    elif 11 <= age <= 15:
        return "Junior", age
    elif 16 <= age <= 35:
        return "Youth", age
    elif 36 <= age <= 55:
        return "Senior", age
    else:
        return "Super Senior", age

# -------------------------------------------------------------
# 3. ആപ്പ് നാവിഗേഷൻ
# -------------------------------------------------------------
st.title("⛪ സെന്റ് ജോർജ്ജസ് ചർച്ച്, മുക്കാട്ടുകര")
st.subheader("ഇടവക ദിന മത്സര രജിസ്ട്രേഷൻ പോർട്ടൽ")

nav_choice = st.radio(
    "📌 പേജ് തിരഞ്ഞെടുക്കുക:", 
    ["✍️ പുതിയ രജിസ്ട്രേഷൻ (Single / Group)", "📊 ലൈവ് റിപ്പോർട്ട് & ഡാഷ്‌ബോർഡ്"], 
    horizontal=True
)

st.markdown("---")

# -------------------------------------------------------------
# 4. രജിസ്ട്രേഷൻ പേജ്
# -------------------------------------------------------------
if nav_choice == "✍️ പുതിയ രജിസ്ട്രേഷൻ (Single / Group)":
    
    st.header("📝 പുതിയ അപേക്ഷ സമർപ്പിക്കുക")
    
    unit = st.selectbox("🏘️ കുടുംബ യൂണിറ്റ് തിരഞ്ഞെടുക്കുക", ALL_UNITS)
    manager_info = st.text_input("👤 ടീം മാനേജരുടെ പേരും ഫോൺ നമ്പറും (ഓപ്ഷണൽ)")

    st.markdown("---")
    
    entry_type = st.radio("രജിസ്ട്രേഷൻ ടൈപ്പ്:", ["👤 വ്യക്തിഗത മത്സരങ്ങൾ (Multiple Participants)", "👥 ഗ്രൂപ്പ് മത്സരങ്ങൾ"], horizontal=True)

    if entry_type == "👤 വ്യക്തിഗത മത്സരങ്ങൾ (Multiple Participants)":
        st.subheader("👤 വ്യക്തിഗത മത്സരങ്ങളുടെ എൻട്രി")
        st.caption("ഒന്നിൽ കൂടുതൽ ആളുകളുടെ വിവരങ്ങൾ ഒന്നിച്ച് ചേർത്ത് താഴെ സബ്മിറ്റ് ചെയ്യാം.")
        
        num_participants = st.number_input("എത്ര മത്സരാർത്ഥികളെ ചേർക്കണം?", min_value=1, max_value=20, value=1, step=1)
        
        participants_data = []

        with st.form("bulk_individual_form"):
            for i in range(int(num_participants)):
                st.markdown(f"#### 🎭 മത്സരാർത്ഥി #{i+1}")
                c1, c2, c3, c4 = st.columns([2, 1.5, 1.5, 3])
                
                with c1:
                    name = st.text_input(f"പേര്", key=f"name_{i}")
                with c2:
                    gender = st.selectbox("ലിംഗം", ["Male", "Female"], key=f"gender_{i}")
                with c3:
                    dob = st.date_input("ജനന തീയതി", value=date(1995, 1, 1), min_value=date(1910, 1, 1), max_value=date.today(), key=f"dob_{i}")
                
                age_cat, age = get_age_category(dob)
                
                with c4:
                    cat_type = st.selectbox("മത്സര വിഭാഗം", ["കലാമത്സരം", "കായിക മത്സരം", "സാഹിത്യമത്സരം"], key=f"cattype_{i}")
                    
                    if cat_type == "കലാമത്സരം":
                        eligible = [k for k, v in ARTS_INDIVIDUAL.items() if age_cat in v]
                    elif cat_type == "കായിക മത്സരം":
                        eligible = [k for k, v in SPORTS_INDIVIDUAL.items() if age_cat in v]
                    else:
                        eligible = LITERARY_INDIVIDUAL
                    
                    selected_events = st.multiselect(f"ഇനങ്ങൾ ({age_cat} - വയസ്സ്: {age})", eligible, max_selections=3, key=f"events_{i}")

                participants_data.append({
                    "വിഭാഗം": cat_type,
                    "യൂണിറ്റ്": unit,
                    "പേര്": name,
                    "DOB": str(dob),
                    "വയസ്സ്": age,
                    "ഏജ് കാറ്റഗറി": age_cat,
                    "ലിംഗം": gender,
                    "തിരഞ്ഞെടുത്ത ഇനങ്ങൾ": ", ".join(selected_events),
                    "ടീം മാനേജർ": manager_info,
                    "രജിസ്റ്റർ ചെയ്ത സമയം": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "is_valid": bool(name and len(selected_events) > 0)
                })
                st.markdown("---")

            submit_bulk = st.form_submit_button("🚀 വ്യക്തിഗത എൻട്രികൾ ഒന്നായി സേവ് ചെയ്യുക")

            if submit_bulk:
                valid_entries = [p for p in participants_data if p["is_valid"]]
                invalid_count = len(participants_data) - len(valid_entries)

                if invalid_count > 0 and len(valid_entries) == 0:
                    st.error("എല്ലാ മത്സരാർത്ഥികളുടെയും പേരും കുറഞ്ഞത് ഒരു ഇനമെങ്കിലും തിരഞ്ഞെടുക്കണം!")
                elif len(valid_entries) > 0:
                    for item in valid_entries:
                        del item["is_valid"]
                    
                    try:
                        append_rows("Individual_Data", valid_entries)
                        st.success(f"🎉 വിജയകരമായി {len(valid_entries)} അപേക്ഷകൾ ഗൂഗിൾ ഷീറ്റിൽ സേവ് ചെയ്തു.")
                    except Exception as ex:
                        st.error(f"സേവ് ചെയ്യുന്നതിൽ തടസ്സം നേരിട്ടു: {ex}")

    else:
        st.subheader("👥 ഗ്രൂപ്പ് മത്സരങ്ങളുടെ എൻട്രി")
        
        with st.form("group_form_single"):
            col1, col2 = st.columns(2)
            with col1:
                g_type = st.selectbox("മത്സര വിഭാഗം", ["കലാമത്സരം", "കായിക മത്സരം"])
                g_event = st.selectbox("ഇനത്തിന്റെ പേര്", ARTS_GROUP if g_type == "കലാമത്സരം" else SPORTS_GROUP)
            with col2:
                selected_zone = "ST MATHEW ZONE"
                for z, u_list in UNITS_BY_ZONE.items():
                    if unit in u_list:
                        selected_zone = z
                        break
                st.text_input("മേഖല (Zone)", value=selected_zone, disabled=True)
                cluster_units = st.multiselect("ക്ലസ്റ്റർ യൂണിറ്റുകൾ (മറ്റ് യൂണിറ്റുകൾ ഉണ്ടെങ്കിൽ)", [u for u in ALL_UNITS if u != unit])

            g_sub = st.form_submit_button("🚀 ഗ്രൂപ്പ് എൻട്രി സേവ് ചെയ്യുക")

            if g_sub:
                g_entry = [{
                    "വിഭാഗം": g_type,
                    "മേഖല": selected_zone,
                    "പ്രധാന യൂണിറ്റ്": unit,
                    "ഇനത്തിന്റെ പേര്": g_event,
                    "ക്ലസ്റ്റർ യൂണിറ്റുകൾ": ", ".join(cluster_units) if cluster_units else "-",
                    "ടീം മാനേജർ": manager_info,
                    "രജിസ്റ്റർ ചെയ്ത സമയം": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }]
                try:
                    append_rows("Group_Data", g_entry)
                    st.success(f"🎉 ഗ്രൂപ്പ് മത്സരം ({g_event}) വിജയകരമായി രജിസ്റ്റർ ചെയ്തു!")
                except Exception as ex:
                    st.error(f"സേവ് ചെയ്യുമ്പോൾ എറർ വന്നിരിക്കുന്നു: {ex}")

# -------------------------------------------------------------
# 5. ലൈവ് റിപ്പോർട്ട് & ഡാഷ്‌ബോർഡ് പേജ് (Zone Matching Robust Fix)
# -------------------------------------------------------------
else:
    st.header("📊 സമഗ്ര റിപ്പോർട്ടുകളും സെൻട്രൽ ഡാഷ്‌ബോർഡും")
    
    if st.button("🔄 ഡാറ്റ പുതുക്കുക (Refresh Live Data)"):
        st.rerun()

    with st.spinner("ഗൂഗിൾ ഷീറ്റിൽ നിന്ന് ലൈവ് വിവരങ്ങൾ ശേഖരിക്കുന്നു..."):
        df_ind = fetch_live_data("Individual_Data")
        df_grp = fetch_live_data("Group_Data")

    tab1, tab2, tab3 = st.tabs(["📌 സെൻട്രൽ ഡാഷ്‌ബോർഡ്", "👤 വ്യക്തിഗത റിപ്പോർട്ട്", "👥 ഗ്രൂപ്പ് റിപ്പോർട്ട്"])

    # Column Matching Logic (യൂണിറ്റ് header ഏതെന്നു കണ്ടെത്തുന്നു)
    unit_col = None
    if not df_ind.empty:
        for c in df_ind.columns:
            if "യൂണിറ്റ്" in str(c) or "unit" in str(c).lower():
                unit_col = c
                break

    with tab1:
        m1, m2, m3 = st.columns(3)
        m1.metric("ആകെ വ്യക്തിഗത എൻട്രികൾ", len(df_ind) if not df_ind.empty else 0)
        m2.metric("ആകെ ഗ്രൂപ്പ് എൻട്രികൾ", len(df_grp) if not df_grp.empty else 0)
        
        # Calculate Unit Counts accurately regardless of space or casing
        counts_dict = {}
        if not df_ind.empty and unit_col:
            # Clean string values
            cleaned_series = df_ind[unit_col].astype(str).str.strip().str.upper()
            counts_dict = cleaned_series.value_counts().to_dict()

        registered_units_count = sum(1 for u in ALL_UNITS if counts_dict.get(u.upper(), 0) > 0)
        m3.metric("രജിസ്റ്റർ ചെയ്ത യൂണിറ്റുകൾ", f"{registered_units_count} / 40")

        st.markdown("---")
        st.subheader("🏘️ 40 യൂണിറ്റുകളുടെ മേഖല തിരിച്ചുള്ള റിപ്പോർട്ട്")
        
        c1, c2 = st.columns(2)
        zones = list(UNITS_BY_ZONE.items())

        for idx, (z_name, u_list) in enumerate(zones):
            target_col = c1 if idx % 2 == 0 else c2
            with target_col:
                st.markdown(f"#### 📍 {z_name}")
                z_rows = []
                for u in u_list:
                    # Match exact unit string ignoring case and space
                    cnt = counts_dict.get(u.strip().upper(), 0)
                    z_rows.append({"യൂണിറ്റ്": u, "എൻട്രികൾ": cnt})
                
                st.dataframe(pd.DataFrame(z_rows), use_container_width=True, hide_index=True)

    with tab2:
        st.subheader("👤 വ്യക്തിഗത അപേക്ഷകൾ")
        
        filter_unit = st.selectbox("യൂണിറ്റ് അനുസരിച്ച് കാണുക:", ["എല്ലാ യൂണിറ്റുകളും"] + ALL_UNITS)
        
        if not df_ind.empty:
            display_df = df_ind.copy()
            if filter_unit != "എല്ലാ യൂണിറ്റുകളും" and unit_col:
                display_df = display_df[display_df[unit_col].astype(str).str.strip().str.upper() == filter_unit.strip().upper()]
            
            st.dataframe(display_df, use_container_width=True)
            
            csv = display_df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Excel/CSV ഡൗൺലോഡ് ചെയ്യുക", csv, "individual_reports.csv", "text/csv")
        else:
            st.info("വ്യക്തിഗത രജിസ്ട്രേഷനുകൾ ഒന്നും കണ്ടെത്തിയിട്ടില്ല.")

    with tab3:
        st.subheader("👥 ഗ്രൂപ്പ് അപേക്ഷകൾ")
        if not df_grp.empty:
            st.dataframe(df_grp, use_container_width=True)
            csv_grp = df_grp.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Excel/CSV ഡൗൺലോഡ് ചെയ്യുക", csv_grp, "group_reports.csv", "text/csv")
        else:
            st.info("ഗ്രൂപ്പ് രജിസ്ട്രേഷനുകൾ ഒന്നും കണ്ടെത്തിയിട്ടില്ല.")
