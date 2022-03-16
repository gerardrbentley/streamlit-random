from contextlib import redirect_stdout, redirect_stderr
import io
import sys
import subprocess
import traceback
import streamlit as st
import pandas as pd
st.set_page_config(layout='wide')

st.header("Left: Body, Middle: Std Out, Right: Std Err")
body, stdout, stderr = st.columns(3)

with redirect_stdout(io.StringIO()) as stdout_f, redirect_stderr(io.StringIO()) as stderr_f:
    try:
        print('Hello World!')
        df = pd.DataFrame({"test": [1,2,3]})
        df.info()
        good_process = subprocess.run(["ls", "-lah", "."], capture_output=True, text=True)
        stdout_f.write(good_process.stdout)
        stderr_f.write(good_process.stderr)
        bad_process = subprocess.run(["ls", "wtf"], capture_output=True, text=True)  # Throws stderr error
        stdout_f.write(bad_process.stdout)
        stdout_f.write(bad_process.stderr) # Also print in in middle column (most of my usecases i like stdout and stderr)
        stderr_f.write(bad_process.stderr)
        x = 1 / 0  # Throws Python Error
    except Exception as e:
        traceback.print_exc()
        traceback.print_exc(file=sys.stdout) # or sys.stdout
button = body.button('wtf')
if button:
    # Outisde of context, doesn't display in streamlit
    print('BUTTON')
body.write(df)
stdout_text = stdout_f.getvalue()
stdout.text(stdout_text)
stderr_text = stderr_f.getvalue()
stderr.text(stderr_text)
