# ==========================================================
# To start this dashboard, just click "Deploy" on Streamlit Cloud!
# ==========================================================

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import re
import unicodedata
import sqlite3
import os
import numpy as np

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
    "New Skill up for future business shift", "TQM ", "Japanese Training", "Strategical Planning"
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
    /* Main background with animated gradient */
    .main {
        background: linear-gradient(-45deg, #e3ffe8, #f7faff, #e8f5ff, #ffe8f5);
        background-size: 400% 400%;
        animation: gradientShift 15s ease infinite;
    }
    
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Enhanced metrics with hover effects */
    .stMetric {
        background: linear-gradient(135deg, #e0f7fa 0%, #b2ebf2 100%) !important;
        border-radius: 15px !important;
        border: 2px solid transparent !important;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1) !important;
        transform: translateY(0) !important;
    }
    
    .stMetric:hover {
        transform: translateY(-5px) scale(1.02) !important;
        box-shadow: 0 12px 25px rgba(0, 0, 0, 0.15) !important;
        border: 2px solid #00bcd4 !important;
        background: linear-gradient(135deg, #b2ebf2 0%, #4dd0e1 100%) !important;
    }
    
    /* Plotly charts with enhanced animations */
    .stPlotlyChart {
        animation: chartSlideUp 1.2s cubic-bezier(0.4, 0, 0.2, 1);
        transition: transform 0.3s ease;
    }
    
    .stPlotlyChart:hover {
        transform: scale(1.01);
    }
    
    @keyframes chartSlideUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* Tab enhancement with animations */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 8px;
        backdrop-filter: blur(10px);
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 60px;
        border-radius: 12px;
        padding: 0 24px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        background: rgba(255, 255, 255, 0.7);
        border: 2px solid transparent;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: linear-gradient(135deg, #81c784 0%, #4caf50 100%);
        transform: translateY(-2px);
        border: 2px solid #388e3c;
        box-shadow: 0 8px 15px rgba(76, 175, 80, 0.3);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #2196f3 0%, #1976d2 100%) !important;
        color: white !important;
        transform: translateY(-3px) !important;
        box-shadow: 0 10px 20px rgba(33, 150, 243, 0.4) !important;
    }
    
    /* Button animations */
    .stButton > button {
        background: linear-gradient(135deg, #64b5f6 0%, #2196f3 100%);
        border: none;
        border-radius: 12px;
        padding: 12px 24px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 6px rgba(33, 150, 243, 0.3);
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #2196f3 0%, #1565c0 100%);
        transform: translateY(-2px) scale(1.05);
        box-shadow: 0 8px 15px rgba(33, 150, 243, 0.4);
    }
    
    .stButton > button:active {
        transform: translateY(0) scale(0.98);
    }
    
    /* Selectbox animations */
    .stSelectbox > div > div {
        border-radius: 12px;
        border: 2px solid #e3f2fd;
        transition: all 0.3s ease;
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
    }
    
    .stSelectbox > div > div:focus-within {
        border-color: #2196f3;
        box-shadow: 0 0 0 3px rgba(33, 150,243, 0.1);
        transform: scale(1.02);
    }
    
    /* Slim slider with white background */
    .stSlider > div > div > div {
        background: white !important;
        border-radius: 4px !important;
        height: 4px !important;
        border: 1px solid #e0e0e0 !important;
    }
    
    /* Slider track styling */
    .stSlider [data-baseweb="slider"] > div {
        background: white !important;
        height: 4px !important;
        border-radius: 4px !important;
    }
    
    /* Slider thumb/handle styling */
    .stSlider [role="slider"] {
        background: #2196f3 !important;
        border: 2px solid white !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2) !important;
        width: 16px !important;
        height: 16px !important;
    }
    
    /* Remove ONLY slider text background colors */
    .stSlider div[data-testid="stTickBar"] div,
    .stSlider div[data-testid="stTickBar"] span,
    .stSlider [role="slider"] + div,
    .stSlider [role="slider"] ~ div,
    .stSlider .stMarkdown,
    .stSlider .stMarkdown > div,
    .stSlider .stMarkdown p {
        background: transparent !important;
        background-color: transparent !important;
    }
    
    /* Target specific slider label elements only */
    .stSlider div[style*="background-color"]:not([role="slider"]) {
        background: transparent !important;
        background-color: transparent !important;
    }
    
    /* Remove background from slider value display only */
    .stSlider [data-testid="stSliderTickBarMin"],
    .stSlider [data-testid="stSliderTickBarMax"] {
        background: transparent !important;
        background-color: transparent !important;
    }
    
    /* File uploader styling */
    .stFileUploader > div {
        border: 2px dashed #4caf50;
        border-radius: 15px;
        background: linear-gradient(135deg, #f1f8e9 0%, #e8f5e8 100%);
        transition: all 0.3s ease;
    }
    
    .stFileUploader > div:hover {
        border-color: #2e7d32;
        background: linear-gradient(135deg, #e8f5e8 0%, #c8e6c9 100%);
        transform: scale(1.02);
    }
    
    /* Title animation */
    h1 {
        background: linear-gradient(135deg, #1976d2, #2196f3, #4caf50, #ff9800);
        background-size: 300% 300%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: titleGradient 8s ease infinite;
        text-align: center;
        font-weight: 700;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    @keyframes titleGradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Subheader animations */
    h2, h3 {
        animation: slideInFromLeft 0.8s ease;
        position: relative;
    }
    
    h2::after, h3::after {
        content: '';
        position: absolute;
        bottom: -5px;
        left: 0;
        width: 0;
        height: 3px;
        background: linear-gradient(90deg, #2196f3, #4caf50);
        animation: underlineExpand 1.5s ease forwards;
    }
    
    @keyframes slideInFromLeft {
        from {
            opacity: 0;
            transform: translateX(-30px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes underlineExpand {
        to {
            width: 100px;
        }
    }
    
    /* DataFrame styling */
    .dataframe {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        animation: tableSlideIn 1s ease;
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
    
    /* Expander enhancements */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
        border-radius: 12px;
        transition: all 0.3s ease;
        border: 2px solid transparent;
    }
    
    .streamlit-expanderHeader:hover {
        background: linear-gradient(135deg, #bbdefb 0%, #90caf9 100%);
        transform: scale(1.02);
        border: 2px solid #2196f3;
        box-shadow: 0 4px 8px rgba(33, 150, 243, 0.2);
    }
    
    /* Progress indicators */
    .stProgress > div > div {
        background: linear-gradient(90deg, #4caf50 0%, #8bc34a 100%);
        border-radius: 10px;
        animation: progressGlow 2s ease infinite alternate;
    }
    
    @keyframes progressGlow {
        from {
            box-shadow: 0 0 5px rgba(76, 175, 80, 0.5);
        }
        to {
            box-shadow: 0 0 15px rgba(76, 175, 80, 0.8);
        }
    }
    
    /* Loading animation for components */
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
    
    .loading {
        animation: pulse 1.5s ease-in-out infinite;
    }
    
    /* Floating elements */
    @keyframes float {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
        100% { transform: translateY(0px); }
    }
    
    .floating {
        animation: float 6s ease-in-out infinite;
    }
    
    /* Info/success/warning message enhancements */
    .stAlert {
        border-radius: 12px;
        border-left: 5px solid;
        animation: alertSlideIn 0.5s ease;
        backdrop-filter: blur(5px);
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
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #2196f3, #4caf50);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #1976d2, #388e3c);
    }
    
    /* Title and content animations */
    @keyframes titleBounce {
        0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
        40% { transform: translateY(-10px); }
        60% { transform: translateY(-5px); }
    }
    
    @keyframes progressBar {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    </style>
    """,
    unsafe_allow_html=True
)
st.markdown(
    """
    <div style="text-align: center; margin-bottom: 2rem;">
        <h1 style="font-size: 3rem; margin-bottom: 0.5rem; animation: titleBounce 2s ease;">
            🏭 RNTBCI-PE BIW Skill Matrix Dashboard
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
    st.markdown(
        """
        <div style="text-align: center; margin: 2rem 0;">
            <h2 style="font-size: 2.5rem; background: linear-gradient(135deg, #1976d2, #4caf50); 
                       -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                       animation: slideInFromLeft 1s ease, textGlow 3s ease infinite alternate;">
                🏭 BIW Process Team Strength Analytics
            </h2>
            <div style="width: 200px; height: 3px; background: linear-gradient(90deg, #2196f3, #4caf50); 
                        margin: 0 auto; border-radius: 2px; animation: expandWidth 1.5s ease;"></div>
        </div>
        <style>
        @keyframes textGlow {
            from { filter: drop-shadow(0 0 5px rgba(25, 118, 210, 0.5)); }
            to { filter: drop-shadow(0 0 15px rgba(76, 175, 80, 0.8)); }
        }
        @keyframes expandWidth {
            from { width: 0; }
            to { width: 200px; }
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # --- 4 Team Pie Charts (First Block) ---
    
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

    skill_areas = []
    # Digital BODY
    px, pe2, m3, px_members, pe2_members = aggregate_group([
        "Simul Process Body", "Simul JIG", "Simul PS"
    ], all_skills)
    skill_areas.append({
        "Skill": "Digital BODY",
        "PX": px, "PE2": pe2, "M3": m3
    })
    
    # Digital covers/Metal
    px, pe2, m3, px_members, pe2_members = aggregate_group([
        "Simul Process Covers", "Simul Process Metal"
    ], all_skills)
    skill_areas.append({
        "Skill": "Digital covers/Metal",
        "PX": px, "PE2": pe2, "M3": m3
    })
    
    # Quality
    px, pe2, m3, px_members, pe2_members = aggregate_group([
        "Physical PQE", "IWS"
    ], all_skills)
    skill_areas.append({
        "Skill": "Quality",
        "PX": px, "PE2": pe2, "M3": m3
    })
    
    # Physical project
    px, pe2, m3, px_members, pe2_members = aggregate_group([
        "Physical Process", "Physical Quality", "Physical Project Management"
    ], all_skills)
    skill_areas.append({
        "Skill": "Physical project",
        "PX": px, "PE2": pe2, "M3": m3
    })

    # Create 4 orbit charts in a row
    import numpy as np
    cols = st.columns(4)
    
    # Orbit chart parameters
    px_radius = 2
    pe2_radius = 3.8
    m3_radius = 5
    
    for idx, skill in enumerate(skill_areas):
        fig_orbit = go.Figure()
        
        # Draw PX orbit (innermost)
        if skill["PX"] > 0:
            theta = np.linspace(0, 2 * np.pi, skill["PX"], endpoint=False)
            x_px = px_radius * np.cos(theta)
            y_px = px_radius * np.sin(theta)
            px_members = skill.get("PX_members", [])
            hover_px = []
            for j in range(skill["PX"]):
                if j < len(px_members):
                    hover_px.append(f"<b>{px_members[j]}</b><br>Skill Area: {skill['Skill']}<br>Level: PX (Basic)")
                else:
                    hover_px.append(f"<b>{skill['Skill']}</b><br>Level: PX<br>Index: {j+1}")
            fig_orbit.add_trace(go.Scatter(
                x=x_px, y=y_px,
                mode="markers",
                marker=dict(size=12, color="#b2dfdb", line=dict(width=2, color="#0097a7")),
                name="PX",
                showlegend=False,
                hoverinfo="text",
                hovertext=hover_px
            ))
        
        # Draw PE2 orbit (middle)
        if skill["PE2"] > 0:
            theta = np.linspace(0, 2 * np.pi, skill["PE2"], endpoint=False)
            x_pe2 = pe2_radius * np.cos(theta)
            y_pe2 = pe2_radius * np.sin(theta)
            pe2_members = skill.get("PE2_members", [])
            hover_pe2 = []
            for j in range(skill["PE2"]):
                if j < len(pe2_members):
                    hover_pe2.append(f"<b>{pe2_members[j]}</b><br>Skill Area: {skill['Skill']}<br>Level: PE2 (Intermediate)")
                else:
                    hover_pe2.append(f"<b>{skill['Skill']}</b><br>Level: PE2<br>Index: {j+1}")
            fig_orbit.add_trace(go.Scatter(
                x=x_pe2, y=y_pe2,
                mode="markers",
                marker=dict(size=10, color="#ffd54f", line=dict(width=2, color="#ff6f00")),
                name="PE2",
                showlegend=False,
                hoverinfo="text",
                hovertext=hover_pe2
            ))
        
        # Draw M3 orbit (outer)
        if skill["M3"] > 0:
            theta = np.linspace(0, 2 * np.pi, skill["M3"], endpoint=False)
            x_m3 = m3_radius * np.cos(theta)
            y_m3 = m3_radius * np.sin(theta)
            m3_members = skill.get("M3_members", [])
            hover_m3 = []
            for j in range(skill["M3"]):
                if j < len(m3_members):
                    hover_m3.append(f"<b>{m3_members[j]}</b><br>Skill Area: {skill['Skill']}<br>Level: M3 (Expert)")
                else:
                    hover_m3.append(f"<b>{skill['Skill']}</b><br>Level: M3<br>Index: {j+1}")
            fig_orbit.add_trace(go.Scatter(
                x=x_m3, y=y_m3,
                mode="markers",
                marker=dict(size=10, color="#ff8a80", line=dict(width=2, color="#b71c1c")),
                name="M3",
                showlegend=False,
                hoverinfo="text",
                hovertext=hover_m3
            ))

        # Add visible grey orbit lines as circles
        circle_shapes = []
        circle_radii = [px_radius, pe2_radius, m3_radius]
        for r in circle_radii:
            circle_shapes.append(dict(
                type="circle",
                xref="x", yref="y",
                x0=-r, y0=-r, x1=r, y1=r,
                line=dict(color="#bbb", width=2, dash="dot"),
                layer="below"
            ))

        # Add PX, PE2, M3 labels on the corresponding circles
        angle_rad = np.deg2rad(30)
        cos30 = np.cos(angle_rad)
        sin30 = np.sin(angle_rad)
        circle_labels = [
            dict(x=px_radius * cos30, y=px_radius * sin30, xref="x", yref="y", text="PX", showarrow=False, font=dict(size=10, color="#bbb"),
                 xanchor="left", yanchor="bottom"),
            dict(x=pe2_radius * cos30, y=pe2_radius * sin30, xref="x", yref="y", text="PE2", showarrow=False, font=dict(size=10, color="#bbb"),
                 xanchor="left", yanchor="bottom"),
            dict(x=m3_radius * cos30, y=m3_radius * sin30, xref="x", yref="y", text="M3", showarrow=False, font=dict(size=10, color="#bbb"),
                 xanchor="left", yanchor="bottom")
        ]
        
        overlay_text = (
            f"<span style='font-size:14px; color:#4a148c;'><b>PX:</b> {skill['PX']} <b>PE2:</b> {skill['PE2']} <b>M3:</b> {skill['M3']}</span>"
        )
        
        fig_orbit.update_layout(
            title=dict(
                text=f"<b>{skill['Skill']}</b>",
                font=dict(size=16),
                x=0.5,
                xanchor="center",
            ),
            xaxis=dict(visible=False, autorange=True, scaleanchor="y", scaleratio=1),
            yaxis=dict(visible=False, autorange=True, scaleanchor="x", scaleratio=1),
            showlegend=False,
            width=300,
            height=300,
            margin=dict(l=10, r=10, t=40, b=40),
            plot_bgcolor='#fff',
            paper_bgcolor='#fff',
            shapes=circle_shapes,
            annotations=circle_labels + [
                dict(
                    x=0, y=-6, xref="x", yref="y",
                    text=overlay_text,
                    showarrow=False,
                    align="center",
                    xanchor="center",
                    yanchor="top",
                    font=dict(size=12, color="#4a148c"),
                    opacity=1,
                )
            ]
        )
        
        with cols[idx]:
            st.plotly_chart(
                fig_orbit,
                use_container_width=True,
                key=f"orbit_chart_{idx}",
                config={"displayModeBar": False}
            )

    st.markdown("---")

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
    st.markdown(
        """
        <div style="margin: 1.5rem 0;">
            <h4 style="font-size: 1.5rem; color: #1976d2; text-align: center;
                       animation: bounceIn 1s ease; position: relative;">
                📊 Team Average Strengths
                <span style="position: absolute; top: -5px; right: -10px; font-size: 0.8rem; 
                             animation: pulse 2s ease infinite;">✨</span>
            </h4>
        </div>
        <style>
        @keyframes bounceIn {
            0% { transform: scale(0.3); opacity: 0; }
            50% { transform: scale(1.05); }
            70% { transform: scale(0.9); }
            100% { transform: scale(1); opacity: 1; }
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    team_metrics = []
    for team in overview_df.index:
        avg = round(overview_df.loc[team].replace(0, pd.NA).mean(), 2)
        team_metrics.append((team, avg))
    cols = st.columns(len(team_metrics))
    for i, (team, avg) in enumerate(team_metrics):
        cols[i].metric(label=team, value=f"{avg}/3")

    # Show interactive activity strength graph for selected team
    st.markdown(
        """
        <div style="margin: 1.5rem 0;">
            <h4 style="font-size: 1.5rem; color: #388e3c; text-align: center;
                       animation: fadeInScale 1.2s ease; position: relative;">
                🎯 Click a Team for Detailed Activity Strength Radar
                <div style="position: absolute; top: -8px; left: 50%; transform: translateX(-50%);
                           width: 6px; height: 6px; background: #4caf50; border-radius: 50%;
                           animation: ping 2s cubic-bezier(0, 0, 0.2, 1) infinite;"></div>
            </h4>
        </div>
        <style>
        @keyframes fadeInScale {
            from { opacity: 0; transform: scale(0.8) translateY(20px); }
            to { opacity: 1; transform: scale(1) translateY(0); }
        }
        @keyframes ping {
            75%, 100% {
                transform: translateX(-50%) scale(2);
                opacity: 0;
            }
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    team_buttons = st.columns(len(TEAM_BLOCKS))
    radar_trigger = st.session_state.get("radar_trigger", None)
    for i, team in enumerate(TEAM_BLOCKS.keys()):
        if team_buttons[i].button(team, key=f"radar_btn_{team}"):
            st.session_state["radar_trigger"] = team
            radar_trigger = team

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
            textfont=dict(color='gray', size=14),
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
            title=dict(text=f"{radar_trigger} Activity Strength Radar (Manager Ratings)", font=dict(size=22)),
            width=900,
            height=700,
            margin=dict(l=60, r=60, t=60, b=60),
            transition={'duration': 1500, 'easing': 'cubic-in-out'},
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        biw_avg = round(sum(skill_avgs_plot[:-1]) / len(skill_avgs_plot[:-1]), 2) if len(skill_avgs_plot) > 1 else 0
        
        # Enhanced average display with animations
        st.markdown(
            f"""
            <div style="text-align: center; margin: 1rem 0;">
                <div style="background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
                            border-radius: 15px; padding: 15px; display: inline-block;
                            animation: avgGlow 3s ease-in-out infinite alternate;
                            box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
                    <span style="font-size: 1.4rem; color: #495057; font-weight: 600;">
                        📊 Overall Activity Average: <span style="color: #007bff; font-size: 1.6rem;">{biw_avg}/3</span>
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
        st.markdown(f"### {radar_trigger} Members Strength Radar")
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
            title=dict(text=f"{radar_trigger} Members Strength Radar (Manager Ratings)", font=dict(size=20)),
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
    # Create floating save button - Tab 2 only
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