# app.py — Viatra (Consumer) + Viatra (Hospital) — Single-file Streamlit App
# ---------------------------------------------------------------------------------
# Enhanced Home/About: interactive cards, CSS, CTAs, and a simple architecture diagram.
# Notes:
# - Run: pip install -U streamlit pandas matplotlib
# - streamlit run app.py
# - This file keeps demo logic for the Consumer and Doctor modules and adds an interactive, styled landing page.
# ---------------------------------------------------------------------------------

import io
import json
from datetime import datetime, date, timedelta
from typing import Dict, List

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

APP_TITLE = "Viatra — Consumer & Hospital Hubs"

# ----------------------------
# Session State Bootstrapping
# ----------------------------

def _init_state():
    ss = st.session_state
    ss.setdefault("active_profile", "Me")
    ss.setdefault("profiles", {"Me": {"dob": None, "gender": None}})
    ss.setdefault("vitals", {"Me": pd.DataFrame(columns=["datetime","systolic","diastolic","hr","glucose"])})
    ss.setdefault("meds", {"Me": []})
    ss.setdefault("records", {"Me": []})
    ss.setdefault("lab_text", "")
    ss.setdefault("challenges", {"Me": {"name": None, "progress": 0, "started": None}})
    ss.setdefault("roster", pd.DataFrame(columns=["date","shift","doctor"]))
    ss.setdefault("patients", pd.DataFrame(columns=["id","name","age","sex","allergies","comorbidities"]))
    ss.setdefault("notes", pd.DataFrame(columns=["patient_id","timestamp","author","note"]))
    ss.setdefault("chat", [])
    ss.setdefault("passport", {"Me": {"immunizations": [], "allergies": [], "conditions": []}})
    ss.setdefault("micro_consults", [])
    ss.setdefault("pilot_requests", [])

_init_state()

# ----------------------------
# CSS & UI Helpers
# ----------------------------

CUSTOM_CSS = """
<style>
:root{--card-bg:#ffffff;--muted:#6b7280;--accent:#0f62fe;--glass:rgba(255,255,255,0.06)}
.app-header{display:flex;align-items:center;justify-content:space-between;padding:18px;border-bottom:1px solid #e6eef8}
.brand{font-weight:700;font-size:20px}
.lead{color:var(--muted);margin-top:6px}
.card-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:18px;margin-top:18px}
.card{background:linear-gradient(180deg, rgba(255,255,255,0.98), rgba(250,250,250,0.98));border-radius:12px;padding:18px;box-shadow:0 6px 20px rgba(15,23,42,0.06);border:1px solid #eef3ff}
.card h4{margin:0 0 6px 0}
.small{font-size:13px;color:var(--muted)}
.kpi{font-size:18px;font-weight:700}
.cta{background:var(--accent);color:white;padding:10px 14px;border-radius:10px;text-decoration:none}
.feature-list{margin:0;padding-left:18px}
.pill{display:inline-block;padding:6px 10px;border-radius:999px;background:#f1f5ff;color:#0b4bd6;font-weight:600;font-size:12px;margin-right:8px}
.footer-small{color:var(--muted);font-size:12px;margin-top:22px}
</style>
"""


def render_card(
    title: str,
    desc: str,
    bullets: List[str] = None,
    kpi: str = None,
    cta_label: str = None,
    key: str = None
):
    card_css = """
    <style>
    .card {
        background: #1E1E1E;
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0px 2px 10px rgba(0,0,0,0.3);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .card:hover {
        transform: translateY(-5px);
        box-shadow: 0px 6px 18px rgba(0,0,0,0.45);
    }
    .card h4 {
        margin: 0 0 10px 0;
        font-size: 1.3rem;
        font-weight: 600;
        color: #ffffff;
    }
    .kpi {
        font-size: 1.1rem;
        font-weight: bold;
        color: #00d4ff;
        margin-bottom: 10px;
    }
    .small {
        font-size: 0.95rem;
        color: #d0d0d0;
        margin-bottom: 10px;
        line-height: 1.5;
    }
    .feature-list {
        list-style: none;
        padding-left: 0;
        margin-bottom: 15px;
    }
    .feature-list li {
        position: relative;
        padding-left: 25px;
        margin-bottom: 8px;
        color: #ededed;
        font-size: 0.95rem;
    }
    .feature-list li::before {
        content: "✔";
        position: absolute;
        left: 0;
        color: #00d4ff;
        font-weight: bold;
    }
    .cta-button {
        display: inline-block;
        background: linear-gradient(90deg, #007bff, #00d4ff);
        color: white !important;
        padding: 10px 18px;
        border-radius: 12px;
        text-decoration: none;
        font-weight: 600;
        transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
        font-size: 0.95rem;
    }
    .cta-button:hover {
        transform: scale(1.05);
        box-shadow: 0px 4px 12px rgba(0,0,0,0.3);
    }
    </style>
    """

    html = f"<div class='card'>"
    html += f"<h4>{title}</h4>"
    if kpi:
        html += f"<div class='kpi'>{kpi}</div>"
    html += f"<div class='small'>{desc}</div>"
    if bullets:
        html += "<ul class='feature-list'>"
        for b in bullets:
            html += f"<li>{b}</li>"
        html += "</ul>"
    if cta_label:
        html += f"<a href='#' class='cta-button'>{cta_label}</a>"
    html += "</div>"

    st.markdown(card_css + html, unsafe_allow_html=True)



# ----------------------------
# Sidebar Navigation
# ----------------------------

st.set_page_config(page_title=APP_TITLE, layout="wide")
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

with st.container():
    st.markdown("<div class='app-header'><div><div class='brand'>Viatra</div><div class='lead'>A smart Personal Health OS + Doctor Cockpit — anticipatory, interoperable, and enterprise-ready.</div></div></div>", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### Navigation")
    page = st.radio(
        "Go to",
        [
            "Home / About",
            "Viatra (Consumer)",
            "Viatra (Hospital)",
        ],
    )

# ----------------------------
# Home / About Page (Smarter UI)
# ----------------------------

if page == "Home / About":
    st.markdown("<div style='display:flex;gap:18px;align-items:center'><div style='flex:1'><h2>Welcome — Viatra</h2><div class='small'>The only platform that gives patients a clinician's view while giving doctors a single, integrated cockpit for care.</div></div><div style='text-align:right'><a class='cta' href='#pilot'>Request a Pilot</a></div></div>", unsafe_allow_html=True)

    st.markdown("<div class='card-grid'>", unsafe_allow_html=True)

    # Consumer Card
    render_card(
        "Consumer Module — Viatra",
        "A clinician-inspired Personal Health OS for patients and families.",
        bullets=[
            "Doctor-style timeline of vitals, labs, meds and wearables",
            "Universal Locker: OCR → structured records (FHIR-ready)",
            "AI Health Interpreter: clinician-style, contextual explanations",
            "Digital Twin & Predictive Risk scoring",
            "Micro-consults & Personalized Preventive Marketplace"
        ],
        kpi="Engagement: pilot KPI — 30% weekly active",
        cta_label="Try Consumer Demo"
    )

    # Doctor Card
    render_card(
        "Hospital Module — Viatra",
        "A one-stop digital cockpit for physicians; designed to integrate with hospital systems.",
        bullets=[
            "Secure patient registry & bedside notes (blockchain anchor optional)",
            "Duty rosters, e-prescription, and interaction checks",
            "Clinical Decision Support & risk flagging",
            "Collaboration, analytics and a Learning Hub"
        ],
        kpi="Efficiency: reduce admin time by 20% (target)",
        cta_label="Request Hospital Pilot"
    )

    # Tech Card
    render_card(
        "Technology Stack & Security",
        "API-first microservices, LLM+guardrails for clinical interpretation, and privacy-first engineering.",
        bullets=[
            "FHIR/HL7 connectors, wearable SDKs, pharmacy APIs",
            "Time-series DB, object store for records, OLAP & analytics",
            "RBAC, encryption, audit logs, optional on-prem installs"
        ],
        kpi="Compliance: HIPAA/GDPR patterns included",
        cta_label="See Architecture"
    )

    # GTM Card
    render_card(
        "Go-to-Market & Monetization",
        "Hybrid revenue model: consumer subscriptions, micro-consults, marketplace commissions, and B2B hospital SaaS.",
        bullets=[
            "Phase 1: D2C adoption & micro-consult monetization",
            "Phase 2: Hospital pilots and enterprise contracts",
            "Strategic lab/pharmacy/payer partnerships"
        ],
        kpi="Revenue mix target: 40% B2B, 40% Marketplace, 20% D2C"
    )

    st.markdown("</div>", unsafe_allow_html=True)

    # # Interactive Architecture Diagram
    # st.markdown("---")
    # st.subheader("Runtime Architecture — Interactive (toy diagram)")
    # if st.checkbox("Show architecture diagram"):
    #     # Draw a simple architecture diagram using matplotlib
    #     fig, ax = plt.subplots(figsize=(9,3))
    #     ax.axis('off')
    #     boxes = ["Wearables & Devices","Consumer App","Ingestion (OCR / FHIR)","AI Interpreter / Twin","Time-series DB / Locker","Viatra / EMR" ]
    #     xs = [0.05,0.28,0.48,0.66,0.84,0.92]
    #     for i, b in enumerate(boxes):
    #         ax.add_patch(plt.Rectangle((xs[i]-0.06,0.35),0.12,0.3,facecolor='#f8fafc',edgecolor='#c7def8'))
    #         ax.text(xs[i],0.5,b,ha='center',va='center',fontsize=9)
    #     # arrows
    #     for i in range(len(xs)-1):
    #         ax.annotate('', xy=(xs[i]+0.06,0.5), xytext=(xs[i+1]-0.06,0.5), arrowprops=dict(arrowstyle='->',color='#1f6feb',lw=1.5))
    #     st.pyplot(fig)
    #     st.caption("This schematic is a simplified view: each box is typically multiple microservices behind APIs.")

    # Request Pilot CTA (form)
    st.markdown("---")
    st.markdown("<a id='pilot'></a><h3>Request a Pilot</h3>", unsafe_allow_html=True)
    with st.form(key='pilot_form'):
        org = st.text_input('Organization / Your Name')
        email = st.text_input('Contact Email')
        use_case = st.selectbox('Primary Use Case', ['Consumer pilot','Hospital pilot','Integration partner','Research collaboration'])
        notes = st.text_area('Notes / Objectives')
        submitted = st.form_submit_button('Request Pilot')
        if submitted:
            st.session_state.pilot_requests.append({
                'org': org,
                'email': email,
                'use_case': use_case,
                'notes': notes,
                'created': datetime.utcnow().isoformat()
            })
            st.success('Pilot request sent — our team will reach out within 48 business hours (demo SLA).')

    if st.session_state.pilot_requests:
        st.markdown("**Recent Pilot Requests (demo)**")
        st.table(pd.DataFrame(st.session_state.pilot_requests).tail(5))

    # Downloadable pitch deck (toy)
    st.markdown("---")
    st.subheader("Download — One-page Pitch (PDF/JSON)")
    pitch = {
        "title": "Viatra — Personal Health OS + Doctor Cockpit",
        "value_prop": "A smart, interoperable health platform that empowers patients with 'doctor-eyes' and gives physicians a unified cockpit. Viatra acts as a predictive, preventive, and personalized health layer on top of existing care journeys.",
        "vision": "We are redefining healthcare from episodic and reactive to continuous, anticipatory, and data-driven.",
        "differentiation": [
            "Consumer module (Viatra): family health hub, personal health OS, AI-driven health interpreter",
            "Doctor module (DoctorHub): streamlined cockpit with predictive triage, patient insights, and reduced admin overhead",
            "Enterprise-ready: interoperable with EMR/EHR, designed for scalability and compliance"
        ],
        "traction": {
            "MVP_status": "Functional demo with patient vitals, AI interpreter, and family health profiles",
            "pipeline": "Exploring hospital pilot collaborations and user beta trials"
        },
        "asks": [
            "Pilot partnership with leading hospitals/clinics",
            "Seed investment to accelerate development and regulatory compliance",
            "Integration pilots with existing hospital information systems"
        ],
        "metrics": {
            "engagement_target": "30% weekly active users (WAU) within 6 months",
            "efficiency_target": "20% reduction in physician admin load",
            "clinical_target": "Improved early detection of high-risk cases by 15%"
        },
        "north_star": "To become the anticipatory health OS — the layer where patients, families, and doctors converge seamlessly."
        }

    pitch_payload = json.dumps(pitch, indent=2)
    st.download_button('Download Pitch (JSON)', data=pitch_payload, file_name='Viatra_pitch.json')

    st.markdown("<div class='footer-small'>Questions? Use the sidebar to navigate to the interactive Consumer & Doctor demos. This landing page is a smart, product-led narrative ready for investor and hospital stakeholders.</div>", unsafe_allow_html=True)

# ----------------------------
# Viatra (Consumer)
# ----------------------------

if page == "Viatra (Consumer)":
    left, right = st.columns([1, 2])

    with left:
        st.subheader("Family Hub")
        prof_names = list(st.session_state.profiles.keys())
        active = st.selectbox("Active profile", prof_names, index=prof_names.index(st.session_state.active_profile))
        if active != st.session_state.active_profile:
            st.session_state.active_profile = active

        new_name = st.text_input("Add profile name")
        if st.button("Add Profile") and new_name and new_name not in st.session_state.profiles:
            st.session_state.profiles[new_name] = {"dob": None, "gender": None}
            st.session_state.vitals[new_name] = pd.DataFrame(columns=["datetime","systolic","diastolic","hr","glucose"]) 
            st.session_state.meds[new_name] = []
            st.session_state.records[new_name] = []
            st.session_state.passport[new_name] = {"immunizations": [], "allergies": [], "conditions": []}
            st.success(f"Profile '{new_name}' added.")

        st.divider()
        st.subheader("Health Passport")
        imms = st.text_area("Immunizations (comma-separated)", value=", ".join(st.session_state.passport[st.session_state.active_profile].get("immunizations", [])))
        alls = st.text_area("Allergies (comma-separated)", value=", ".join(st.session_state.passport[st.session_state.active_profile].get("allergies", [])))
        cond = st.text_area("Chronic Conditions (comma-separated)", value=", ".join(st.session_state.passport[st.session_state.active_profile].get("conditions", [])))
        if st.button("Update Passport"):
            st.session_state.passport[st.session_state.active_profile] = {
                "immunizations": [x.strip() for x in imms.split(",") if x.strip()],
                "allergies": [x.strip() for x in alls.split(",") if x.strip()],
                "conditions": [x.strip() for x in cond.split(",") if x.strip()],
            }
            st.success("Passport updated.")
        passport_payload = json.dumps({
            "profile": st.session_state.active_profile,
            **st.session_state.passport[st.session_state.active_profile]
        }, indent=2)
        st.download_button("Download Passport (JSON)", data=passport_payload, file_name="health_passport.json")

        st.divider()
        st.subheader("Medication Companion")
        meds_str = st.text_input("Current meds (comma-separated)", value=", ".join(st.session_state.meds[st.session_state.active_profile]))
        if st.button("Save Med List"):
            st.session_state.meds[st.session_state.active_profile] = [m.strip() for m in meds_str.split(",") if m.strip()]
            st.success("Medication list saved.")

    with right:
        st.subheader("Personal Health OS")
        with st.expander("Log Vitals"):
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                date = st.date_input("Date", value=datetime.now().date())
                time = st.time_input("Time", value = datetime.now().time())
            with col2:
                sys = st.number_input("Systolic", 80, 220, 120)
            with col3:
                dia = st.number_input("Diastolic", 40, 130, 80)
            with col4:
                hr = st.number_input("Heart Rate", 40, 200, 72)
            with col5:
                glu = st.number_input("Glucose (mg/dL)", 60, 400, 95)
            if st.button("Add Entry"):
                df = st.session_state.vitals[st.session_state.active_profile]
                st.session_state.vitals[st.session_state.active_profile] = pd.concat([
                    df,
                    pd.DataFrame([{"date":date, "time":time, "systolic": sys, "diastolic": dia, "hr": hr, "glucose": glu}])
                ], ignore_index=True)
                st.success("Entry added.")

        vitals_df = st.session_state.vitals[st.session_state.active_profile]
        if vitals_df.empty:
            st.info("No vitals yet — use the Log Vitals form to add data.")
        else:
            st.table(vitals_df.tail(6))

        st.divider()
        st.subheader("AI Health Interpreter (Demo)")
        lab_text = st.text_area("Paste lab/prescription text here", height=120)
        if st.button("Interpret"):
            st.session_state.lab_text = lab_text
        if st.session_state.lab_text:
            st.warning("This demo uses heuristic parsing. Integrate LLMs with clinical guardrails in production.")
            st.write(st.session_state.lab_text[:1000])

# ----------------------------
# Viatra (Hospital)
# ----------------------------

if page == "Viatra (Hospital)":
    st.markdown("**Operating Model:** Centralized cockpit for patient management, scheduling, e-prescriptions, decision support, collaboration, analytics, and learning — designed to integrate with existing HIS/EMR via FHIR/HL7.")

    tabs = st.tabs([
        "Patient Management",
        "Scheduling & Duty",
        "Rx & Meds",
        "Decision Support",
        "Collaboration",
        "Analytics",
        "Learning & Research",
    ])

    # Patient Management
    with tabs[0]:
        st.subheader("Patient Registry")
        c1, c2, c3, c4, c5, c6 = st.columns(6)
        with c1:
            pid = st.text_input("ID")
        with c2:
            pname = st.text_input("Name")
        with c3:
            page = st.number_input("Age", 0, 120, 40)
        with c4:
            psex = st.selectbox("Sex", ["M","F","Other"])
        with c5:
            pall = st.text_input("Allergies")
        with c6:
            pcom = st.text_input("Comorbidities")
        if st.button("Add / Update Patient"):
            df = st.session_state.patients
            df = df[df["id"] != pid]
            st.session_state.patients = pd.concat([df, pd.DataFrame([{"id": pid, "name": pname, "age": page, "sex": psex, "allergies": pall, "comorbidities": pcom}])], ignore_index=True)
            st.success("Patient upserted.")
        st.dataframe(st.session_state.patients)

    # Scheduling & Duty
    with tabs[1]:
        st.subheader("Rosters & Shifts")
        rdate = st.date_input("Date", value=date.today())
        rshift = st.selectbox("Shift", ["Morning","Evening","Night"]) 
        rdoc = st.text_input("Doctor")
        if st.button("Add to Roster"):
            st.session_state.roster = pd.concat([
                st.session_state.roster,
                pd.DataFrame([{"date": rdate.isoformat(), "shift": rshift, "doctor": rdoc}])
            ], ignore_index=True)
            st.success("Roster entry added.")
        st.dataframe(st.session_state.roster.sort_values(by=["date","shift"]))

    # Prescription & Medication Management
    with tabs[2]:
        st.subheader("E-Prescription")
        rx_name = st.text_input("Patient Name")
        rx_drugs = st.text_area("Medications (comma-separated)")
        rx_notes = st.text_area("Instructions")
        if st.button("Generate Rx"):
            meds = [m.strip() for m in rx_drugs.split(",") if m.strip()]
            st.json({"patient": rx_name, "meds": meds, "instructions": rx_notes})
            st.success("E-prescription generated (demo).")

    # Collaboration & Analytics (simplified)
    with tabs[4]:
        st.subheader("Secure Chat (Demo)")
        msg = st.text_input("Message")
        if st.button("Send") and msg:
            st.session_state.chat.append({"when": datetime.utcnow().isoformat(), "who": "Dr. Demo", "msg": msg})
        if st.session_state.chat:
            st.table(pd.DataFrame(st.session_state.chat))

    with tabs[5]:
        st.subheader("Operational Analytics (Demo)")
        dates = pd.date_range(date.today() - timedelta(days=29), periods=30)
        appts = pd.Series([max(5, int(20 + i % 7 - (i//5))) for i in range(30)], index=dates)
        fig1, ax1 = plt.subplots()
        ax1.plot(appts.index, appts.values)
        ax1.set_title("Daily Appointments (synthetic)")
        ax1.set_xlabel("Date")
        ax1.set_ylabel("Count")
        st.pyplot(fig1)

# ----------------------------
# Footer
# ----------------------------

st.divider()
st.caption("© 2025 Viatra — This MVP is for demonstration only and does not provide medical advice.")
