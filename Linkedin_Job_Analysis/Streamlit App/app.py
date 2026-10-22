
from pathlib import Path

import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="LinkedIn Job Market Explorer",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Project folder and CSV file paths
ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "data" / "cleaned_data"


@st.cache_data
def load_data():
    jobs = pd.read_csv(
        DATA_PATH / "jobs_cleaned.csv",
        dtype={"job_id": str}
    )

    skills = pd.read_csv(
        DATA_PATH / "job_skills.csv",
        dtype={"job_id": str}
    )

    return jobs, skills


jobs, skills = load_data()

# Clean blank city values for accurate counts
if "city" in jobs.columns:
    jobs["city"] = jobs["city"].replace(r"^\s*$", pd.NA, regex=True)


st.title("💼 LinkedIn Job Market Explorer")

st.markdown(
    "Explore job opportunities, hiring trends, and in-demand skills "
    "using real-world job posting data."
)

st.caption("Data Analytics Project | Python • Selenium • Pandas • Streamlit")

st.sidebar.title("Job Explorer")
st.sidebar.caption("Find opportunities that match your interests.")
st.sidebar.divider()

st.sidebar.subheader("Filter Jobs")

# Job Role Filter
if "role_category" in jobs.columns:
    roles = sorted(jobs["role_category"].dropna().unique().tolist())
    selected_role = st.sidebar.selectbox(
        "Select Job Role",
        ["All Roles"] + roles
    )
else:
    selected_role = "All Roles"

# City Filter
if "city" in jobs.columns:
    cities = sorted(jobs["city"].dropna().unique().tolist())
    selected_city = st.sidebar.selectbox(
        "Select City",
        ["All Cities"] + cities
    )
else:
    selected_city = "All Cities"

# Company sort

companies = sorted(
    jobs["company"].dropna().astype(str).unique().tolist()
)

selected_company = st.sidebar.selectbox(
    "Select Company",
    ["All Companies"] + companies
)


# Apply filters
filtered_jobs = jobs.copy()

if selected_role != "All Roles" and "role_category" in filtered_jobs.columns:
    filtered_jobs = filtered_jobs[
        filtered_jobs["role_category"] == selected_role
    ]

if selected_city != "All Cities" and "city" in filtered_jobs.columns:
    filtered_jobs = filtered_jobs[
        filtered_jobs["city"] == selected_city
    ]


if selected_company != "All Companies":
    filtered_jobs = filtered_jobs[
        filtered_jobs["company"] == selected_company
    ]

# Summary metrics

c1, c2, c3 = st.columns(3)

c1.metric("Total Jobs", filtered_jobs["job_id"].nunique())
c2.metric("Total Companies", filtered_jobs["company"].nunique())
c3.metric("Total Cities", filtered_jobs["city"].nunique())


st.divider()

st.subheader("Job Listings")

columns_to_show = [
    col for col in [
        "title",
        "company",
        "city",
        "role_category",
        "seniority_level",
        "posted_date",
        "job_url"
    ]
    if col in jobs.columns
]

st.subheader("Available Job Opportunities")

st.caption(
    f"Showing {filtered_jobs['job_id'].nunique()} jobs "
    "based on your selected filters."
)

st.dataframe(
    filtered_jobs[columns_to_show],
    hide_index=True,
    width="stretch",
    column_config={
        "job_url": st.column_config.LinkColumn(
            "Job Link",
            display_text="Open Job"
        )
    }
)

st.dataframe(
    filtered_jobs[columns_to_show],
    hide_index=True,
    use_container_width=True,
    column_config={
        "job_url": st.column_config.LinkColumn(
            "Job Link",
            display_text="Open Job"
        )
    }
)

st.divider()
st.header("Job Market Analysis")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Jobs by Role")

    if "role_category" in filtered_jobs.columns:
        role_counts = (
            filtered_jobs["role_category"]
            .fillna("Unknown")
            .value_counts()
            .head(10)
        )

        st.bar_chart(role_counts)

with col2:
    st.subheader("Top Hiring Companies")

    if "company" in filtered_jobs.columns:
        company_counts = (
            filtered_jobs["company"]
            .fillna("Unknown")
            .value_counts()
            .head(10)
        )

        st.bar_chart(company_counts)

st.divider()
st.header("Most In-Demand Skills")

if "skill" in skills.columns and "job_id" in skills.columns:

    top_skills = (
        skills.groupby("skill")["job_id"]
        .nunique()
        .sort_values(ascending=False)
        .head(10)
        .sort_values()
    )

    st.bar_chart(top_skills)

else:
    st.warning("Check the column names in job_skills.csv")

st.divider()
st.header("🎯 Find Jobs by Your Skills")

if "skill" in skills.columns and "job_id" in skills.columns:

    all_skills = sorted(
        skills["skill"].dropna().astype(str).unique().tolist()
    )

    selected_skills = st.multiselect(
        "Select your skills",
        options=all_skills,
        placeholder="Choose skills like SQL, Python, Power BI"
    )

    if selected_skills:
        matching_ids = (
            skills[
                skills["skill"].isin(selected_skills)
            ]
            .groupby("job_id")["skill"]
            .nunique()
        )

        matching_ids = matching_ids[
            matching_ids == len(set(selected_skills))
        ].index

        matched_jobs = filtered_jobs[
            filtered_jobs["job_id"].isin(matching_ids)
        ]

        st.metric("Matching Jobs", matched_jobs["job_id"].nunique())

        st.dataframe(
            matched_jobs[columns_to_show],
            hide_index=True,
            width="stretch",
            column_config={
                "job_url": st.column_config.LinkColumn(
                    "Job Link",
                    display_text="Open Job"
                )
            }
        )
    else:
        st.info("Select one or more skills to find matching jobs.")

else:
    st.warning("Check the skill and job_id column names.")



'''   RUN THIS FILE IN TERMINAL 
.\.venv\Scripts\python.exe -m streamlit run "Streamlit App\app.py"'''