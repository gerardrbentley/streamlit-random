import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Personal Spending Dashboard", page_icon="💰",
)
st.write("""\
# Streamlit Personal Spending Dashboard 💰

Built for [#30DaysOfStreamlit](https://share.streamlit.io/streamlit/30days) Day 4 (a day late 😄) with ❤️ from [Gar's Bar](https://tech.gerardbentley.com/)
""")
with st.expander("What's This?"):
    st.write("""\
Check out the example bank dataset or upload your own bank / debit card / credit card / spending spreadsheet!

Analyze your total and average spending over each month / week / day / year / quarter.
See what the minimum / maximum / total number of purchases were in each period.

If your data has a description / name / category column, view how many times you've made those purchases.

Or use it on other roughly timeseries aggregated univariate data!
""")

upload_data = st.file_uploader(
    "Bank / Credit Card Spreadsheet", type=["csv", "xls", "xlsx", "xlsm"]
)

if upload_data is None:
    st.info(
        "No File uploaded. Using example data from a [Kaggle Dataset](https://www.kaggle.com/datasets/apoorvwatsky/bank-transaction-data). Upload a CSV to use your own data!"
    )
    upload_data = open("data/bank.xlsx", mode="rb")
    separator = ","
    use_sample = True
else:
    separator = st.text_input(
        "CSV Delimiter",
        value=",",
        max_chars=1,
        help="How your CSV values are separated (doesn't matter for excel)",
    )
    use_sample = False


@st.cache_data
def read_csv_or_excel(data, sep):
    try:
        raw_df = pd.read_csv(data, sep=sep)
    except UnicodeDecodeError:
        try:
            raw_df = pd.read_excel(data)
        except Exception as e:
            raise e
    return raw_df


raw_df = read_csv_or_excel(upload_data, separator)
with st.expander("Show Raw Data"):
    st.json(raw_df.iloc[:100].to_json())

columns = list(raw_df.columns)
with st.expander("Show all columns"):
    st.write(" | ".join(columns))

time_col_default = 1 if use_sample else 0
val_col_default = 5 if use_sample else 1
description_col_default = 2 if use_sample else 2
sampling_options = {
    "Monthly": "M",
    "Weekly": "W",
    "Yearly": "A",
    "Daily": "D",
    "Quarterly": "Q",
}
with st.form("timeseries"):
    time_col = st.selectbox(
        "Time Column",
        columns,
        time_col_default,
        help="Name of the column in your csv with time period data",
    )
    only_negatives = st.checkbox(
        "Only use Negative values", help="If checked, will filter out any positive amount values"
    )
    value_col = st.selectbox(
        "Values Column",
        columns,
        val_col_default,
        help="Name of column with dollar values",
    )
    sampling_period = st.selectbox(
        "Time Series Period",
        sampling_options,
        help="How to define samples. Pandas will aggregate entries between periods to create a well-formed Time Series",
    )
    if len(columns) > 2:
        description_col = st.selectbox(
            "Description Column",
            columns,
            description_col_default,
            help="Name of column with descriptions / names",
        )
        top_n = st.number_input(
            "Number of Top Spending Categories to Show", min_value=1, value=5
        )
    else:
        description_col = None

    submitted = st.form_submit_button("Update Dataset")

if not submitted:
    st.info('Press "Update Dataset" to display your data')
    st.stop()

if description_col is None:
    filtered_columns = [time_col, value_col]
else:
    filtered_columns = [time_col, value_col, description_col]
filtered_df = raw_df[filtered_columns].copy()

if only_negatives:
    filtered_df = filtered_df[filtered_df[value_col] < 0.0]
if description_col is not None:
    filtered_df[description_col] = filtered_df[description_col].fillna('').astype(str)
filtered_df = filtered_df.dropna()
with st.expander("Show Filtered Data"):
    st.dataframe(filtered_df)


@st.cache_data
def get_timeseries_dfs(filtered_df, sampling_period, time_col):
    clean_df = filtered_df.copy()
    clean_df[time_col] = pd.to_datetime(clean_df[time_col])
    freq_string = sampling_options[sampling_period]
    clean_df = clean_df.set_index(time_col)
    clean_df = clean_df.resample(freq_string)

    agg_dfs = {
        "Sum": clean_df.sum(),
        "Mean": clean_df.mean(),
        "Max": clean_df.max(),
        "Min": clean_df.min(),
        "Count": clean_df.count(),
    }
    for key, df in agg_dfs.items():
        agg_dfs[key][value_col] = df[value_col].fillna(0.0)
    return agg_dfs


agg_dfs = get_timeseries_dfs(filtered_df, sampling_period, time_col)
with st.expander("Show Resampled Data"):
    st.write("Number of samples:", len(agg_dfs["Sum"]))
    for name, df in agg_dfs.items():
        st.subheader(f"{name} of {value_col} ({sampling_period})")
        st.dataframe(df)


def line_chart(df):
    return px.line(df, x=df.index, y=value_col)


for name, df in agg_dfs.items():
    st.subheader(f"{name} of {value_col} ({sampling_period})")
    fig = line_chart(df)
    st.plotly_chart(fig, use_container_width=True)

if description_col is not None:
    st.subheader("Top Spending Categories")
    descriptions = filtered_df[description_col].value_counts()
    st.dataframe(descriptions.iloc[:top_n])
else:
    st.warning("No Description column. Cannot show top categories")
