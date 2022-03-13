# Streamlit Random Apps

Made with :heart: from [Gar's Bar](https://tech.gerardbentley.com/)

## Function to Streamlit Form

Powered by `Streamlit-Pydantic`.
Utilize `inspect.signature` to build an input class to a function definition.

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

## Basic File Drop

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
