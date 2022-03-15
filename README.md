# Streamlit Random Apps

Made with :heart: from [Gar's Bar](https://tech.gerardbentley.com/)

- [Streamlit Random Apps](#streamlit-random-apps)
  - [Darts API Playground](#darts-api-playground)
  - [Streamlit Full Stack 3 Ways](#streamlit-full-stack-3-ways)
  - [Fidelity / Personal Stock Account Dashboard](#fidelity--personal-stock-account-dashboard)
  - [URL Scanner](#url-scanner)
  - [Peak Weather: NH 4,000 Footers](#peak-weather-nh-4000-footers)
  - [AWS Textract Document Text Scan](#aws-textract-document-text-scan)
  - [Darts Intro](#darts-intro)
  - [Function to Streamlit Form](#function-to-streamlit-form)
  - [Python Web Form Generator](#python-web-form-generator)
  - [Basic File Drop](#basic-file-drop)
  - [Gif Maker](#gif-maker)

## Darts API Playground

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/gerardrbentley/darts-playground/main)

Explore the Datasets, Metrics, and Models of the Darts Time Series library.

See: [Github Repo](https://github.com/gerardrbentley/darts-playground)

## Streamlit Full Stack 3 Ways

[![Littlest Veresion in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/gerardrbentley/streamlit-fullstack/app.py)

[![Postgres Version on VPS](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://streamlit-postgres.gerardbentley.com/)

[![PG + Go Version on VPS](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://st-pg-go.gerardbentley.com/)

Demo of Full Stack Streamlit Concept.
Deployed with 3 increasingly complicated backends.

See: [Github Repo](https://github.com/gerardrbentley/streamlit-fullstack)

## Fidelity / Personal Stock Account Dashboard

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/gerardrbentley/fidelity-account-overview/main/app.py)

Upload a CSV export from Fidelity investment account(s) and visualize profits and losses from select tickers and accounts.

See: [Github Repo](https://github.com/gerardrbentley/fidelity-account-overview)

## URL Scanner

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/gerardrbentley/streamlit-url-scanner/main/streamlit_app/streamlit_app.py)

Using AWS Rekognition + Streamlit to provide interactive OCR URL Scanner / Text Extraction on real world images.

See: [Github Repo](https://github.com/gerardrbentley/streamlit-url-scanner)

## Peak Weather: NH 4,000 Footers

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/gerardrbentley/peak-weather/main/streamlit_app/streamlit_app.py)

Use async http request library `httpx` to make 48 api calls roughly simultaneously in one Python process.
Feed a dashboard of weather for all 4,000 foot mountains in New Hampshire.

See: [Github Repo](https://github.com/gerardrbentley/peak-weather)

## AWS Textract Document Text Scan

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/gerardrbentley/textract-streamlit-example/main/streamlit_app/streamlit_app.py)

Using AWS Textract + S3 + Streamlit to provide interactive OCR Web App.

See: [Github Repo](https://github.com/gerardrbentley/textract-streamlit-example)


## Darts Intro

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/gerardrbentley/timeseries-examples/main/streamlit_apps/02_darts.py)

~1 for 1 exploration of Darts quick start with Streamlit + some interactive forecasting of Uploaded CSV.

Exploring Time Series in: [Github Repo](https://github.com/gerardrbentley/timeseries-examples)

## Function to Streamlit Form

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/gerardrbentley/streamlit-random/main/st_func_form.py)

Powered by `Streamlit-Pydantic`.
Utilizes `inspect.signature` to build an input class to a function definition.

What's the point?

Even more rapid development!

Take any CLI or other functional API and create an input form for them.
Encourage developers to write accurate type hints ;)

```py
from inspect import Parameter
import streamlit as st
import streamlit_pydantic as sp
from inspect import signature
from pydantic import create_model


def crunch_the_numbers(ticker: str, num_periods: int = 10) -> dict:
    return {"ticker": ticker, "value": num_periods * 100.00}

pydantic_fields = {
    x.name: (
        (x.annotation, ...)
        if x.default == x.empty
        else (x.annotation, x.default)
    )
    for x in signature(crunch_the_numbers).parameters.values()
}
PydanticFormModel = create_model("PydanticFormModel", **pydantic_fields)

input_col, output_col = st.columns(2)
with input_col:
    data = sp.pydantic_form(key="some_form", model=PydanticFormModel)
if data:
    output_col.json(crunch_the_numbers(**data.dict()))
```

## Python Web Form Generator

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/gerardrbentley/python-form-generator/main/app.py)

Powered by `Streamlit-Pydantic`.
Generate a Streamlit web form UI + Pydantic models from an example JSON data structure.

See: [Github Repo](https://github.com/gerardrbentley/python-form-generator)

## Basic File Drop

Not live, as there is no point.

Make a web frontend that you can access from local network and drop any number of files to host computer!
All in ~10 lines of code.

```py
import streamlit as st
from pathlib import Path

files = st.file_uploader("uploads", accept_multiple_files=True)
destination = Path('downloads')
destination.mkdir(exist_ok=True)

for f in files:
    bytes_data = f.read()
    st.write("filename:", f.name)
    st.write(f"{len(bytes_data) = }")
    new_file = destination / f.name
    new_file.write_bytes(bytes_data)
```

## Gif Maker

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/gerardrbentley/gif-maker/main)
