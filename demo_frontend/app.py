import json
import os
from typing import Any, Optional, Dict

import requests
import streamlit as st


st.set_page_config(
    page_title="CareerAI | Interview Demo",
    page_icon="🧠",
    layout="wide",
)

st.markdown(
    """
    <style>
    .block-container {
        padding-top: 1.7rem;
        max-width: 1250px;
    }
    [data-testid="stMetric"] {
        border: 1px solid #dbe2ef;
        border-radius: 12px;
        padding: 14px;
    }
    .header-sub {
        color: #64748b;
        margin-top: -8px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


DEFAULT_URL = os.getenv(
    "CAREERAI_API_URL",
    "http://localhost:8001",
).rstrip("/")


if "token" not in st.session_state:
    st.session_state.token = None

if "resume_id" not in st.session_state:
    st.session_state.resume_id = 17

if "job_id" not in st.session_state:
    st.session_state.job_id = 28


# --------------------------------------------------
# API CLIENT
# --------------------------------------------------

def api(
    method: str,
    path: str,
    *,
    data: Optional[Dict] = None,
    form: Optional[Dict] = None,
    file=None,
    timeout: int = 90,
) -> Any:

    headers = (
        {
            "Authorization": (
                f"Bearer {st.session_state.token}"
            )
        }
        if st.session_state.token
        else {}
    )

    base = st.session_state.base_url

    try:
        response = requests.request(
            method,
            f"{base}{path}",
            headers=headers,
            json=data,
            data=form,
            files=file,
            timeout=timeout,
        )

        if not response.ok:
            try:
                detail = response.json()
            except ValueError:
                detail = response.text[:350]

            raise RuntimeError(
                f"HTTP {response.status_code}: {detail}"
            )

        return (
            response.json()
            if response.content
            else {}
        )

    except requests.RequestException as exc:
        raise RuntimeError(
            f"API connection problem: {exc}"
        ) from exc


def call_and_show_error(func):
    try:
        return func()
    except Exception as exc:
        st.error(str(exc))
        return None


def show_skills(skills, label):
    st.markdown(f"**{label}**")

    if skills:
        st.write(
            " · ".join(
                f"`{s}`"
                for s in skills
            )
        )
    else:
        st.caption("None returned")


# --------------------------------------------------
# PAGE HEADER
# --------------------------------------------------

st.title("🧠 CareerAI")

st.markdown(
    '<div class="header-sub">'
    'AI-powered career intelligence · Live backend demo'
    '</div>',
    unsafe_allow_html=True,
)


# --------------------------------------------------
# SIDEBAR & AUTHENTICATION
# --------------------------------------------------

with st.sidebar:

    st.header("Connection")

    st.session_state.base_url = st.text_input(
        "CareerAI API URL",
        value=st.session_state.get(
            "base_url",
            DEFAULT_URL,
        ),
    ).rstrip("/")

    if st.button(
        "Check backend",
        use_container_width=True,
    ):
        result = call_and_show_error(
            lambda: api("GET", "/health")
        )

        if result:
            st.success(
                f"API: {result.get('status')} | "
                f"DB: {result.get('database')}"
            )

    if st.session_state.token:

        st.success("Authenticated")

        if st.button(
            "Log out",
            use_container_width=True,
        ):
            st.session_state.token = None
            st.rerun()

    else:

        with st.form("login"):

            email = st.text_input("Email")

            password = st.text_input(
                "Password",
                type="password",
            )

            login = st.form_submit_button(
                "Sign in",
                use_container_width=True,
            )

        if login:

            result = call_and_show_error(
                lambda: api(
                    "POST",
                    "/auth/login",
                    form={
                        "username": email,
                        "password": password,
                    },
                )
            )

            if (
                isinstance(result, dict)
                and result.get("access_token")
            ):
                st.session_state.token = (
                    result["access_token"]
                )
                st.rerun()

    st.divider()

    st.number_input(
        "Resume ID",
        min_value=1,
        key="resume_id",
    )

    st.number_input(
        "Job ID",
        min_value=1,
        key="job_id",
    )

    st.caption(
        "Defaults: processed resume #17 and "
        "demo job #28. Demo job is synthetic, "
        "not a live vacancy."
    )


# --------------------------------------------------
# LOGIN REQUIRED
# --------------------------------------------------

if not st.session_state.token:

    st.info(
        "Sign in with your existing CareerAI "
        "account to use the protected API endpoints."
    )

    st.stop()


rid = st.session_state.resume_id
jid = st.session_state.job_id


# --------------------------------------------------
# NAVIGATION
# --------------------------------------------------

p_overview, p_matching, p_cv, p_rag, p_upload = (
    st.tabs(
        [
            "Overview",
            "Job Matching",
            "AI CV Improvement",
            "RAG Assistant",
            "Resume Upload",
        ]
    )
)


# --------------------------------------------------
# OVERVIEW
# --------------------------------------------------

with p_overview:

    st.subheader("Project overview")

    st.caption(
        "Numbers below are retrieved live from "
        "your backend, not pre-filled examples."
    )

    if st.button("Load overview"):

        health = call_and_show_error(
            lambda: api("GET", "/health")
        )

        resume = call_and_show_error(
            lambda: api(
                "GET",
                f"/resumes/{rid}",
            )
        )

        jobs = call_and_show_error(
            lambda: api("GET", "/jobs")
        )

        columns = st.columns(3)

        columns[0].metric(
            "API",
            (
                health.get("status", "unknown")
                if isinstance(health, dict)
                else "unavailable"
            ),
        )

        columns[1].metric(
            "Resume status",
            (
                resume.get("status", "unknown")
                if isinstance(resume, dict)
                else "unavailable"
            ),
        )

        job_count = (
            len(jobs)
            if isinstance(jobs, list)
            else (
                len(jobs.get("jobs", []))
                if isinstance(jobs, dict)
                else "—"
            )
        )

        columns[2].metric(
            "Visible active jobs",
            job_count,
        )

        if resume:

            with st.expander(
                "Resume response",
                expanded=False,
            ):
                st.json(resume)

    st.markdown(
        "**Demo flow:** Authenticate → "
        "Check processed resume → "
        "View job match → "
        "Generate AI CV advice → "
        "Ask the RAG knowledge base"
    )


# --------------------------------------------------
# HYBRID JOB MATCHING
# --------------------------------------------------

with p_matching:

    st.subheader("Hybrid job matching")

    st.caption(
        "Backend: pgvector candidate retrieval, "
        "cross-encoder reranking, explainable "
        "weighted score; optional ML shadow predictions."
    )

    if st.button(
        "Calculate matches",
        type="primary",
    ):

        result = call_and_show_error(
            lambda: api(
                "GET",
                f"/matches/resumes/{rid}"
                "?limit=20&offset=0",
                timeout=180,
            )
        )

        if isinstance(result, dict):
            st.session_state.matches = result

    result = st.session_state.get("matches")

    if result:

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "Candidates",
            result.get("total_candidates", "—"),
        )

        c2.metric(
            "Returned",
            result.get("returned_count", "—"),
        )

        c3.metric(
            "Algorithm",
            result.get(
                "configuration",
                {},
            ).get(
                "algorithm_version",
                "—",
            ),
        )

        matches = result.get("matches", [])

        if not matches:

            st.warning(
                "No matched candidates. Ensure "
                "active demo jobs have embeddings "
                "and the resume is processed."
            )

        for match in matches:

            with st.container(border=True):

                a, b = st.columns([4, 1])

                a.markdown(
                    f"### {match.get('title', 'Job')} "
                    f"— {match.get('company_name', '')}"
                )

                b.metric(
                    "Match score",
                    f"{match.get('match_score', 0):.2f}%",
                )

                score = match.get(
                    "score_breakdown",
                    {},
                )

                chart_data = {
                    label: score.get(key, 0)
                    for label, key in [
                        ("Skills", "skill_score"),
                        ("Semantic", "semantic_score"),
                        ("Seniority", "seniority_score"),
                        ("Location", "location_score"),
                        ("Reranker", "reranker_score"),
                    ]
                }

                st.bar_chart(
                    chart_data,
                    horizontal=True,
                    x_label="Score (0–100)",
                )

                show_skills(
                    match.get("matched_skills"),
                    "Matched skills",
                )

                show_skills(
                    match.get("missing_skills"),
                    "Missing skills",
                )

                st.info(
                    match.get(
                        "explanation",
                        "No explanation",
                    )
                )

                with st.expander("Full match data"):
                    st.json(match)


# --------------------------------------------------
# AI CV IMPROVEMENT
# --------------------------------------------------

with p_cv:

    st.subheader(
        "Gemini-assisted CV improvement"
    )

    st.caption(
        "Uses the real CV improvement endpoint "
        "and shows returned agent results."
    )

    if st.button(
        "Analyze CV for selected job",
        type="primary",
    ):

        result = call_and_show_error(
            lambda: api(
                "GET",
                f"/cv-improvements/resumes/"
                f"{rid}/jobs/{jid}",
                timeout=180,
            )
        )

        if isinstance(result, dict):
            st.session_state.improvement = result

    improvement = st.session_state.get(
        "improvement"
    )

    if improvement:

        st.success(
            "Provider: "
            f"{improvement.get('llm_metadata', {}).get('provider', 'unknown')}"
        )

        st.markdown("#### AI summary")

        st.write(
            improvement.get(
                "summary",
                "No summary returned",
            )
        )

        analysis = improvement.get(
            "resume_analysis",
            {},
        )

        a, b = st.columns(2)

        a.metric(
            "Target role in parsed CV",
            analysis.get(
                "target_role",
                "—",
            ),
        )

        b.metric(
            "Parsed seniority",
            analysis.get(
                "seniority",
                "—",
            ),
        )

        gap = improvement.get(
            "skill_gap",
            {},
        )

        show_skills(
            gap.get("matched_skills", []),
            "Matched skills",
        )

        show_skills(
            gap.get("missing_skills", []),
            "Skill gaps",
        )

        st.markdown(
            "#### Improvement recommendations"
        )

        for suggestion in improvement.get(
            "suggestions",
            [],
        ):

            with st.expander(
                f"{suggestion.get('priority', '')} "
                f"· {suggestion.get('title', '')}"
            ):

                st.write(
                    suggestion.get(
                        "description",
                        "",
                    )
                )

        st.markdown(
            "#### Rewrite suggestions"
        )

        for item in improvement.get(
            "rewrite_suggestions",
            [],
        ):

            with st.container(border=True):

                st.markdown(
                    f"**{item.get('section', 'Section')}**"
                )

                st.write(
                    item.get(
                        "suggested_text",
                        "",
                    )
                )

                st.caption(
                    item.get(
                        "reason",
                        "",
                    )
                )

        with st.expander(
            "Complete API response"
        ):
            st.json(improvement)


# --------------------------------------------------
# RAG KNOWLEDGE ASSISTANT
# --------------------------------------------------

with p_rag:

    st.subheader(
        "RAG knowledge assistant"
    )

    st.caption(
        "This module has not yet been validated "
        "with a live request. Load the API schema "
        "to inspect required fields; never "
        "fabricate a response."
    )

    if st.button(
        "Inspect RAG request schema"
    ):

        schema = call_and_show_error(
            lambda: api(
                "GET",
                "/openapi.json",
            )
        )

        if isinstance(schema, dict):

            ask_spec = schema.get(
                "paths",
                {},
            ).get(
                "/knowledge/ask",
                {},
            ).get(
                "post",
                {},
            )

            st.json(
                {
                    "requestBody": ask_spec.get(
                        "requestBody"
                    ),
                    "schemas": schema.get(
                        "components",
                        {},
                    ).get(
                        "schemas",
                        {},
                    ),
                }
            )

    draft = st.text_area(
        "Request JSON for POST /knowledge/ask",
        value="{}",
        height=100,
        help=(
            "Match the request model shown "
            "by the API schema / Swagger."
        ),
    )

    if st.button("Ask knowledge base"):

        try:

            payload = json.loads(draft)

            if (
                not isinstance(payload, dict)
                or not payload
            ):

                st.warning(
                    "Enter a non-empty JSON "
                    "object conforming to "
                    "the endpoint schema."
                )

            else:

                answer = call_and_show_error(
                    lambda: api(
                        "POST",
                        "/knowledge/ask",
                        data=payload,
                        timeout=180,
                    )
                )

                if answer is not None:
                    st.json(answer)

        except ValueError as exc:

            st.error(
                f"Invalid JSON: {exc}"
            )


# --------------------------------------------------
# RESUME UPLOAD
# --------------------------------------------------

with p_upload:

    st.subheader("Upload CV")

    st.caption(
        "This submits to your existing backend "
        "and may launch asynchronous Celery processing."
    )

    uploaded = st.file_uploader(
        "Choose CV PDF",
        type=["pdf"],
    )

    if (
        uploaded is not None
        and st.button("Upload resume")
    ):

        result = call_and_show_error(
            lambda: api(
                "POST",
                "/resumes/upload",
                file={
                    "file": (
                        uploaded.name,
                        uploaded.getvalue(),
                        "application/pdf",
                    )
                },
                timeout=90,
            )
        )

        if result is not None:

            st.json(result)

            st.info(
                "If processing is queued, use "
                "the returned resume ID and "
                "check its status before matching."
            )