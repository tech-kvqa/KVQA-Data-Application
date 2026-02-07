from flask import Flask, request, jsonify, send_file, abort
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from models import *
from datetime import timedelta
import os
from docxtpl import DocxTemplate, RichText
import pandas as pd
import traceback
import numpy as np
from xml.sax.saxutils import escape
from dotenv import load_dotenv
from functools import wraps
import io
from functools import wraps
import re
from werkzeug.utils import secure_filename
from urllib.parse import quote
import random

load_dotenv()

app = Flask(__name__)
CORS(app, supports_credentials=True,)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    'DATABASE_URL')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=2)

db.init_app(app)
bcrypt.init_app(app)
jwt = JWTManager(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

# EXCEL_FILE = "D:/Anurag/Office/KVQA KAF Data Upload Application/Data1.xlsx"     # path to your Excel file
# SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/1fzYnnOKHt3houEzNolPJKEw9PIKJkvDJbfcmKgUIjQs/export?format=csv&gid=0"     # path to your SPREADSHEET file
TEMPLATE_FILE = "D:/Anurag/Office/KVQA KAF Data Upload Application/backend/templates/template.docx"  # path to your Word template
OUTPUT_DIR = "generated_docs"

os.makedirs(OUTPUT_DIR, exist_ok=True)

def admin_required(fn):
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        if not user or user.role != "admin":
            return {"error": "Admin access required"}, 403
        return fn(*args, **kwargs)
    return wrapper

def seed_initial_admin():
    admins_data = [
        {"username": "admin", "password": "admin123", "role": "admin"},
    ]

    for data in admins_data:
        existing_user = User.query.filter_by(username=data["username"]).first()
        if not existing_user:
            user = User(username=data["username"], role=data["role"])
            user.set_password(data["password"])
            db.session.add(user)

    db.session.commit()
    print("✅ Admin user(s) seeded successfully!")

with app.app_context():
    db.create_all()
    seed_initial_admin()

def read_vertical_excel_as_df(file_path, engine="openpyxl"):
    """
    Reads CSPL + ISMS vertical Excel and returns a DataFrame
    with columns = field names and rows = records.
    
    Assumptions:
    - Column 0 = field names
    - Column 1..N = values for each record
    - Each record can occupy multiple columns (like Excel export)
    """
    import pandas as pd

    # Read Excel without header
    df_raw = pd.read_excel(file_path, engine=engine, header=None, keep_default_na=False)

    # Drop fully empty rows
    df_raw = df_raw.dropna(how="all")

    if df_raw.shape[1] < 2:
        raise ValueError("Excel must have at least two columns (field, value)")

    # Field names in first column
    keys = df_raw.iloc[:, 0].astype(str).str.strip()

    # Values: all remaining columns, transpose if needed
    values = df_raw.iloc[:, 1:]

    # If multiple columns, each column represents a record
    records = []
    for col_idx in range(values.shape[1]):
        record_values = values.iloc[:, col_idx].tolist()
        record = dict(zip(keys, record_values))
        records.append(record)

    df = pd.DataFrame(records)
    # Clean column names
    df.columns = [c.strip().replace(" ", "_") for c in df.columns]

    return df


@app.route('/')
def home():
    return "KVQA KAF Data Entry Application Started"

@app.route("/register", methods=["POST"])
@admin_required
def register():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    role = data.get("role", "user")

    if not username or not password:
        return {"error": "Username and password required"}, 400

    if User.query.filter_by(username=username).first():
        return {"error": "User already exists"}, 400

    new_user = User(username=username)
    new_user.set_password(password)

    db.session.add(new_user)
    db.session.commit()

    return {"message": f"User '{username}' created with role '{role}'"}, 201

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return {"error": "Invalid username or password"}, 401

    access_token = create_access_token(identity=str(user.id))
    return jsonify(access_token=access_token, role=user.role)

@app.route("/protected", methods=["GET"])
@jwt_required()
def protected():
    current_user_id = int(get_jwt_identity())
    user = User.query.get(current_user_id)
    return {"message": f"Hello {user.username}, you are logged in!"}

@app.route("/users", methods=["GET"])
def get_users():
    users = User.query.all()
    return jsonify([{"id": u.id, "username": u.username, "role": u.role} for u in users])

CATEGORY_TEMPLATES = {
    "APL": {
        "QMS": {
            "3_manday": os.path.join(TEMPLATES_DIR, "APL/template1.docx"),
            "6_manday": os.path.join(TEMPLATES_DIR, "APL/template2.docx"),
        },
        "EMS": {
            "4_manday": os.path.join(TEMPLATES_DIR, "APL/ems_4_manday.docx"),
            "6_manday": os.path.join(TEMPLATES_DIR, "APL/ems_6_manday.docx"),
        },
        "OHSMS": {
            "4_manday": os.path.join(TEMPLATES_DIR, "APL/ohsas_4_manday.docx"),
            "6_manday": os.path.join(TEMPLATES_DIR, "APL/ohsas_6_manday.docx"),
        },
        "IMS": {
            "8_manday": os.path.join(TEMPLATES_DIR, "APL/ims_8_manday.docx"),
            "9_manday": os.path.join(TEMPLATES_DIR, "APL/ims_9_manday.docx"),
            "10_manday": os.path.join(TEMPLATES_DIR, "APL/ims_10_manday.docx"),
        }
    }, 
    "CSPL": {
        "QMS": {
            "3_manday": os.path.join(TEMPLATES_DIR, "CSPL/template1.docx"),
            "6_manday": os.path.join(TEMPLATES_DIR, "CSPL/template2.docx"),
        },
        "EMS": {
            "4_manday": os.path.join(TEMPLATES_DIR, "CSPL/ems_4_manday.docx"),
            "6_manday": os.path.join(TEMPLATES_DIR, "CSPL/ems_6_manday.docx"),
        },
        "OHSMS": {
            "4_manday": os.path.join(TEMPLATES_DIR, "CSPL/ohsas_4_manday.docx"),
            "6_manday": os.path.join(TEMPLATES_DIR, "CSPL/ohsas_6_manday.docx"),
        },
        "IMS": {
            "8_manday": os.path.join(TEMPLATES_DIR, "CSPL/ims_8_manday.docx"),
            "9_manday": os.path.join(TEMPLATES_DIR, "CSPL/ims_9_manday.docx"),
            "10_manday": os.path.join(TEMPLATES_DIR, "CSPL/ims_10_manday.docx"),
        },
        "ISMS":{
            "7_manday": os.path.join(TEMPLATES_DIR, "CSPL/isms_7_manday.docx")
        }
    }, 
}

CATEGORY_COLUMNS = {
    "QMS": [
        'S.No', 'Certificate_No', 'Certificate_Issue_Date', 'Surveillance_1_date', 'Surveillance_2_date',
        'certification_audit_conducted', 'Closure_Date', 'Organization_Name', 'Address', 
        'Temp_Address', 'Temp_manday', 'Scope_s', 'Director_Name', 'MR_Name', 'IAF_CODE', 'MANDAY', 
        'stage_1_manday', 'stage_2_manday', 'Surveillance_Manday', 'Risk_Category', 'NO_OF_EMPLOYEE', 
        'audit_number', 'phone_number', 'mail_id', 'Lead_Auditor', 'Auditor', 'Verification_Auditor', 
        'Stage_1_Date', 'stage_1_schedule_date', 'Stage_2_Date', 'stage_2_schedule_date', 'Starting_Date', 
        'manual_date', 'manual_number', 'procedure_number', 'Questionnaire_date', 'Quotation_date', 
        'contract_review_Date', 'quotation_number', 'Internal_Audit_NO', 'Internal_Auditor_name', 
        'Auditor_Qualification', 'Non_conformity', 'Internal_Audit_Date', 'MRM_Date', 'MRM_NO', 
        'MRM_Agenda', 'INTERNAL_ISSUE_NO', 'INTERNAL_ISSUE', 'EXTERNAL_ISSUE', 'interested_parties_NO', 
        'interested_parties', 'PROCESS', 'Key_process', 'objective_NO', 'QUALITY_OBJECTIVE_CO', 
        'legal_REGISTER_NO', 'legal_LICENSE', 'risk_register_NO', 'risk_AND_MITIGATION', 'Planning_the_stage_2'
    ],
    "EMS": [
        'S.No', 'Certificate_No', 'Certificate_Issue_Date', 'Surveillance_1_date', 
        'Surveillance_2_date', 'certification_audit_conducted', 'Closure_Date', 
        'Organization_Name', 'Address', 'Temp_Address', 'Temp_manday', 'Scope_s', 
        'Director_Name', 'MR_Name', 'IAF_CODE', 'MANDAY', 'stage_1_manday', 'stage_2_manday', 
        'Surveillance_Manday', 'Risk_Category', 'NO_OF_EMPLOYEE', 'audit_number', 'phone_number', 
        'mail_id', 'Lead_Auditor', 'Auditor', 'Verification_Auditor', 'Stage_1_Date', 
        'stage_1_schedule_date', 'Stage_2_Date', 'stage_2_schedule_date', 'Starting_Date', 
        'manual_date', 'manual_number', 'procedure_number', 'Questionnaire_date', 'Quotation_date', 
        'contract_review_Date', 'quotation_number', 'Internal_Audit_NO', 'Internal_Auditor_name', 
        'Auditor_Qualification', 'Non_conformity', 'Internal_Audit_Date', 'MRM_Date', 'MRM_NO', 
        'MRM_Agenda', 'INTERNAL_ISSUE_NO', 'INTERNAL_ISSUE', 'EXTERNAL_ISSUE', 'interested_parties_NO', 
        'interested_parties', 'PROCESS', 'Key_process', 'objective_NO', 'EMS_OBJECTIVE', 
        'legal_REGISTER_NO', 'legal_LICENSE', 'risk_register_NO', 'risk_AND_MITIGATION', 
        'ASPECT_IMPACT_NO', 'EMS_ASPECT_IMPACT', 'Planning_the_stage_2'
    ],
    "OHSMS": [
        'S.No', 'Certificate_No', 'Certificate_Issue_Date', 'Surveillance_1_date', 
        'Surveillance_2_date', 'certification_audit_conducted', 'Closure_Date', 
        'Organization_Name', 'Address', 'Temp_Address', 'Temp_manday', 'Scope_s', 'Director_Name', 
        'MR_Name', 'IAF_CODE', 'MANDAY', 'stage_1_manday', 'stage_2_manday', 
        'Surveillance_Manday', 'Risk_Category', 'NO_OF_EMPLOYEE', 'audit_number', 'phone_number', 
        'mail_id', 'Lead_Auditor', 'Auditor', 'Verification_Auditor', 'Stage_1_Date', 
        'stage_1_schedule_date', 'Stage_2_Date', 'stage_2_schedule_date', 'Starting_Date', 
        'manual_date', 'manual_number', 'procedure_number', 'Questionnaire_date', 'Quotation_date', 
        'contract_review_Date', 'quotation_number', 'Internal_Audit_NO', 'Safety_officer_name', 
        'Internal_Auditor_name', 'Auditor_Qualification', 'Non_conformity', 'Internal_Audit_Date', 
        'MRM_Date', 'MRM_NO', 'MRM_Agenda', 'INTERNAL_ISSUE_NO', 'INTERNAL_ISSUE', 'EXTERNAL_ISSUE', 
        'interested_parties_NO', 'interested_parties', 'PROCESS', 'Key_process', 'objective_NO', 
        'OHS_OBJECTIVE', 'legal_REGISTER_NO', 'legal_LICENSE', 'HIRA_NO', 'risk_AND_MITIGATION', 
        'HIRA_Comments', 'Planning_the_stage_2'
    ],
    "IMS": [
        'S.No', 'Certificate_Issue_Date', 'Surveillance_1_date', 'Surveillance_2_date', 
        'certification_audit_conducted', 'Closure_Date', 'Starting_Date', 'manual_date', 
        'Internal_Audit_Date', 'MRM_Date', 'Stage_1_Date', 'stage_1_schedule_date', 'Stage_2_Date', 
        'stage_2_schedule_date', 'Questionnaire_date', 'Quotation_date', 'contract_review_Date', 
        'Certificate_No_QMS', 'Certificate_No_EMS', 'Certificate_No_OHS', 'Organization_Name', 
        'Address', 'Temp_Address', 'Temp_manday', 'Scope_s', 'Director_Name', 'MR_Name', 'IAF_CODE', 
        'manday_calculation', 'MANDAY', 'stage_1_manday', 'stage_2_manday', 'Surveillance_Manday', 
        'Risk_Category', 'NO_OF_EMPLOYEE', 'audit_number', 'phone_number', 'mail_id', 'Lead_Auditor',
        'Auditor', 'Verification_Auditor', 'manual_number', 'procedure_number', 'quotation_number',
        'DR_Name', 'EHS_Manager', 'safety_officer', 'Internal_Auditor_name', 'Auditor_Qualification', 
        'Non_conformity', 'MRM_NO', 'MRM_Agenda', 'INTERNAL_ISSUE_NO', 'INTERNAL_ISSUE', 
        'EXTERNAL_ISSUE', 'interested_parties_NO', 'interested_parties', 'PROCESS', 'Key_process', 
        'IMS_objective_NO', 'IMS_OBJECTIVE', 'legal_REGISTER_NO', 'legal_LICENSE', 'HIRA_NO', 
        'risk_AND_MITIGATION', 'HIRA_Comments', 'ASPECT_IMPACT_NO', 'ASPECT_IMPACT_COMMENT', 
        'Planning_the_stage_2'
    ],
    "ISMS":[
        'S.No', 'Certificate_Issue_Date', 'Surveillance_1_date', 'Surveillance_2_date', 
        'certification_audit_conducted', 'Closure_Date', 'Starting_Date', 'manual_date', 
        'Internal_Audit_Date', 'MRM_Date', 'Stage_1_Date', 'stage_1_schedule_date', 'Stage_2_Date', 
        'stage_2_schedule_date', 'Questionnaire_date', 'Quotation_date', 'contract_review_Date', 
        'Certificate_No', 'Organization_Name', 'Address', 'Certification_Site', 'SOA_Version', 
        'Risk_Assessment_Methodology', 'Risk_Register_Version', 'Scope_s', 'Compliance_manager', 
        'MANDAY', 'stage_1_manday', 'stage_2_manday', 'Risk_Category', 'NO_OF_EMPLOYEE', 'audit_number', 
        'Lead_Auditor', 'Auditor', 'Verification_Auditor'
    ]
}

CATEGORY_CHECKLIST_TEMPLATES = {
    "APL": {
        "QMS": [
            os.path.join(TEMPLATES_DIR, "APL/QMS_checklist.docx"),
            os.path.join(TEMPLATES_DIR, "APL/QMS_checklist_02.docx"),
            os.path.join(TEMPLATES_DIR, "APL/QMS_checklist_03.docx"),
            os.path.join(TEMPLATES_DIR, "APL/QMS_checklist_04.docx"),
            os.path.join(TEMPLATES_DIR, "APL/QMS_checklist_05.docx"),
            os.path.join(TEMPLATES_DIR, "APL/QMS_checklist_06.docx"),
        ],
        "EMS": [
            os.path.join(TEMPLATES_DIR, "APL/EMS_checklist.docx"),
            os.path.join(TEMPLATES_DIR, "APL/EMS_checklist_02.docx"),
            os.path.join(TEMPLATES_DIR, "APL/EMS_checklist_03.docx"),
            os.path.join(TEMPLATES_DIR, "APL/EMS_checklist_04.docx"),
            os.path.join(TEMPLATES_DIR, "APL/EMS_checklist_05.docx"),
            os.path.join(TEMPLATES_DIR, "APL/EMS_checklist_06.docx"),
        ],
        "OHSMS": [
            os.path.join(TEMPLATES_DIR, "APL/OHSMS_checklist.docx"),
            os.path.join(TEMPLATES_DIR, "APL/OHSMS_checklist_02.docx"),
            os.path.join(TEMPLATES_DIR, "APL/OHSMS_checklist_03.docx"),
            os.path.join(TEMPLATES_DIR, "APL/OHSMS_checklist_04.docx"),
            os.path.join(TEMPLATES_DIR, "APL/OHSMS_checklist_05.docx"),
            os.path.join(TEMPLATES_DIR, "APL/OHSMS_checklist_06.docx"),
        ],
        "IMS": [
            os.path.join(TEMPLATES_DIR, "APL/IMS_checklist.docx"),
            os.path.join(TEMPLATES_DIR, "APL/IMS_checklist_02.docx"),
            os.path.join(TEMPLATES_DIR, "APL/IMS_checklist_03.docx")
        ],
    },
    "CSPL": {
        "QMS": [
            os.path.join(TEMPLATES_DIR, "CSPL/QMS_checklist.docx"),
            os.path.join(TEMPLATES_DIR, "CSPL/QMS_checklist_02.docx"),
            os.path.join(TEMPLATES_DIR, "CSPL/QMS_checklist_03.docx"),
            os.path.join(TEMPLATES_DIR, "CSPL/QMS_checklist_04.docx"),
            os.path.join(TEMPLATES_DIR, "CSPL/QMS_checklist_05.docx"),
            os.path.join(TEMPLATES_DIR, "CSPL/QMS_checklist_06.docx"),
        ],
        "EMS": [
            os.path.join(TEMPLATES_DIR, "CSPL/EMS_checklist.docx"),
            os.path.join(TEMPLATES_DIR, "CSPL/EMS_checklist_02.docx"),
            os.path.join(TEMPLATES_DIR, "CSPL/EMS_checklist_03.docx"),
            os.path.join(TEMPLATES_DIR, "CSPL/EMS_checklist_04.docx"),
            os.path.join(TEMPLATES_DIR, "CSPL/EMS_checklist_05.docx"),
            os.path.join(TEMPLATES_DIR, "CSPL/EMS_checklist_06.docx"),
        ],
        "OHSMS": [
            os.path.join(TEMPLATES_DIR, "CSPL/OHSMS_checklist.docx"),
            os.path.join(TEMPLATES_DIR, "CSPL/OHSMS_checklist_02.docx"),
            os.path.join(TEMPLATES_DIR, "CSPL/OHSMS_checklist_03.docx"),
            os.path.join(TEMPLATES_DIR, "CSPL/OHSMS_checklist_04.docx"),
            os.path.join(TEMPLATES_DIR, "CSPL/OHSMS_checklist_05.docx"),
            os.path.join(TEMPLATES_DIR, "CSPL/OHSMS_checklist_06.docx"),
        ],
        "IMS": [
            os.path.join(TEMPLATES_DIR, "CSPL/IMS_checklist.docx"),
            os.path.join(TEMPLATES_DIR, "CSPL/IMS_checklist_02.docx"),
            os.path.join(TEMPLATES_DIR, "CSPL/IMS_checklist_03.docx")
        ],
    },
}

def make_browser_safe_filename(org_name, category):
    org_name = org_name.strip()
    org_name_safe = re.sub(r'[^\w]', '_', org_name)
    org_name_safe = re.sub(r'_+', '_', org_name_safe)
    org_name_safe = org_name_safe.strip('_')
    category_upper = category.lower()
    full_name = f"{org_name_safe}-{category_upper}.docx"
    print("Safe Full Filename:", full_name)
    return full_name


@app.route("/generate-docx/<int:file_id>/<int:row_id>", methods=["GET"])
@jwt_required()
def generate_docx(file_id, row_id):
    try:
        current_user_id = int(get_jwt_identity())

        user_file = UserFile.query.filter_by(
            id=file_id,
            user_id=current_user_id,
            source_type="uploaded"
        ).first()

        if not user_file:
            return jsonify({"error": "File not found or access denied"}), 404

        category = user_file.category
        company = request.args.get("company", user_file.company).upper()
        manday_key = request.args.get("template_type")

        if company not in CATEGORY_TEMPLATES:
            return jsonify({"error": f"Invalid company: {company}"}), 400

        if category not in CATEGORY_TEMPLATES[company]:
            return jsonify({"error": f"No templates for {company} - {category}"}), 400

        template_file = CATEGORY_TEMPLATES[company][category].get(manday_key)
        if not template_file or not os.path.exists(template_file):
            return jsonify({"error": f"No template for {company} - {category} - {manday_key}"}), 400

        ext = user_file.file_path.lower().split(".")[-1]
        if ext in ["xlsm", "xlsx"]:
            df = pd.read_excel(user_file.file_path, engine="openpyxl")
        elif ext == "xls":
            df = pd.read_excel(user_file.file_path, engine="xlrd")
        elif ext == "csv":
            try:
                df = pd.read_csv(user_file.file_path, encoding="utf-8")
            except:
                df = pd.read_csv(user_file.file_path, encoding="latin1")
        else:
            return jsonify({"error": f"Unsupported file type: {ext}"}), 400

        df.columns = [c.strip().replace(" ", "_").replace("/", "_") for c in df.columns]
        df.reset_index(inplace=True)
        df.rename(columns={"index": "id"}, inplace=True)
        df["id"] = df["id"] + 1

        row = df[df["id"] == row_id].to_dict(orient="records")
        if not row:
            return jsonify({"error": "Row not found"}), 404

        row_data = row[0]

        for k, v in row_data.items():

            if isinstance(v, (pd.Timestamp, datetime)):
                row_data[k] = v.strftime("%d-%m-%Y")

            elif isinstance(v, str):
                row_data[k] = (
                    v.replace("&", "&amp;")
                    .replace("<", "&lt;")
                    .replace(">", "&gt;")
                )

            elif pd.isna(v):
                row_data[k] = ""

        doc = DocxTemplate(template_file)
        doc.render(row_data)

        org_name = row_data.get("Organization_Name", f"record_{file_id}_{row_id}")
        org_name_safe = re.sub(r'[^\w]', '_', org_name).strip("_")
        file_name_safe = f"{org_name_safe}-{category.lower()}.docx"
        output_path = os.path.join(OUTPUT_DIR, file_name_safe)

        doc.save(output_path)

        with open(output_path, "rb") as f:
            new_doc = GeneratedDoc(
                row_id=row_id,
                file_name=file_name_safe,
                file_data=f.read(),
                user_id=current_user_id,
                category=category,
                company=company 
            )
        db.session.add(new_doc)

        generated_file = UserFile(
            user_id=current_user_id,
            file_name=file_name_safe,
            file_path=output_path,
            source_type="generated",
            category=category,
            company=company
        )
        db.session.add(generated_file)

        db.session.commit()

        return send_file(
            output_path,
            as_attachment=True,
            download_name=file_name_safe,
            mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

    except Exception as e:
        db.session.rollback()
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
    
@app.route("/generate-docx-isms/<int:file_id>", methods=["GET"])
@jwt_required()
def generate_docx_isms(file_id):
    """
    Generates DOCX from vertical ISMS Excel.
    Frontend passes ?col_id=1 (Column B), 2 (Column C), etc.
    """
    try:
        current_user_id = int(get_jwt_identity())

        # Fetch uploaded ISMS Excel
        user_file = UserFile.query.filter_by(
            id=file_id,
            user_id=current_user_id,
            category="ISMS",
            company="CSPL",
            source_type="uploaded"
        ).first()

        if not user_file or not os.path.exists(user_file.file_path):
            return jsonify({"error": "ISMS file not found or missing"}), 404

        # Load ISMS template
        isms_templates = CATEGORY_TEMPLATES.get("CSPL", {}).get("ISMS", {})
        if not isms_templates:
            return jsonify({"error": "No ISMS templates configured"}), 400

        template_path = list(isms_templates.values())[0]
        if not os.path.exists(template_path):
            return jsonify({"error": "ISMS template file missing"}), 400

        # Read Excel (vertical format)
        ext = user_file.file_path.lower().split(".")[-1]
        engine = "openpyxl" if ext in ["xlsx", "xlsm"] else None
        df_raw = pd.read_excel(user_file.file_path, engine=engine, header=None, keep_default_na=False)

        if df_raw.empty or df_raw.shape[1] < 2:
            return jsonify({"error": "Excel contains no data"}), 400

        # Determine column to generate
        col_id = int(request.args.get("col_id", 1))  # Column B = 1
        if col_id <= 0 or col_id >= df_raw.shape[1]:
            return jsonify({"error": "Invalid col_id"}), 400

        # Column A = field names, Column col_id = values
        field_names = df_raw.iloc[:, 0].astype(str).str.strip()
        values = df_raw.iloc[:, col_id]

        # Build dictionary for DOCX
        clean_data = {}
        for key, val in zip(field_names, values):
            key_safe = re.sub(r"[^\w]", "_", key)
            if isinstance(val, (pd.Timestamp, datetime)):
                clean_data[key_safe] = val.strftime("%d-%m-%Y")
            elif pd.isna(val):
                clean_data[key_safe] = ""
            else:
                clean_data[key_safe] = str(val)

        # Render DOCX
        doc = DocxTemplate(template_path)
        doc.render(clean_data)

        # Save output
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        org_name = clean_data.get("Organization_Name", f"ISMS_Record_{col_id}")
        safe_org = re.sub(r"[^\w]", "_", org_name)
        output_name = f"{safe_org}.docx"
        output_path = os.path.join(OUTPUT_DIR, output_name)
        doc.save(output_path)

        # Store in DB
        with open(output_path, "rb") as f:
            gen_doc = GeneratedDoc(
                row_id=col_id,
                file_name=output_name,
                file_data=f.read(),
                user_id=current_user_id,
                category="ISMS",
                company="CSPL"
            )
            db.session.add(gen_doc)

        db.session.add(UserFile(
            user_id=current_user_id,
            file_name=output_name,
            file_path=output_path,
            source_type="generated",
            category="ISMS",
            company="CSPL"
        ))

        db.session.commit()

        # Send file
        response = send_file(
            output_path,
            as_attachment=True,
            download_name=output_name,
            mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
        response.headers["Access-Control-Expose-Headers"] = "Content-Disposition"
        return response

    except Exception as e:
        db.session.rollback()
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

    
# @app.route("/upload-file", methods=["POST"])
# @jwt_required()
# def upload_file():
#     try:
#         current_user_id = int(get_jwt_identity())

#         if "file" not in request.files:
#             return {"error": "No file uploaded"}, 400

#         file = request.files["file"]
#         if file.filename == "":
#             return {"error": "No file selected"}, 400

#         category = request.form.get("category")
#         company = request.form.get("company", "").upper()
#         print("Company:", company)
#         print("Category:", category)

#         if not category:
#             return {"error": "Category is required"}, 400

#         if company not in CATEGORY_TEMPLATES:
#             return {"error": f"Invalid company: {company}"}, 400

#         user_dir = os.path.join("uploads", str(current_user_id))
#         os.makedirs(user_dir, exist_ok=True)
#         file_path = os.path.join(user_dir, file.filename)
#         file.save(file_path)

#         ext = file.filename.lower().split(".")[-1]

#         if ext in ["xlsm", "xlsx", "xls"]:
#             df = pd.read_excel(file_path, engine="openpyxl")
#         elif ext == "csv":
#             try:
#                 df = pd.read_csv(file_path, encoding="utf-8")
#             except UnicodeDecodeError:
#                 df = pd.read_csv(file_path, encoding="latin1")
#         else:
#             return {"error": f"Unsupported file format: {ext}"}, 400

#         df.columns = [c.strip().replace(" ", "_").replace("/", "_") for c in df.columns]

#         required_cols = CATEGORY_COLUMNS.get(category, [])
#         missing = [col for col in required_cols if col not in df.columns]
#         if missing:
#             return {
#                 "error": f"Uploaded file does not match expected format for {category}. Missing: {missing}"
#             }, 400

#         user_file = UserFile(
#             user_id=current_user_id,
#             file_name=file.filename,
#             file_path=file_path,
#             source_type="uploaded",
#             category=category,
#             company=company
#         )
#         db.session.add(user_file)
#         db.session.commit()

#         return {"message": "File uploaded successfully", "file_id": user_file.id}

#     except Exception as e:
#         db.session.rollback()
#         return {"error": str(e)}, 500


@app.route("/upload-file", methods=["POST"])
@jwt_required()
def upload_file():
    try:
        current_user_id = int(get_jwt_identity())

        # ----------------------------
        # Basic validations
        # ----------------------------
        if "file" not in request.files:
            return {"error": "No file uploaded"}, 400

        file = request.files["file"]
        if file.filename == "":
            return {"error": "No file selected"}, 400

        category = request.form.get("category")
        company = request.form.get("company", "").upper()

        if not category:
            return {"error": "Category is required"}, 400

        if company not in CATEGORY_TEMPLATES:
            return {"error": f"Invalid company: {company}"}, 400

        # ----------------------------
        # Detect vertical ISMS format
        # ----------------------------
        is_vertical_isms = (category.upper() == "ISMS" and company == "CSPL")

        # ----------------------------
        # Save uploaded file
        # ----------------------------
        user_dir = os.path.join("uploads", str(current_user_id))
        os.makedirs(user_dir, exist_ok=True)

        file_path = os.path.join(user_dir, file.filename)
        file.save(file_path)

        ext = file.filename.lower().split(".")[-1]

        # ----------------------------
        # Read file
        # ----------------------------
        if ext in ["xls", "xlsx", "xlsm"]:
            if is_vertical_isms:
                # 🔴 Vertical ISMS → NO HEADER
                df = pd.read_excel(file_path, engine="openpyxl", header=None)
            else:
                # 🟢 Normal horizontal
                df = pd.read_excel(file_path, engine="openpyxl")

        elif ext == "csv":
            if is_vertical_isms:
                return {"error": "ISMS vertical format supports Excel only"}, 400

            try:
                df = pd.read_csv(file_path, encoding="utf-8")
            except UnicodeDecodeError:
                df = pd.read_csv(file_path, encoding="latin1")

        else:
            return {"error": f"Unsupported file format: {ext}"}, 400

        # ----------------------------
        # Column normalization (ONLY for horizontal files)
        # ----------------------------
        if not is_vertical_isms:
            df.columns = [
                str(c).strip().replace(" ", "_").replace("/", "_")
                for c in df.columns
            ]

        # ----------------------------
        # Validate structure
        # ----------------------------
        if is_vertical_isms:
            # Basic sanity check for vertical format
            if df.shape[1] < 2:
                return {
                    "error": "Invalid ISMS format. Expected two columns (Field, Value)."
                }, 400
        else:
            # Horizontal category validation
            required_cols = CATEGORY_COLUMNS.get(category, [])
            missing = [col for col in required_cols if col not in df.columns]
            if missing:
                return {
                    "error": f"Uploaded file does not match expected format for {category}. "
                             f"Missing columns: {missing}"
                }, 400

        # ----------------------------
        # Save DB record
        # ----------------------------
        user_file = UserFile(
            user_id=current_user_id,
            file_name=file.filename,
            file_path=file_path,
            source_type="uploaded",
            category=category,
            company=company
        )

        db.session.add(user_file)
        db.session.commit()

        return {
            "message": "File uploaded successfully",
            "file_id": user_file.id
        }

    except Exception as e:
        db.session.rollback()
        traceback.print_exc()
        return {"error": str(e)}, 500


@app.route("/my-files", methods=["GET"])
@jwt_required()
def my_files():
    current_user_id = int(get_jwt_identity())
    files = UserFile.query.filter_by(user_id=current_user_id).all()
    return jsonify([
        {
            "id": f.id,
            "file_name": f.file_name,
            "uploaded_at": f.uploaded_at.strftime("%Y-%m-%d %H:%M:%S"),
            "source_type": f.source_type
        } for f in files
    ])

# @app.route("/excel-rows/<int:file_id>", methods=["GET"])
# @jwt_required()
# def get_excel_rows(file_id):
#     try:
#         current_user_id = int(get_jwt_identity())
#         user_file = UserFile.query.filter_by(id=file_id, user_id=current_user_id).first()
#         if not user_file:
#             return {"error": "File not found or access denied"}, 404

#         ext = user_file.file_path.lower().split(".")[-1]

#         if ext in ["xlsm", "xlsx"]:
#             xl = pd.ExcelFile(user_file.file_path, engine="openpyxl")
#         elif ext == "xls":
#             xl = pd.ExcelFile(user_file.file_path, engine="xlrd")
#         elif ext == "csv":
#             df_master = pd.read_csv(user_file.file_path)
#         else:
#             return {"error": f"Unsupported file type: {ext}"}, 400

#         category = user_file.category.upper()
#         sheet_name_map = {
#             "QMS": "QMS 2025",
#             "EMS": "EMS 2025",
#             "OHSMS": "OHSMS 2025",
#             "IMS": "IMS 2025"
#         }
#         df_master = xl.parse(sheet_name_map.get(category, xl.sheet_names[0]))
#         df_master.columns = [c.strip().replace(" ", "_").replace("/", "_") for c in df_master.columns]

#         checklist_sheets = [s for s in xl.sheet_names if category in s and "Checklist" in s]

#         if checklist_sheets:
#             df_checklist = xl.parse(checklist_sheets[0])
#             df_checklist.columns = [c.strip().replace(" ", "_").replace("/", "_") for c in df_checklist.columns]

#             if category == "IMS" and "Certificate_No_QMS" in df_checklist.columns:
#                 df_checklist["Certificate_No"] = df_checklist["Certificate_No_QMS"].astype(str).str.strip().str.upper()
#             elif "Certificate_No" in df_checklist.columns:
#                 df_checklist["Certificate_No"] = df_checklist["Certificate_No"].astype(str).str.strip().str.upper()

#             checklist_certs = set(df_checklist["Certificate_No"].tolist())
#         else:
#             checklist_certs = set()

#         df_master.reset_index(inplace=True)
#         df_master.rename(columns={"index": "id"}, inplace=True)
#         df_master["id"] = df_master["id"] + 1

#         if category == "IMS":
#             cert_col = "Certificate_No_QMS" if "Certificate_No_QMS" in df_master.columns else None
#         else:
#             cert_col = "Certificate_No" if "Certificate_No" in df_master.columns else None

#         if cert_col:
#             df_master["Certificate_No"] = (
#                 df_master[cert_col].astype(str).str.strip().str.upper()
#             )
#         else:
#             df_master["Certificate_No"] = None

#         df_master["ChecklistAvailable"] = df_master["Certificate_No"].apply(lambda x: x in checklist_certs)

#         generated_rows = {
#             g.row_id
#             for g in GeneratedDoc.query.filter_by(
#                 user_id=current_user_id,
#                 category=user_file.category,
#                 company=user_file.company   # NEW ✔
#             ).all()
#         }

#         df_master["Status"] = df_master["id"].apply(lambda x: "Generated" if x in generated_rows else "Pending")

#         generated_checklists = {
#             c.row_id
#             for c in ChecklistDoc.query.filter_by(
#                 user_id=current_user_id,
#                 category=user_file.category,
#                 company=user_file.company
#             ).all()
#         }
        
#         df_master["ChecklistGenerated"] = df_master["id"].apply(lambda x: x in generated_checklists)

#         df_master = df_master.replace({np.nan: None, np.inf: None, -np.inf: None})

#         return jsonify(df_master.to_dict(orient="records"))

#     except Exception as e:
#         return {"error": str(e)}, 500

@app.route("/excel-rows/<int:file_id>", methods=["GET"])
@jwt_required()
def get_excel_rows(file_id):
    try:
        current_user_id = int(get_jwt_identity())
        user_file = UserFile.query.filter_by(id=file_id, user_id=current_user_id).first()
        if not user_file:
            return {"error": "File not found or access denied"}, 404

        ext = user_file.file_path.lower().split(".")[-1]

        if ext in ["xlsm", "xlsx"]:
            xl = pd.ExcelFile(user_file.file_path, engine="openpyxl")
        elif ext == "xls":
            xl = pd.ExcelFile(user_file.file_path, engine="xlrd")
        elif ext == "csv":
            df_master = pd.read_csv(user_file.file_path)
        else:
            return {"error": f"Unsupported file type: {ext}"}, 400

        # --- Load master sheet ---
        # category = user_file.category.upper()
        # sheet_name_map = {
        #     "QMS": "QMS 2025",
        #     "EMS": "EMS 2025",
        #     "OHSMS": "OHSMS 2025",
        #     "IMS": "IMS 2025"
        # }
        # df_master = xl.parse(sheet_name_map.get(category, xl.sheet_names[0]))

        category = user_file.category.upper()
        company = user_file.company.upper()

        # 🔴 SPECIAL CASE: CSPL + ISMS (vertical)
        if company == "CSPL" and category == "ISMS":
            df_master = read_vertical_excel_as_df(
                user_file.file_path,
                engine="openpyxl"
            )

        else:
            sheet_name_map = {
                "QMS": "QMS 2025",
                "EMS": "EMS 2025",
                "OHSMS": "OHSMS 2025",
                "IMS": "IMS 2025"
            }

            df_master = xl.parse(sheet_name_map.get(category, xl.sheet_names[0]))
            df_master.columns = [c.strip().replace(" ", "_").replace("/", "_") for c in df_master.columns]

        # --- Load checklist sheet ---
        checklist_sheets = [s for s in xl.sheet_names if category in s and "Checklist" in s]
        # if checklist_sheets:
        #     df_checklist = xl.parse(checklist_sheets[0])
        #     df_checklist.columns = [c.strip().replace(" ", "_").replace("/", "_") for c in df_checklist.columns]
        #     # Normalize Certificate_No
        #     if "Certificate_No" in df_checklist.columns:
        #         df_checklist["Certificate_No"] = df_checklist["Certificate_No"].astype(str).str.strip().str.upper()
        #     checklist_certs = set(df_checklist["Certificate_No"].tolist())
        # else:
        #     checklist_certs = set()

        if checklist_sheets:
            df_checklist = xl.parse(checklist_sheets[0])
            df_checklist.columns = [c.strip().replace(" ", "_").replace("/", "_") for c in df_checklist.columns]

            # For IMS, map Certificate_No_QMS
            if category == "IMS" and "Certificate_No_QMS" in df_checklist.columns:
                df_checklist["Certificate_No"] = df_checklist["Certificate_No_QMS"].astype(str).str.strip().str.upper()
            elif "Certificate_No" in df_checklist.columns:
                df_checklist["Certificate_No"] = df_checklist["Certificate_No"].astype(str).str.strip().str.upper()

            checklist_certs = set(df_checklist["Certificate_No"].tolist())
        else:
            checklist_certs = set()

        # --- Prepare master rows ---
        df_master.reset_index(inplace=True)
        df_master.rename(columns={"index": "id"}, inplace=True)
        df_master["id"] = df_master["id"] + 1

        # if "Certificate_No" in df_master.columns:
        #     df_master["Certificate_No"] = df_master["Certificate_No"].astype(str).str.strip().str.upper()

        if category == "IMS":
            cert_col = "Certificate_No_QMS" if "Certificate_No_QMS" in df_master.columns else None
        else:
            cert_col = "Certificate_No" if "Certificate_No" in df_master.columns else None

        if cert_col:
            df_master["Certificate_No"] = (
                df_master[cert_col].astype(str).str.strip().str.upper()
            )
        else:
            df_master["Certificate_No"] = None

        # Mark rows for which checklist exists
        df_master["ChecklistAvailable"] = df_master["Certificate_No"].apply(lambda x: x in checklist_certs)

        # Mark rows already generated
        # generated_rows = {
        #     g.row_id
        #     for g in GeneratedDoc.query.filter_by(user_id=current_user_id, category=user_file.category).all()
        # }

        generated_rows = {
            g.row_id
            for g in GeneratedDoc.query.filter_by(
                user_id=current_user_id,
                category=user_file.category,
                company=user_file.company   # NEW ✔
            ).all()
        }

        df_master["Status"] = df_master["id"].apply(lambda x: "Generated" if x in generated_rows else "Pending")

        # generated_checklists = {
        #     c.row_id
        #     for c in ChecklistDoc.query.filter_by(user_id=current_user_id, category=user_file.category).all()
        # }

        generated_checklists = {
            c.row_id
            for c in ChecklistDoc.query.filter_by(
                user_id=current_user_id,
                category=user_file.category,
                company=user_file.company   # NEW ✔
            ).all()
        }
        
        df_master["ChecklistGenerated"] = df_master["id"].apply(lambda x: x in generated_checklists)

        df_master = df_master.replace({np.nan: None, np.inf: None, -np.inf: None})

        return jsonify(df_master.to_dict(orient="records"))

    except Exception as e:
        return {"error": str(e)}, 500


@app.route("/generated-docs", methods=["GET"])
@jwt_required()
def get_generated_docs():
    current_user_id = int(get_jwt_identity())
    category = request.args.get("category", None)
    company = request.args.get("company")

    query = GeneratedDoc.query.filter_by(user_id=current_user_id)

    if category:
        query = query.filter(
            db.func.lower(db.func.trim(GeneratedDoc.category)) == category.strip().lower()
        )

    if company:
        query = query.filter(
            db.func.lower(db.func.trim(GeneratedDoc.company)) == company.strip().lower()
        )

    docs = query.order_by(GeneratedDoc.created_at.desc()).all()

    return jsonify([
        {
            "id": d.id,
            "row_id": d.row_id,
            "file_name": d.file_name,
            "category": d.category,
            "company": d.company,
            "created_at": d.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "source": "GeneratedDoc"
        } for d in docs
    ])

@app.route("/download-generated-file/<file_name>", methods=["GET"])
@jwt_required()
def download_generated_file(file_name):
    current_user_id = int(get_jwt_identity())
    doc = GeneratedDoc.query.filter_by(file_name=file_name, user_id=current_user_id).first()
    if not doc:
        return {"error": "File not found or access denied"}, 404

    return send_file(
        io.BytesIO(doc.file_data),
        as_attachment=True,
        download_name=doc.file_name,
        mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )


@app.route("/init-db")
def init_db():
    try:
        db.create_all()
        return {"message": "Database initialized successfully!"}
    except Exception as e:
        return {"error": str(e)}, 500

## Admin Routes

@app.route("/admin/all-files", methods=["GET"])
@admin_required
def admin_all_files():
    files = UserFile.query.all()
    return jsonify([
        {
            "id": f.id,
            "username": f.user.username,
            "file_name": f.file_name,
            "category": f.category,
            "uploaded_at": f.uploaded_at.strftime("%Y-%m-%d %H:%M:%S"),
            "source_type": f.source_type
        } for f in files
    ])

@app.route("/admin/generated-docs", methods=["GET"])
@admin_required
def admin_generated_docs():
    docs = GeneratedDoc.query.order_by(GeneratedDoc.created_at.desc()).all()
    return jsonify([
        {
            "id": d.id,
            "username": d.user.username,
            "row_id": d.row_id,
            "file_name": d.file_name,
            "category": d.category,
            "created_at": d.created_at.strftime("%Y-%m-%d %H:%M:%S")
        } for d in docs
    ])

@app.route("/create-initial-admin", methods=["POST"])
def create_initial_admin():
    if User.query.filter_by(role="admin").first():
        return {"error": "Admin already exists"}, 400

    data = request.json
    username = data.get("username", "admin")
    password = data.get("password", "admin123")

    admin = User(username=username, role="admin")
    admin.set_password(password)

    db.session.add(admin)
    db.session.commit()

    return {"message": f"Initial admin '{username}' created"}, 201

@app.route("/admin/files", methods=["GET"])
@jwt_required()
def get_all_files():
    current_user_id = int(get_jwt_identity())
    user = User.query.get(current_user_id)

    if not user or user.role != "admin":
        return {"error": "Unauthorized"}, 403

    user_id = request.args.get("user_id")
    files_data = []

    if user_id:
        generated_files = GeneratedDoc.query.filter_by(user_id=user_id).all()
    else:
        generated_files = GeneratedDoc.query.all()

    for g in generated_files:
        files_data.append({
            "id": g.id,
            "file_name": g.file_name,
            "category": g.category,
            "uploaded_at": g.created_at,
            "user": g.user.username,
            "source": "generated"
        })

    return {"files": files_data}, 200

@app.route("/download/<string:source>/<int:file_id>", methods=["GET"])
@jwt_required()
def download_file(source, file_id):
    current_user_id = int(get_jwt_identity())
    user = User.query.get(current_user_id)

    if not user or user.role != "admin":
        return {"error": "Unauthorized"}, 403

    if source == "uploaded":
        file = UserFile.query.get(file_id)
        if not file:
            return abort(404, "File not found")

        if not file.file_path or not os.path.exists(file.file_path):
            return abort(404, "File path not valid")

        return send_file(
            file.file_path,
            as_attachment=True,
            download_name=file.file_name
        )

    elif source == "generated":
        file = GeneratedDoc.query.get(file_id)
        if not file:
            return abort(404, "File not found")

        return send_file(
            io.BytesIO(file.file_data),
            as_attachment=True,
            download_name=file.file_name,
            mimetype="application/octet-stream"
        )

    else:
        return abort(400, "Invalid source")

@app.route("/all-generated-docs", methods=["GET"])
def get_all_generated_docs():
    docs = GeneratedDoc.query.all()
    return jsonify([
        {
            "id": d.id,
            "row_id": d.row_id,
            "file_name": d.file_name,
            "created_at": d.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "category": d.category
        } for d in docs
    ])

########################################## CHECKLIST CODE  ###########################################

@app.route("/generate-checklist/<int:file_id>/<int:row_id>", methods=["GET"])
@jwt_required()
def generate_checklist(file_id, row_id):
    try:
        current_user_id = int(get_jwt_identity())

        user_file = UserFile.query.filter_by(
            id=file_id,
            user_id=current_user_id,
            source_type="uploaded"
        ).first()
        if not user_file:
            return jsonify({"error": "File not found or access denied"}), 404

        category = user_file.category.upper()
        company = request.args.get("company", user_file.company).upper()

        if company not in CATEGORY_CHECKLIST_TEMPLATES:
            return jsonify({"error": f"Invalid company: {company}"}), 400

        if category not in CATEGORY_CHECKLIST_TEMPLATES[company]:
            return jsonify({"error": f"No checklist templates for {company} - {category}"}), 400

        template_candidates = CATEGORY_CHECKLIST_TEMPLATES[company][category]

        if not template_candidates:
            return jsonify({"error": f"No checklist templates found for {company}-{category}"}), 400

        template_file = random.choice(template_candidates)

        if not os.path.exists(template_file):
            return jsonify({"error": f"Template file not found: {template_file}"}), 400

        ext = user_file.file_path.lower().split(".")[-1]

        if ext in ["xlsm", "xlsx"]:
            xl = pd.ExcelFile(user_file.file_path, engine="openpyxl")
        elif ext == "xls":
            xl = pd.ExcelFile(user_file.file_path, engine="xlrd")
        elif ext == "csv":
            return jsonify({"error": "Checklist generation not supported for CSV"}), 400
        else:
            return jsonify({"error": f"Unsupported file type: {ext}"}), 400

        print("Sheets found in Excel:", xl.sheet_names)

        sheet_name_map = {
            "QMS": "QMS 2025",
            "EMS": "EMS 2025",
            "OHSMS": "OHSMS 2025",
            "IMS": "IMS 2025",
        }

        main_sheet = sheet_name_map.get(category)

        if main_sheet not in xl.sheet_names:
            return jsonify({"error": f"Master sheet '{main_sheet}' not found"}), 400

        df_master = xl.parse(main_sheet)
        df_master.columns = [c.strip().replace(" ", "_").replace("/", "_") for c in df_master.columns]

        sheet_candidates = [s for s in xl.sheet_names if category in s and "Checklist" in s]

        if not sheet_candidates:
            return jsonify({"error": f"No checklist sheet found for {category}"}), 404

        df_checklist = xl.parse(sheet_candidates[0])
        df_checklist.columns = [c.strip().replace(" ", "_").replace("/", "_") for c in df_checklist.columns]

        master_row = df_master.reset_index()
        master_row.rename(columns={"index": "id"}, inplace=True)
        master_row["id"] = master_row["id"] + 1

        selected_row = master_row[master_row["id"] == row_id].to_dict(orient="records")

        if not selected_row:
            return jsonify({"error": "Row not found in master sheet"}), 404

        master_data = selected_row[0]

        match_column = "Certificate_No_QMS" if category == "IMS" else "Certificate_No"
        certificate_no = master_data.get(match_column)

        if not certificate_no or str(certificate_no).strip().lower() in ["", "none", "null"]:
            return jsonify({"error": f"No valid {match_column} found for row"}), 400

        if match_column not in df_checklist.columns:
            return jsonify({"error": f"Checklist missing required column {match_column}"}), 400

        checklist_row = df_checklist[df_checklist[match_column] == certificate_no].to_dict(orient="records")

        if not checklist_row:
            return jsonify({"error": f"No checklist entry for {match_column} = {certificate_no}"}), 404

        row_data = checklist_row[0]

        context = {**master_data, **row_data}

        for k, v in context.items():
            if isinstance(v, pd.Timestamp):
                context[k] = v.strftime("%d-%m-%Y")
            elif pd.isna(v) or str(v).strip().lower() == "null":
                context[k] = "NA"
            elif isinstance(v, str):
                context[k] = v.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

        doc = DocxTemplate(template_file)
        doc.render(context)

        org_name = context.get("Organization_Name", f"record_{file_id}_{row_id}")
        org_name_safe = re.sub(r"[^\w]", "_", org_name).strip("_")

        file_name_safe = f"{org_name_safe}_{category}_checklist.docx"
        output_path = os.path.join(OUTPUT_DIR, file_name_safe)

        doc.save(output_path)

        with open(output_path, "rb") as f:
            new_record = ChecklistDoc(
                row_id=row_id,
                file_name=file_name_safe,
                file_data=f.read(),
                user_id=current_user_id,
                category=category,
                company=company
            )
            db.session.add(new_record)

        generated_file = UserFile(
            user_id=current_user_id,
            file_name=file_name_safe,
            file_path=output_path,
            source_type="generated",
            category=category,
            company=company
        )
        db.session.add(generated_file)

        db.session.commit()

        return send_file(output_path, as_attachment=True, download_name=file_name_safe)

    except Exception as e:
        traceback.print_exc()
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route("/delete-generated/<string:category>/<int:row_id>", methods=["DELETE"])
@jwt_required()
def delete_generated_doc(category, row_id):
    try:
        current_user_id = int(get_jwt_identity())
        category = category.upper()

        docs = GeneratedDoc.query.filter_by(row_id=row_id, user_id=current_user_id, category=category).all()
        if not docs:
            return jsonify({"error": "Generated document not found"}), 404

        for doc in docs:
            file_path = os.path.join(OUTPUT_DIR, doc.file_name)
            if os.path.exists(file_path):
                os.remove(file_path)
            db.session.delete(doc)

        db.session.commit()
        return jsonify({"message": f"Deleted generated doc(s) for row {row_id}, category {category}"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@app.route("/delete-checklist/<string:category>/<int:row_id>", methods=["DELETE"])
@jwt_required()
def delete_checklist(category, row_id):
    try:
        current_user_id = int(get_jwt_identity())
        category = category.upper()

        checklist_docs = ChecklistDoc.query.filter_by(
            row_id=row_id, user_id=current_user_id, category=category
        ).all()

        if not checklist_docs:
            return jsonify({"error": "Checklist document not found"}), 404

        for doc in checklist_docs:
            file_path = os.path.join(OUTPUT_DIR, doc.file_name)
            if os.path.exists(file_path):
                os.remove(file_path)
            db.session.delete(doc)

        db.session.commit()
        return jsonify({"message": f"Deleted checklist(s) for row {row_id}, category {category}"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route("/generated-checklists", methods=["GET"])
@jwt_required()
def get_generated_checklists():
    current_user_id = int(get_jwt_identity())

    category = request.args.get("category", None)
    company = request.args.get("company", None)

    query = ChecklistDoc.query.filter_by(user_id=current_user_id)

    if category:
        query = query.filter(
            db.func.lower(db.func.trim(ChecklistDoc.category)) == category.strip().lower()
        )

    if company:
        query = query.filter(
            db.func.lower(db.func.trim(ChecklistDoc.company)) == company.strip().lower()
        )

    docs = query.order_by(ChecklistDoc.created_at.desc()).all()

    return jsonify([
        {
            "id": d.id,
            "row_id": d.row_id,
            "file_name": d.file_name,
            "category": d.category,
            "company": d.company,
            "created_at": d.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "source": "ChecklistDoc"
        } for d in docs
    ])

@app.route("/download-checklist-file/<file_name>", methods=["GET"])
@jwt_required()
def download_checklist_file(file_name):
    current_user_id = int(get_jwt_identity())
    doc = ChecklistDoc.query.filter_by(file_name=file_name, user_id=current_user_id).first()
    if not doc:
        return {"error": "File not found or access denied"}, 404

    return send_file(
        io.BytesIO(doc.file_data),
        as_attachment=True,
        download_name=doc.file_name,
        mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )

if __name__ == "__main__":
    app.run(debug=True)