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

def fetch_worksheet_data(worksheet_name):
    try:
        sh = get_gspread_client()
        ws = sh.worksheet(worksheet_name)
        records = ws.get_all_records()
        return pd.DataFrame(records)
    except Exception as e:
        return pd.DataFrame()

def append_data(worksheet_name, row_dict):
    sh = get_gspread_client()
    ws = sh.worksheet(worksheet_name)
    existing_records = ws.get_all_values()
    if not existing_records:
        ws.append_row(list(row_dict.keys()))
    ws.append_row(list(row_dict.values()))

# -------------------------------------------------------------
# 1. 40 കുടുംബ യൂണിറ്റുകളുടെ ഔദ്യോഗിക ലിസ്റ്റ് (4 Zones)
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
# 2. മാപ്പിംഗ് & വാലിഡേഷൻ റൂളുകൾ
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
    "Basket Ball Throw": ["Sub Junior", "Junior", "Youth", "Senior"],
    "100 Mtr. Race": ["Sub Junior", "Junior", "Youth", "Senior"],
    "200 Mtr. Race": ["Sub Junior", "Junior", "Youth", "Senior"],
    "400 Mtr. Race": ["Sub Junior", "Junior", "Youth", "Senior"],
    "Long Jump": ["Sub Junior", "Junior", "Youth", "Senior"],
    "Shot Put": ["Sub Junior", "Junior", "Youth", "Senior"]
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
# 3. ആപ്പ് ഇന്റർഫേസ് & മുകളിലെ ലിങ്കുകൾ
# -------------------------------------------------------------
st.title("⛪ സെന്റ് ജോർജ്ജസ് ചർച്ച്, മുക്കാട്ടുകര")
st.subheader("ഇടവക ദിന കലാ-സാഹിത്യ-കായിക മത്സര പോർട്ടൽ")

# മുകളിൽ നൽകിയിരിക്കുന്ന ലിങ്ക് / ടാബുകൾ
view_option = st.radio(
    "📌 നാവിഗേഷൻ (Navigation Links)", 
    ["✍️ രജിസ്ട്രേഷൻ ഫോം (Registration)", "📌 സെൻട്രൽ ഡാഷ്‌ബോർഡ്", "📊 റിപ്പോർട്ടുകൾ (Reports)"], 
    horizontal=True
)

st.markdown("---")

# -------------------------------------------------------------
# 4. പ്രഥമ പേജ്: രജിസ്ട്രേഷൻ ഫോം
# -------------------------------------------------------------
if view_option == "✍️ രജിസ്ട്രേഷൻ ഫോം (Registration)":
    
    reg_type = st.radio("രജിസ്ട്രേഷൻ ടൈപ്പ് തിരഞ്ഞെടുക്കുക:", ["വ്യക്തിഗത മത്സരം (Individual Entry)", "ഗ്രൂപ്പ് മത്സരം (Group Entry)"], horizontal=True)
    st.markdown("---")

    if reg_type == "വ്യക്തിഗത മത്സരം (Individual Entry)":
        st.header("✍️ വ്യക്തിഗത മത്സരങ്ങൾ - രജിസ്ട്രേഷൻ")
        
        with st.form("ind_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                category_type = st.selectbox("മത്സര വിഭാഗം", ["കലാമത്സരം", "കായിക മത്സരം", "സാഹിത്യമത്സരം"])
                unit = st.selectbox("കുടുംബ യൂണിറ്റ് തിരഞ്ഞെടുക്കുക (40 Units)", ALL_UNITS)
                participant_name = st.text_input("മത്സരാർത്ഥിയുടെ പേര്")
                gender = st.selectbox("ലിംഗം", ["Male", "Female"])
            
            with col2:
                dob = st.date_input("ജനന തീയതി", value=date(2000, 1, 1), min_value=date(1930, 1, 1), max_value=date.today())
                manager_info = st.text_input("ടീം മാനേജരുടെ പേരും ഫോൺ നമ്പറും")

            age_cat, age = get_age_category(dob)
            st.info(f"💡 **കണക്കാക്കിയ വയസ്സ്:** {age} | **അർഹമായ ഏജ് കാറ്റഗറി:** {age_cat}")

            if category_type == "കലാമത്സരം":
                eligible_events = [item for item, cats in ARTS_INDIVIDUAL.items() if age_cat in cats]
            elif category_type == "കായിക മത്സരം":
                eligible_events = [item for item, cats in SPORTS_INDIVIDUAL.items() if age_cat in cats]
            else:
                eligible_events = LITERARY_INDIVIDUAL

            if not eligible_events:
                st.warning(f"{age_cat} വിഭാഗത്തിന് {category_type}-ൽ വ്യക്തിഗത മത്സരങ്ങൾ ലഭ്യമല്ല!")
                selected_events = []
            else:
                selected_events = st.multiselect(
                    "മത്സരങ്ങൾ തിരഞ്ഞെടുക്കുക (പരമാവധി 3 ഇനങ്ങൾ)",
                    options=eligible_events,
                    max_selections=3
                )

            submit_btn = st.form_submit_button("രജിസ്റ്റർ ചെയ്യുക")

            if submit_btn:
                if not participant_name:
                    st.error("മത്സരാർത്ഥിയുടെ പേര് നൽകണം!")
                elif len(selected_events) == 0:
                    st.error("കുറഞ്ഞത് ഒരു മത്സരമെങ്കിലും തിരഞ്ഞെടുക്കുക!")
                else:
                    entry = {
                        "വിഭാഗം": category_type,
                        "യൂണിറ്റ്": unit,
                        "പേര്": participant_name,
                        "DOB": str(dob),
                        "വയസ്സ്": age,
                        "ഏജ് കാറ്റഗറി": age_cat,
                        "ലിംഗം": gender,
                        "തിരഞ്ഞെടുത്ത ഇനങ്ങൾ": ", ".join(selected_events),
                        "ടീം മാനേജർ": manager_info,
                        "രജിസ്റ്റർ ചെയ്ത സമയം": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    try:
                        append_data("Individual_Data", entry)
                        st.success(f"വിജയകരമായി രജിസ്റ്റർ ചെയ്തു! ({participant_name} - {unit})")
                    except Exception as ex:
                        st.error(f"ഡാറ്റാബേസ് സേവ് ചെയ്യുന്നതിൽ തടസ്സം നേരിട്ടു: {ex}")

    else:
        st.header("👥 ഗ്രൂപ്പ് മത്സരങ്ങൾ - രജിസ്ട്രേഷൻ")
        
        with st.form("group_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                g_type = st.selectbox("മത്സര വിഭാഗം", ["കലാമത്സരം", "കായിക മത്സരം"])
                main_unit = st.selectbox("പ്രധാന യൂണിറ്റ് (Main Unit)", ALL_UNITS)
                g_event = st.selectbox("ഇനത്തിന്റെ പേര്", ARTS_GROUP if g_type == "കലാമത്സരം" else SPORTS_GROUP)
            with col2:
                zone = st.selectbox("മേഖല (Zone)", list(UNITS_BY_ZONE.keys()))
                manager = st.text_input("ടീം മാനേജർ വിവരങ്ങൾ")
                cluster_unit = st.multiselect("ക്ലസ്റ്റർ യൂണിറ്റ് (മറ്റ് യൂണിറ്റുകൾ ഉണ്ടെങ്കിൽ)", [u for u in ALL_UNITS if u != main_unit])

            g_submit = st.form_submit_button("ഗ്രൂപ്പ് എൻട്രി സേവ് ചെയ്യുക")
            if g_submit:
                g_entry = {
                    "വിഭാഗം": g_type,
                    "മേഖല": zone,
                    "പ്രധാന യൂണിറ്റ്": main_unit,
                    "ഇനത്തിന്റെ പേര്": g_event,
                    "ക്ലസ്റ്റർ യൂണിറ്റുകൾ": ", ".join(cluster_unit) if cluster_unit else "-",
                    "ടീം മാനേജർ": manager,
                    "രജിസ്റ്റർ ചെയ്ത സമയം": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                try:
                    append_data("Group_Data", g_entry)
                    st.success(f"ഗ്രൂപ്പ് എൻട്രി വിജയകരമായി രജിസ്റ്റർ ചെയ്തു! ({main_unit})")
                except Exception as ex:
                    st.error(f"ഡാറ്റാബേസ് സേവ് ചെയ്യുന്നതിൽ തടസ്സം നേരിട്ടു: {ex}")

# -------------------------------------------------------------
# 5. ഡാഷ്‌ബോർഡ്
# -------------------------------------------------------------
elif view_option == "📌 സെൻട്രൽ ഡാഷ്‌ബോർഡ്":
    st.header("📌 സെൻട്രൽ കമ്മിറ്റി ഡാഷ്‌ബോർഡ്")
    
    with st.spinner("ഡാറ്റ പുതുക്കുന്നു..."):
        df_ind = fetch_worksheet_data("Individual_Data")
        df_grp = fetch_worksheet_data("Group_Data")

    c1, c2, c3 = st.columns(3)
    c1.metric("ആകെ വ്യക്തിഗത എൻട്രികൾ", len(df_ind) if not df_ind.empty else 0)
    c2.metric("ആകെ ഗ്രൂപ്പ് എൻട്രികൾ", len(df_grp) if not df_grp.empty else 0)
    
    registered_units = df_ind["യൂണിറ്റ്"].nunique() if not df_ind.empty and "യൂണിറ്റ്" in df_ind.columns else 0
    c3.metric("രജിസ്റ്റർ ചെയ്ത യൂണിറ്റുകൾ", f"{registered_units} / 40")

    st.markdown("---")
    st.subheader("🏘️️ 40 യൂണിറ്റുകളുടെ ലിസ്റ്റും രജിസ്ട്രേഷൻ നിലയും")
    
    col1, col2 = st.columns(2)
    zones = list(UNITS_BY_ZONE.items())
    
    for i, (zone_name, units) in enumerate(zones):
        target_col = col1 if i % 2 == 0 else col2
        with target_col:
            st.markdown(f"#### 📍 {zone_name}")
            zone_df = pd.DataFrame({"യൂണിറ്റിന്റെ പേര്": units})
            
            if not df_ind.empty and "യൂണിറ്റ്" in df_ind.columns:
                reg_counts = df_ind["യൂണിറ്റ്"].value_counts().to_dict()
                zone_df["വ്യക്തിഗത എൻട്രികൾ"] = zone_df["യൂണിറ്റിന്റെ പേര്"].map(reg_counts).fillna(0).astype(int)
            else:
                zone_df["വ്യക്തിഗത എൻട്രികൾ"] = 0
                
            st.dataframe(zone_df, use_container_width=True, hide_index=True)

# -------------------------------------------------------------
# 6. റിപ്പോർട്ടുകൾ
# -------------------------------------------------------------
elif view_option == "📊 റിപ്പോർട്ടുകൾ (Reports)":
    st.header("📊 സമഗ്ര റിപ്പോർട്ടുകൾ")
    
    with st.spinner("ഡാറ്റാബേസിൽ നിന്ന് എൻട്രികൾ ശേഖരിക്കുന്നു..."):
        df_ind = fetch_worksheet_data("Individual_Data")
        df_grp = fetch_worksheet_data("Group_Data")

    tab1, tab2, tab3 = st.tabs(["വ്യക്തിഗത മത്സരങ്ങൾ", "ഗ്രൂപ്പ് മത്സരങ്ങൾ", "🏘️ യൂണിറ്റ് തിരിച്ചുള്ള റിപ്പോർട്ട്"])
    
    with tab1:
        if not df_ind.empty:
            st.dataframe(df_ind, use_container_width=True)
            csv_ind = df_ind.to_csv(index=False).encode('utf-8')
            st.download_button("Excel/CSV ഡൗൺലോഡ് ചെയ്യുക", csv_ind, "individual_participants.csv", "text/csv")
        else:
            st.info("വ്യക്തിഗത എൻട്രികളൊന്നും ലഭ്യമായിട്ടില്ല.")

    with tab2:
        if not df_grp.empty:
            st.dataframe(df_grp, use_container_width=True)
            csv_grp = df_grp.to_csv(index=False).encode('utf-8')
            st.download_button("Excel/CSV ഡൗൺലോഡ് ചെയ്യുക", csv_grp, "group_teams.csv", "text/csv")
        else:
            st.info("ഗ്രൂപ്പ് എൻട്രികളൊന്നും ലഭ്യമായിട്ടില്ല.")

    with tab3:
        selected_u = st.selectbox("യൂണിറ്റ് തിരഞ്ഞെടുക്കുക", ALL_UNITS)
        if not df_ind.empty and "യൂണിറ്റ്" in df_ind.columns:
            unit_filtered = df_ind[df_ind["യൂണിറ്റ്"] == selected_u]
            st.write(f"**{selected_u}** യൂണിറ്റിൽ നിന്നും വന്ന ആകെ വ്യക്തിഗത അപേക്ഷകൾ: **{len(unit_filtered)}**")
            if not unit_filtered.empty:
                st.dataframe(unit_filtered, use_container_width=True)
            else:
                st.info("ഈ യൂണിറ്റിൽ നിന്നും ഇതുവരെ അപേക്ഷകളൊന്നും ലഭിച്ചിട്ടില്ല.")
        else:
            st.info("ഡാറ്റയൊന്നും ലഭ്യമായിട്ടില്ല.")
