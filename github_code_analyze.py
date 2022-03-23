from io import StringIO
from subprocess import check_output, run
import pandas as pd
import streamlit as st
from pathlib import Path

repos = Path('repos')
@st.experimental_memo
def analyze_repo(repo):
    user, repo_name = repo.split('/')
    d = repos / repo_name
    print(d)
    if not d.exists():
        run(["git", "clone", "--depth", "1", f"https://github.com/{repo}", d])

    # Get Series that contains all lines of code
    # Relies on unix find to find files and wc -l to count lines
    all_file_lines = (
        pd.read_csv(
            StringIO(
                check_output(
                    f"find {repo_name.replace('-', '_')} -type f -iname *.* -exec wc -l {{}} ;".split(), cwd=d
                ).decode()
            ),
            delimiter=" ",
            index_col=[1],
            names="lines path".split(),
        )
        .squeeze("columns")
        .pipe(lambda s: s.set_axis(map(Path, s.index)))
    )

    interesting_file_lines = all_file_lines[
        all_file_lines.index.map(
            lambda p: "package-lock.json" not in str(p) and f"{repo_name.replace('-','_')}/_testing" not in str(p) and f"{repo_name.replace('-','_')}/tests" not in str(p)
        )
    ]

    # Group into parent folders and file types
    per_type_lines = interesting_file_lines.pipe(
        lambda s: s.groupby(
            [s.index.map(lambda p: p.parents[1]), s.index.map(lambda p: p.suffix)]
        ).sum()
    ).unstack(fill_value=0)

    return per_type_lines


st.title("Github Lines of Code Analyzer")

st.sidebar.header("Configuraton")
all_repos = st.sidebar.text_area("Enter list of repos as username/repository")

if all_repos == "":
    st.warning("Enter repository info")
    st.stop()

main_chart = st.bar_chart()
for repo in all_repos.splitlines():
    with st.spinner(f"Analyzing {repo}"):
        analysis = analyze_repo(repo.rstrip())
        total_lines = analysis.sum().sum()
        main_chart.add_rows(pd.Series([total_lines], index=[repo], name=repo))
        st.subheader(f"{total_lines} Lines in {repo}!")
        analysis.index = analysis.index.astype('str')
        st.bar_chart(analysis)
        st.bar_chart(analysis.sum())
