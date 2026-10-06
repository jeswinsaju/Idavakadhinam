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
    page_title="St. George Parish Day Portal v3.0",
    page_icon="⛪",
    layout="wide",
)


# =============================================================
# CONSTANTS
# =============================================================

SHEET_INDIVIDUAL = "Individual_Data"
SHEET_GROUP = "Group_Data"


# =============================================================
# ZONES AND FAMILY UNITS
# =============================================================

UNITS_BY_ZONE = {

    "ST MATHEW ZONE": [
        "ALL SAINTS",
        "ST. ALPHONSA",
        "DON BOSCO",
        "ST MARYS",
        "LOURDMATHA",
        "ST ANTONYS",
        "ST VICENT DE PAUL",
        "MARIA GORETHI",
        "SACRES HEART",
        "ST JOSEPH",
        "ST MICHEAL",
    ],

    "ST MARKOSE ZONE": [
        "MADONA",
        "HOLY FAMILY",
        "ST AUGUSTIN",
        "ST.CHAVARA KURIAKOSE",
        "ASSISSI",
        "ST.REETHA",
        "ST.PAUL",
        "ST PETER",
        "ST BENEDICT",
    ],

    "ST LUKE ZONE": [
        "LITTLE FLOWER",
        "ST. THOMAS",
        "ST. RAPHEAL",
        "JOHN PAUL",
        "ST.MARIAM THRESIA",
        "ST.CARLO",
        "ST.ANNES",
        "HOLY SPIRIT",
        "ST SEBASTIAN",
    ],

    "ST JOHN ZONE": [
        "MOTHER THERESA",
        "ST.JUDE",
        "ST.JAMES",
        "JOHN MARIA VIYYANI",
        "CHRISTURAJ",
        "ST.ALOYSIUS",
        "HOLY ANGELS",
        "ST FRANCIS XAVIER",
        "ST.DOMINIC SAVIO",
        "ST. CLARE",
        "INFANT JESUS",
    ],
}


ALL_UNITS = [
    unit
    for units in UNITS_BY_ZONE.values()
    for unit in units
]


# =============================================================
# INDIVIDUAL EVENTS
# =============================================================

ARTS_INDIVIDUAL = {

    "പ്രച്ഛന്നവേഷം (FANCY DRESS)": [
        "Kiddies",
        "Sub Junior",
        "Junior",
    ],

    "നാടോടിനൃത്തം (FOLK DANCE)": [
        "Kiddies",
        "Sub Junior",
        "Junior",
        "Youth",
    ],

    "ലളിത ഗാനം (LIGHT MUSIC)": [
        "Sub Junior",
        "Junior",
        "Youth",
        "Senior",
        "Super Senior",
    ],

    "ഏകാഭിനയം (MONO ACT)": [
        "Sub Junior",
        "Junior",
        "Youth",
    ],

    "നിമിഷ പ്രസംഗം (MINUTE SPEECH)": [
        "Sub Junior",
        "Junior",
        "Youth",
    ],

    "പുത്തൻ പാന": [
        "Youth",
        "Senior",
        "Super Senior",
    ],
}


# =============================================================
# SPORTS EVENTS
# =============================================================

SPORTS_INDIVIDUAL = {

    "50 Mtr. Race": [
        "Kiddies",
    ],

    "Spoon Race": [
        "Kiddies",
    ],

    "Cricket Ball Throw": [
        "Kiddies",
    ],

    "1500 MTR Walking": [
        "Super Senior",
    ],

    "Penalty Shootout": [
        "Kiddies",
        "Sub Junior",
        "Junior",
        "Youth",
        "Senior",
        "Super Senior",
    ],

    "Basket Ball Throw": [
        "Sub Junior",
        "Junior",
        "Youth",
        "Senior",
        "Super Senior",
    ],

    "100 Mtr. Race": [
        "Sub Junior",
        "Junior",
        "Youth",
        "Senior",
    ],

    "200 Mtr. Race": [
        "Sub Junior",
        "Junior",
        "Youth",
        "Senior",
    ],

    "400 Mtr. Race": [
        "Sub Junior",
        "Junior",
        "Youth",
        "Senior",
    ],

    "Long Jump": [
        "Sub Junior",
        "Junior",
        "Youth",
        "Senior",
    ],

    "Shot Put": [
        "Sub Junior",
        "Junior",
        "Youth",
        "Senior",
        "Super Senior",
    ],
}


# =============================================================
# LITERARY EVENTS
# =============================================================

LITERARY_INDIVIDUAL = [
    "ഉപന്യാസം",
    "കഥ രചന",
    "കവിത രചന",
    "ക്വിസ്",
    "ചിത്രാങ്കനം",
]


# =============================================================
# GROUP EVENTS
# =============================================================

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

    """
    Supports both:

    [connections.gsheets]

    and

    [gsheets]
    """

    try:

        if (
            "connections" in st.secrets
            and "gsheets" in st.secrets["connections"]
        ):

            return st.secrets["connections"]["gsheets"]

        if "gsheets" in st.secrets:

            return st.secrets["gsheets"]

    except Exception:
        pass

    raise RuntimeError(
        "Google Sheets secrets not found. "
        "Configure [connections.gsheets] "
        "in .streamlit/secrets.toml."
    )


def get_gspread_client():

    secrets = get_gsheets_secrets()

    required = [
        "type",
        "project_id",
        "private_key_id",
        "private_key",
        "client_email",
        "client_id",
    ]

    missing = [
        key
        for key in required
        if not secrets.get(key)
    ]

    if missing:

        raise RuntimeError(
            "Missing Google credential fields: "
            + ", ".join(missing)
        )

    private_key = str(
        secrets["private_key"]
    ).replace("\\n", "\n")

    creds_dict = {

        "type": secrets["type"],

        "project_id": secrets["project_id"],

        "private_key_id": secrets["private_key_id"],

        "private_key": private_key,

        "client_email": secrets["client_email"],

        "client_id": secrets["client_id"],

        "token_uri": secrets.get(
            "token_uri",
            "https://oauth2.googleapis.com/token",
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

    spreadsheet_url = (
        secrets.get("spreadsheet")
        or secrets.get("spreadsheet_url")
    )

    if not spreadsheet_url:

        raise RuntimeError(
            "Spreadsheet URL is missing. "
            "Add 'spreadsheet' or "
            "'spreadsheet_url' in secrets.toml."
        )

    client = get_gspread_client()

    return client.open_by_url(spreadsheet_url)


def get_worksheet(
    worksheet_name,
    create_if_missing=False,
):

    sh = get_spreadsheet()

    try:

        return sh.worksheet(worksheet_name)

    except gspread.WorksheetNotFound:

        if create_if_missing:

            return sh.add_worksheet(
                title=worksheet_name,
                rows=1000,
                cols=30,
            )

        raise RuntimeError(
            f"Worksheet '{worksheet_name}' "
            "was not found in the Google Sheet."
        )


def fetch_live_data(worksheet_name):

    """
    Read complete worksheet into DataFrame.
    """

    try:

        ws = get_worksheet(worksheet_name)

        records = ws.get_all_records()

        if not records:

            return pd.DataFrame(), None

        df = pd.DataFrame(records)

        df.columns = [
            str(column).strip()
            for column in df.columns
        ]

        return df, None

    except Exception as exc:

        return pd.DataFrame(), str(exc)


def append_rows(
    worksheet_name,
    list_of_dicts,
):

    if not list_of_dicts:
        return

    ws = get_worksheet(
        worksheet_name,
        create_if_missing=True,
    )

    existing_values = ws.get_all_values()

    if not existing_values:

        headers = list(
            list_of_dicts[0].keys()
        )

        ws.append_row(
            headers,
            value_input_option="USER_ENTERED",
        )

    headers = ws.row_values(1)

    if not headers:

        headers = list(
            list_of_dicts[0].keys()
        )

        ws.append_row(
            headers,
            value_input_option="USER_ENTERED",
        )

    rows = []

    for item in list_of_dicts:

        rows.append([
            item.get(header, "")
            for header in headers
        ])

    ws.append_rows(
        rows,
        value_input_option="USER_ENTERED",
    )


def test_google_connection():

    try:

        sh = get_spreadsheet()

        return True, sh.title

    except Exception as exc:

        return False, str(exc)


# =============================================================
# TEXT / MATCHING HELPERS
# =============================================================

def clean_text(value):

    if value is None:
        return ""

    return re.sub(
        r"[^a-zA-Z0-9]",
        "",
        str(value),
    ).lower()


def normalized_text(value):

    if value is None:
        return ""

    value = str(value).strip().lower()

    value = re.sub(
        r"[\u200b-\u200f\u202a-\u202e]",
        "",
        value,
    )

    value = re.sub(
        r"[^a-z0-9]+",
        "",
        value,
    )

    return value


def _norm(value):

    return normalized_text(value)


def _split_values(value):

    if value is None:
        return []

    return [
        str(x).strip()
        for x in re.split(
            r"[,;\n|]+",
            str(value),
        )
        if str(x).strip()
    ]


def find_column(
    df,
    possible_names,
):

    if df.empty:
        return None

    for column in df.columns:

        column_clean = clean_text(column)

        for possible in possible_names:

            if clean_text(possible) in column_clean:

                return column

    return None


# =============================================================
# UNIT / ZONE HELPERS
# =============================================================

def get_zone_for_unit(unit_name):

    target = _norm(unit_name)

    for zone, units in UNITS_BY_ZONE.items():

        for unit in units:

            if _norm(unit) == target:

                return zone

    return "UNKNOWN"


def _row_has_unit(
    row,
    unit_name,
    preferred_col=None,
):

    target = _norm(unit_name)

    if not target:
        return False

    columns = []

    if (
        preferred_col
        and preferred_col in row.index
    ):

        columns.append(preferred_col)

    columns.extend([
        c
        for c in row.index
        if c not in columns
    ])

    for column in columns:

        value = row.get(column, "")

        if value is None:
            continue

        # First check separated values.
        parts = _split_values(value)

        for part in parts:

            if _norm(part) == target:

                return True

        # Then check complete cell.
        if _norm(value) == target:

            return True

    return False


def _rows_for_unit(
    df,
    unit_name,
    preferred_col=None,
):

    if df.empty:

        return df.copy()

    mask = df.apply(

        lambda row:
        _row_has_unit(
            row,
            unit_name,
            preferred_col,
        ),

        axis=1,
    )

    return df.loc[mask].copy()


def _derive_unit(
    row,
    preferred_col=None,
):

    """
    Determine which known family unit belongs
    to this registration row.

    This is especially important for:

    Individual_Data:
        യൂണിറ്റ്

    Group_Data:
        പ്രധാന യൂണിറ്റ്
        ക്ലസ്റ്റർ യൂണിറ്റുകൾ
    """

    # ---------------------------------------------------------
    # 1. Check preferred unit column first
    # ---------------------------------------------------------

    if (
        preferred_col
        and preferred_col in row.index
    ):

        preferred_value = str(
            row.get(
                preferred_col,
                "",
            )
        ).strip()

        for unit in ALL_UNITS:

            if _norm(preferred_value) == _norm(unit):

                return unit

    # ---------------------------------------------------------
    # 2. Check every known unit against every column
    # ---------------------------------------------------------

    for unit in ALL_UNITS:

        if _row_has_unit(
            row,
            unit,
            preferred_col,
        ):

            return unit

    return "UNKNOWN"


def _prepare_dashboard_data(
    df,
    preferred_unit_col,
):

    if df.empty:

        return df.copy()

    work = df.copy()

    work["__Dashboard Unit"] = work.apply(

        lambda row:
        _derive_unit(
            row,
            preferred_unit_col,
        ),

        axis=1,
    )

    work["__Dashboard Zone"] = (
        work["__Dashboard Unit"]
        .apply(
            lambda unit:
            get_zone_for_unit(unit)
            if unit != "UNKNOWN"
            else "UNKNOWN"
        )
    )

    return work


# =============================================================
# EVENT HELPERS
# =============================================================

def _event_counts(
    df,
    event_col,
    prefix="",
):

    counts = {}

    if df.empty or not event_col:

        return counts

    for value in df[event_col].fillna(""):

        for event in _split_values(value):

            if event:

                label = (
                    f"{prefix}{event}"
                    if prefix
                    else event
                )

                counts[label] = (
                    counts.get(label, 0) + 1
                )

    return counts


# =============================================================
# AGE CATEGORY
# =============================================================

def get_age_category(dob):

    """
    Competition age categories:

        0–5    = Kiddies
        6–10   = Sub Junior
        11–15  = Junior
        16–35  = Youth
        36–55  = Senior
        56+    = Super Senior

    IMPORTANT:
    There is NO upper age limit.
    """

    today = date.today()

    age = (
        today.year
        - dob.year
        - (
            (today.month, today.day)
            < (dob.month, dob.day)
        )
    )

    if age <= 5:

        return "Kiddies", age

    elif age <= 10:

        return "Sub Junior", age

    elif age <= 15:

        return "Junior", age

    elif age <= 35:

        return "Youth", age

    elif age <= 55:

        return "Senior", age

    else:

        # 56 years and above
        return "Super Senior", age


# =============================================================
# CONNECTION STATUS
# =============================================================

def show_connection_status():

    st.caption(
        "✅ Dashboard v3.0 • "
        "Google Sheets Live Registration System"
    )

    with st.sidebar:

        st.markdown(
            "### 🔧 System Status"
        )

        if st.button(
            "🔌 Test Google Sheets Connection",
            use_container_width=True,
        ):

            ok, result = (
                test_google_connection()
            )

            if ok:

                st.success(
                    f"Connected: {result}"
                )

            else:

                st.error(
                    "Connection failed"
                )

                st.code(result)

        st.caption(
            "Use the connection test if "
            "dashboard data is empty."
        )


# =============================================================
# HEADER
# =============================================================

st.title(
    "⛪ സെന്റ് ജോർജ്ജസ് ചർച്ച്, മുക്കാട്ടുകര"
)

st.subheader(
    "ഇടവക ദിന മത്സര രജിസ്ട്രേഷൻ പോർട്ടൽ"
)

show_connection_status()


# =============================================================
# NAVIGATION
# =============================================================

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

if (
    nav_choice
    == "✍️ പുതിയ രജിസ്ട്രേഷൻ (Single / Group)"
):

    st.header(
        "📝 പുതിയ അപേക്ഷ സമർപ്പിക്കുക"
    )

    # ---------------------------------------------------------
    # UNIT
    # ---------------------------------------------------------

    unit = st.selectbox(

        "🏘️ കുടുംബ യൂണിറ്റ് തിരഞ്ഞെടുക്കുക *",

        ALL_UNITS,

    )

    detected_zone = get_zone_for_unit(unit)

    st.info(
        f"📍 തിരഞ്ഞെടുത്ത യൂണിറ്റിന്റെ മേഖല (Zone): "
        f"**{detected_zone}**"
    )

    # ---------------------------------------------------------
    # MANAGER DETAILS
    # ---------------------------------------------------------

    c_m1, c_m2 = st.columns(2)

    with c_m1:

        tm_name = st.text_input(
            "👤 ടീം മാനേജരുടെ പേര് *"
        )

        tm_phone = st.text_input(
            "📞 ടീം മാനേജരുടെ ഫോൺ നമ്പർ *"
        )

    with c_m2:

        atm_name = st.text_input(
            "👤 അസിസ്റ്റന്റ് ടീം മാനേജരുടെ പേര് *"
        )

        atm_phone = st.text_input(
            "📞 അസിസ്റ്റന്റ് ടീം മാനേജരുടെ ഫോൺ നമ്പർ *"
        )

    st.markdown("---")

    # ---------------------------------------------------------
    # REGISTRATION TYPE
    # ---------------------------------------------------------

    entry_type = st.radio(

        "രജിസ്ട്രേഷൻ ടൈപ്പ്:",

        [
            "👤 വ്യക്തിഗത മത്സരങ്ങൾ (Multiple Participants)",
            "👥 ഗ്രൂപ്പ് മത്സരങ്ങൾ",
        ],

        horizontal=True,
    )

    # =========================================================
    # INDIVIDUAL REGISTRATION
    # =========================================================

    if (
        entry_type
        == "👤 വ്യക്തിഗത മത്സരങ്ങൾ (Multiple Participants)"
    ):

        st.subheader(
            "👤 വ്യക്തിഗത മത്സരങ്ങളുടെ എൻട്രി"
        )

        num_participants = st.number_input(

            "എത്ര മത്സരാർത്ഥികളെ ചേർക്കണം?",

            min_value=1,

            max_value=20,

            value=1,

            step=1,

        )

        participants_data = []

        with st.form(
            "bulk_individual_form"
        ):

            for i in range(
                int(num_participants)
            ):

                st.markdown(
                    f"#### 🎭 മത്സരാർത്ഥി #{i + 1}"
                )

                c1, c2, c3, c4 = st.columns(
                    [2, 1.2, 1.8, 3]
                )

                # -------------------------------------------------
                # NAME
                # -------------------------------------------------

                with c1:

                    name = st.text_input(
                        "പേര് *",
                        key=f"name_{i}",
                    )

                # -------------------------------------------------
                # GENDER
                # -------------------------------------------------

                with c2:

                    gender = st.selectbox(

                        "ലിംഗം",

                        [
                            "Male",
                            "Female",
                        ],

                        key=f"gender_{i}",
                    )

                # -------------------------------------------------
                # DOB
                # -------------------------------------------------

                with c3:

                    dob = st.date_input(

                        "ജനന തീയതി (DOB) *",

                        value=date(
                            2010,
                            1,
                            1,
                        ),

                        # IMPORTANT:
                        # Allows participants born
                        # before 1970, 1960, etc.
                        min_value=date(
                            1900,
                            1,
                            1,
                        ),

                        max_value=date.today(),

                        key=f"dob_{i}",
                    )

                # -------------------------------------------------
                # AGE
                # -------------------------------------------------

                age_cat, age = (
                    get_age_category(dob)
                )

                # -------------------------------------------------
                # EVENTS
                # -------------------------------------------------

                with c4:

                    cat_type = st.selectbox(

                        "മത്സര വിഭാഗം",

                        [
                            "കലാമത്സരം",
                            "കായിക മത്സരം",
                            "സാഹിത്യമത്സരം",
                        ],

                        key=f"cattype_{i}",
                    )

                    if (
                        cat_type
                        == "കലാമത്സരം"
                    ):

                        eligible = [

                            event

                            for event, categories
                            in ARTS_INDIVIDUAL.items()

                            if age_cat
                            in categories
                        ]

                    elif (
                        cat_type
                        == "കായിക മത്സരം"
                    ):

                        eligible = [

                            event

                            for event, categories
                            in SPORTS_INDIVIDUAL.items()

                            if age_cat
                            in categories
                        ]

                    else:

                        eligible = (
                            LITERARY_INDIVIDUAL
                        )

                    st.caption(
                        f"പ്രായം: **{age}** | "
                        f"Age Category: **{age_cat}**"
                    )

                    if eligible:

                        selected_events = st.multiselect(

                            f"ഇനങ്ങൾ "
                            f"({age_cat} - വയസ്സ്: {age}) *",

                            eligible,

                            max_selections=3,

                            key=f"events_{i}",
                        )

                    else:

                        selected_events = []

                        st.warning(
                            "ഈ പ്രായ വിഭാഗത്തിന് "
                            "ഈ മത്സര വിഭാഗത്തിൽ "
                            "ഇനങ്ങൾ ലഭ്യമല്ല."
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

                    "തിരഞ്ഞെടുത്ത ഇനങ്ങൾ":
                        ", ".join(
                            selected_events
                        ),

                    "ടീം മാനേജർ": (

                        f"{tm_name.strip()} "
                        f"({tm_phone.strip()})"

                        if tm_name.strip()

                        else ""
                    ),

                    "അസിസ്റ്റന്റ് മാനേജർ": (

                        f"{atm_name.strip()} "
                        f"({atm_phone.strip()})"

                        if atm_name.strip()

                        else ""
                    ),

                    "രജിസ്റ്റർ ചെയ്ത സമയം":
                        datetime.now().strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ),

                    "_valid":
                        bool(
                            name.strip()
                            and selected_events
                        ),
                })

                st.markdown("---")

            submit_bulk = st.form_submit_button(

                "🚀 വ്യക്തിഗത എൻട്രികൾ "
                "ഒന്നായി സേവ് ചെയ്യുക",

                use_container_width=True,
            )

        # -----------------------------------------------------
        # SAVE INDIVIDUAL
        # -----------------------------------------------------

        if submit_bulk:

            if (
                not tm_name.strip()
                or not tm_phone.strip()
                or not atm_name.strip()
                or not atm_phone.strip()
            ):

                st.error(

                    "⚠️ മാനേജരുടെയും "
                    "അസിസ്റ്റന്റ് മാനേജരുടെയും "
                    "പേരും ഫോൺ നമ്പറും നിർബന്ധമാണ്."
                )

            else:

                valid_entries = [

                    participant

                    for participant
                    in participants_data

                    if participant["_valid"]
                ]

                if (
                    len(valid_entries)
                    != len(participants_data)
                ):

                    st.error(

                        "⚠️ എല്ലാ മത്സരാർത്ഥികളുടെയും "
                        "പേരും കുറഞ്ഞത് ഒരു "
                        "മത്സര ഇനവും നൽകുക."
                    )

                else:

                    for item in valid_entries:

                        item.pop(
                            "_valid",
                            None,
                        )

                    try:

                        append_rows(
                            SHEET_INDIVIDUAL,
                            valid_entries,
                        )

                        st.success(

                            f"🎉 {len(valid_entries)} "
                            "അപേക്ഷകൾ Google Sheets-ൽ "
                            "വിജയകരമായി സേവ് ചെയ്തു."
                        )

                        st.rerun()

                    except Exception as exc:

                        st.error(

                            "❌ Google Sheets-ലേക്ക് "
                            "സേവ് ചെയ്യാൻ കഴിഞ്ഞില്ല."
                        )

                        with st.expander(
                            "🔍 Technical error"
                        ):

                            st.exception(exc)

    # =========================================================
    # GROUP REGISTRATION
    # =========================================================

    else:

        st.subheader(
            "👥 ഗ്രൂപ്പ് മത്സരങ്ങളുടെ എൻട്രി"
        )

        g_type = st.selectbox(

            "മത്സര വിഭാഗം തിരഞ്ഞെടുക്കുക",

            [
                "കലാമത്സരം",
                "കായിക മത്സരം",
            ],

            key="group_cat_select",
        )

        available_group_events = (

            ARTS_GROUP

            if g_type == "കലാമത്സരം"

            else SPORTS_GROUP
        )

        with st.form(
            "group_form_single"
        ):

            col1, col2 = st.columns(2)

            with col1:

                st.info(
                    f"തിരഞ്ഞെടുത്ത വിഭാഗം: "
                    f"**{g_type}**"
                )

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

                    [
                        u
                        for u in ALL_UNITS
                        if u != unit
                    ],

                    key="cluster_units",
                )

            submit_group = st.form_submit_button(

                "🚀 ഗ്രൂപ്പ് എൻട്രി സേവ് ചെയ്യുക",

                use_container_width=True,
            )

        # -----------------------------------------------------
        # SAVE GROUP
        # -----------------------------------------------------

        if submit_group:

            if (
                not tm_name.strip()
                or not tm_phone.strip()
                or not atm_name.strip()
                or not atm_phone.strip()
            ):

                st.error(

                    "⚠️ മാനേജരുടെയും "
                    "അസിസ്റ്റന്റ് മാനേജരുടെയും "
                    "പേരും ഫോൺ നമ്പറും നിർബന്ധമാണ്."
                )

            else:

                g_entry = [{

                    "വിഭാഗം":
                        g_type,

                    "മേഖല":
                        detected_zone,

                    "പ്രധാന യൂണിറ്റ്":
                        unit,

                    "ഇനത്തിന്റെ പേര്":
                        g_event,

                    "ക്ലസ്റ്റർ യൂണിറ്റുകൾ":
                        (
                            ", ".join(
                                cluster_units
                            )
                            if cluster_units
                            else "-"
                        ),

                    "ടീം മാനേജർ":
                        (
                            f"{tm_name.strip()} "
                            f"({tm_phone.strip()})"
                        ),

                    "അസിസ്റ്റന്റ് മാനേജർ":
                        (
                            f"{atm_name.strip()} "
                            f"({atm_phone.strip()})"
                        ),

                    "രജിസ്റ്റർ ചെയ്ത സമയം":
                        datetime.now().strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ),
                }]

                try:

                    append_rows(
                        SHEET_GROUP,
                        g_entry,
                    )

                    st.success(

                        f"🎉 ഗ്രൂപ്പ് മത്സരം "
                        f"({g_event}) "
                        "വിജയകരമായി രജിസ്റ്റർ ചെയ്തു."
                    )

                    st.rerun()

                except Exception as exc:

                    st.error(

                        "❌ Google Sheets-ലേക്ക് "
                        "സേവ് ചെയ്യാൻ കഴിഞ്ഞില്ല."
                    )

                    with st.expander(
                        "🔍 Technical error"
                    ):

                        st.exception(exc)


# =============================================================
# CENTRAL DASHBOARD
# =============================================================

else:

    st.header(
        "📊 സെൻട്രൽ ഡാഷ്‌ബോർഡ്"
    )

    st.caption(
        "⛪ St. George Parish Day • "
        "Live Registration Command Center"
    )

    # =========================================================
    # ACTION BAR
    # =========================================================

    action1, action2, action3, action4 = st.columns(
        [1.2, 1.2, 1.2, 3]
    )

    with action1:

        if st.button(
            "🔄 Refresh",
            use_container_width=True,
        ):

            st.rerun()

    with action2:

        if st.button(
            "🔌 Test Connection",
            use_container_width=True,
        ):

            ok, result = (
                test_google_connection()
            )

            if ok:

                st.success(
                    f"Connected: {result}"
                )

            else:

                st.error(
                    "Google Sheets connection failed."
                )

                st.code(result)

    with action3:

        auto_refresh = st.toggle(
            "Auto refresh",
            value=False,
        )

    with action4:

        st.info(
            "Dashboard reads "
            "Individual_Data and Group_Data "
            "directly from Google Sheets."
        )

    if auto_refresh:

        st.caption(
            "🔄 Auto refresh is enabled. "
            "Click Refresh for an immediate "
            "live reload."
        )

    # =========================================================
    # LOAD DATA
    # =========================================================

    with st.spinner(
        "📡 Google Sheets-ൽ നിന്ന് "
        "live data ലോഡ് ചെയ്യുന്നു..."
    ):

        df_ind, ind_error = (
            fetch_live_data(
                SHEET_INDIVIDUAL
            )
        )

        df_grp, grp_error = (
            fetch_live_data(
                SHEET_GROUP
            )
        )

    # =========================================================
    # CONNECTION ERRORS
    # =========================================================

    if ind_error:

        st.error(
            "❌ Individual_Data വായിക്കാൻ കഴിഞ്ഞില്ല."
        )

        with st.expander(
            "Individual_Data error"
        ):

            st.code(ind_error)

    if grp_error:

        st.error(
            "❌ Group_Data വായിക്കാൻ കഴിഞ്ഞില്ല."
        )

        with st.expander(
            "Group_Data error"
        ):

            st.code(grp_error)

    # =========================================================
    # FIND COLUMNS
    # =========================================================

    unit_col_ind = find_column(

        df_ind,

        [
            "യൂണിറ്റ്",
            "unit",
            "family unit",
            "unit name",
        ],
    )

    unit_col_grp = find_column(

        df_grp,

        [
            "പ്രധാന യൂണിറ്റ്",
            "പ്രധാന യൂണിറ്റ് പേര്",
            "ക്ലസ്റ്റർ യൂണിറ്റുകൾ",
            "യൂണിറ്റ്",
            "unit",
            "main unit",
            "main_unit",
            "family unit",
        ],
    )

    events_col_ind = find_column(

        df_ind,

        [
            "തിരഞ്ഞെടുത്ത ഇനങ്ങൾ",
            "events",
            "ഇനങ്ങൾ",
            "event",
        ],
    )

    events_col_grp = find_column(

        df_grp,

        [
            "ഇനത്തിന്റെ പേര്",
            "event",
            "ഇനം",
            "events",
        ],
    )

    zone_col_ind = find_column(

        df_ind,

        [
            "മേഖല",
            "zone",
        ],
    )

    zone_col_grp = find_column(

        df_grp,

        [
            "മേഖല",
            "zone",
        ],
    )

    # =========================================================
    # PREPARE DASHBOARD DATA
    # =========================================================

    ind = _prepare_dashboard_data(
        df_ind,
        unit_col_ind,
    )

    grp = _prepare_dashboard_data(
        df_grp,
        unit_col_grp,
    )

    # =========================================================
    # DATA QUALITY
    # =========================================================

    if (
        not ind_error
        and ind.empty
    ):

        st.warning(
            "⚠️ Individual_Data is connected, "
            "but no individual rows were loaded."
        )

    if (
        not grp_error
        and grp.empty
    ):

        st.warning(
            "⚠️ Group_Data is connected, "
            "but no group rows were loaded."
        )

    # =========================================================
    # FILTER BAR
    # =========================================================

    st.subheader(
        "🎛️ Dashboard Filters"
    )

    filter1, filter2, filter3 = st.columns(3)

    with filter1:

        zone_options = [
            "All Zones"
        ] + list(
            UNITS_BY_ZONE.keys()
        )

        selected_zone = st.selectbox(

            "Zone",

            zone_options,

            key="central_zone_filter",
        )

    zone_units = (

        ALL_UNITS

        if selected_zone == "All Zones"

        else UNITS_BY_ZONE.get(
            selected_zone,
            [],
        )
    )

    with filter2:

        selected_unit = st.selectbox(

            "Family Unit",

            [
                "All Units"
            ] + zone_units,

            key="central_unit_filter",
        )

    with filter3:

        registration_type = st.selectbox(

            "Registration Type",

            [
                "All",
                "Individual",
                "Group",
            ],

            key="central_type_filter",
        )

    # =========================================================
    # APPLY FILTERS
    # =========================================================

    ind_view = ind.copy()

    grp_view = grp.copy()

    if selected_zone != "All Zones":

        ind_view = ind_view[
            ind_view[
                "__Dashboard Zone"
            ].eq(selected_zone)
        ]

        grp_view = grp_view[
            grp_view[
                "__Dashboard Zone"
            ].eq(selected_zone)
        ]

    if selected_unit != "All Units":

        ind_view = _rows_for_unit(

            ind_view,

            selected_unit,

            unit_col_ind,
        )

        grp_view = _rows_for_unit(

            grp_view,

            selected_unit,

            unit_col_grp,
        )

    if registration_type == "Individual":

        grp_view = (
            grp_view
            .iloc[0:0]
            .copy()
        )

    elif registration_type == "Group":

        ind_view = (
            ind_view
            .iloc[0:0]
            .copy()
        )

    # =========================================================
    # KPI CARDS
    # =========================================================

    individual_count = len(
        ind_view
    )

    group_count = len(
        grp_view
    )

    total_count = (
        individual_count
        + group_count
    )

    registered_unit_set = set(

        x

        for x in pd.concat(

            [

                (
                    ind_view[
                        "__Dashboard Unit"
                    ]

                    if "__Dashboard Unit"
                    in ind_view

                    else pd.Series(
                        dtype=str
                    )
                ),

                (
                    grp_view[
                        "__Dashboard Unit"
                    ]

                    if "__Dashboard Unit"
                    in grp_view

                    else pd.Series(
                        dtype=str
                    )
                ),
            ],

            ignore_index=True,
        ).tolist()

        if x in ALL_UNITS
    )

    k1, k2, k3, k4, k5 = st.columns(5)

    k1.metric(
        "👤 Individual",
        individual_count,
    )

    k2.metric(
        "👥 Group",
        group_count,
    )

    k3.metric(
        "📋 Total",
        total_count,
    )

    k4.metric(

        "🏘️ Units Registered",

        f"{len(registered_unit_set)} / "
        f"{len(ALL_UNITS)}",
    )

    k5.metric(

        "📈 Avg / Registered Unit",

        round(
            total_count
            / len(registered_unit_set),
            1,
        )
        if registered_unit_set
        else 0,
    )

    st.markdown("---")

    # =========================================================
    # UNIT PERFORMANCE MATRIX
    # =========================================================

    st.subheader(
        f"🏘️ Unit Performance — "
        f"All {len(ALL_UNITS)} Units"
    )

    unit_rows = []

    for zone, units in (
        UNITS_BY_ZONE.items()
    ):

        for current_unit in units:

            n_ind = len(
                _rows_for_unit(
                    ind_view,
                    current_unit,
                    unit_col_ind,
                )
            )

            n_grp = len(
                _rows_for_unit(
                    grp_view,
                    current_unit,
                    unit_col_grp,
                )
            )

            unit_rows.append({

                "Zone":
                    zone,

                "Unit":
                    current_unit,

                "Individual":
                    n_ind,

                "Group":
                    n_grp,

                "Total":
                    n_ind + n_grp,

                "Status":
                    (
                        "✅ Registered"
                        if (
                            n_ind + n_grp
                        )
                        else
                        "⏳ No Entry"
                    ),
            })

    unit_df = pd.DataFrame(
        unit_rows
    )

    u1, u2 = st.columns(
        [2, 1]
    )

    with u1:

        st.dataframe(

            unit_df.sort_values(

                [
                    "Total",
                    "Unit",
                ],

                ascending=[
                    False,
                    True,
                ],
            ),

            use_container_width=True,

            hide_index=True,

            height=520,
        )

    with u2:

        registered = unit_df[
            unit_df["Total"] > 0
        ]

        pending = unit_df[
            unit_df["Total"] == 0
        ]

        st.metric(
            "✅ Registered Units",
            len(registered),
        )

        st.metric(
            "⏳ Units Without Entry",
            len(pending),
        )

        if not pending.empty:

            st.markdown(
                "**⏳ Pending Units**"
            )

            st.write(
                ", ".join(
                    pending["Unit"].tolist()
                )
            )

    st.markdown("---")

    # =========================================================
    # ZONE + EVENT ANALYTICS
    # =========================================================

    left, right = st.columns(2)

    with left:

        st.subheader(
            "🗺️ Zone Performance"
        )

        zone_rows = []

        for zone in UNITS_BY_ZONE:

            z_ind = int(

                (
                    ind_view[
                        "__Dashboard Zone"
                    ]
                    == zone
                ).sum()
            )

            z_grp = int(

                (
                    grp_view[
                        "__Dashboard Zone"
                    ]
                    == zone
                ).sum()
            )

            zone_rows.append({

                "Zone":
                    zone,

                "Individual":
                    z_ind,

                "Group":
                    z_grp,

                "Total":
                    z_ind + z_grp,
            })

        zone_df = pd.DataFrame(
            zone_rows
        )

        st.dataframe(

            zone_df,

            use_container_width=True,

            hide_index=True,
        )

        st.bar_chart(

            zone_df.set_index(
                "Zone"
            )["Total"]
        )

    with right:

        st.subheader(
            "🎯 Top Events"
        )

        event_counts = {}

        individual_event_counts = (
            _event_counts(
                ind_view,
                events_col_ind,
            )
        )

        for event, count in (
            individual_event_counts.items()
        ):

            event_counts[event] = (
                event_counts.get(
                    event,
                    0,
                )
                + count
            )

        group_event_counts = (
            _event_counts(
                grp_view,
                events_col_grp,
                prefix="👥 ",
            )
        )

        for event, count in (
            group_event_counts.items()
        ):

            event_counts[event] = (
                event_counts.get(
                    event,
                    0,
                )
                + count
            )

        if event_counts:

            event_df = pd.DataFrame(

                list(
                    event_counts.items()
                ),

                columns=[
                    "Event",
                    "Registrations",
                ],
            ).sort_values(

                "Registrations",

                ascending=False,

            ).head(15)

            st.dataframe(

                event_df,

                use_container_width=True,

                hide_index=True,
            )

            st.bar_chart(

                event_df.set_index(
                    "Event"
                )["Registrations"]
            )

        else:

            st.info(
                "No event data available "
                "for the selected filters."
            )

    st.markdown("---")

    # =========================================================
    # DETAILED UNIT VIEW
    # =========================================================

    st.subheader(
        "🔎 Detailed Unit View"
    )

    detail_unit = st.selectbox(

        "Select a unit to inspect",

        [
            "-- Select Unit --"
        ] + ALL_UNITS,

        key="detail_unit",
    )

    if (
        detail_unit
        != "-- Select Unit --"
    ):

        d_ind = _rows_for_unit(

            ind,

            detail_unit,

            unit_col_ind,
        )

        d_grp = _rows_for_unit(

            grp,

            detail_unit,

            unit_col_grp,
        )

        st.info(

            f"📍 {detail_unit} • "
            f"{get_zone_for_unit(detail_unit)} • "
            f"Individual: {len(d_ind)} • "
            f"Group: {len(d_grp)} • "
            f"Total: "
            f"{len(d_ind) + len(d_grp)}"
        )

        dt1, dt2 = st.columns(2)

        # -----------------------------------------------------
        # INDIVIDUAL DETAIL
        # -----------------------------------------------------

        with dt1:

            st.markdown(
                "#### 👤 Individual Entries"
            )

            if d_ind.empty:

                st.info(
                    "ഈ യൂണിറ്റിൽ "
                    "individual registration ഇല്ല."
                )

            else:

                st.dataframe(

                    d_ind.drop(

                        columns=[
                            "__Dashboard Unit",
                            "__Dashboard Zone",
                        ],

                        errors="ignore",
                    ),

                    use_container_width=True,

                    hide_index=True,
                )

        # -----------------------------------------------------
        # GROUP DETAIL
        # -----------------------------------------------------

        with dt2:

            st.markdown(
                "#### 👥 Group Entries"
            )

            if d_grp.empty:

                st.info(
                    "ഈ യൂണിറ്റിൽ "
                    "group registration ഇല്ല."
                )

            else:

                st.dataframe(

                    d_grp.drop(

                        columns=[
                            "__Dashboard Unit",
                            "__Dashboard Zone",
                        ],

                        errors="ignore",
                    ),

                    use_container_width=True,

                    hide_index=True,
                )

    st.markdown("---")

    # =========================================================
    # RECENT REGISTRATIONS
    # =========================================================

    st.subheader(
        "🕒 Recent Registrations"
    )

    recent_frames = []

    if not ind_view.empty:

        temp = ind_view.copy()

        temp["__Type"] = "Individual"

        recent_frames.append(temp)

    if not grp_view.empty:

        temp = grp_view.copy()

        temp["__Type"] = "Group"

        recent_frames.append(temp)

    if recent_frames:

        recent = pd.concat(
            recent_frames,
            ignore_index=True,
        )

        time_col = find_column(

            recent,

            [
                "രജിസ്റ്റർ ചെയ്ത സമയം",
                "registered time",
                "timestamp",
                "date",
                "time",
            ],
        )

        if time_col:

            recent["__SortTime"] = (
                pd.to_datetime(
                    recent[time_col],
                    errors="coerce",
                )
            )

            recent = recent.sort_values(

                "__SortTime",

                ascending=False,
            )

        recent_display = (

            recent.head(20)

            .drop(

                columns=[
                    "__Dashboard Unit",
                    "__Dashboard Zone",
                    "__SortTime",
                ],

                errors="ignore",
            )
        )

        st.dataframe(

            recent_display,

            use_container_width=True,

            hide_index=True,
        )

    else:

        st.info(
            "No registrations found "
            "for the selected filters."
        )

    # =========================================================
    # FULL REPORT TABS
    # =========================================================

    tab_ind, tab_grp, tab_diag = st.tabs(

        [
            "👤 Individual Report",
            "👥 Group Report",
            "🛠️ Data Diagnostics",
        ]
    )

    # =========================================================
    # INDIVIDUAL REPORT
    # =========================================================

    with tab_ind:

        st.subheader(
            "All Individual Registrations"
        )

        if not df_ind.empty:

            st.dataframe(

                df_ind,

                use_container_width=True,

                hide_index=True,

                height=500,
            )

            csv = (
                df_ind
                .to_csv(
                    index=False
                )
                .encode("utf-8-sig")
            )

            st.download_button(

                "📥 Download Individual CSV",

                csv,

                "all_individual_reports.csv",

                "text/csv",

                use_container_width=True,
            )

        else:

            st.info(
                "Individual_Data has no rows."
            )

    # =========================================================
    # GROUP REPORT
    # =========================================================

    with tab_grp:

        st.subheader(
            "All Group Registrations"
        )

        if not df_grp.empty:

            st.dataframe(

                df_grp,

                use_container_width=True,

                hide_index=True,

                height=500,
            )

            csv_grp = (
                df_grp
                .to_csv(
                    index=False
                )
                .encode("utf-8-sig")
            )

            st.download_button(

                "📥 Download Group CSV",

                csv_grp,

                "all_group_reports.csv",

                "text/csv",

                use_container_width=True,
            )

        else:

            st.info(
                "Group_Data has no rows."
            )

    # =========================================================
    # DATA DIAGNOSTICS
    # =========================================================

    with tab_diag:

        st.subheader(
            "🛠️ Data Diagnostics"
        )

        d1, d2, d3, d4 = st.columns(4)

        d1.metric(
            "Individual Rows",
            len(df_ind),
        )

        d2.metric(
            "Group Rows",
            len(df_grp),
        )

        d3.metric(

            "Individual Unit Column",

            "Found"
            if unit_col_ind
            else "Fallback",
        )

        d4.metric(

            "Group Unit Column",

            "Found"
            if unit_col_grp
            else "Fallback",
        )

        # -----------------------------------------------------
        # INDIVIDUAL COLUMNS
        # -----------------------------------------------------

        st.markdown(
            "#### Individual_Data Columns"
        )

        if not df_ind.empty:

            st.write(
                list(df_ind.columns)
            )

        else:

            st.write(
                "No columns"
            )

        # -----------------------------------------------------
        # GROUP COLUMNS
        # -----------------------------------------------------

        st.markdown(
            "#### Group_Data Columns"
        )

        if not df_grp.empty:

            st.write(
                list(df_grp.columns)
            )

        else:

            st.write(
                "No columns"
            )

        # -----------------------------------------------------
        # UNKNOWN ROWS
        # -----------------------------------------------------

        unknown_ind = (

            int(
                (
                    ind[
                        "__Dashboard Unit"
                    ]
                    == "UNKNOWN"
                ).sum()
            )

            if not ind.empty

            else 0
        )

        unknown_grp = (

            int(
                (
                    grp[
                        "__Dashboard Unit"
                    ]
                    == "UNKNOWN"
                ).sum()
            )

            if not grp.empty

            else 0
        )

        if (
            unknown_ind == 0
            and unknown_grp == 0
        ):

            st.success(
                "✅ All registration rows "
                "are mapped to known family units."
            )

        else:

            st.warning(

                f"Unmatched individual rows: "
                f"{unknown_ind} | "
                f"Unmatched group rows: "
                f"{unknown_grp}"
            )

        # -----------------------------------------------------
        # UNKNOWN INDIVIDUAL ROWS
        # -----------------------------------------------------

        if unknown_ind:

            st.markdown(
                "**Individual rows not mapped "
                "to a known unit**"
            )

            st.dataframe(

                ind[
                    ind[
                        "__Dashboard Unit"
                    ] == "UNKNOWN"
                ].drop(

                    columns=[
                        "__Dashboard Unit",
                        "__Dashboard Zone",
                    ],

                    errors="ignore",
                ),

                use_container_width=True,

                hide_index=True,
            )

        # -----------------------------------------------------
        # UNKNOWN GROUP ROWS
        # -----------------------------------------------------

        if unknown_grp:

            st.markdown(
                "**Group rows not mapped "
                "to a known unit**"
            )

            st.dataframe(

                grp[
                    grp[
                        "__Dashboard Unit"
                    ] == "UNKNOWN"
                ].drop(

                    columns=[
                        "__Dashboard Unit",
                        "__Dashboard Zone",
                    ],

                    errors="ignore",
                ),

                use_container_width=True,

                hide_index=True,
            )
