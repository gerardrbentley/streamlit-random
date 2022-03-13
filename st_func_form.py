import streamlit as st
import base64
with open("demos/st_func_form.gif", "rb") as f:
    contents = f.read()
    data_url = base64.b64encode(contents).decode("utf-8")

"## Function Signature -> Streamlit Form"
with st.expander("TL;DR"):
    "### Function -> Signature -> Pydantic Class -> Streamlit-Pydantic Form -> Function Input Data From UI"
    st.markdown(
        f'<img src="data:image/gif;base64,{data_url}" alt="screencast of app" width="500px">',
        unsafe_allow_html=True,
    )

    with st.echo():

        def crunch_the_numbers(ticker: str, num_periods: int = 10) -> dict:
            return {"ticker": ticker, "value": num_periods * 100.00}

    with st.echo("below"):
        from inspect import Parameter
        import streamlit_pydantic as sp
        from inspect import signature
        from pydantic import create_model

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
            output_col.subheader("Input:")
            output_col.json(data.json())
            output_col.subheader("Output:")
            output_col.json(crunch_the_numbers(**data.dict()))

"### The inspect module lets us look into live Python code objects"
with st.echo():
    from inspect import signature

"### This function will be our test subject. It takes in a string ticker and a number of periods"
with st.echo():

    def crunch_the_numbers(ticker: str, num_periods: int = 10) -> dict:
        return {"ticker": ticker, "num_periods": num_periods, "value": 100.00}


"### So what does this signature thing do?"
with st.echo():
    st.write(signature.__doc__)

"### And what does it look like for our function?"
with st.echo():
    sig = signature(crunch_the_numbers)
    st.write(sig)
    st.write(type(sig))

"### We're getting somewhere, but what is this Signature thing?"
with st.echo():
    st.text(type(sig).__doc__)

with st.expander("TANGENT: But what if we didn't get any docs from the __doc__...?"):
    "Time to hack at the live object"
    with st.echo():
        attribute_map = {x: x for x in dir(sig) if not x.startswith("_")}
        st.write(attribute_map)

    "`dir` lists out all of the attributes of a python object (slightly [different from __dict__](https://stackoverflow.com/a/14361362/15685218))."
    "Filtering out attributes that start with `_` will exclude object's dunder attributes and ['private' attributes](https://docs.python.org/3/tutorial/classes.html#private-variables)"
    "It's named [after the DOS command of the same name](https://stackoverflow.com/a/48912069/15685218)."

"### We'll focus on the `parameters`."
"### So what do we get from this `parameters` OrderedDict?"
with st.echo():
    for name, parameter in sig.parameters.items():
        st.write(name, parameter, type(parameter))

"### What can we do with one of these parameter things?"
with st.echo():
    parameter = sig.parameters["ticker"]
    st.write(type(parameter))
    st.text(type(parameter).__doc__)

"""\
### Each of these attributes will help in the streamlit form input widget

- `name` will determine the label for the widget (maybe get fancy with formatting too!)
- `default` will determine a default `value` for the widget
- `annotation` will determine the type of widget to use
- `kind` will determine if the widget is optional or required
"""
with st.echo():
    for name, parameter in sig.parameters.items():
        st.subheader(f"{parameter.name = }")
        st.write("parameter.default: ", parameter.default)
        st.write("parameter.annotation: ", parameter.annotation)
        st.write("parameter.kind: ", parameter.kind)

"### For this example we'll handle just the 2 different parameter types with an if statement"
with st.echo():
    input_col, output_col = st.columns(2)
    output_col.subheader("Input:")
    for name, parameter in sig.parameters.items():
        kwargs = {"label": parameter.name, "key": parameter.name}
        # Ignore default value if it is empty, Streamlit doesn't handle None as value
        if parameter.default != parameter.empty:
            kwargs["value"] = parameter.default

        if parameter.annotation == str:
            input_col.text_input(**kwargs)
        elif parameter.annotation == int:
            input_col.number_input(**kwargs)

        output_col.write(f"{name}: {st.session_state[name]}")
    output_col.subheader("Output:")
    output = crunch_the_numbers(st.session_state.ticker, st.session_state.num_periods)
    output_col.write(output)

"### What about Forms???"
with st.echo():
    input_col, output_col = st.columns(2)
    output_col.subheader("Input:")
    with input_col, st.form("my_form"):
        for name, parameter in sig.parameters.items():
            kwargs = {"label": parameter.name, "key": parameter.name + "_form"}
            if parameter.default != parameter.empty:
                kwargs["value"] = parameter.default
            if parameter.annotation == str:
                st.text_input(**kwargs)
            elif parameter.annotation == int:
                st.number_input(**kwargs)
            output_col.write(f"{name}: {st.session_state[name + '_form']}")
        submitted = st.form_submit_button()
    output_col.subheader("Output:")
    if submitted:
        output = crunch_the_numbers(
            st.session_state.ticker_form, st.session_state.num_periods_form
        )
        output_col.write(output)

"""\
### Time to get super lazy

[Streamlit-Pydantic](https://github.com/LukasMasuch/streamlit-pydantic) gives us creation of UI form from Pydantic `BaseModel` or standard lib `dataclass`.

So we just have to get from function parameters to dataclass or BaseModel and we're golden!

Starting with the standard library: https://docs.python.org/3/library/dataclasses.html#dataclasses.make_dataclass
"""
with st.echo():
    import streamlit_pydantic as sp
    from dataclasses import make_dataclass, field, asdict

    def get_field_tuple(parameter: Parameter):
        if parameter.default != parameter.empty:
            return (
                parameter.name,
                parameter.annotation,
                field(default=parameter.default),
            )
        else:
            return (parameter.name, parameter.annotation)

    fields = [get_field_tuple(x) for x in sig.parameters.values()]
    FormModel = make_dataclass("FormModel", fields)
    st.write(FormModel)
    st.write(FormModel.__doc__)

"### Most Excellent. Now for the Final Dataclass Form!"
with st.echo():
    input_col, output_col = st.columns(2)
    output_col.subheader("Input:")
    with input_col:
        data = sp.pydantic_form(key="sp_form", model=FormModel)
    if data:
        output_col.subheader("Output:")
        output_col.json(asdict(data))
        # Access with kwargs expansion from data
        output = crunch_the_numbers(**asdict(data))
        # Or access explicitly from session_state
        output = crunch_the_numbers(
            st.session_state.ticker_form, st.session_state.num_periods_form
        )
        output_col.write(output)

"""\
### And Pydantic version works too!

https://pydantic-docs.helpmanual.io/usage/models/#dynamic-model-creation
"""
with st.echo():
    from pydantic import create_model

    def get_pydantic_tuple(parameter: Parameter):
        if parameter.default != parameter.empty:
            return (parameter.annotation, parameter.default)
        else:
            return (parameter.annotation, ...)

    pydantic_fields = {x.name: get_pydantic_tuple(x) for x in sig.parameters.values()}
    PydanticFormModel = create_model("PydanticFormModel", **pydantic_fields)
    st.write(signature(PydanticFormModel))
    input_col, output_col = st.columns(2)
    output_col.subheader("Input:")
    with input_col:
        data = sp.pydantic_form(key="sp_pydantic_form", model=PydanticFormModel)
    if data:
        output_col.json(data.json())
        output_col.subheader("Output:")
        output = crunch_the_numbers(**data.dict())
        output_col.write(output)


"""\
### What Next?

The main advantage of this setup is easy memoization with [streamlit memo](https://blog.streamlit.io/new-experimental-primitives-for-caching/) ([experimental docs](https://docs.streamlit.io/library/api-reference/performance/st.experimental_memo))

Outside of that, you can get a starting interface to most well documented functions from your favorite libraries!

You can handle *args and **kwargs as text areas that are parsed after submission, but probably won't play nicely with Streamlit Pydantic.
Also using raw `eval` would open up to remote code execution, so passing complex Python objects on the fly is difficult in var args.
"""

with st.echo():

    def crunch_kwargs(*args, **kwargs) -> dict:
        return {"value": sum(args), **kwargs}


with st.echo("below"):
    from ast import literal_eval

    input_col, output_col = st.columns(2)
    output_col.subheader("Input:")
    for name, parameter in signature(crunch_kwargs).parameters.items():
        default = parameter.default
        if parameter.kind == Parameter.VAR_POSITIONAL and default == parameter.empty:
            default = "[]"
        elif parameter.kind == Parameter.VAR_KEYWORD and default == parameter.empty:
            default = "{}"

        input_col.text_area(name, value=default, key=name)

    output_col.subheader("Output:")
    raw_args = st.session_state.args
    raw_kwargs = st.session_state.kwargs
    st.write(raw_args, raw_kwargs, type(raw_args), type(raw_kwargs))
    args = literal_eval(raw_args)
    kwargs = literal_eval(raw_kwargs)
    st.write(args, kwargs)
    output = crunch_kwargs(*args, **kwargs)
    output_col.write(output)
