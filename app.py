# -*- coding: utf-8 -*-

import re
from datetime import date

import pandas as pd
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="St. George Parish Day Portal",
    page_icon="⛪",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# APPLICATION TITLE
# ============================================================

st.title("⛪ St. George Parish Day")
st.caption("Registration and Central Dashboard Portal")


# ============================================================
# ZONES AND UNITS
# ============================================================

ZONES = {
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
    for zone_units in ZONES.values()
    for unit in zone_units
]


# ============================================================
# EVENT DEFINITIONS
# ============================================================

INDIVIDUAL_EVENTS = {
    "Arts": {
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
    },
    "Sports": {
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
        ],
    },
    "Literary": {
        "ഉപന്യാസം": [
            "Kiddies",
            "Sub Junior",
            "Junior",
            "Youth",
            "Senior",
            "Super Senior",
        ],
        "കഥ രചന": [
            "Kiddies",
            "Sub Junior",
            "Junior",
            "Youth",
            "Senior",
            "Super Senior",
        ],
        "കവിത രചന": [
            "Kiddies",
            "Sub Junior",
            "Junior",
            "Youth",
            "Senior",
            "Super Senior",
        ],
        "ക്വിസ്": [
            "Kiddies",
            "Sub Junior",
            "Junior",
            "Youth",
            "Senior",
            "Super Senior",
        ],
        "ചിത്രാങ്കനം": [
            "Kiddies",
            "Sub Junior",
            "Junior",
            "Youth",
            "Senior",
            "Super Senior",
        ],
    },
}


GROUP_EVENTS = {
    "Arts": {
        "Group Dance - Kiddies": ["Kiddies"],
        "Group Dance - Sub Junior": ["Sub Junior"],
        "Group Dance - Junior": ["Junior"],
        "Group Dance - Youth": ["Youth"],
        "Mime": [
            "Sub Junior",
            "Junior",
            "Youth",
        ],
        "Group Song": [
            "Junior",
            "Youth",
            "Senior",
            "Super Senior",
        ],
        "മാർഗംകളി": [
            "Youth",
            "Senior",
            "Super Senior",
        ],
    },
    "Sports": {
        "4 X 100 Relay (SUB JUNIOR - BOYS)": [
            "Sub Junior",
        ],
        "4 X 100 Relay (SUB JUNIOR - GIRLS)": [
            "Sub Junior",
        ],
        "4 X 100 Relay (JUNIOR - BOYS)": [
            "Junior",
        ],
        "4 X 100 Relay (JUNIOR - GIRLS)": [
            "Junior",
        ],
        "4 X 100 Relay (YOUTH - BOYS)": [
            "Youth",
        ],
        "4 X 100 Relay (YOUTH - GIRLS)": [
            "Youth",
        ],
        "4 X 100 Relay (SENIOR - MEN)": [
            "Senior",
        ],
        "4 X 100 Relay (SENIOR - WOMEN)": [
            "Senior",
        ],
        "4x400 Relay": [
            "Sub Junior",
            "Junior",
            "Youth",
            "Senior",
        ],
        "Badminton Doubles (BOYS)": [
            "Sub Junior",
            "Junior",
            "Youth",
            "Senior",
        ],
        "Badminton Doubles (GIRLS)": [
            "Sub Junior",
            "Junior",
            "Youth",
            "Senior",
        ],
        "Men's Football 5s (Maximum 7 Players)": [
            "Sub Junior",
            "Junior",
            "Youth",
            "Senior",
        ],
        "Men's Cricket 6s (Maximum 7 Players)": [
            "Sub Junior",
            "Junior",
            "Youth",
            "Senior",
        ],
    },
}


# ============================================================
# AGE CATEGORY
# ============================================================

def get_age_category(dob):
    """
    Competition age categories:

    0-5   = Kiddies
    6-10  = Sub Junior
    11-15 = Junior
    16-35 = Youth
    36-55 = Senior
    56+   = Super Senior

    There is NO upper age limit.
    """

    today = date.today()

    age = today.year - dob.year - (
        (today.month, today.day) < (dob.month, dob.day)
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
        return "Super Senior", age


# ============================================================
# TEXT NORMALIZATION
# ============================================================

def clean_text(value):
    if value is None:
        return ""

    text = str(value).strip()

    text = re.sub(r"\s+", " ", text)

    return text


def _norm(value):
    """
    Strong normalization used for unit matching.
    """

    text = clean_text(value).upper()

    replacements = {
        ".": "",
        ",": "",
        "-": "",
        "_": "",
        "/": "",
        "\\": "",
        "(": "",
        ")": "",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    text = re.sub(r"\s+", "", text)

    return text


def _split_values(value):
    if value is None:
        return []

    text = clean_text(value)

    if not text:
        return []

    parts = re.split(
        r"[,;/|\n]+",
        text
    )

    return [
        clean_text(part)
        for part in parts
        if clean_text(part)
    ]


# ============================================================
# STREAMLIT VERSION COMPATIBILITY
# ============================================================
# Newer Streamlit versions replaced use_container_width=True with
# width="stretch" (and eventually removed the old argument).
# These helpers work on both old and new versions.

def show_df(data, **kwargs):
    kwargs.pop("use_container_width", None)
    kwargs.setdefault("hide_index", True)

    try:
        st.dataframe(data, width="stretch", **kwargs)
    except TypeError:
        st.dataframe(data, use_container_width=True, **kwargs)


def wide_button(label, **kwargs):
    kwargs.pop("use_container_width", None)

    try:
        return st.button(label, width="stretch", **kwargs)
    except TypeError:
        return st.button(label, use_container_width=True, **kwargs)


def bordered_container():
    try:
        return st.container(border=True)
    except TypeError:
        return st.container()


# ============================================================
# GOOGLE SHEETS CONFIGURATION
# ============================================================

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


def get_gsheets_secrets():
    """
    Supports both:

    [connections.gsheets]

    and

    [gsheets]
    """

    secrets = st.secrets

    if "connections" in secrets:
        try:
            connections = secrets["connections"]

            if "gsheets" in connections:
                return dict(connections["gsheets"])
        except Exception:
            pass

    if "gsheets" in secrets:
        try:
            return dict(secrets["gsheets"])
        except Exception:
            pass

    raise RuntimeError(
        "Google Sheets secrets were not found. "
        "Configure [connections.gsheets] or [gsheets] in Streamlit Secrets."
    )


def get_gspread_client():
    config = get_gsheets_secrets()

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
        if key not in config or not config[key]
    ]

    if missing:
        raise RuntimeError(
            "Missing Google credentials: "
            + ", ".join(missing)
        )

    private_key = str(config["private_key"])

    if "\\n" in private_key:
        private_key = private_key.replace("\\n", "\n")

    service_account_info = {
        "type": config["type"],
        "project_id": config["project_id"],
        "private_key_id": config["private_key_id"],
        "private_key": private_key,
        "client_email": config["client_email"],
        "client_id": config["client_id"],
    }

    if "auth_uri" in config:
        service_account_info["auth_uri"] = config["auth_uri"]

    if "token_uri" in config:
        service_account_info["token_uri"] = config["token_uri"]

    credentials = Credentials.from_service_account_info(
        service_account_info,
        scopes=SCOPES,
    )

    return gspread.authorize(credentials)


def get_spreadsheet(client):
    config = get_gsheets_secrets()

    spreadsheet_url = config.get(
        "spreadsheet_url",
        config.get("spreadsheet", ""),
    )

    if not spreadsheet_url:
        raise RuntimeError(
            "Spreadsheet URL/name not found in Google Sheets secrets."
        )

    spreadsheet_url = str(spreadsheet_url).strip()

    if spreadsheet_url.startswith("http"):
        return client.open_by_url(spreadsheet_url)

    return client.open(spreadsheet_url)


def get_worksheet(spreadsheet, worksheet_name):
    """
    Find a tab by name. Matching ignores case, spaces, underscores and
    punctuation ("Individual Data" == "Individual_Data"). A new tab is
    created only when no similar tab exists.
    """

    try:
        return spreadsheet.worksheet(worksheet_name)

    except gspread.WorksheetNotFound:
        pass

    wanted = _norm(worksheet_name)

    for sheet in spreadsheet.worksheets():

        if _norm(sheet.title) == wanted:
            return sheet

    return spreadsheet.add_worksheet(
        title=worksheet_name,
        rows=1000,
        cols=40,
    )


# ============================================================
# GOOGLE SHEETS DATA FUNCTIONS
# ============================================================

def fetch_live_data(worksheet):
    """
    Read a worksheet into a DataFrame.

    Unlike get_all_records(), this does NOT fail when the header row has
    blank or duplicate cells, and it ignores completely empty rows.
    Errors are raised so the caller can show them.
    """

    values = worksheet.get_all_values()

    if len(values) < 2:
        return pd.DataFrame()

    raw_headers = values[0]

    headers = []
    seen = {}

    for index, header in enumerate(raw_headers):

        header = clean_text(header) or f"Column {index + 1}"

        if header in seen:
            seen[header] += 1
            header = f"{header} ({seen[header]})"
        else:
            seen[header] = 1

        headers.append(header)

    rows = []

    for row in values[1:]:

        if not any(clean_text(cell) for cell in row):
            continue

        padded = list(row) + [""] * (len(headers) - len(row))

        rows.append(padded[: len(headers)])

    if not rows:
        return pd.DataFrame()

    return pd.DataFrame(rows, columns=headers)


@st.cache_data(ttl=10, show_spinner=False)
def load_sheet_df(sheet_name):
    """
    Cached read (10 seconds) so repeated clicks do not exhaust the
    Google Sheets read quota. The Refresh button clears this cache.
    """

    client = get_gspread_client()

    spreadsheet = get_spreadsheet(client)

    worksheet = get_worksheet(spreadsheet, sheet_name)

    return fetch_live_data(worksheet)


@st.cache_data(ttl=10, show_spinner=False)
def sheet_overview():
    """
    Which spreadsheet is the app really connected to, and which tabs
    does it contain? Used by the dashboard "Data check".
    """

    client = get_gspread_client()

    spreadsheet = get_spreadsheet(client)

    return {
        "title": spreadsheet.title,
        "url": spreadsheet.url,
        "tabs": [
            (sheet.title, sheet.row_count)
            for sheet in spreadsheet.worksheets()
        ],
    }


def append_rows(worksheet, rows):
    """
    Append dictionary rows according to the worksheet headers.

    Headers are matched ignoring case/spaces. Any column that is not
    in the sheet yet is added to the header row, so no value is lost.
    """

    if not rows:
        return

    existing_values = worksheet.get_all_values()

    if not existing_values or not any(
        clean_text(cell) for cell in existing_values[0]
    ):
        headers = list(rows[0].keys())

        worksheet.update(
            range_name="A1",
            values=[headers],
        )

    else:
        headers = list(existing_values[0])

        normalised = {
            _norm(header): header
            for header in headers
            if clean_text(header)
        }

        missing = [
            key
            for key in rows[0].keys()
            if _norm(key) not in normalised
        ]

        if missing:

            headers = headers + missing

            worksheet.update(
                range_name="A1",
                values=[headers],
            )

    lookup = {
        _norm(header): index
        for index, header in enumerate(headers)
        if clean_text(header)
    }

    values = []

    for row in rows:

        line = [""] * len(headers)

        for key, value in row.items():

            position = lookup.get(_norm(key))

            if position is not None:
                line[position] = value

        values.append(line)

    if values:
        worksheet.append_rows(
            values,
            value_input_option="USER_ENTERED",
        )


def test_google_connection():
    try:
        client = get_gspread_client()
        spreadsheet = get_spreadsheet(client)

        return True, spreadsheet.title

    except Exception as exc:
        return False, str(exc)


# ============================================================
# COLUMN HELPERS
# ============================================================

def find_column(df, candidates):
    if df is None or df.empty:
        return None

    columns = list(df.columns)

    normalized_columns = {
        _norm(column): column
        for column in columns
    }

    for candidate in candidates:
        key = _norm(candidate)

        if key in normalized_columns:
            return normalized_columns[key]

    # Partial match
    for candidate in candidates:
        key = _norm(candidate)

        for normalized, original in normalized_columns.items():
            if key and key in normalized:
                return original

    return None


def _row_has_unit(row, target_unit):
    """
    Check whether a row belongs to the selected unit.

    Preferred columns are checked first.
    A fallback scan across all cells is also performed.
    """

    target = _norm(target_unit)

    if not target:
        return False

    preferred_columns = [
        "Unit",
        "Unit Name",
        "യൂണിറ്റ്",
        "പ്രധാന യൂണിറ്റ്",
        "Main Unit",
        "Cluster Unit",
        "Cluster Units",
        "Unit/Zone",
    ]

    for column_name in preferred_columns:

        actual_column = None

        for column in row.index:
            if _norm(column) == _norm(column_name):
                actual_column = column
                break

        if actual_column is None:
            continue

        cell_value = row.get(actual_column, "")

        for value in _split_values(cell_value):
            if _norm(value) == target:
                return True

    # Fallback: scan the complete row.
    for value in row.values:

        for part in _split_values(value):

            if _norm(part) == target:
                return True

    return False


def _rows_for_unit(df, unit):
    if df is None or df.empty:
        return pd.DataFrame()

    mask = df.apply(
        lambda row: _row_has_unit(row, unit),
        axis=1,
    )

    return df.loc[mask].copy()


# ============================================================
# ZONE HELPERS
# ============================================================

def get_zone_for_unit(unit):
    target = _norm(unit)

    for zone, units in ZONES.items():

        for current_unit in units:

            if _norm(current_unit) == target:
                return zone

    return "UNASSIGNED"


def _derive_unit(row):
    """
    Try to identify the main unit from a registration row.
    """

    preferred_columns = [
        "Unit",
        "Unit Name",
        "യൂണിറ്റ്",
        "പ്രധാന യൂണിറ്റ്",
        "Main Unit",
        "Main Unit Name",
    ]

    for preferred in preferred_columns:

        for column in row.index:

            if _norm(column) == _norm(preferred):

                value = clean_text(row.get(column, ""))

                if value:
                    for unit in ALL_UNITS:
                        if _norm(unit) == _norm(value):
                            return unit

                    # Partial matching
                    for unit in ALL_UNITS:
                        if _norm(unit) in _norm(value):
                            return unit

    # Search every cell as fallback
    for value in row.values:

        value_text = clean_text(value)

        if not value_text:
            continue

        for unit in ALL_UNITS:

            if _norm(unit) == _norm(value_text):
                return unit

    return "UNKNOWN"


# ============================================================
# DASHBOARD DATA PREPARATION
# ============================================================

def _prepare_dashboard_data(df):
    if df is None or df.empty:
        return df

    data = df.copy()

    data["Dashboard Unit"] = data.apply(
        _derive_unit,
        axis=1,
    )

    data["Dashboard Zone"] = data["Dashboard Unit"].apply(
        get_zone_for_unit
    )

    # Fallback: use the saved "Zone" column when the unit is unknown.
    zone_col = next(
        (c for c in data.columns if _norm(c) == "ZONE"),
        None,
    )

    if zone_col is not None:

        valid_zones = {_norm(z): z for z in ZONES}

        data["Dashboard Zone"] = [
            current
            if current != "UNASSIGNED"
            else valid_zones.get(_norm(saved), "UNASSIGNED")
            for current, saved in zip(
                data["Dashboard Zone"], data[zone_col]
            )
        ]

    return data


def _event_counts(df):
    """
    Try to identify an event column and return event counts.
    """

    if df is None or df.empty:
        return pd.Series(dtype="int64")

    event_column = find_column(
        df,
        [
            "Event",
            "Event Name",
            "Competition",
            "Item",
            "ഇനം",
            "മത്സരം",
        ],
    )

    if not event_column:
        return pd.Series(dtype="int64")

    series = (
        df[event_column]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    series = series[series != ""]

    return series.value_counts()


# ============================================================
# DATE OF BIRTH PICKER (Day / Month / Year dropdowns)
# ============================================================
# st.date_input's calendar makes it very hard to go back to old
# years. Three dropdowns let the user jump straight to any year
# from the current year back to 1920.

MONTH_NAMES = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]

DOB_MIN_YEAR = 1920


def dob_picker(label, key_prefix, default_year=2010):
    """
    Returns a datetime.date, or None if the chosen date is invalid
    (e.g. 31 February or a date in the future).
    """

    st.markdown(f"**{label}**")

    today = date.today()

    years = list(range(today.year, DOB_MIN_YEAR - 1, -1))

    if default_year not in years:
        default_year = years[0]

    c_day, c_month, c_year = st.columns([1, 2, 1.4])

    with c_day:
        day = st.selectbox(
            "Day",
            list(range(1, 32)),
            key=f"{key_prefix}_day",
        )

    with c_month:
        month_name = st.selectbox(
            "Month",
            MONTH_NAMES,
            key=f"{key_prefix}_month",
        )

    with c_year:
        year = st.selectbox(
            "Year",
            years,
            index=years.index(default_year),
            key=f"{key_prefix}_year",
        )

    month = MONTH_NAMES.index(month_name) + 1

    try:
        dob = date(year, month, day)
    except ValueError:
        st.error(
            f"{day} {month_name} {year} is not a valid date."
        )
        return None

    if dob > today:
        st.error("Date of birth cannot be in the future.")
        return None

    return dob

# ============================================================
# SESSION STATE
# ============================================================

if "page" not in st.session_state:
    st.session_state.page = "Registration"

if "refresh_counter" not in st.session_state:
    st.session_state.refresh_counter = 0

if "form_version" not in st.session_state:
    st.session_state.form_version = 0

if "flash" not in st.session_state:
    st.session_state.flash = ""


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("⛪ Parish Day Portal")

    page = st.radio(
        "Navigation",
        [
            "Registration",
            "Central Dashboard",
            "Google Sheets Test",
        ],
        index=[
            "Registration",
            "Central Dashboard",
            "Google Sheets Test",
        ].index(st.session_state.page),
    )

    st.session_state.page = page

    st.divider()

    st.subheader("Age Categories")

    st.markdown(
        """
        **Kiddies:** 0 - 5 years

        **Sub Junior:** 6 - 10 years

        **Junior:** 11 - 15 years

        **Youth:** 16 - 35 years

        **Senior:** 36 - 55 years

        **Super Senior:** 56+ years
        """
    )

    st.divider()

    st.caption(
        "St. George Parish Day Registration System"
    )


# ============================================================
# REGISTRATION PAGE
# ============================================================
# NOTE: The widgets here are intentionally NOT inside st.form().
# Inside a form Streamlit does not update anything until the submit
# button is pressed, which is why Zone / Unit / DOB / Age Category
# looked broken. Without a form they update instantly.

if page == "Registration":

    st.header("📝 Participant Registration")

    # Changing this number gives every widget a fresh key,
    # which clears the whole form after a successful save.
    fv = st.session_state.form_version

    if st.session_state.flash:
        st.success(st.session_state.flash)
        st.session_state.flash = ""

    registration_type = st.radio(
        "Registration Type",
        [
            "Individual Registration",
            "Group Registration",
        ],
        horizontal=True,
    )

    st.divider()

    # --------------------------------------------------------
    # INDIVIDUAL REGISTRATION
    # --------------------------------------------------------

    if registration_type == "Individual Registration":

        st.subheader("👤 Individual Registration")

        col1, col2 = st.columns(2)

        with col1:

            name = st.text_input(
                "പങ്കെടുക്കുന്ന വ്യക്തിയുടെ പേര് *",
                key=f"ind_name_{fv}",
            )

            zone = st.selectbox(
                "സോൺ (Zone) *",
                list(ZONES.keys()),
                key=f"ind_zone_{fv}",
            )

            # Units are filtered by the selected zone.
            # The zone is part of the key so the list refreshes properly.
            unit = st.selectbox(
                "യൂണിറ്റ് *",
                ZONES[zone],
                key=f"ind_unit_{fv}_{zone}",
            )

            phone = st.text_input(
                "ഫോൺ നമ്പർ",
                key=f"ind_phone_{fv}",
            )

            gender = st.selectbox(
                "ലിംഗം",
                ["Male", "Female", "Other"],
                key=f"ind_gender_{fv}",
            )

        with col2:

            dob = dob_picker(
                "ജനന തീയതി (DOB) *",
                key_prefix=f"ind_dob_{fv}",
            )

            age_category = None
            calculated_age = None

            if dob is not None:

                age_category, calculated_age = get_age_category(
                    dob
                )

                st.info(
                    f"Calculated Age: **{calculated_age} years**\n\n"
                    f"Category: **{age_category}**"
                )

            st.text_input(
                "Zone",
                value=zone,
                disabled=True,
                key=f"ind_zone_display_{fv}_{zone}",
            )

        st.divider()

        st.subheader("🎯 Select Events")

        selected_events = []

        if age_category is None:

            st.warning(
                "Select a valid date of birth to see the events."
            )

        else:

            for category, events in INDIVIDUAL_EVENTS.items():

                available = [
                    event_name
                    for event_name, categories in events.items()
                    if age_category in categories
                ]

                if not available:
                    continue

                st.markdown(
                    f"### {category}"
                )

                for event_name in available:

                    selected = st.checkbox(
                        event_name,
                        key=f"ind_{fv}_{category}_{event_name}",
                    )

                    if selected:
                        selected_events.append(
                            event_name
                        )

        st.divider()

        submitted = wide_button(
            "💾 Save Individual Registration",
            use_container_width=True,
            type="primary",
            key=f"ind_submit_{fv}",
        )

        if submitted:

            if not clean_text(name):

                st.error(
                    "Please enter the participant name."
                )

            elif dob is None:

                st.error(
                    "Please select a valid date of birth."
                )

            elif not selected_events:

                st.error(
                    "Please select at least one event."
                )

            else:

                try:

                    client = get_gspread_client()

                    spreadsheet = get_spreadsheet(
                        client
                    )

                    worksheet = get_worksheet(
                        spreadsheet,
                        "Individual_Data",
                    )

                    rows = []

                    for event_name in selected_events:

                        rows.append(
                            {
                                "Timestamp": pd.Timestamp.now().strftime(
                                    "%Y-%m-%d %H:%M:%S"
                                ),
                                "Name": clean_text(name),
                                "Unit": unit,
                                "Zone": zone,
                                "Phone": phone,
                                "Gender": gender,
                                "DOB": dob.strftime(
                                    "%Y-%m-%d"
                                ),
                                "Age": calculated_age,
                                "Age Category": age_category,
                                "Event": event_name,
                            }
                        )

                    append_rows(
                        worksheet,
                        rows,
                    )

                    st.session_state.flash = (
                        f"Registration saved successfully for "
                        f"{clean_text(name)} "
                        f"({len(selected_events)} event(s))."
                    )

                    st.cache_data.clear()

                    st.session_state.form_version += 1

                    st.rerun()

                except Exception as exc:

                    st.error(
                        "Unable to save registration."
                    )

                    st.exception(exc)

    # --------------------------------------------------------
    # GROUP REGISTRATION
    # --------------------------------------------------------

    else:

        st.subheader("👥 Group Registration")

        col1, col2 = st.columns(2)

        with col1:

            group_name = st.text_input(
                "Group / Team Name *",
                key=f"grp_name_{fv}",
            )

            zone = st.selectbox(
                "സോൺ (Zone) *",
                list(ZONES.keys()),
                key=f"grp_zone_{fv}",
            )

            main_unit = st.selectbox(
                "പ്രധാന യൂണിറ്റ് *",
                ZONES[zone],
                key=f"grp_unit_{fv}_{zone}",
            )

            group_contact = st.text_input(
                "Contact Number",
                key=f"grp_contact_{fv}",
            )

        with col2:

            group_category = st.selectbox(
                "Group Category",
                [
                    "Kiddies",
                    "Sub Junior",
                    "Junior",
                    "Youth",
                    "Senior",
                    "Super Senior",
                ],
                key=f"grp_category_{fv}",
            )

            group_size = st.number_input(
                "Number of Participants",
                min_value=1,
                max_value=100,
                value=1,
                step=1,
                key=f"grp_size_{fv}",
            )

        st.divider()

        st.subheader("🎯 Group Events")

        selected_group_events = []

        for category, events in GROUP_EVENTS.items():

            available = [
                event_name
                for event_name, categories in events.items()
                if group_category in categories
            ]

            if not available:
                continue

            st.markdown(
                f"### {category}"
            )

            for event_name in available:

                selected = st.checkbox(
                    event_name,
                    key=f"grp_{fv}_{category}_{event_name}",
                )

                if selected:
                    selected_group_events.append(
                        event_name
                    )

        st.divider()

        st.subheader(
            "Additional Cluster Units"
        )

        cluster_units = st.multiselect(
            "If this group represents multiple units, select them here.",
            [
                u
                for u in ALL_UNITS
                if u != main_unit
            ],
            key=f"grp_cluster_{fv}_{main_unit}",
        )

        submitted = wide_button(
            "💾 Save Group Registration",
            use_container_width=True,
            type="primary",
            key=f"grp_submit_{fv}",
        )

        if submitted:

            if not clean_text(group_name):

                st.error(
                    "Please enter the group/team name."
                )

            elif not selected_group_events:

                st.error(
                    "Please select at least one group event."
                )

            else:

                try:

                    client = get_gspread_client()

                    spreadsheet = get_spreadsheet(
                        client
                    )

                    worksheet = get_worksheet(
                        spreadsheet,
                        "Group_Data",
                    )

                    unit_text = ", ".join(
                        [main_unit] + cluster_units
                    )

                    rows = []

                    for event_name in selected_group_events:

                        rows.append(
                            {
                                "Timestamp": pd.Timestamp.now().strftime(
                                    "%Y-%m-%d %H:%M:%S"
                                ),
                                "Group Name": clean_text(group_name),
                                "പ്രധാന യൂണിറ്റ്": main_unit,
                                "Cluster Units": unit_text,
                                "Zone": zone,
                                "Contact": group_contact,
                                "Category": group_category,
                                "Participants": group_size,
                                "Event": event_name,
                            }
                        )

                    append_rows(
                        worksheet,
                        rows,
                    )

                    st.session_state.flash = (
                        f"Group registration saved successfully for "
                        f"{clean_text(group_name)} "
                        f"({len(selected_group_events)} event(s))."
                    )

                    st.cache_data.clear()

                    st.session_state.form_version += 1

                    st.rerun()

                except Exception as exc:

                    st.error(
                        "Unable to save group registration."
                    )

                    st.exception(exc)


# ============================================================
# GOOGLE SHEETS TEST
# ============================================================

elif page == "Google Sheets Test":

    st.header("🔌 Google Sheets Connection Test")

    st.write(
        "Use this page to verify the Google Sheets connection."
    )

    if wide_button(
        "🔄 Test Google Connection",
        use_container_width=True,
    ):

        success, result = test_google_connection()

        if success:

            st.success(
                f"Google Sheets connection successful: {result}"
            )

        else:

            st.error(
                "Google Sheets connection failed."
            )

            st.code(
                result
            )


# ============================================================
# CENTRAL DASHBOARD
# ============================================================

elif page == "Central Dashboard":

    st.header("📊 Central Dashboard")

    st.caption(
        "Live registration overview from Individual_Data and Group_Data"
    )

    # --------------------------------------------------------
    # DASHBOARD CONTROLS
    # --------------------------------------------------------

    col1, col2, col3 = st.columns(
        [1, 1, 2]
    )

    with col1:

        refresh_clicked = wide_button(
            "🔄 Refresh Dashboard",
            use_container_width=True,
        )

    with col2:

        show_empty_units = st.checkbox(
            "Show units with zero entries",
            value=True,
        )

    with col3:

        selected_zone = st.selectbox(
            "Filter by Zone",
            [
                "ALL ZONES"
            ] + list(ZONES.keys()),
        )

    if refresh_clicked:

        st.cache_data.clear()

        st.rerun()

    st.divider()

    # --------------------------------------------------------
    # LOAD GOOGLE SHEETS
    # --------------------------------------------------------

    try:

        individual_df = load_sheet_df("Individual_Data")

        group_df = load_sheet_df("Group_Data")

    except Exception as exc:

        st.error(
            "Unable to connect to Google Sheets."
        )

        st.exception(exc)

        st.stop()

    # --------------------------------------------------------
    # PREPARE DATA
    # --------------------------------------------------------

    individual_df = _prepare_dashboard_data(
        individual_df
    )

    group_df = _prepare_dashboard_data(
        group_df
    )

    # --------------------------------------------------------
    # TOP METRICS
    # --------------------------------------------------------

    individual_count = (
        len(individual_df)
        if not individual_df.empty
        else 0
    )

    group_count = (
        len(group_df)
        if not group_df.empty
        else 0
    )

    individual_people = individual_count

    # Since individual rows are normally one row per event,
    # show event registrations separately.
    individual_event_count = individual_count

    group_event_count = group_count

    total_event_entries = (
        individual_event_count
        + group_event_count
    )

    m1, m2, m3, m4 = st.columns(4)

    m1.metric(
        "👤 Individual Entries",
        individual_people,
    )

    m2.metric(
        "👥 Group Entries",
        group_count,
    )

    m3.metric(
        "🎯 Individual Event Entries",
        individual_event_count,
    )

    m4.metric(
        "🏆 Total Event Entries",
        total_event_entries,
    )

    st.divider()

    # --------------------------------------------------------
    # ZONE SUMMARY
    # --------------------------------------------------------

    _nothing_loaded = individual_df.empty and group_df.empty

    if _nothing_loaded:

        st.warning(
            "No registration rows were found in the connected Google "
            "Sheet. Open the Data check below to see which spreadsheet "
            "and tabs the app is reading."
        )

    st.caption(
        "Last loaded: "
        + pd.Timestamp.now().strftime("%d %b %Y, %I:%M:%S %p")
        + " (data refreshes every 10 seconds, or press Refresh)"
    )

    with st.expander(
        "🛠️ Data check (rows loaded from Google Sheets)",
        expanded=_nothing_loaded,
    ):

        try:

            overview_info = sheet_overview()

            st.write(
                f"**Connected spreadsheet:** "
                f"[{overview_info['title']}]({overview_info['url']})"
            )

            st.write(
                "**Tabs found:** "
                + ", ".join(
                    f"{name} ({rows} rows)"
                    for name, rows in overview_info["tabs"]
                )
            )

        except Exception as exc:

            st.error(f"Could not read spreadsheet details: {exc}")

        for label, frame in (
            ("Individual_Data", individual_df),
            ("Group_Data", group_df),
        ):

            if frame is None or frame.empty:
                st.write(f"**{label}:** 0 rows")
                continue

            st.write(
                f"**{label}:** {len(frame)} rows"
            )

            st.caption(
                "Columns: "
                + ", ".join(
                    c for c in frame.columns
                    if c not in ("Dashboard Unit", "Dashboard Zone")
                )
            )

            unmatched = frame[frame["Dashboard Unit"] == "UNKNOWN"]

            if not unmatched.empty:
                st.warning(
                    f"{len(unmatched)} row(s) have a unit that does not "
                    "match any unit in the list:"
                )
                show_df(
                    unmatched.drop(
                        columns=["Dashboard Unit", "Dashboard Zone"],
                        errors="ignore",
                    )
                )

    st.subheader("🗺️ Zone Summary")

    zone_rows = []

    zones_to_show = list(ZONES.keys())

    if selected_zone != "ALL ZONES":
        zones_to_show = [
            selected_zone
        ]

    for zone in zones_to_show:

        zone_individual = 0
        zone_group = 0

        if not individual_df.empty:

            zone_individual = int(
                (
                    individual_df["Dashboard Zone"]
                    == zone
                ).sum()
            )

        if not group_df.empty:

            zone_group = int(
                (
                    group_df["Dashboard Zone"]
                    == zone
                ).sum()
            )

        zone_rows.append(
            {
                "Zone": zone,
                "Individual Entries": zone_individual,
                "Group Entries": zone_group,
                "Total Entries": (
                    zone_individual
                    + zone_group
                ),
            }
        )

    if selected_zone == "ALL ZONES":

        un_ind = (
            int((individual_df["Dashboard Zone"] == "UNASSIGNED").sum())
            if not individual_df.empty else 0
        )

        un_grp = (
            int((group_df["Dashboard Zone"] == "UNASSIGNED").sum())
            if not group_df.empty else 0
        )

        if un_ind + un_grp > 0:

            zone_rows.append(
                {
                    "Zone": "UNASSIGNED",
                    "Individual Entries": un_ind,
                    "Group Entries": un_grp,
                    "Total Entries": un_ind + un_grp,
                }
            )

    zone_summary_df = pd.DataFrame(
        zone_rows
    )

    show_df(
        zone_summary_df,
        use_container_width=True,
        hide_index=True,
    )

    st.divider()

    # --------------------------------------------------------
    # UNIT-BY-UNIT DASHBOARD
    # --------------------------------------------------------

    st.subheader("🏘️ Unit-wise Registration Dashboard")

    for zone in zones_to_show:

        st.markdown(
            f"## 📍 {zone}"
        )

        zone_units = ZONES.get(
            zone,
            []
        )

        for unit in zone_units:

            unit_individual_df = _rows_for_unit(
                individual_df,
                unit,
            )

            unit_group_df = _rows_for_unit(
                group_df,
                unit,
            )

            individual_entries = len(
                unit_individual_df
            )

            group_entries = len(
                unit_group_df
            )

            total_entries = (
                individual_entries
                + group_entries
            )

            # --------------------------------------------
            # IMPORTANT:
            # Show ALL SAINTS and every other unit
            # even when no data exists.
            # --------------------------------------------

            if (
                not show_empty_units
                and total_entries == 0
            ):
                continue

            with bordered_container():

                title_col, metric_col = st.columns(
                    [4, 1]
                )

                with title_col:

                    st.markdown(
                        f"### ⛪ {unit}"
                    )

                    st.caption(
                        f"{zone}"
                    )

                with metric_col:

                    st.metric(
                        "Total",
                        total_entries,
                    )

                c1, c2, c3 = st.columns(3)

                c1.metric(
                    "👤 Individual",
                    individual_entries,
                )

                c2.metric(
                    "👥 Group",
                    group_entries,
                )

                c3.metric(
                    "🎯 Event Entries",
                    total_entries,
                )

                # ----------------------------------------
                # INDIVIDUAL DATA
                # ----------------------------------------

                st.markdown(
                    "#### 👤 Individual Entries"
                )

                if individual_entries > 0:

                    display_df = unit_individual_df.copy()

                    hidden_columns = [
                        "Dashboard Unit",
                        "Dashboard Zone",
                    ]

                    display_df = display_df.drop(
                        columns=[
                            column
                            for column in hidden_columns
                            if column in display_df.columns
                        ],
                        errors="ignore",
                    )

                    show_df(
                        display_df,
                        use_container_width=True,
                        hide_index=True,
                    )

                else:

                    st.info(
                        f"{unit} യൂണിറ്റിൽ വ്യക്തിഗത രജിസ്ട്രേഷൻ ഒന്നുമില്ല."
                    )

                # ----------------------------------------
                # GROUP DATA
                # ----------------------------------------

                st.markdown(
                    "#### 👥 Group Entries"
                )

                if group_entries > 0:

                    group_display_df = unit_group_df.copy()

                    hidden_columns = [
                        "Dashboard Unit",
                        "Dashboard Zone",
                    ]

                    group_display_df = group_display_df.drop(
                        columns=[
                            column
                            for column in hidden_columns
                            if column in group_display_df.columns
                        ],
                        errors="ignore",
                    )

                    show_df(
                        group_display_df,
                        use_container_width=True,
                        hide_index=True,
                    )

                else:

                    st.info(
                        "Group_Data-ൽ ഈ യൂണിറ്റിനായി ഡാറ്റ ലഭ്യമല്ല."
                    )

    st.divider()

    # --------------------------------------------------------
    # EVENT SUMMARY
    # --------------------------------------------------------

    st.subheader("🎯 Event-wise Summary")

    tab1, tab2 = st.tabs(
        [
            "Individual Events",
            "Group Events",
        ]
    )

    with tab1:

        individual_event_counts = _event_counts(
            individual_df
        )

        if not individual_event_counts.empty:

            event_table = (
                individual_event_counts
                .rename("Registrations")
                .reset_index()
                .rename(
                    columns={
                        "index": "Event"
                    }
                )
            )

            show_df(
                event_table,
                use_container_width=True,
                hide_index=True,
            )

        else:

            st.info(
                "No individual event data available."
            )

    with tab2:

        group_event_counts = _event_counts(
            group_df
        )

        if not group_event_counts.empty:

            event_table = (
                group_event_counts
                .rename("Registrations")
                .reset_index()
                .rename(
                    columns={
                        "index": "Event"
                    }
                )
            )

            show_df(
                event_table,
                use_container_width=True,
                hide_index=True,
            )

        else:

            st.info(
                "No group event data available."
            )

    # --------------------------------------------------------
    # RAW DATA
    # --------------------------------------------------------

    st.divider()

    with st.expander(
        "🔍 View Raw Individual_Data"
    ):

        if not individual_df.empty:

            raw_individual = individual_df.drop(
                columns=[
                    "Dashboard Unit",
                    "Dashboard Zone",
                ],
                errors="ignore",
            )

            show_df(
                raw_individual,
                use_container_width=True,
                hide_index=True,
            )

        else:

            st.info(
                "Individual_Data is empty."
            )

    with st.expander(
        "🔍 View Raw Group_Data"
    ):

        if not group_df.empty:

            raw_group = group_df.drop(
                columns=[
                    "Dashboard Unit",
                    "Dashboard Zone",
                ],
                errors="ignore",
            )

            show_df(
                raw_group,
                use_container_width=True,
                hide_index=True,
            )

        else:

            st.info(
                "Group_Data is empty."
            )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "⛪ St. George Parish Day Portal | Registration + Central Dashboard"
)
