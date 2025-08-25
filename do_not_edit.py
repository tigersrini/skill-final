# ==========================================================
# To start this dashboard, just click "Deploy" on Streamlit Cloud!
# ==========================================================

import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import re
import unicodedata
import sqlite3
import os
import numpy as np
# --- Password Authentication ---
def password_page():
    st.title("Dashboard Login")
    password = st.text_input("Enter password:", type="password")
    if st.button("Login"):
        if password == "RNTBCI_PE":
            st.session_state["authenticated"] = True
        else:
            st.error("Incorrect password. Please try again.")

# --- Main App Entry Point ---
if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    password_page()
    st.stop()

# Add custom background color using CSS
st.markdown(
    """
    <style>
        body {
            background-color: #f4f7fa;
        }
        .stApp {
            background-color: #f4f7fa;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# === Official mapping ===
TEAM_BLOCKS = {
    "Process - Covers": [
        "Panel division / Weld Division", "Gun selection & Gun panel check & Weld macro",
        "Datum / Production ID creation", "Hem tool / Hem marriage / Hem Flange check",
        "PR Check", "Specsheet [UCF]","Specsheet [Jig]" ,"Cycle time study (INR Line, HEM Line)", "POS"
    ],
    "Process - Metal": [
        "Bulk List", "Operation Sheet", "Air Tool Access & Work Posture Check", "Panel Comparison",
        "PQ Check", "Specsheet", "Check Gauge Specsheet", "QVCC (Quality Circle)"
    ],
    "Process - Body": [
        "Panel Division", "Part List", "Weld Division", "Weld Balance", "PR Check2", "Gun Panel Check",
        "Panel Comparison2", "Datum Creation", "ACL Management", "ID / Marking",

        "Part Flow", "Wrong Set Prevention", "Spec Sheet", "Weld Macro", "Weld Pitch Macro", "CUS Creation", 
        "Input Validation", "CM Proposals", "Report Preparation"
    ],
    "JIG": [
        "NX CAD Tool", "Concept Jig", "Weld Balance2", "Facet Modeling", "2D Detailing",
        "TCM to 3D", "Jig Kinematics", "PSW Confirmation", "CM for Welding Jig", "Jig Report", "Ergonomics Check"
    ],
    "PS": [
        "TCM & PSI Tool", "SRS Weld Feasibility", "Shimawari Kun", "Facility Confirmation", "Cell Building",
        "Tool Kinematics & Feasibility", "Countermeasure Proposal / Adaption", "CUS Preparation – Product (Weld, Panel, Jig)",
        "Analytical Thinking & Approach", "Report Preparation2", "New Member Skill-Up", "Project Kickoff & Schedule Forecast",
        "Customer Interaction & Negotiation "
    ],
    "PHYSICAL": [
        "Manufacturing Plan Creation", "Direct Material & DST", "Master Schedule Creation", "Milestone Management (PPCM)",
        "Cost Reduction in Estimation", "Trial Operation – VC, PT Lot", "Built-in Quality & Hemming",
        "Installation & Commissioning", "Panel Joinery – Welding & Sealer", "POS Preparation",
        "About Tensya 35 items", "Planning of body accuracy", "In house Supplier parts condition.", 
        "\xa0Inspection Standard B Creation", "DEA Measurement Preparation", "N-PES & Control Graph Documentation", 
        "\xa0Marking of Weld Point", "\xa0Square Check", "Gabari Template Creation", "Welding Destruction Test", 
        "OEE Management", "Cycle Time Study", "Facility Handover to Plant"
    ],
    "BOP / PQE": [
        "PR Check3", "Datum Check", "Gauge check", "New Project Development", "Tachiai", "Monozukri",
        "Simul Study [R&N]", "WOS File creation [R]", "Process Validation [R&N]"
    ],
    "IWS / QAR": [
        "Tip Camera", "Weld Inspection Camera", "IWS", "Weld Check Area"
    ]
}
GENERAL_SKILLS = [
    "Digitalization", "Automation", "Documentation & Presentation",
    "New Skill up for future business shift", "TQM ", "Japanese Training", "Project management"
]

# --- Skill Descriptions (for viewing only, not used in calculations) ---
SKILL_DESCRIPTIONS = {
    # General Skills
    "Digitalization": "PX: Uses basic digital tools and software as instructed.\nPE2: Improves work efficiency using digital solutions, trains others on new tools.\nM3: Leads digital transformation, integrates advanced digital systems into team workflow.",
    "Automation": "PX: Follows automated procedures and operates simple automated equipment.\nPE2: Identifies automation opportunities and implements improvements in daily tasks.\nM3: Drives large-scale automation projects, sets automation strategy for the department.",
    "Documentation & Presentation": "PX: Prepares basic reports and presentations as guided.\nPE2: Creates structured documentation, delivers effective presentations to team.\nM3: Sets documentation standards, coaches team in advanced presentation and reporting skills.",
    "New Skill up for future business shift": "PX: Participates in training for new skills relevant to business changes.\nPE2: Leads learning initiatives, mentors team on adapting to new business skills.\nM3: Anticipates skill needs, designs upskilling strategies for organization-wide adaptation.",
    "TQM ": "PX: Applies basic TQM tools and follows quality procedures.\nPE2: Leads small TQM projects, analyzes data for quality improvement.\nM3: Drives TQM initiatives, sets quality vision and ensures organization-wide implementation.",
    "Japanese Training": "PX: Understands and uses basic Japanese greetings, phrases, and workplace terms.\nPE2: Communicates effectively in Japanese for work discussions, prepares simple documents in Japanese.\nM3: Conducts meetings, negotiations, and presentations fluently in Japanese; mentors team on cross-cultural communication.",
    "Strategical Planning": "PX: Supports planning activities by gathering data and following given strategies.\nPE2: Develops action plans aligned with departmental goals, evaluates outcomes for improvement.\nM3: Defines long-term strategic goals, aligns cross-functional initiatives to organizational vision.",
    
    # Process - Covers
    "Panel division / Weld Division": "PX: Follows instructions to divide panels and allocate welds as per guidelines.\nPE2: Manages panel division, ensures weld allocation meets process requirements, suggests improvements.\nM3: Strategizes panel division and weld allocation to optimize production, ensures process alignment across projects.",
    "Gun selection & Gun panel check & Weld macro": "PX: Selects appropriate gun and performs basic panel/weld checks as per SOP.\nPE2: Oversees gun selection, reviews weld macro logic, and guides panel checking for quality.\nM3: Defines gun selection standards, optimizes weld macros, and leads troubleshooting for critical weld issues.",
    "Datum / Production ID creation": "PX: Creates datum and production IDs by following templates and standard practices.\nPE2: Ensures accuracy in datum/ID creation, checks consistency, and updates as needed.\nM3: Establishes datum/ID strategy, audits compliance, and integrates into digital systems.",
    "Hem tool / Hem marriage / Hem Flange check": "PX: Operates hem tools and performs basic marriage/flange checks as instructed.\nPE2: Validates hem tool setups, manages hem marriage process, and addresses issues.\nM3: Develops and standardizes hem tool and marriage procedures, drives process innovation.",
    "PR Check": "PX: Conducts PR checks using checklists, flags any deviations.\nPE2: Supervises PR checks, ensures corrective actions, and trains juniors.\nM3: Implements and audits PR check process, drives improvements across teams.",
    "Specsheet [UCF]": "PX: Assists in preparing UCF specsheets using defined formats.\nPE2: Reviews and validates UCF specsheets for accuracy, manages version control.\nM3: Standardizes UCF specsheet creation, ensures integration with global practices.",
    "Specsheet [Jig]": "PX: Prepares basic jig specsheets under supervision.\nPE2: Leads jig specsheet preparation and ensures technical correctness.\nM3: Oversees jig spec documentation, establishes global standards.",
    "Cycle time study (INR Line, HEM Line)": "PX: Collects cycle time data and fills study sheets as instructed.\nPE2: Analyzes cycle time data, identifies improvement areas, and proposes optimizations.\nM3: Establishes cycle time KPIs, leads plant-wide optimization initiatives.",
    "POS": "PX: Performs basic POS (Point of Supply/Service) activities as per SOP.\nPE2: Manages POS process, checks for issues, and proposes corrective actions.\nM3: Designs POS process, ensures integration with production systems, and drives cost/time optimization.",
    
    # Process - Metal
    "Bulk List": "PX: Prepares bulk lists using provided formats.\nPE2: Reviews and verifies bulk lists for completeness and accuracy.\nM3: Standardizes bulk list processes, ensures alignment with supply systems.",
    "Operation Sheet": "PX: Fills operation sheets as instructed.\nPE2: Validates and updates operation sheets, manages documentation flow.\nM3: Defines operation sheet standards, ensures best practices across teams.",
    "Air Tool Access & Work Posture Check": "PX: Follows air tool access and posture instructions.\nPE2: Audits tool access, suggests ergonomic improvements.\nM3: Implements ergonomic programs, sets audit schedules.",
    "Panel Comparison": "PX: Performs basic panel comparison checks.\nPE2: Analyzes differences, suggests corrections, updates records.\nM3: Standardizes panel comparison methods, drives improvement projects.",
    "PQ Check": "PX: Conducts PQ (Process Quality) checks per checklist.\nPE2: Reviews PQ results, manages corrective actions.\nM3: Oversees PQ process, implements improvements plant-wide.",
    "Specsheet": "PX: Prepares basic specsheets.\nPE2: Validates specsheets, manages revisions.\nM3: Standardizes specsheets, ensures cross-team adoption.",
    "Check Gauge Specsheet": "PX: Records gauge data in specsheets.\nPE2: Verifies gauge specsheets, corrects discrepancies.\nM3: Sets gauge specsheet standards, drives digital adoption.",
    "QVCC (Quality Circle)": "PX: Participates in QVCC activities, follows instructions.\nPE2: Facilitates small QVCC projects, mentors team members.\nM3: Leads cross-functional QVCC, aligns with company strategy.",
    
    # Process - Body
    "Panel Division": "PX: Follows instructions for panel division tasks.\nPE2: Manages panel division, ensures process compliance.\nM3: Defines division standards, audits process effectiveness.",
    "Part List": "PX: Prepares part lists as per guidelines.\nPE2: Verifies and updates part lists for accuracy.\nM3: Standardizes part list process, ensures integration with BOM.",
    "Weld Division": "PX: Allocates welds as instructed.\nPE2: Oversees weld division, suggests layout improvements.\nM3: Establishes weld division standards, drives plant optimization.",
    "Weld Balance": "PX: Follows weld balance instructions, records data.\nPE2: Analyzes weld balance, identifies and solves issues.\nM3: Optimizes weld balance strategy, leads global benchmarking.",
    "PR Check2": "PX: Conducts PR checks per checklist.\nPE2: Supervises PR check activities, ensures follow-up actions.\nM3: Sets PR check policy, audits implementation.",
    "Gun Panel Check": "PX: Performs gun panel checks as per SOP.\nPE2: Validates gun panel checks, corrects detected issues.\nM3: Defines check strategy, implements improvements.",
    "Panel Comparison2": "PX: Executes basic panel comparisons.\nPE2: Reviews and analyzes results, proposes changes.\nM3: Audits panel comparison processes, aligns standards.",
    "Datum Creation": "PX: Creates datum points following instructions.\nPE2: Ensures datum accuracy, updates documentation.\nM3: Sets datum standards, audits for consistency.",
    "ACL Management": "PX: Follows ACL data entry/update procedures.\nPE2: Oversees ACL management, corrects errors.\nM3: Defines ACL management process, leads audits.",
    "ID / Marking": "PX: Applies IDs/marks as instructed.\nPE2: Ensures correct marking and documentation.\nM3: Sets marking standards, audits compliance.",
    "Part Flow": "PX: Follows part flow instructions during production.\nPE2: Analyzes and optimizes part flow, removes bottlenecks.\nM3: Designs part flow strategy, leads cross-team improvements.",
    "Wrong Set Prevention": "PX: Uses prevention tools as per instructions.\nPE2: Validates and improves prevention measures.\nM3: Establishes prevention policies, drives new initiatives.",
    "Spec Sheet": "PX: Assists in spec sheet preparation.\nPE2: Leads spec sheet validation and management.\nM3: Standardizes spec sheet practices, ensures plant-wide compliance.",
    "Weld Macro": "PX: Executes weld macros as per guidelines.\nPE2: Optimizes weld macro logic, trains others.\nM3: Develops and deploys advanced weld macro strategies.",
    "Weld Pitch Macro": "PX: Uses pitch macro as per instruction.\nPE2: Analyzes pitch macro data, proposes improvements.\nM3: Sets standards for pitch macros, ensures global adoption.",
    "CUS Creation": "PX: Prepares CUS documents as per template.\nPE2: Validates and updates CUS documentation.\nM3: Standardizes CUS process, integrates with digital tools.",
    "Input Validation": "PX: Validates input data as per checklist.\nPE2: Manages and reviews validation process.\nM3: Sets validation protocols, audits compliance.",
    "CM Proposals": "PX: Suggests basic corrective measures.\nPE2: Leads proposal development, implements changes.\nM3: Drives strategic CM projects, ensures alignment with goals.",
    "Report Preparation": "PX: Assists in report preparation as guided.\nPE2: Prepares comprehensive reports, ensures accuracy.\nM3: Reviews and approves reports, sets reporting standards.",
    
    # JIG
    "NX CAD Tool": "PX: Operates NX CAD tool for simple tasks.\nPE2: Designs and modifies jigs using NX CAD, trains others.\nM3: Establishes NX CAD best practices, drives innovation.",
    "Concept Jig": "PX: Prepares concept jigs as instructed.\nPE2: Develops and validates jig concepts.\nM3: Defines concept jig strategies, standardizes designs.",
    "Weld Balance2": "PX: Records weld balance data for jigs.\nPE2: Analyzes and optimizes jig weld balance.\nM3: Sets standards for weld balance in jig design.",
    "Facet Modeling": "PX: Performs basic facet modeling tasks.\nPE2: Leads modeling activities, ensures quality.\nM3: Innovates and optimizes facet modeling processes.",
    "2D Detailing": "PX: Assists with 2D detailing under guidance.\nPE2: Prepares and reviews 2D details for jigs.\nM3: Standardizes 2D detailing methods, leads audits.",
    "TCM to 3D": "PX: Converts TCM data to 3D as per instructions.\nPE2: Manages 3D conversion, ensures data accuracy.\nM3: Develops TCM to 3D conversion standards, automates process.",
    "Jig Kinematics": "PX: Supports basic jig kinematics tasks.\nPE2: Analyzes and solves kinematics issues, updates design.\nM3: Sets kinematics design strategy, leads R&D.",
    "PSW Confirmation": "PX: Follows procedures for PSW confirmation.\nPE2: Validates PSW documents, ensures process compliance.\nM3: Sets PSW policies, audits effectiveness.",
    "CM for Welding Jig": "PX: Assists with change management (CM) for jigs.\nPE2: Manages CM activities, implements improvements.\nM3: Leads strategic CM projects, aligns with global standards.",
    "Jig Report": "PX: Prepares simple jig reports.\nPE2: Reviews and submits jig reports, ensures data quality.\nM3: Audits and standardizes jig reporting.",
    "Ergonomics Check": "PX: Follows ergonomics checklist during jig work.\nPE2: Analyzes ergonomics, implements improvements.\nM3: Establishes ergonomics programs, audits compliance.",
    
    # PS
    "TCM & PSI Tool": "PX: Operates TCM/PSI tools as instructed.\nPE2: Optimizes tool use, solves basic issues.\nM3: Drives tool adoption, leads tool improvement projects.",
    "SRS Weld Feasibility": "PX: Follows SRS weld feasibility study steps.\nPE2: Conducts and documents feasibility studies.\nM3: Standardizes and audits weld feasibility practices.",
    "Shimawari Kun": "PX: Operates Shimawari Kun for basic checks.\nPE2: Troubleshoots and optimizes usage, trains others.\nM3: Implements Shimawari Kun as standard tool, leads improvements.",
    "Facility Confirmation": "PX: Supports facility confirmation activities.\nPE2: Manages facility confirmation, ensures readiness.\nM3: Establishes confirmation standards, drives improvements.",
    "Cell Building": "PX: Follows instructions for cell building.\nPE2: Manages and optimizes cell setup.\nM3: Defines cell building strategies, ensures best practices.",
    "Tool Kinematics & Feasibility": "PX: Conducts kinematic checks as per guide.\nPE2: Validates tool kinematics, resolves issues.\nM3: Sets tool kinematics standards, leads feasibility studies.",
    "Countermeasure Proposal / Adaption": "PX: Suggests simple countermeasures.\nPE2: Leads proposal development and implementation.\nM3: Drives strategic countermeasure initiatives.",
    "CUS Preparation – Product (Weld, Panel, Jig)": "PX: Prepares CUS docs as per template.\nPE2: Reviews and updates CUS documents.\nM3: Standardizes and audits CUS process.",
    "Analytical Thinking & Approach": "PX: Uses analytical tools with guidance.\nPE2: Solves problems using structured analysis.\nM3: Teaches analytical thinking, sets frameworks.",
    "Report Preparation2": "PX: Assists in report making.\nPE2: Prepares and reviews reports for completeness.\nM3: Standardizes reporting, ensures insights are actionable.",
    "New Member Skill-Up": "PX: Participates in skill-up training.\nPE2: Leads training sessions, mentors new members.\nM3: Designs skill-up programs, tracks progress.",
    "Project Kickoff & Schedule Forecast": "PX: Supports project kickoff, attends meetings.\nPE2: Manages schedules, updates project plans.\nM3: Defines project launch strategy, reviews progress.",
    "Customer Interaction & Negotiation ": "PX: Participates in customer meetings with guidance.\nPE2: Manages day-to-day customer communications.\nM3: Leads negotiations, handles escalations.",
    
    # PHYSICAL
    "Manufacturing Plan Creation": "PX: Prepares manufacturing plans as instructed.\nPE2: Validates and improves manufacturing plans.\nM3: Defines manufacturing strategy, audits plans.",
    "Direct Material & DST": "PX: Documents material and DST data.\nPE2: Manages material lists, optimizes DST use.\nM3: Sets material/DST strategy, audits inventory.",
    "Master Schedule Creation": "PX: Assists in creating master schedule.\nPE2: Updates and maintains schedule, solves issues.\nM3: Establishes scheduling policy, leads optimization.",
    "Milestone Management (PPCM)": "PX: Tracks milestones, updates records.\nPE2: Manages milestone progress, addresses delays.\nM3: Sets milestone strategy, audits for compliance.",
    "Cost Reduction in Estimation": "PX: Supports cost estimation tasks.\nPE2: Identifies and implements cost reduction ideas.\nM3: Drives cost reduction strategy, tracks results.",
    "Trial Operation – VC, PT Lot": "PX: Participates in trial operations as per instructions.\nPE2: Manages trial operation logistics, documents results.\nM3: Defines trial operation process, leads reviews.",
    "Built-in Quality & Hemming": "PX: Follows BIQ and hemming checks.\nPE2: Validates quality, solves basic issues.\nM3: Sets BIQ strategy, ensures process excellence.",
    "Installation & Commissioning": "PX: Assists in installation and commissioning.\nPE2: Manages installation, troubleshoots issues.\nM3: Defines process, ensures best practices are followed.",
    "Panel Joinery – Welding & Sealer": "PX: Applies welding/sealer as per instructions.\nPE2: Reviews joinery quality, optimizes application.\nM3: Standardizes joinery practices, drives improvements.",
    "POS Preparation": "PX: Prepares POS as guided.\nPE2: Reviews and optimizes POS prep process.\nM3: Sets POS standards, ensures integration.",
    "About Tensya 35 items": "PX: Reviews Tensya checklist.\nPE2: Ensures all Tensya items are addressed.\nM3: Audits and standardizes Tensya checks.",
    "Planning of body accuracy": "PX: Collects and documents body accuracy data.\nPE2: Analyzes data, suggests accuracy improvements.\nM3: Develops accuracy plan, reviews compliance.",
    "In house Supplier parts condition.": "PX: Checks supplier parts as per SOP.\nPE2: Manages supplier parts quality, raises issues.\nM3: Audits supplier performance, drives improvement plans.",
    "\xa0Inspection Standard B Creation": "PX: Prepares Inspection Standard B documents as instructed, following templates.\nPE2: Reviews and updates Inspection Standard B, ensures accuracy and completeness.\nM3: Defines Inspection Standard B policy, standardizes documentation, audits for compliance.",
    "DEA Measurement Preparation": "PX: Assists with DEA measurement prep.\nPE2: Manages DEA measurements, ensures data quality.\nM3: Defines DEA measurement process, audits usage.",
    "N-PES & Control Graph Documentation": "PX: Fills control graph docs.\nPE2: Manages and reviews N-PES docs.\nM3: Standardizes N-PES process, drives digitalization.",
    "\xa0Marking of Weld Point": "PX: Marks weld points as per work instructions and drawings.\nPE2: Verifies accuracy of weld point marking, corrects any errors found.\nM3: Develops marking standards for weld points, audits process quality, and implements improvements.",
    "\xa0Square Check": "PX: Performs basic square checks using standard tools.\nPE2: Analyzes square check results, documents findings, and resolves minor issues.\nM3: Establishes square check procedures, leads audits, and drives best practice adoption.",
    "Gabari Template Creation": "PX: Prepares templates as per instructions.\nPE2: Manages template accuracy, solves issues.\nM3: Standardizes template process, drives automation.",
    "Welding Destruction Test": "PX: Performs basic weld destruction tests.\nPE2: Analyzes test results, updates documentation.\nM3: Sets testing protocols, reviews results for trends.",
    "OEE Management": "PX: Records OEE data.\nPE2: Analyzes OEE, implements improvements.\nM3: Drives OEE strategy, benchmarks performance.",
    "Cycle Time Study": "PX: Assists with cycle time data collection.\nPE2: Reviews and analyzes cycle times, proposes changes.\nM3: Establishes cycle time targets, audits progress.",
    "Facility Handover to Plant": "PX: Supports handover process, prepares docs.\nPE2: Manages handover, ensures all deliverables met.\nM3: Audits and standardizes handover process.",
    
    # BOP / PQE
    "PR Check3": "PX: Performs PR checks as per list.\nPE2: Reviews and validates PR checks, follows up on issues.\nM3: Audits and improves PR check process.",
    "Datum Check": "PX: Conducts datum checks per instruction.\nPE2: Manages datum checks, solves discrepancies.\nM3: Sets datum check policy, leads audits.",
    "Gauge check": "PX: Performs gauge checks as instructed.\nPE2: Validates and documents gauge checks.\nM3: Standardizes gauge checking, audits compliance.",
    "New Project Development": "PX: Supports new project tasks as assigned.\nPE2: Manages project activities, tracks milestones.\nM3: Leads project development, defines strategy.",
    "Tachiai": "PX: Participates in Tachiai activities.\nPE2: Coordinates Tachiai, ensures readiness.\nM3: Defines Tachiai process, leads cross-team efforts.",
    "Monozukri": "PX: Follows Monozukri improvement practices.\nPE2: Leads small Monozukri projects, trains team.\nM3: Drives Monozukri culture, benchmarks improvements.",
    "Simul Study [R&N]": "PX: Supports simulation studies.\nPE2: Manages simulation runs, analyzes outputs.\nM3: Defines simulation standards, audits effectiveness.",
    "WOS File creation [R]": "PX: Prepares WOS files as per SOP.\nPE2: Reviews and updates WOS files.\nM3: Standardizes WOS file process, ensures digital integration.",
    "Process Validation [R&N]": "PX: Follows process validation checklist.\nPE2: Conducts and documents process validation.\nM3: Sets validation policy, audits across projects.",
    
    # IWS / QAR
    "Tip Camera": "PX: Operates tip camera for basic inspections.\nPE2: Analyzes camera data, resolves issues.\nM3: Implements tip camera best practices, leads adoption.",
    "Weld Inspection Camera": "PX: Uses weld inspection camera as instructed.\nPE2: Validates inspection results, trains others.\nM3: Sets inspection standards, audits usage.",
    "IWS": "PX: Supports IWS activities as per plan.\nPE2: Manages IWS process, documents outputs.\nM3: Optimizes IWS implementation, ensures plant-wide compliance.",
    "Weld Check Area": "PX: Performs weld checks in assigned area.\nPE2: Supervises area checks, solves detected issues.\nM3: Defines area check policy, leads improvement programs."
}

def rating_to_num(x):
    if pd.isna(x): return 0
    s = str(x)
    s = "".join(" " if unicodedata.category(c) == "Zs" else c for c in s)
    s = re.sub(r"[^\w\d ]", "", s, flags=re.UNICODE)
    s = re.sub(" +", " ", s).strip().lower()
    s = s.replace(" ", "")
    if s in ["", "none", "na", "null"]: return 0
    if "m3" in s or "expert" in s or "pe3" in s or "level3" in s or "exp" in s or s == "3": return 3
    if "pe2" in s or "intermediate" in s or "level2" in s or s == "2": return 2
    if "px" in s or "basic" in s or "level1" in s or s == "1": return 1
    nums = re.findall(r'\d', s)
    if nums:
        num = int(nums[0])
        if num in [0,1,2,3]: return num
    return 0

def rating_to_label(val):
    if val == 3: return "🟩 M3 (Expert)"
    if val == 2: return "🟧 PE2 (Intermediate)"
    if val == 1: return "🟨 PX (Basic Level)"
    return "⬜ Blank"

def norm_team_name(s):
    return str(s).strip().replace(" ", "").lower()

db_path = os.path.join(os.path.dirname(__file__), 'manager_ratings.db')
conn = sqlite3.connect(db_path, check_same_thread=False)
c = conn.cursor()
c.execute('''
    CREATE TABLE IF NOT EXISTS manager_ratings (
        employee_id TEXT,
        skill TEXT,
        rating INTEGER,
        PRIMARY KEY (employee_id, skill)
    )
''')
conn.commit()

def get_employee_id(row):
    if pd.notna(row.get('Name')):
        return f"Name:{row['Name']}"
    elif pd.notna(row.get('Name2')):
        return f"Name2:{row['Name2']}"
    elif pd.notna(row.get('Email')):
        return f"Email:{row['Email']}"
    return None

def load_manager_ratings(employee_id, core_skills):
    c.execute('SELECT skill, rating FROM manager_ratings WHERE employee_id=?', (employee_id,))
    ratings = dict(c.fetchall())
    return [ratings.get(skill, 0) for skill in core_skills]

def save_manager_ratings(employee_id, core_skills, ratings):
    for skill, rating in zip(core_skills, ratings):
        c.execute('REPLACE INTO manager_ratings (employee_id, skill, rating) VALUES (?, ?, ?)', (employee_id, skill, rating))
    conn.commit()

def export_manager_ratings():
    df = pd.read_sql_query('SELECT * FROM manager_ratings', conn)
    return df

# --- Streamlit Page Config ---
st.set_page_config(page_title="RNTBCI-PE BIW Skill Matrix", layout="wide", page_icon="🏭")
st.markdown(
    """
    <style>
    body, .main, .block-container {
        background: linear-gradient(120deg, #e0eafc 0%, #f8f9fa 100%) !important;
        color: #222 !important;
        font-family: 'Inter', 'Segoe UI', 'Roboto', Arial, sans-serif !important;
    }
    .block-container {
        border-radius: 24px;
        box-shadow: 0 8px 32px rgba(42,82,152,0.10);
        padding: 2.5rem 2.5rem 2.5rem 2.5rem !important;
        margin-top: 1.5rem;
        background: rgba(255,255,255,0.90) !important;
        backdrop-filter: blur(8px);
    }
    h1, h2, h3 {
        color: #2a5298 !important;
        font-family: 'Inter', 'Segoe UI', 'Roboto', Arial, sans-serif !important;
        font-weight: 700;
        letter-spacing: 0.02em;
        background: none !important;
        text-shadow: 0 2px 12px rgba(42,82,152,0.08);
    }
    h1 {
        font-size: 2.4rem !important;
        margin-bottom: 0.7rem !important;
        text-align: center;
        background: none !important;
        border-bottom: 2px solid #e0eafc;
        padding-bottom: 0.5rem;
    }
    h2 {
        font-size: 1.6rem !important;
        margin-top: 2.2rem !important;
        margin-bottom: 1.2rem !important;
        text-align: center;
        border-bottom: 2px solid #e0eafc;
        padding-bottom: 0.4rem;
    }
    h3 {
        font-size: 1.2rem !important;
        margin-top: 1.7rem !important;
        margin-bottom: 0.8rem !important;
        text-align: left;
    }
    body, .main, .block-container, .stTabs, .stButton > button, .dataframe, .streamlit-expanderHeader, .stAlert {
        font-size: 18px !important;
    }
    .stButton > button {
        background: linear-gradient(90deg, #2a5298 0%, #1e3c72 100%) !important;
        color: #fff !important;
        border: none !important;
        border-radius: 12px !important;
        font-size: 18px !important;
        font-weight: 600 !important;
        padding: 0.7rem 1.4rem !important;
        margin: 0.4rem 0.1rem !important;
        box-shadow: 0 2px 16px rgba(42,82,152,0.10);
        transition: background 0.2s, box-shadow 0.2s;
        backdrop-filter: blur(2px);
    }
    .stButton > button:hover {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%) !important;
        box-shadow: 0 6px 24px rgba(42,82,152,0.18);
        border: none !important;
    }
    .stFileUploader > div {
        border: 2px dashed #2a5298;
        border-radius: 16px;
        background: rgba(255,255,255,0.7);
        transition: all 0.3s ease;
        box-shadow: 0 2px 12px rgba(42,82,152,0.06);
        backdrop-filter: blur(2px);
    }
    .stFileUploader > div:hover {
        border-color: #1e3c72;
        background: #e0eafc;
        transform: scale(1.02);
    }
    .stSlider > div > div > div {
        background: #e0eafc !important;
        border-radius: 6px !important;
        height: 5px !important;
        border: 1px solid #2a5298 !important;
    }
    .stSlider [role="slider"] {
        background: #2a5298 !important;
        border: 2px solid #fff !important;
        box-shadow: 0 2px 8px rgba(42,82,152,0.10) !important;
        width: 18px !important;
        height: 18px !important;
    }
    .stTabs [data-baseweb="tab-panel"] {
        animation: tabContentSlide 0.8s cubic-bezier(0.4, 0, 0.2, 1);
        background: rgba(255,255,255,0.90) !important;
        border-radius: 18px;
        box-shadow: 0 2px 16px rgba(42,82,152,0.08);
        backdrop-filter: blur(4px);
        margin-bottom: 1.5rem;
    }
    @keyframes tabContentSlide {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    .dataframe {
        border-radius: 16px;
        overflow: hidden;
        box-shadow: 0 4px 24px rgba(42,82,152,0.10);
        animation: tableSlideIn 1s ease;
        background: rgba(255,255,255,0.90);
        backdrop-filter: blur(2px);
    }
    @keyframes tableSlideIn {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    .streamlit-expanderHeader {
        background: rgba(255,255,255,0.7) !important;
        border-radius: 14px;
        transition: all 0.3s ease;
        border: 2px solid #2a5298 !important;
        box-shadow: 0 2px 12px rgba(42,82,152,0.06);
        backdrop-filter: blur(2px);
    }
    .streamlit-expanderHeader:hover {
        background: #e0eafc !important;
        transform: scale(1.02);
        border: 2px solid #1e3c72 !important;
        box-shadow: 0 4px 16px rgba(42,82,152,0.12);
    }
    .stAlert {
        border-radius: 14px;
        border-left: 5px solid #2a5298;
        animation: alertSlideIn 0.5s ease;
        backdrop-filter: blur(5px);
        background: rgba(255,255,255,0.90) !important;
        color: #222 !important;
        box-shadow: 0 2px 12px rgba(42,82,152,0.08);
    }
    @keyframes alertSlideIn {
        from {
            opacity: 0;
            transform: translateX(-30px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    ::-webkit-scrollbar {
        width: 8px;
    }
    ::-webkit-scrollbar-track {
        background: #e0eafc;
        border-radius: 10px;
    }
    ::-webkit-scrollbar-thumb {
        background: #2a5298;
        border-radius: 10px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #1e3c72;
    }
    </style>
    """,
    unsafe_allow_html=True
)
st.markdown(
    """
    <div style="text-align: center; margin-bottom: 2rem;">
        <h1 style="font-size: 3rem; margin-bottom: 0.5rem; animation: titleBounce 2s ease;">
             RNTBCI-PE BIW Skill Matrix Dashboard
        </h1>
        <div style="height: 4px; background: linear-gradient(90deg, #2196f3, #4caf50, #ff9800, #e91e63); 
                    border-radius: 2px; animation: progressBar 3s ease-in-out infinite;"></div>
    </div>
    """,
    unsafe_allow_html=True
)

# --- Hide file uploader after upload ---
if 'file_uploaded' not in st.session_state:
    st.session_state['file_uploaded'] = False

if not st.session_state['file_uploaded']:
    st.markdown(
        """
        <div style="text-align: center; margin: 2rem 0;">
            <div style="background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
                        border: 3px dashed #4caf50; border-radius: 20px; padding: 2rem;
                        animation: uploadPulse 3s ease-in-out infinite;
                        box-shadow: 0 8px 25px rgba(76, 175, 80, 0.1);">
                <h3 style="color: #2e7d32; margin-bottom: 1rem; animation: bounce 2s infinite;">
                    📁 Upload Your BIW Skill Matrix Excel File
                </h3>
                <p style="color: #666; font-size: 1.1rem; margin-bottom: 1.5rem;">
                    Drag and drop your Excel file here or click to browse
                </p>
            </div>
        </div>
        <style>
        @keyframes uploadPulse {
            0%, 100% { transform: scale(1); border-color: #4caf50; }
            50% { transform: scale(1.02); border-color: #2e7d32; }
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    excel_file = st.file_uploader("Upload Skill Matrix Excel", type=["xlsx"], label_visibility="collapsed")
    if excel_file:
        # Show loading animation
        st.markdown(
            """
            <div style="text-align: center; margin: 1rem 0;">
                <div style="background: linear-gradient(135deg, #e8f5e8 0%, #c8e6c9 100%);
                            border-radius: 12px; padding: 1rem;
                            animation: loadingSuccess 1s ease;">
                    <span style="font-size: 1.5rem; color: #2e7d32;">✅</span>
                    <span style="color: #2e7d32; font-weight: 600; margin-left: 0.5rem;">
                        File uploaded successfully! Loading dashboard...
                    </span>
                </div>
            </div>
            <style>
            @keyframes loadingSuccess {
                from { opacity: 0; transform: translateY(20px); }
                to { opacity: 1; transform: translateY(0); }
            }
            </style>
            """,
            unsafe_allow_html=True
        )
        st.session_state['file_uploaded'] = True
        st.session_state['excel_file'] = excel_file
        st.rerun()
    else:
        st.markdown(
            """
            <div style="text-align: center; margin: 1rem 0; padding: 1rem;
                        background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
                        border: 1px solid #ffc107; border-radius: 12px;
                        animation: infoGlow 2s ease-in-out infinite alternate;">
                <span style="font-size: 1.2rem;">💡</span>
                <span style="color: #856404; font-weight: 500; margin-left: 0.5rem;">
                    Please upload your BIW Skill Matrix Excel file to get started!
                </span>
            </div>
            <style>
            @keyframes infoGlow {
                from { box-shadow: 0 0 5px rgba(255, 193, 7, 0.3); }
                to { box-shadow: 0 0 15px rgba(255, 193, 7, 0.6); }
            }
            </style>
            """,
            unsafe_allow_html=True
        )
        st.stop()
else:
    excel_file = st.session_state['excel_file']

df = pd.read_excel(excel_file)
df = df.loc[:, ~df.columns.duplicated()]

def assign_block(row):
    team_val = norm_team_name(row.get("NISSAN-BIW Team's", ""))
    for key in TEAM_BLOCKS:
        if team_val == norm_team_name(key):
            return key
    return None

df["__block__"] = df.apply(assign_block, axis=1)

df["__block__"] = df.apply(assign_block, axis=1)

# Initialize session state for floating controls
if 'floating_team_filter' not in st.session_state:
    st.session_state['floating_team_filter'] = ""
if 'floating_member_filter' not in st.session_state:
    st.session_state['floating_member_filter'] = "All"
if 'show_floating_filters' not in st.session_state:
    st.session_state['show_floating_filters'] = False

# Add CSS to hide sidebar completely
st.markdown(
    """
    <style>
    /* Completely hide sidebar */
    .css-1d391kg,
    .css-1aumxhk,
    section[data-testid="stSidebar"],
    .sidebar .sidebar-content {
        display: none !important;
        width: 0 !important;
    }
    
    /* Ensure main content takes full width */
    .block-container {
        max-width: 100% !important;
        padding-left: 1rem !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Default selections for Tab 1 (no floating controls)
selected_team = ""
team_df = df
names = team_df["Name"].fillna(team_df["Name2"]).fillna(team_df["Email"]).tolist()
selected_name = "All"

tab1, tab2 = st.tabs(["🏭 BIW Process Team Overview", "🧑‍💼 Member Wise Analysis"])

# Add loading overlay CSS for smooth transitions
st.markdown(
    """
    <style>
    /* Loading overlay for smooth transitions */
    .stTabs [data-baseweb="tab-panel"] {
        animation: tabContentSlide 0.8s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    @keyframes tabContentSlide {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* Enhanced container animations */
    .element-container {
        animation: containerFadeIn 0.6s ease;
    }
    
    @keyframes containerFadeIn {
    
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Smooth scrolling */
    html {
        scroll-behavior: smooth;
    }
    
    /* Enhanced focus states */
    .stSelectbox > div > div:focus,
    .stSlider:focus-within {
        outline: 2px solid #2196f3;
        outline-offset: 2px;
        border-radius: 8px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ===================== TAB 1 =====================
with tab1:
    # --- PIE CHART: Skill Area Distribution (Tab 1 Top) ---
    import plotly.graph_objects as go
    skill_data = [
        {'Skill': 'Physical project', 'PX': 3, 'PE2': 18, 'M3': 0},
        {'Skill': 'Quality', 'PX': 2, 'PE2': 7, 'M3': 0},
        {'Skill': 'Digital covers/Metal', 'PX': 2, 'PE2': 7, 'M3': 0},
        {'Skill': 'Digital BODY', 'PX': 10, 'PE2': 10, 'M3': 0}
    ]
    pie_labels = [item['Skill'] for item in skill_data]
    pie_text = [f"{item['Skill']}<br>PX:{item['PX']}, PE2:{item['PE2']}" for item in skill_data]
    pie_values = [item["PX"] + item["PE2"] + item["M3"] for item in skill_data]
    pie_colors = ["#4e79a7", "#1de5f3", "#76b7b2", "#59a14f"]  # Changed orange to gold
    pie_fig = go.Figure(data=[go.Pie(
        labels=pie_labels,
        values=pie_values,
        marker=dict(colors=pie_colors),
        hole=0.0,
        text=pie_text,
        textinfo="text",
        textfont=dict(size=18, color="white"),
        pull=[0.01]*len(pie_labels)
    )])
    pie_fig.update_layout(
        title=dict(
            text="-PE Global Headcount -<span style='color:#4e79a9'><b>59</b></span>",
            font=dict(size=38)
        ),
        legend_title="Core Teams",
        legend=dict(font=dict(size=20)),
        height=900
    )
    left_col, right_col = st.columns([1,1])
    with left_col:
        st.plotly_chart(pie_fig)

    # --- 4 Small Pie Charts for Each Team ---
    st.markdown("<h2 style='text-align:left; margin-bottom:1rem;'>Skill Competency</h2>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    # Add custom CSS for uniform button size and background
    st.markdown(
        """
        <style>
        div[data-testid="stButton"] button {
            background-color: #27c47d !important;
            color: white !important;
            min-width: 180px !important;
            min-height: 56px !important;
            font-size: 18px !important;
            border-radius: 16px !important;
            margin: 12px 0 !important;
            box-shadow: 0 8px 2opx rgba(39,196,125,0.15) !important;
            font-weight: 600 !important;
            letter-spacing: 1px !important;
            transition: background 0.2s !important;
            display: inline-block !important;
        }
        div[data-testid="stButton"] button:hover {
            background-color: #1ea76b !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    small_pie_cols = st.columns(4)
    pie_chart_map = [
        {"pie": "Physical project", "buttons": ["PHYSICAL"]},
        {"pie": "Quality", "buttons": ["BOP / PQE", "IWS / QAR"]},
        {"pie": "Digital covers/Metal", "buttons": ["Process - Covers", "Process - Metal", "JIG", "PS"]},
        {"pie": "Digital BODY", "buttons": ["Process - Body", "JIG", "PS"]}
    ]
    radar_trigger = st.session_state.get("radar_trigger", None)
    for i, mapping in enumerate(pie_chart_map):
        team_data = next((item for item in skill_data if item["Skill"] == mapping["pie"]), None)
        if team_data:
            small_labels = [f"PX ({team_data['PX']})", f"PE2 ({team_data['PE2']})"]
            small_values = [team_data['PX'], team_data['PE2']]
            small_colors = ["#4e79a7", "#ffb300"]
            small_pie = go.Figure(data=[go.Pie(
                labels=small_labels,
                values=small_values,
                marker=dict(colors=small_colors),
                hole=0.1,
                textinfo="label",
                textfont=dict(size=16, color="white"),
                pull=[0.01, 0.01]
            )])
            small_pie.update_layout(
                title=dict(text=mapping["pie"], font=dict(size=20)),
                showlegend=False,
                margin=dict(l=10, r=10, t=40, b=10),
                height=400,
                width=300
            )
            small_pie_cols[i].plotly_chart(small_pie)
            # Buttons mapped below each pie chart
            for btn_team in mapping["buttons"]:
                unique_key = f"radar_btn_{mapping['pie'].replace(' ', '_')}_{btn_team.replace(' ', '_')}"
                if small_pie_cols[i].button(btn_team, key=unique_key):
                    st.session_state["radar_trigger"] = btn_team
                    radar_trigger = btn_team

    # Helper: aggregate PX, PE2, M3 and member lists for a group of skills
    def aggregate_group(skills, all_skills):
        px = pe2 = m3 = 0
        px_members = []
        pe2_members = []
        for s in skills:
            skill = next((x for x in all_skills if x["Skill"] == s), None)
            if skill:
                px += skill["PX"]
                pe2 += skill["PE2"]
                m3 += skill["M3"]
                px_members.extend(skill.get("PX_members", []))
                pe2_members.extend(skill.get("PE2_members", []))
        return px, pe2, m3, px_members, pe2_members

    # All original skills for lookup (hardcoded data as requested)
    all_skills = [
        {"Skill": "Simul Process Body", "PX": 5, "PE2": 5, "M3": 0, 
         "PX_members": ["ANANDHAN", "DURGA", "NITHYA SHREE", "SANOFAR NISHA", "VISHAL"],
         "PE2_members": ["ARULMURUGAN", "MANIKANDAN", "Santhosh Kumar", "SARAVANAKUMAR", "PITHA"]},
        {"Skill": "Simul JIG", "PX": 3, "PE2": 1, "M3": 0,
         "PX_members": ["NANDINI", "SHILPA", "VIJAYALAKSHMI"],
         "PE2_members": ["SRINIVASAN"]},
        {"Skill": "Simul PS", "PX": 2, "PE2": 4, "M3": 0,
         "PX_members": ["GAYATHRI", "RAGHURAM"],
         "PE2_members": ["KARTHICK", "PERUMAL", "PREMKUMAR", "PREM KUMAR"]},
        {"Skill": "Simul Process Covers", "PX": 1, "PE2": 6, "M3": 0,
         "PX_members": ["NAMBI NARAYANAN"],
         "PE2_members": ["CHARAN", "POOVARAGAVAN", "SAVAN", "SENTHIL KUMAR", "SHANMUGHA BHARATHI", "PREM KUMAR"]},
        {"Skill": "Simul Process Metal", "PX": 1, "PE2": 1, "M3": 0,
         "PX_members": ["TIPPIL KRISHNA"],
         "PE2_members": ["SURBHI"]},
        {"Skill": "Physical PQE", "PX": 0, "PE2": 4, "M3": 0,
         "PX_members": [],
         "PE2_members": ["LAKSHMANAN", "SENTHIL KUMAR", "Vinothkumar", "BALA SUNDARAM"]},
        {"Skill": "IWS", "PX": 2, "PE2": 3, "M3": 0,
         "PX_members": ["NANDITA ROUT", "SURESH"],
         "PE2_members": ["KISHORE KUMAR", "SRINIVAS", "VIVEK"]},
        {"Skill": "Physical Process", "PX": 2, "PE2": 6, "M3": 0,
         "PX_members": ["AYYANAR", "RAJAMOHAN"],
         "PE2_members": ["GOPI", "KALIYAN", "MARIMUTHU", "PAVEEN PRASANTH", "SAKTHIVEL", "NAGARAJ"]},
        {"Skill": "Physical Quality", "PX": 1, "PE2": 8, "M3": 0,
         "PX_members": ["MURUGAN"],
         "PE2_members": ["ALAN SUDHIV", "ASHOKKUMAR", "Balaji", "HARI PRASAD", "SENTHIL KUMARAN", "VASANTHAKUMAR", "Arokiasamy", "VIGNESH RAJ"]},
        {"Skill": "Physical Project Management", "PX": 0, "PE2": 4, "M3": 0,
         "PX_members": [],
         "PE2_members": ["ANANDAN", "Lokesh Ram", "Martin", "SILAMBARASAN"]},
    ]

    # Calculate big orbital chart data (all combined)
    total_px = sum(skill["PX"] for skill in all_skills)
    total_pe2 = sum(skill["PE2"] for skill in all_skills)
    total_m3 = sum(skill["M3"] for skill in all_skills)
    
    all_px_members = []
    all_pe2_members = []
    for skill in all_skills:
        all_px_members.extend(skill.get("PX_members", []))
        all_pe2_members.extend(skill.get("PE2_members", []))



    # Add section title for the 4 smaller charts

    skill_areas = []
    # Digital BODY
    px, pe2, m3, px_members, pe2_members = aggregate_group([
        "Simul Process Body", "Simul JIG", "Simul PS"
    ], all_skills)
    skill_areas.append({
        "Skill": "Digital BODY",
        "PX": px, "PE2": pe2, "M3": m3,
        "PX_members": px_members, "PE2_members": pe2_members
    })
    
    # Digital covers/Metal
    px, pe2, m3, px_members, pe2_members = aggregate_group([
        "Simul Process Covers", "Simul Process Metal"
    ], all_skills)
    skill_areas.append({
        "Skill": "Digital covers/Metal",
        "PX": px, "PE2": pe2, "M3": m3,
        "PX_members": px_members, "PE2_members": pe2_members
    })
    
    # Quality
    px, pe2, m3, px_members, pe2_members = aggregate_group([
        "Physical PQE", "IWS"
    ], all_skills)
    skill_areas.append({
        "Skill": "Quality",
        "PX": px, "PE2": pe2, "M3": m3,
        "PX_members": px_members, "PE2_members": pe2_members
    })
    
    # Physical project
    px, pe2, m3, px_members, pe2_members = aggregate_group([
        "Physical Process", "Physical Quality", "Physical Project Management"
    ], all_skills)
    skill_areas.append({
        "Skill": "Physical project",
        "PX": px, "PE2": pe2, "M3": m3,
        "PX_members": px_members, "PE2_members": pe2_members
    })


    # Build a DataFrame: rows=teams, cols=activities, values=avg manager rating
    overview_data = {}
    for team, skills in TEAM_BLOCKS.items():
        team_members = df[df["__block__"] == team]
        skill_avgs = []
        for skill in skills:
            ratings = []
            for idx, row in team_members.iterrows():
                employee_id = get_employee_id(row)
                if employee_id:
                    mgr_ratings = load_manager_ratings(employee_id, [skill])
                    ratings.append(mgr_ratings[0])
            avg_skill = round(sum(ratings)/len(ratings), 2) if ratings else 0
            skill_avgs.append(avg_skill)
        overview_data[team] = skill_avgs

    # Create DataFrame for display
    max_skills = max(len(skills) for skills in TEAM_BLOCKS.values())
    columns = [f"Activity {i+1}" for i in range(max_skills)]
    overview_df = pd.DataFrame.from_dict(overview_data, orient='index')
    overview_df.columns = columns[:overview_df.shape[1]]

    # Show metrics for each team (average across all activities)
    # ...existing code...

    if radar_trigger:
        skills = TEAM_BLOCKS[radar_trigger]
        skill_avgs = overview_data[radar_trigger]
        skills_plot = skills + [skills[0]]
        skill_avgs_plot = skill_avgs + [skill_avgs[0]]
        fig_biw_team = go.Figure()
        fig_biw_team.add_trace(go.Scatterpolar(
            r=skill_avgs_plot,
            theta=skills_plot,
            name='Avg Manager Rating (Skill)',
            line=dict(color='purple', width=4),
            mode="lines+markers+text",
            text=[str(v) for v in skill_avgs_plot],
            textfont=dict(color='gray', size=20),
            textposition='top center'
        ))
        fig_biw_team.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 3],
                    tickvals=[0, 1, 2, 3],
                    ticktext=[" ", "PX", "PE2", "       M3"],
                    tickfont=dict(size=18, color='black')
                ),
                angularaxis=dict(
                    tickfont=dict(size=18, color='black'),
                    layer="above traces",
                    rotation=90,
                    direction="clockwise"
                )
            ),
            showlegend=True,
            legend=dict(font=dict(size=20)),
            title=dict(text=f"{radar_trigger} Activity Strength Radar", font=dict(size=22)),
            width=200,
            height=700,
            margin=dict(l=60, r=100, t=60, b=60),
            transition={'duration': 1500, 'easing': 'cubic-in-out'},
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        biw_avg = round(sum(skill_avgs_plot[:-1]) / len(skill_avgs_plot[:-1]), 2) if len(skill_avgs_plot) > 1 else 0
        
        # Enhanced average display with animations
        st.markdown(
            f"""
            <div style="text-align: left; margin: 2rem 0;">
                <div style="background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
                            border-radius: 15px; padding: 15px; display: inline-block;
                            animation: avgGlow 3s ease-in-out infinite alternate;
                            box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
                    <span style="font-size: 1.4rem; color: #495057; font-weight: 600;">
                         Overall Activity Average: <span style="color: #007bff; font-size: 1.6rem;">{biw_avg}/3</span>
                    </span>
                </div>
            </div>
            <style>
            @keyframes avgGlow {{
                from {{ box-shadow: 0 4px 15px rgba(0,123,255,0.2); }}
                to {{ box-shadow: 0 8px 25px rgba(0,123,255,0.4); }}
            }}
            </style>
            """,
            unsafe_allow_html=True
        )
        st.plotly_chart(fig_biw_team, use_container_width=True)

        # --- Automatically show Team Members Strength Radar after activity radar ---
        st.markdown("---")
        # Title hidden as requested
        members = df[df["__block__"] == radar_trigger]
        member_names = members["Name"].fillna(members["Name2"]).fillna(members["Email"]).tolist()
        mgr_avgs = []
        for idx, row in members.iterrows():
            employee_id = get_employee_id(row)
            core_skills = TEAM_BLOCKS[radar_trigger]
            if employee_id:
                mgr_ratings = load_manager_ratings(employee_id, core_skills)
            else:
                mgr_ratings = [0] * len(core_skills)
            avg_mgr = round(sum(mgr_ratings)/len(mgr_ratings), 2) if mgr_ratings else 0
            mgr_avgs.append(avg_mgr)
        member_names += [member_names[0]]
        mgr_avgs += [mgr_avgs[0]]
        fig_member_strength = go.Figure()
        fig_member_strength.add_trace(go.Scatterpolar(
            r=mgr_avgs,
            theta=member_names,
            name='Manager Avg Rating',
            line=dict(color='deepskyblue', width=4),
            mode="lines+markers+text",
            text=[str(v) for v in mgr_avgs],
            textfont=dict(color='gray', size=14),
            textposition='top center'
        ))
        fig_member_strength.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 3],
                    tickvals=[0, 1, 2, 3],
                    ticktext=[" ", "PX", "PE2", "       M3"],
                    tickfont=dict(size=18, color='black')
                ),
                angularaxis=dict(
                    tickfont=dict(size=18, color='black'),
                    layer="above traces",
                    rotation=90,
                    direction="clockwise"
                )
            ),
        showlegend=True,
        legend=dict(font=dict(size=20)),
        title=dict(text=f"{radar_trigger} Members Strength Radar", font=dict(size=20)),
            width=700,
            height=600,
            margin=dict(l=60, r=60, t=60, b=60),
            transition={'duration': 1000}
        )
        
        members_avg = round(sum(mgr_avgs[:-1]) / len(mgr_avgs[:-1]), 2) if len(mgr_avgs) > 1 else 0
    # Team Members Avg line hidden as requested
        st.plotly_chart(fig_member_strength, use_container_width=True)
        
        with st.expander("📊 Manager Average Ratings per Member (out of 3)", expanded=False):
            avg_table = pd.DataFrame({
                "Member": member_names[:-1],
                "Manager Avg Rating": mgr_avgs[:-1]
            })
            st.dataframe(avg_table.style.bar(subset=["Manager Avg Rating"], color='#ffe066'), use_container_width=True)

    # --- Team Members Strength Radar (Manager Ratings Only) ---
    if selected_team and selected_team in TEAM_BLOCKS:
        st.markdown(f"### {selected_team} Members Strength Radar")
        members = df[df["__block__"] == selected_team]
        member_names = members["Name"].fillna(members["Name2"]).fillna(members["Email"]).tolist()
        mgr_avgs = []
        for idx, row in members.iterrows():
            employee_id = get_employee_id(row)
            core_skills = TEAM_BLOCKS[selected_team]
            if employee_id:
                mgr_ratings = load_manager_ratings(employee_id, core_skills)
            else:
                mgr_ratings = [0] * len(core_skills)
            avg_mgr = round(sum(mgr_ratings)/len(mgr_ratings), 2) if mgr_ratings else 0
            mgr_avgs.append(avg_mgr)
        member_names += [member_names[0]]
        mgr_avgs += [mgr_avgs[0]]
        fig_member_strength = go.Figure()
        fig_member_strength.add_trace(go.Scatterpolar(
            r=mgr_avgs,
            theta=member_names,
            name='Manager Avg Rating',
            line=dict(color='deepskyblue', width=4),
            mode="lines+markers+text",
            text=[str(v) for v in mgr_avgs],
            textfont=dict(color='gray', size=14),
            textposition='top center'
        ))
        fig_member_strength.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 3],
                    tickvals=[0, 1, 2, 3],
                    ticktext=[" ", "PX", "PE2", "       M3"],
                    tickfont=dict(size=18, color='black')
                ),
                angularaxis=dict(
                    tickfont=dict(size=18, color='black'),
                    layer="above traces",
                    rotation=90,
                    direction="clockwise"
                )
            ),
            showlegend=True,
            title=dict(text=f"{selected_team} Members Strength Radar (Manager Ratings)", font=dict(size=20)),
            width=700,
            height=600,
            margin=dict(l=60, r=60, t=60, b=60),
            transition={'duration': 1000}
        )
        
        members_avg = round(sum(mgr_avgs[:-1]) / len(mgr_avgs[:-1]), 2) if len(mgr_avgs) > 1 else 0
        st.markdown(f"<span style='font-size:18px; color:gray;'>Team Members Avg: <b>{members_avg}/3</b></span>", unsafe_allow_html=True)
        st.plotly_chart(fig_member_strength, use_container_width=True)
        
        with st.expander("📊 Manager Average Ratings per Member (out of 3)", expanded=False):
            avg_table = pd.DataFrame({
                "Member": member_names[:-1],
                "Manager Avg Rating": mgr_avgs[:-1]
            })
            st.dataframe(avg_table.style.bar(subset=["Manager Avg Rating"], color='#ffe066'), use_container_width=True)
    else:
        st.info("Click a team button above to see both activity strength and members' strength radar.")

# ===================== TAB 2 =====================
with tab2:
    # --- Team Average Metrics (moved from Tab 1) ---
    team_metrics = []
    for team in overview_df.index:
        avg = round(overview_df.loc[team].replace(0, pd.NA).mean(), 2)
        team_metrics.append((team, avg))
    cols = st.columns(len(team_metrics))
    for i, (team, avg) in enumerate(team_metrics):
        cols[i].metric(label=team, value=f"{avg}/3")
    # Team Member Explorer header in black
    st.markdown('<h2 style="color:#000; font-weight:700;">Team Member Explorer</h2>', unsafe_allow_html=True)
    # ...existing code...
    st.markdown(
        """
        <div id="floating-save-button" style="position: fixed; bottom: 20px; right: 2x0px; z-index: 1000;">
            <div style="background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
                        color: white; border-radius: 50px; padding: 12px 18px;
                        box-shadow: 0 4px 15px rgba(40, 167, 69, 0.3);
                        cursor: pointer; transition: all 0.3s ease;
                        backdrop-filter: blur(10px); border: 2px solid rgba(255,255,255,0.2);
                        animation: float 6s ease-in-out infinite;"
                 onclick="this.style.transform='scale(0.95)'; setTimeout(() => this.style.transform='scale(1)', 150);">
                <span style="font-size: 14px; font-weight: 600;">💾 Save Ratings</span>
                <div style="font-size: 10px; opacity: 0.9; margin-top: 2px;">
                    Quick Save
                </div>
            </div>
        </div>
        
        <style>
        @keyframes float {
            0%, 100% { transform: translateY(0px); }
            50% { transform: translateY(-8px); }
        }
        
        #floating-save-button:hover {
            transform: translateY(-3px) scale(1.05);
            box-shadow: 0 8px 25px rgba(40, 167, 69, 0.5);
        }
        
        /* Hide floating controls on mobile */
        @media (max-width: 768px) {
            #floating-save-button { display: none; }
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Simple filter controls without toggle
    st.markdown("### 🎯 Filter Controls")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        team_options = sorted(df["__block__"].dropna().unique())
        selected_team = st.selectbox(
            "🏢 Filter by Team", 
            [""] + team_options,
            index=0 if not st.session_state['floating_team_filter'] else team_options.index(st.session_state['floating_team_filter']) + 1 if st.session_state['floating_team_filter'] in team_options else 0,
            key="floating_team_selectbox"
        )
        st.session_state['floating_team_filter'] = selected_team
    
    with col2:
        if selected_team == "All Teams" or selected_team == "":
            team_df = df
        else:
            team_df = df[df["__block__"] == selected_team]
        
        names = team_df["Name"].fillna(team_df["Name2"]).fillna(team_df["Email"]).tolist()
        selected_name = st.selectbox(
            "👤 Select Employee", 
            ["All"] + names,
            index=0 if st.session_state['floating_member_filter'] == "All" else names.index(st.session_state['floating_member_filter']) + 1 if st.session_state['floating_member_filter'] in names else 0,
            key="floating_member_selectbox"
        )
        st.session_state['floating_member_filter'] = selected_name

    st.markdown(
        f"""
        <div style="text-align: center; margin: 2rem 0;">
            <h2 style="font-size: 2.2rem; background: linear-gradient(135deg, #ff6b35, #f7931e); 
                       -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                       animation: slideInFromRight 1s ease;">
                🧑‍💼 Team Member Explorer ({selected_team})
            </h2>
            <div style="width: 150px; height: 3px; background: linear-gradient(90deg, #ff6b35, #f7931e); 
                        margin: 0 auto; border-radius: 2px; animation: expandWidth 1.5s ease;"></div>
        </div>
        <style>
        @keyframes slideInFromRight {{
            from {{
                opacity: 0;
                transform: translateX(30px);
            }}
            to {{
                opacity: 1;
                transform: translateX(0);
            }}
        }}
        </style>
        """,
        unsafe_allow_html=True
    )
    if 'last_selected_name' not in st.session_state:
        st.session_state['last_selected_name'] = selected_name

    if selected_name != st.session_state['last_selected_name']:
        if st.session_state.get('unsaved_changes', False):
            st.warning("You have unsaved manager ratings. Please save or discard changes before switching employees.")
            st.stop()
        st.session_state['last_selected_name'] = selected_name

    emp_row = None
    core_skills = []
    manager_ratings = []
    general_manager_ratings = []
    employee_id = None
    unsaved_changes = st.session_state.get('unsaved_changes', False)

    if selected_name == "All":
        st.info("Select an employee to rate skills.")
    else:
        emp_row = team_df[team_df["Name"] == selected_name]
        if emp_row.empty:
            emp_row = team_df[team_df["Name2"] == selected_name]
        if emp_row.empty:
            emp_row = team_df[team_df["Email"] == selected_name]
        if not emp_row.empty:
            emp_row = emp_row.iloc[0]
            block = emp_row["__block__"]
            st.markdown(f"### {selected_name}")
            st.markdown(f"**Designation:** {emp_row.get('Designation','')}  \n**Team:** {block}")
            col1, col2 = st.columns(2)
            with col1:
                if block and block in TEAM_BLOCKS:
                    core_skills = TEAM_BLOCKS[block]
                    categories = core_skills.copy()
                    values = [rating_to_num(emp_row.get(skill, "")) for skill in categories]
                    categories += [categories[0]]
                    values += [values[0]]
                    fig = go.Figure()
                    fig.add_trace(go.Scatterpolar(
                        r=values,
                        theta=categories,
                        name=selected_name,
                        line=dict(color='royalblue', width=4),
                        mode="lines+markers+text",
                        text=[str(v) for v in values],
                        textfont=dict(color='gray', size=14),
                        textposition='top center'
                    ))
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 3],
                        tickvals=[0, 1, 2, 3],
                        ticktext=[" ", "PX", "PE2", "       M3"],
                        tickfont=dict(size=18, color='black')
                    ),
                    angularaxis=dict(tickfont=dict(size=18, color='black'))
                ),
                showlegend=False,
                title=dict(text=f"{block} Core Skills", font=dict(size=22)),
                width=600,
                height=500,
                transition={'duration': 1000}
            )
            st.plotly_chart(fig, use_container_width=True)
            with col2:
                categories = GENERAL_SKILLS.copy()
                values = [rating_to_num(emp_row.get(skill, "")) for skill in categories]
                categories += [categories[0]]
                values += [values[0]]
                fig2 = go.Figure()
                fig2.add_trace(go.Scatterpolar(
                    r=values,
                    theta=categories,
                    name=selected_name,
                    line=dict(color='orange', width=4),
                    mode="lines+markers+text",
                    text=[str(v) for v in values],
                    textfont=dict(color='gray', size=14),
                    textposition='top center'
                ))
            fig2.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 3],
                        tickvals=[0, 1, 2, 3],
                        ticktext=[" ", "PX", "PE2", "       M3"],
                        tickfont=dict(size=18, color='black')
                    ),
                    angularaxis=dict(tickfont=dict(size=18, color='black'))
                ),
                showlegend=False,
                title=dict(text="General Skills", font=dict(size=22)),
                width=600,
                height=500,
                transition={'duration': 1000}
            )
            st.plotly_chart(fig2, use_container_width=True)
            data = []
            core_skills = TEAM_BLOCKS.get(block, [])
            for skill in core_skills + GENERAL_SKILLS:
                data.append({
                    "Skill": skill,
                    "Self Rating": rating_to_label(rating_to_num(emp_row.get(skill, "")))
                })
            with st.expander("Skill Details Table", expanded=False):
                st.dataframe(pd.DataFrame(data).style.highlight_max(axis=0, color='#ffe066'))

            # --- Manager Rating Section (Core Skills) ---
            st.markdown(
                """
                <div style="margin: 2rem 0 1rem 0;">
                    <h4 style="font-size: 1.6rem; color: #1976d2; 
                               background: linear-gradient(135deg, rgba(25, 118, 210, 0.1), rgba(33, 150, 243, 0.05));
                               padding: 15px; border-radius: 12px; border-left: 4px solid #2196f3;
                               animation: slideInFromLeft 0.8s ease; position: relative;">
                        👨‍💼 Manager Evaluation (Core Skills)
                        <div style="position: absolute; top: 10px; right: 15px; 
                                   font-size: 1.2rem; animation: rotate 4s linear infinite;">⚙️</div>
                    </h4>
                </div>
                <style>
                @keyframes rotate {
                    from { transform: rotate(0deg); }
                    to { transform: rotate(360deg); }
                }
                </style>
                """,
                unsafe_allow_html=True
            )
            employee_id = get_employee_id(emp_row)
            if employee_id:
                manager_ratings = load_manager_ratings(employee_id, core_skills)
                general_manager_ratings = load_manager_ratings(employee_id, GENERAL_SKILLS)
            else:
                manager_ratings = [0] * len(core_skills)
                general_manager_ratings = [0] * len(GENERAL_SKILLS)

            max_cols = 4
            slider_length = 250

            for i in range(0, len(core_skills), max_cols):
                cols = st.columns(min(max_cols, len(core_skills) - i))
                for j, skill in enumerate(core_skills[i:i+max_cols]):
                    with cols[j]:
                        # Show skill name and description if available
                        st.markdown(f"""
                        <div style='min-height:40px; font-size:18px; color:#2E86AB; font-weight:bold;
                                    background:linear-gradient(135deg, #f0f8ff 0%, #e6f3ff 100%);
                                    padding:12px; border-radius:12px; border-left:4px solid #2E86AB; 
                                    margin-bottom:12px; position:relative; overflow:hidden;
                                    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                                    cursor: pointer; animation: skillSlideIn 0.6s ease {i*0.1}s both;
                                    box-shadow: 0 2px 8px rgba(46, 134, 171, 0.1);'
                             onmouseover='this.style.transform="translateY(-2px) scale(1.02)"; 
                                        this.style.boxShadow="0 8px 25px rgba(46, 134, 171, 0.2)";
                                        this.style.background="linear-gradient(135deg, #e6f3ff 0%, #d1ecf1 100%)";'
                             onmouseout='this.style.transform="translateY(0) scale(1)"; 
                                       this.style.boxShadow="0 2px 8px rgba(46, 134, 171, 0.1)";
                                       this.style.background="linear-gradient(135deg, #f0f8ff 0%, #e6f3ff 100%)";'>
                            <b>{skill}</b>
                            <div style='position:absolute; top:0; left:0; width:100%; height:2px;
                                       background:linear-gradient(90deg, transparent, #2E86AB, transparent);
                                       animation: shimmer 2s ease-in-out infinite;'></div>
                        </div>
                        <style>
                        @keyframes skillSlideIn {{
                            from {{
                                opacity: 0;
                                transform: translateX(-30px);
                            }}
                            to {{
                                opacity: 1;
                                transform: translateX(0);
                            }}
                        }}
                        @keyframes shimmer {{
                            0% {{ transform: translateX(-100%); }}
                            100% {{ transform: translateX(100%); }}
                        }}
                        </style>
                        """, unsafe_allow_html=True)
                        
                        desc = SKILL_DESCRIPTIONS.get(skill, None)
                        if desc:
                            # Make PX, PE2, M3 bold in descriptions
                            desc_bold = desc.replace("PX:", "<b>PX:</b>").replace("PE2:", "<b>PE2:</b>").replace("M3:", "<b>M3:</b>")
                            st.markdown(f"<div style='font-size:13px; color:#555; margin-bottom:4px; white-space:pre-line'>{desc_bold}</div>", unsafe_allow_html=True)
                        
                        # Show self rating for comparison
                        self_rating = rating_to_num(emp_row.get(skill, ""))
                        self_rating_label = rating_to_label(self_rating)
                        st.markdown(f"<div style='font-size:14px; color:#666; margin-bottom:8px; padding:4px; background:#f8f9fa; border-radius:4px;'><b>Self Rating:</b> {self_rating_label} ({self_rating})</div>", unsafe_allow_html=True)
                        val = st.slider(
                            label="",
                            min_value=0,
                            max_value=3,
                            value=manager_ratings[i + j],
                            format="%d",
                            key=f"mgr_slider_{employee_id}_{skill}",
                            label_visibility="collapsed",
                            step=1,
                            help="0=Blank, 1=PX, 2=PE2, 3=M3",
                        )
                        # Add visual label below slider
                        if val == 0:
                            st.markdown("<div style='text-align:center; font-size:12px; color:#666; margin-top:-10px;'>⬜ Blank</div>", unsafe_allow_html=True)
                        elif val == 1:
                            st.markdown("<div style='text-align:center; font-size:12px; color:#666; margin-top:-10px;'>🟨 PX</div>", unsafe_allow_html=True)
                        elif val == 2:
                            st.markdown("<div style='text-align:center; font-size:12px; color:#666; margin-top:-10px;'>🟧 PE2</div>", unsafe_allow_html=True)
                        elif val == 3:
                            st.markdown("<div style='text-align:center; font-size:12px; color:#666; margin-top:-10px;'>🟩 M3</div>", unsafe_allow_html=True)
                        
                        st.markdown(
                            f"""
                            <style>
                            div[data-testid="stSlider"][key="mgr_slider_{employee_id}_{skill}"] {{
                                width: {slider_length}px !important;
                                min-width: {slider_length}px !important;
                                max-width: {slider_length}px !important;
                                background: linear-gradient(90deg, #e0f7fa 0%, #ffe066 100%);
                                border-radius: 8px;
                            }}
                            </style>
                            """,
                            unsafe_allow_html=True,
                        )
                        if val != manager_ratings[i + j]:
                            st.session_state['unsaved_changes'] = True
                        manager_ratings[i + j] = val

            st.markdown(
                """
                <div style="margin: 2rem 0 1rem 0;">
                    <h4 style="font-size: 1.6rem; color: #388e3c; 
                               background: linear-gradient(135deg, rgba(56, 142, 60, 0.1), rgba(76, 175, 80, 0.05));
                               padding: 15px; border-radius: 12px; border-left: 4px solid #4caf50;
                               animation: slideInFromRight 0.8s ease; position: relative;">
                        🌟 Manager Evaluation (General Skills)
                        <div style="position: absolute; top: 10px; right: 15px; 
                                   font-size: 1.2rem; animation: bounce 2s ease infinite;">⭐</div>
                    </h4>
                </div>
                <style>
                @keyframes bounce {
                    0%, 100% { transform: translateY(0); }
                    50% { transform: translateY(-10px); }
                }
                </style>
                """,
                unsafe_allow_html=True
            )
            for i in range(0, len(GENERAL_SKILLS), max_cols):
                cols = st.columns(min(max_cols, len(GENERAL_SKILLS) - i))
                for j, skill in enumerate(GENERAL_SKILLS[i:i+max_cols]):
                    with cols[j]:
                        # Show skill name and description if available
                        st.markdown(f"""
                        <div style='min-height:40px; font-size:18px; color:#A0522D; font-weight:bold;
                                    background:linear-gradient(135deg, #fff8f0 0%, #ffefe6 100%);
                                    padding:12px; border-radius:12px; border-left:4px solid #A0522D; 
                                    margin-bottom:12px; position:relative; overflow:hidden;
                                    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                                    cursor: pointer; animation: skillSlideIn 0.6s ease {i*0.1}s both;
                                    box-shadow: 0 2px 8px rgba(160, 82, 45, 0.1);'
                             onmouseover='this.style.transform="translateY(-2px) scale(1.02)"; 
                                        this.style.boxShadow="0 8px 25px rgba(160, 82, 45, 0.2)";
                                        this.style.background="linear-gradient(135deg, #ffefe6 0%, #fde7d9 100%)";'
                             onmouseout='this.style.transform="translateY(0) scale(1)"; 
                                       this.style.boxShadow="0 2px 8px rgba(160, 82, 45, 0.1)";
                                       this.style.background="linear-gradient(135deg, #fff8f0 0%, #ffefe6 100%)";'>
                            <b>{skill}</b>
                            <div style='position:absolute; top:0; left:0; width:100%; height:2px;
                                       background:linear-gradient(90deg, transparent, #A0522D, transparent);
                                       animation: shimmer 2s ease-in-out infinite;'></div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        desc = SKILL_DESCRIPTIONS.get(skill, None)
                        if desc:
                            # Make PX, PE2, M3 bold in descriptions
                            desc_bold = desc.replace("PX:", "<b>PX:</b>").replace("PE2:", "<b>PE2:</b>").replace("M3:", "<b>M3:</b>")
                            st.markdown(f"<div style='font-size:13px; color:#555; margin-bottom:4px; white-space:pre-line'>{desc_bold}</div>", unsafe_allow_html=True)
                        
                        # Show self rating for comparison
                        self_rating = rating_to_num(emp_row.get(skill, ""))
                        self_rating_label = rating_to_label(self_rating)
                        st.markdown(f"""
                        <div style='font-size:14px; color:#555; margin-bottom:10px; padding:8px 12px; 
                                    background:linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); 
                                    border-radius:8px; border: 1px solid #dee2e6;
                                    position:relative; overflow:hidden;
                                    animation: selfRatingFadeIn 0.8s ease {i*0.05}s both;
                                    transition: all 0.3s ease;'
                             onmouseover='this.style.background="linear-gradient(135deg, #e9ecef 0%, #ffeaa7 100%)";
                                        this.style.transform="scale(1.02)";
                                        this.style.borderColor="#f39c12";'
                             onmouseout='this.style.background="linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%)";
                                       this.style.transform="scale(1)";
                                       this.style.borderColor="#dee2e6";'>
                            <b>Self Rating:</b> {self_rating_label} ({self_rating})
                            <div style='position:absolute; bottom:0; left:0; width:{self_rating*33.33}%; height:2px;
                                       background:linear-gradient(90deg, #f39c12, #e67e22);
                                       animation: progressExpand 1s ease 0.5s both;'></div>
                        </div>
                        """, unsafe_allow_html=True)
                        val = st.slider(
                            label="",
                            min_value=0,
                            max_value=3,
                            value=general_manager_ratings[i + j],
                            format="%d",
                            key=f"mgr_slider_general_{employee_id}_{skill}",
                            label_visibility="collapsed",
                            step=1,
                            help="0=Blank, 1=PX, 2=PE2, 3=M3",
                        )
                        # Add visual label below slider
                        if val == 0:
                            st.markdown("<div style='text-align:center; font-size:12px; color:#666; margin-top:-10px;'>⬜ Blank</div>", unsafe_allow_html=True)
                        elif val == 1:
                            st.markdown("<div style='text-align:center; font-size:12px; color:#666; margin-top:-10px;'>🟨 PX</div>", unsafe_allow_html=True)
                        elif val == 2:
                            st.markdown("<div style='text-align:center; font-size:12px; color:#666; margin-top:-10px;'>🟧 PE2</div>", unsafe_allow_html=True)
                        elif val == 3:
                            st.markdown("<div style='text-align:center; font-size:12px; color:#666; margin-top:-10px;'>🟩 M3</div>", unsafe_allow_html=True)
                        
                        st.markdown(
                            f"""
                            <style>
                            div[data-testid="stSlider"][key="mgr_slider_general_{employee_id}_{skill}"] {{
                                width: {slider_length}px !important;
                                min-width: {slider_length}px !important;
                                max-width: {slider_length}px !important;
                                background: linear-gradient(90deg, #e0f7fa 0%, #ffe066 100%);
                                border-radius: 8px;
                            }}
                            </style>
                            """,
                            unsafe_allow_html=True,
                        )
                        if val != general_manager_ratings[i + j]:
                            st.session_state['unsaved_changes'] = True
                        general_manager_ratings[i + j] = val

            st.markdown("---")
            
            # Enhanced save button with animations
            save_clicked = st.button(
                "💾 Save Manager Ratings", 
                key="save_mgr_bottom",
                help="Save all manager ratings to database"
            )
            
            # Add button styling
            st.markdown(
                """
                <style>
                [data-testid="stButton"] > button {
                    background: linear-gradient(135deg, #28a745 0%, #20c997 100%) !important;
                    color: white !important;
                    border: none !important;
                    border-radius: 12px !important;
                    padding: 15px 30px !important;
                    font-size: 18px !important;
                    font-weight: 600 !important;
                    text-transform: uppercase !important;
                    letter-spacing: 1px !important;
                    box-shadow: 0 8px 15px rgba(40, 167, 69, 0.3) !important;
                    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
                    position: relative !important;
                    overflow: hidden !important;
                }
                
                [data-testid="stButton"] > button:hover {
                    background: linear-gradient(135deg, #20c997 0%, #17a2b8 100%) !important;
                    transform: translateY(-3px) scale(1.05) !important;
                    box-shadow: 0 15px 25px rgba(40, 167, 69, 0.4) !important;
                }
                
                [data-testid="stButton"] > button:active {
                    transform: translateY(-1px) scale(1.02) !important;
                    animation: buttonRipple 0.6s ease !important;
                }
                
                @keyframes buttonRipple {
                    0% { box-shadow: 0 0 0 0 rgba(40, 167, 69, 0.7); }
                    70% { box-shadow: 0 0 0 10px rgba(40, 167, 69, 0); }
                    100% { box-shadow: 0 0 0 0 rgba(40, 167, 69, 0); }
                }
                </style>
                """,
                unsafe_allow_html=True
            )
            
            if save_clicked:
                if employee_id:
                    # Show animated loading state
                    with st.spinner('Saving ratings...'):
                        save_manager_ratings(employee_id, core_skills, manager_ratings)
                        save_manager_ratings(employee_id, GENERAL_SKILLS, general_manager_ratings)
                        st.session_state['unsaved_changes'] = False
                    
                    # Enhanced success message with animations
                    st.markdown(
                        f"""
                        <div style="background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
                                    color: #155724; padding: 15px; border-radius: 12px;
                                    border-left: 5px solid #28a745; margin: 1rem 0;
                                    animation: successSlideIn 0.8s cubic-bezier(0.4, 0, 0.2, 1);
                                    box-shadow: 0 4px 6px rgba(40, 167, 69, 0.1);
                                    position: relative; overflow: hidden;">
                            <div style="display: flex; align-items: center; gap: 10px;">
                                <span style="font-size: 1.5rem; animation: checkmark 1s ease;">✅</span>
                                <div>
                                    <strong>Success!</strong> Manager ratings saved for {selected_name}
                                    <div style="font-size: 0.9rem; opacity: 0.8;">All changes have been stored in the database</div>
                                </div>
                            </div>
                            <div style="position: absolute; top: 0; left: -100%; width: 100%; height: 100%;
                                       background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
                                       animation: shimmerSuccess 2s ease-in-out;"></div>
                        </div>
                        <style>
                        @keyframes successSlideIn {{
                            from {{
                                opacity: 0;
                                transform: translateY(30px) scale(0.9);
                            }}
                            to {{
                                opacity: 1;
                                transform: translateY(0) scale(1);
                            }}
                        }}
                        @keyframes checkmark {{
                            0% {{ transform: scale(0); }}
                            50% {{ transform: scale(1.2); }}
                            100% {{ transform: scale(1); }}
                        }}
                        @keyframes shimmerSuccess {{
                            0% {{ left: -100%; }}
                            100% {{ left: 100%; }}
                        }}
                        </style>
                        """,
                        unsafe_allow_html=True
                    )

            # --- Self, Manager, and Target Radar for Core Skills ---
            categories = core_skills.copy()
            categories += [categories[0]]
            self_values = [rating_to_num(emp_row.get(skill, "")) for skill in core_skills]
            self_values += [self_values[0]]
            mgr_values = manager_ratings + [manager_ratings[0]]

            designation = str(emp_row.get('Designation', '')).strip().lower()
            if 'graduate engineering trainee' in designation:
                target_val = 0
            elif 'engineer' in designation or 'senior engineer' in designation:
                target_val = 1
            elif any(x in designation for x in ['assistant manager', 'deputy manager']):
                target_val = 2
            else:
                target_val = 3
            target_values = [target_val for _ in core_skills]
            target_values += [target_val]

            radar_fig = go.Figure()
            radar_fig.add_trace(go.Scatterpolar(
                r=self_values,
                theta=categories,
                name='Self Rating',
                line=dict(color='royalblue', width=4),
                mode="lines+markers+text",
                text=[str(v) for v in self_values],
                textfont=dict(color='gray', size=14),
                textposition='top center'
            ))
            radar_fig.add_trace(go.Scatterpolar(
                r=mgr_values,
                theta=categories,
                name='Manager Rating',
                line=dict(color='orange', width=4),
                mode="lines+markers+text",
                text=[str(v) for v in mgr_values],
                textfont=dict(color='gray', size=14),
                textposition='top center'
            ))
            radar_fig.add_trace(go.Scatterpolar(
                r=target_values,
                theta=categories,
                name='Target (Designation)',
                line=dict(color='green', dash='dash', width=3),
                mode="lines+markers+text",
                text=[str(v) for v in target_values],
                textfont=dict(color='gray', size=14),
                textposition='top center'
            ))
            radar_fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 3],
                        tickvals=[0, 1, 2, 3],
                        ticktext=[" ", "PX", "PE2", "       M3"],
                        tickfont=dict(size=18, color='black')
                    ),
                    angularaxis=dict(
                        tickfont=dict(size=18, color='black'),
                        layer="above traces",
                        rotation=90,
                        direction="clockwise"
                    )
                ),
                showlegend=True,
                legend=dict(font=dict(size=20)),
                title=dict(text=f"{block} Core Skills: Self vs Manager vs Target", font=dict(size=22)),
                width=1000,
                height=900,
                margin=dict(l=120, r=120, t=100, b=180),
                transition={'duration': 1000}
            )
            
            self_avg = round(sum(self_values[:-1]) / len(self_values[:-1]), 2) if len(self_values) > 1 else 0
            mgr_avg = round(sum(mgr_values[:-1]) / len(mgr_values[:-1]), 2) if len(mgr_values) > 1 else 0
            target_avg = round(sum(target_values[:-1]) / len(target_values[:-1]), 2) if len(target_values) > 1 else 0
            st.markdown(
                f"<span style='font-size:18px; color:gray;'>Self Avg: <b>{self_avg}/3</b> | "
                f"Manager Avg: <b>{mgr_avg}/3</b> | Target Avg: <b>{target_avg}/3</b></span>",
                unsafe_allow_html=True
            )
            st.plotly_chart(radar_fig, use_container_width=True)

            # --- Self, Manager Radar for General Skills (Target as highlight only) ---
            categories = GENERAL_SKILLS.copy()
            categories += [categories[0]]
            self_values = [rating_to_num(emp_row.get(skill, "")) for skill in GENERAL_SKILLS]
            self_values += [self_values[0]]
            mgr_values = general_manager_ratings + [general_manager_ratings[0]]

            radar_fig2 = go.Figure()
            radar_fig2.add_trace(go.Scatterpolar(
                r=self_values,
                theta=categories,
                name='Self Rating',
                line=dict(color='royalblue', width=4),
                mode="lines+markers+text",
                text=[str(v) for v in self_values],
                textfont=dict(color='gray', size=14),
                textposition='top center'
            ))
            radar_fig2.add_trace(go.Scatterpolar(
                r=mgr_values,
                theta=categories,
                name='Manager Rating',
                line=dict(color='orange', width=4),
                mode="lines+markers+text",
                text=[str(v) for v in mgr_values],
                textfont=dict(color='gray', size=14),
                textposition='top center'
            ))
            radar_fig2.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 3],
                        tickvals=[0, 1, 2, 3],
                        ticktext=[" ", "PX", "PE2", "       M3"],
                        tickfont=dict(size=18, color='black')
                    ),
                    angularaxis=dict(
                        tickfont=dict(size=18, color='black'),
                        layer="above traces",
                        rotation=90,
                        direction="clockwise"
                    ),
                    bgcolor="white"
                ),
                shapes=[
                    dict(
                        type="circle",
                        xref="paper", yref="paper",
                        x0=0.5-0.25*target_val/3, y0=0.5-0.25*target_val/3,
                        x1=0.5+0.25*target_val/3, y1=0.5+0.25*target_val/3,
                        line=dict(color="green", width=3, dash="dash"),
                        layer="below"
                    )
                ] if target_val > 0 else [],
                showlegend=True,
                title=dict(text=f"General Skills: Self vs Manager (Target Level Highlighted)", font=dict(size=22)),
                width=1000,
                height=900,
                margin=dict(l=120, r=120, t=100, b=180),
                transition={'duration': 1000}
            )
            self_gen_avg = round(sum(self_values[:-1]) / len(self_values[:-1]), 2) if len(self_values) > 1 else 0
            mgr_gen_avg = round(sum(mgr_values[:-1]) / len(mgr_values[:-1]), 2) if len(mgr_values) > 1 else 0
            st.markdown(
                f"<span style='font-size:18px; color:gray;'>Self Avg: <b>{self_gen_avg}/3</b> | "
                f"Manager Avg: <b>{mgr_gen_avg}/3</b></span>",
                unsafe_allow_html=True
            )
            st.plotly_chart(radar_fig2, use_container_width=True)
        else:
            st.warning("Selected employee not found!")

# =========================
# Big Planet Stacked Bar Chart
# =========================
import matplotlib.pyplot as plt
import numpy as np

def plot_big_planet_stacked_bar_chart(data, categories, planets, title="Big Planet Stacked Bar Chart"):
    """
    Plots a stacked bar chart for the big planet chart.
    data: 2D list or numpy array of shape (len(planets), len(categories))
    categories: list of category names (stacked segments)
    planets: list of planet names (x-axis)
    """
    data = np.array(data)
    ind = np.arange(len(planets))
    bottom = np.zeros(len(planets))
    plt.figure(figsize=(12, 7))
    for i, cat in enumerate(categories):
        plt.bar(ind, data[:, i], bottom=bottom, label=cat)
        bottom += data[:, i]
    plt.xticks(ind, planets, rotation=45, ha='right')
    plt.ylabel('Value')
    plt.title(title)
    plt.legend()
    plt.tight_layout()
    plt.show()

# Example usage (replace with your actual data):

# --- BIW Skill Distribution Horizontal Stacked Bar Chart (BOTTOM OF PAGE) ---

# --- BIW Skill Distribution Horizontal Stacked Bar Chart (TOP OF PAGE) ---
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

