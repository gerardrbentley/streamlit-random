import ast
from datetime import datetime
from enum import Enum
from typing import Literal, Optional
import streamlit as st
import streamlit_pydantic as sp
from pydantic import BaseModel, Field
from streamlit_pydantic.types import FileContent
import requests


import pandas as pd
import inspect
from docstring_parser import parse
"""\
# Pandas Power 🐼

[pandas](https://pandas.pydata.org/docs/getting_started/index.html) is an extremely popular Python library (with ~18 million weekly downloads according to [snyk](https://snyk.io/advisor/python/pandas))

It's fantastic for handling data, so what if we made some of it's powerful bits web interactive?

Made with ❤️ from [Gar's Bar](https://tech.gerardbentley.com/)

## Dataframes from HTML

`df = pd.read_html(str, path object, or file-like object with HTML)`

If you have a chunk of HTML that contains tables of data in `<table></table>` tags, you can extract that data with pandas.

The HTML can come from a file or from making an HTTP request.

Don't have a url?
Try this one:
"""
st.code("https://en.wikipedia.org/wiki/Climate_of_Antarctica")
with st.expander('pd.read_html doc'):
    pd.read_html

parsed = parse(pd.read_html.__doc__)
args = {x.arg_name: x for x in parsed.params}
parsed_csv = parse(pd.read_csv.__doc__)
args_csv = {x.arg_name: x for x in parsed_csv.params}
sig = inspect.signature(pd.read_html)

def get_field_args(parameter):
    return (
        (parameter.annotation, ...)
        if parameter.default == parameter.empty
        else (parameter.annotation, parameter.default)
    )
pydantic_fields = {
    x.name: get_field_args(x)
    for x in sig.parameters.values()
}
class FlavorValue(Enum):
    LXML = 'lxml'
    BS4 = 'BeautifulSoup4'

PARSED_FIELDS = ['header', 'index_col', 'skiprows', 'attrs', 'parse_dates', 'encoding']

class ReadHTMLRequest(BaseModel):
    match: str = Field('.+', description=args['match'].description)
    flavor: Optional[Literal['lxml', 'bs4']] = Field('lxml', description=args['flavor'].description)
    header: Optional[str] = Field('None', description=args['header'].description + ' (Ex. "0", "1", "[0,1]")')
    index_col: Optional[str] = Field('None', description=args['index_col'].description + ' (Ex. "0", "1", "[0,1]")')
    skiprows: Optional[str] = Field('None', description=args['skiprows'].description + ' (Ex. "0", "1", "[0,1]")')
    attrs: Optional[str] = Field('None', description=args['attrs'].description + """ (Ex. "{'id': 'table'}")""")
    parse_dates: Optional[str] = Field('False', description=args_csv['parse_dates'].description)
    thousands: Optional[str] = Field(',', description=args['thousands'].description)
    encoding: Optional[str] = Field('None', description=args['encoding'].description)
    decimal: Optional[str] = Field('.', description=args['decimal'].description)
    # Requires making / choosing functions. Can do post-processing instead probably in most cases
    # converters: Optional[str] = Field('.', description=args['converters'].description)
    # na_values: Optional[str] = Field('None', description=args['na_values'].description)
    # keep_default_na: Optional[bool] = Field(True, description=args['keep_default_na'].description)
    displayed_only: Optional[bool] = Field(True, description=args['displayed_only'].description)


class RawReadHTML(ReadHTMLRequest):
    io: str = Field(..., format="multi-line", description="Raw HTML with tables")

class UrlReadHTML(ReadHTMLRequest):
    url: str = Field(description="Web address to fetch tables from")

class FileReadHTML(ReadHTMLRequest):
    html_file: FileContent = Field(
        ...,
        description="Upload an HTML File",
    )

raw_html_request = 'Raw HTML'
file_html_request = 'File Upload HTML'
url_request = 'URL Fetch'
options = {url_request: UrlReadHTML, raw_html_request: RawReadHTML, file_html_request: FileReadHTML}
request_type = st.radio('From URL, Uploaded HTML, or Raw HTML?', options, help='Choose how to submit your HTML data with tables to parse')

sp.pydantic_form(key="form", model=options[request_type], group_optional_fields='expander')

@st.experimental_memo
def convert_df(df: pd.DataFrame) -> bytes:
    return df.to_csv().encode('utf-8')

@st.experimental_memo
def fetch_html_from_url(url: str) -> str:
    response = requests.get(url)
    return response.text

def data_is_invalid(data, request_type):
    return (request_type == url_request and data.get('url') == '') or (request_type == file_html_request and data.get('html_file', 'n/a') is None) or (request_type == raw_html_request and data.get('io') == '')

# Hack around streamlit-pydantic form to persist after download button clicks
if 'form-data' in st.session_state:
    data = st.session_state['form-data']
    if data_is_invalid(data, request_type):
        st.stop()
    data_class = options[request_type]
    data = data_class(**data)
    kwargs = data.dict()
    with st.expander("Raw Form Inputs"):
        st.write(kwargs)

    if request_type == url_request:
        raw_html = fetch_html_from_url(data.url)
        kwargs = data.dict(exclude={'url'})
        kwargs['io'] = raw_html
    elif request_type == file_html_request:
        kwargs = data.dict(exclude={'html_file'})
        kwargs['io'] = data.html_file.as_str()

    for field in PARSED_FIELDS:
        kwargs[field] = ast.literal_eval(kwargs[field])
    
    with st.expander("pd.read_html Inputs"):
        st.write(kwargs)

    dataframes = pd.read_html(**kwargs)
    if not len(dataframes):
        st.warning("No Tables / Dataframes found 😿")
        st.stop()

    st.subheader("All Returned Tables/ Dataframes")
    for i, df in enumerate(dataframes):
        st.subheader(f"Table #{i + 1}")
        st.write(df)

        st.download_button(
            label=f"Download Table #{i + 1} as CSV",
            data=convert_df(df),
            file_name=f"table_{i+1}_{datetime.now().strftime('%Y_%m_%d_%H_%M_%S_%f')}.csv",
            mime='text/csv',
        )
