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

# app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.db"
# app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# app.config["SQLALCHEMY_SECRET_KEY"] = "anuragiitmadras"

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    'DATABASE_URL')  # Use full URL from Render
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

    # return {"message": "User registered successfully"}, 201
    return {"message": f"User '{username}' created with role '{role}'"}, 201


# ---------- Login ----------
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return {"error": "Invalid username or password"}, 401

    # create JWT token with string identity
    access_token = create_access_token(identity=str(user.id))
    return jsonify(access_token=access_token, role=user.role)


# ---------- Protected Example ----------
# @app.route("/protected", methods=["GET"])
# @jwt_required()
# def protected():
#     current_user_id = get_jwt_identity()
#     user = User.query.get(current_user_id)
#     return {"message": f"Hello {user.username}, you are logged in!"}

@app.route("/protected", methods=["GET"])
@jwt_required()
def protected():
    current_user_id = int(get_jwt_identity())
    user = User.query.get(current_user_id)
    return {"message": f"Hello {user.username}, you are logged in!"}



# ---------- Get All Users (Optional Admin Route) ----------
@app.route("/users", methods=["GET"])
def get_users():
    users = User.query.all()
    return jsonify([{"id": u.id, "username": u.username, "role": u.role} for u in users])

# ---------- Get Excel Rows ----------
# @app.route("/excel-rows", methods=["GET"])
# @jwt_required()
# def get_excel_rows():
#     try:
#         # df = pd.read_excel(EXCEL_FILE)
#         print("Current user:", get_jwt_identity())
#         df = pd.read_excel(EXCEL_FILE)
#         # df = pd.read_csv(SHEET_CSV_URL)
#         print("Columns read from Google Sheet:", df.columns.tolist())
#         print("First 5 rows:", df.head())

#         # Normalize column names (remove spaces, replace with _)
#         df.columns = [c.strip().replace(" ", "_").replace("/", "_") for c in df.columns]

#         # Add ID column for frontend selection
#         df.reset_index(inplace=True)
#         df.rename(columns={"index": "id"}, inplace=True)
#         df["id"] = df["id"] + 1

#         # Add status column: "Generated" or "Pending"
#         generated_rows = {g.row_id for g in GeneratedDoc.query.all()}
#         df["Status"] = df["id"].apply(lambda x: "Generated" if x in generated_rows else "Pending")

#         df = df.replace({np.nan: None, np.inf: None, -np.inf: None})

#         return jsonify(df.to_dict(orient="records"))
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# @app.route("/excel-rows", methods=["GET"])
# @jwt_required()
# def get_excel_rows():
#     try:
#         print("Current user:", get_jwt_identity())

#         df = pd.read_csv(
#             SHEET_CSV_URL,
#             quotechar='"',
#             encoding='utf-8',
#             engine='python'
#         )

#         df = df.dropna(how='all')
#         if df.empty:
#             return jsonify({"error": "No data found in Google Sheet"}), 400

#         df.columns = [c.strip().replace(" ", "_").replace("/", "_") for c in df.columns]

#         df.reset_index(inplace=True)
#         df.rename(columns={"index": "id"}, inplace=True)
#         df["id"] = df["id"] + 1

#         generated_rows = {g.row_id for g in GeneratedDoc.query.all()}
#         df["Status"] = df["id"].apply(lambda x: "Generated" if x in generated_rows else "Pending")

#         df = df.replace({np.nan: None, np.inf: None, -np.inf: None})

#         return jsonify(df.to_dict(orient="records"))

#     except Exception as e:
#         print("❌ Error fetching Excel rows:", e)
#         return jsonify({"error": str(e)}), 500



# @app.route("/generate-docx/<int:row_id>", methods=["GET"])
# @jwt_required()
# def generate_docx(row_id):
#     try:
#         current_user_id = int(get_jwt_identity())
#         template_type = request.args.get("template_type", "template1")  # default
#         # template_type = request.args.get("template_type", "template1")
#         # comment_type = request.args.get("comment_type", "prefilled")  # default

#         if template_type == "template1":
#             template_file = "D:/Anurag/Office/KVQA KAF Data Upload Application/backend/templates/template1.docx"
#         else:
#             template_file = "D:/Anurag/Office/KVQA KAF Data Upload Application/backend/templates/template2.docx"

#         # if template_type == "template1" and comment_type == "custom":
#         #     template_file = "backend/templates/template1_custom.docx"
#         # elif template_type == "template1" and comment_type == "prefilled":
#         #     template_file = "backend/templates/template1_prefilled.docx"
#         # elif template_type == "template2" and comment_type == "custom":
#         #     template_file = "backend/templates/template2_custom.docx"
#         # else:
#         #     template_file = "backend/templates/template2_prefilled.docx"

#         user_file = UserFile.query.filter_by(id=file_id, user_id=current_user_id, source_type="uploaded").first()
#         if not user_file:
#             return jsonify({"error": "File not found or access denied"}), 404

#         # df = pd.read_excel(EXCEL_FILE)
#         df = (
#             pd.read_excel(user_file.file_path)
#             if user_file.file_path.endswith(".xlsx")
#             else pd.read_csv(user_file.file_path)
#         )
#         # df = pd.read_csv(SHEET_CSV_URL)
#         df.columns = [c.strip().replace(" ", "_").replace("/", "_") for c in df.columns]

#         df.reset_index(inplace=True)
#         df.rename(columns={"index": "id"}, inplace=True)
#         df["id"] = df["id"] + 1

#         row = df[df["id"] == row_id].to_dict(orient="records")
#         if not row:
#             return jsonify({"error": "Row not found"}), 404

#         row_data = row[0]

#         for k, v in row_data.items():
#             if isinstance(v, pd.Timestamp):
#                 row_data[k] = v.strftime("%d-%m-%Y")
#             elif pd.isna(v):  # Replace NaN or None with "NA" for Word template
#                 row_data[k] = "NA"

#         print("Row data being rendered:", row_data)
#         print("Template path:", template_file)

#         doc = DocxTemplate(template_file)
#         doc.render(row_data)

#         file_name = f"record_{row_id}_{template_type}.docx"
#         output_path = os.path.join(OUTPUT_DIR, file_name)
#         doc.save(output_path)

#         # Save in DB
#         # new_record = GeneratedDoc(row_id=row_id, file_name=file_name)
#         # db.session.add(new_record)
#         # db.session.commit()

#         new_record = GeneratedDoc(row_id=row_id, file_name=file_name, user_id=current_user_id)
#         db.session.add(new_record)

#         # Also record in UserFile for tracking
#         user_file_record = UserFile(
#             user_id=current_user_id,
#             file_name=file_name,
#             file_path=output_path,
#             source_type="generated"
#         )
#         db.session.add(user_file_record)

#         db.session.commit()

#         return send_file(output_path, as_attachment=True)

#     except Exception as e:
#         print("❌ Error in generate_docx:", str(e))
#         traceback.print_exc()
#         return jsonify({"error": str(e)}), 500

CATEGORY_TEMPLATES = {
    "QMS": {
        "3_manday": os.path.join(TEMPLATES_DIR, "template1.docx"),
        "6_manday": os.path.join(TEMPLATES_DIR, "template2.docx"),
    },
    "EMS": {
        "4_manday": os.path.join(TEMPLATES_DIR, "ems_4_manday.docx"),
        "6_manday": os.path.join(TEMPLATES_DIR, "ems_6_manday.docx"),
    },
    "OHSMS": {
        "4_manday": os.path.join(TEMPLATES_DIR, "ohsas_4_manday.docx"),
        "6_manday": os.path.join(TEMPLATES_DIR, "ohsas_6_manday.docx"),
    },
    "IMS": {
        "8_manday": os.path.join(TEMPLATES_DIR, "ims_8_manday.docx"),
        "9_manday": os.path.join(TEMPLATES_DIR, "ims_9_manday.docx"),
        "10_manday": os.path.join(TEMPLATES_DIR, "ims_10_manday.docx"),
    }
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
    ]
}

CATEGORY_CHECKLIST_TEMPLATES = {
    "QMS": [
        os.path.join(TEMPLATES_DIR, "QMS_checklist.docx"),
        os.path.join(TEMPLATES_DIR, "QMS_checklist_02.docx"),
        os.path.join(TEMPLATES_DIR, "QMS_checklist_03.docx"),
        os.path.join(TEMPLATES_DIR, "QMS_checklist_04.docx"),
        os.path.join(TEMPLATES_DIR, "QMS_checklist_05.docx"),
        os.path.join(TEMPLATES_DIR, "QMS_checklist_06.docx"),
    ],
    "EMS": [
        os.path.join(TEMPLATES_DIR, "EMS_checklist.docx"),
        os.path.join(TEMPLATES_DIR, "EMS_checklist_02.docx"),
        os.path.join(TEMPLATES_DIR, "EMS_checklist_03.docx"),
        os.path.join(TEMPLATES_DIR, "EMS_checklist_04.docx"),
        os.path.join(TEMPLATES_DIR, "EMS_checklist_05.docx"),
        os.path.join(TEMPLATES_DIR, "EMS_checklist_06.docx"),
    ],
    "OHSMS": [
        os.path.join(TEMPLATES_DIR, "OHSMS_checklist.docx"),
        os.path.join(TEMPLATES_DIR, "OHSMS_checklist_02.docx"),
        os.path.join(TEMPLATES_DIR, "OHSMS_checklist_03.docx"),
        os.path.join(TEMPLATES_DIR, "OHSMS_checklist_04.docx"),
        os.path.join(TEMPLATES_DIR, "OHSMS_checklist_05.docx"),
        os.path.join(TEMPLATES_DIR, "OHSMS_checklist_06.docx"),
    ],
    "IMS": [
        os.path.join(TEMPLATES_DIR, "IMS_checklist.docx"),
        os.path.join(TEMPLATES_DIR, "IMS_checklist_02.docx"),
        os.path.join(TEMPLATES_DIR, "IMS_checklist_03.docx")
    ],
}

def make_browser_safe_filename(org_name, category):
    org_name = org_name.strip()
    org_name_safe = re.sub(r'[^\w]', '_', org_name)  # only letters, numbers, underscore
    org_name_safe = re.sub(r'_+', '_', org_name_safe)  # collapse repeated underscores
    org_name_safe = org_name_safe.strip('_')  # remove leading/trailing underscores
    category_upper = category.lower()
    full_name = f"{org_name_safe}-{category_upper}.docx"
    print("Safe Full Filename:", full_name)
    return full_name


@app.route("/generate-docx/<int:file_id>/<int:row_id>", methods=["GET"])
@jwt_required()
def generate_docx(file_id, row_id):
    try:
        current_user_id = int(get_jwt_identity())

        # Find the uploaded file for this user
        user_file = UserFile.query.filter_by(
            id=file_id,
            user_id=current_user_id,
            source_type="uploaded"
        ).first()

        if not user_file:
            return jsonify({"error": "File not found or access denied"}), 404
        
        category = user_file.category
        manday_key = request.args.get("template_type")

        # Validate mapping
        if category not in CATEGORY_TEMPLATES:
            return jsonify({"error": f"No templates configured for {category}"}), 400
        template_file = CATEGORY_TEMPLATES[category].get(manday_key)
        if not template_file or not os.path.exists(template_file):
            return jsonify({"error": f"No template for {category} - {manday_key}"}), 400

        # # Load Excel/CSV

        ext = user_file.file_path.lower().split(".")[-1]

        if ext in ["xlsm", "xlsx"]:
            df = pd.read_excel(user_file.file_path, engine="openpyxl")
        elif ext == "xls":
            df = pd.read_excel(user_file.file_path, engine="xlrd")  # only if old .xls
        elif ext == "csv":
            try:
                df = pd.read_csv(user_file.file_path, encoding="utf-8")
            except UnicodeDecodeError:
                df = pd.read_csv(user_file.file_path, encoding="latin1")
        else:
            return jsonify({"error": f"Unsupported file type: {ext}"}), 
            
        df.columns = [c.strip().replace(" ", "_").replace("/", "_") for c in df.columns]

        df.reset_index(inplace=True)
        df.rename(columns={"index": "id"}, inplace=True)
        df["id"] = df["id"] + 1

        if "certification_audit_conducted" in df.columns:
            if pd.api.types.is_datetime64_any_dtype(df["certification_audit_conducted"]):
                df["certification_audit_conducted"] = df["certification_audit_conducted"].dt.strftime("%b-%y")

        # --- Force date columns to dd-mm-yyyy ---
        date_cols = [
            "Certificate_Issue_Date", "Surveillance_1_date", "Surveillance_2_date", "Closure_Date",
            "Starting_Date", "manual_date", "Internal_Audit_Date", "MRM_Date",
            "Stage_1_Date", "stage_1_schedule_date", "stage_2_schedule_date",
            "Questionnaire_date", "Quotation_date", "contract_review_Date"
        ]
        # for col in date_cols:
        #     if col in df.columns:
        #         df[col] = pd.to_datetime(df[col], errors="coerce").dt.strftime("%d-%m-%Y")
        #         df[col] = df[col].fillna("NA")

        for col in date_cols:
            if col in df.columns:
                # --- For IMS, skip parsing Stage_1_Date ---
                if category.upper() == "IMS" and col == "Stage_1_Date":
                    # Keep it as raw string (text)
                    df[col] = df[col].astype(str).fillna("NA")
                else:
                    # Normal case: convert to dd-mm-yyyy format
                    df[col] = pd.to_datetime(df[col], errors="coerce").dt.strftime("%d-%m-%Y")
                    df[col] = df[col].fillna("NA")


        # Get row by ID
        row = df[df["id"] == row_id].to_dict(orient="records")
        if not row:
            return jsonify({"error": "Row not found"}), 404

        row_data = row[0]

        # Convert dates and handle NaN
        # for k, v in row_data.items():
        #     if isinstance(v, pd.Timestamp):
        #         row_data[k] = v.strftime("%d-%m-%Y")
        #     elif pd.isna(v):
        #         row_data[k] = "NA"

        for k, v in row_data.items():
            if isinstance(v, str):
                # escape &, <, > for Word XML, keep everything else as-is
                row_data[k] = v.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            elif pd.isna(v):
                row_data[k] = "NA"
            elif isinstance(v, pd.Timestamp):
                row_data[k] = v.strftime("%d-%m-%Y")

        if "INTERNAL_ISSUE_NO" in row_data and isinstance(row_data["INTERNAL_ISSUE_NO"], str):
            row_data["INTERNAL_ISSUE_NO"] = escape(row_data["INTERNAL_ISSUE_NO"])


        # Render Word doc
        doc = DocxTemplate(template_file)
        doc.render(row_data)

        # file_name = f"record_{file_id}_{row_id}_{template_type}.docx"
        # output_path = os.path.join(OUTPUT_DIR, file_name)
        # doc.save(output_path)

        # org_name = row_data.get("Organization_Name", f"record_{file_id}_{row_id}")
        # safe_org_name = "".join(c if c.isalnum() or c in (" ", "_", "-") else "_" for c in org_name).strip()
        # file_name = f"{safe_org_name}_{category}.docx"

        org_name = row_data.get("Organization_Name", f"record_{file_id}_{row_id}")
        org_name = org_name.strip()
        org_name_safe = re.sub(r'[^\w]', '_', org_name)  # only letters, numbers, underscore
        org_name_safe = re.sub(r'_+', '_', org_name_safe)  # collapse repeated underscores
        org_name_safe = org_name_safe.strip('_')  # remove leading/trailing underscores
        category_upper = category.lower()
        file_name_safe = f"{org_name_safe}-{category_upper}.docx"
        print("File Name Safe: ", file_name_safe)
        file_name = quote(file_name_safe)
        print("File Name: ", file_name)

        output_path = os.path.join(OUTPUT_DIR, file_name_safe)
        doc.save(output_path)

        # Save in DB
        # new_record = GeneratedDoc(
        #     row_id=row_id,
        #     file_name=file_name,
        #     user_id=current_user_id
        # )
        # db.session.add(new_record)

        with open(output_path, "rb") as f:
            new_record = GeneratedDoc(
                row_id=row_id,
                file_name=file_name,
                file_data=f.read(),   # save as bytes
                user_id=current_user_id,
                category = category
            )
        db.session.add(new_record)

        # Also record in UserFile for tracking
        user_file_record = UserFile(
            user_id=current_user_id,
            file_name=file_name,
            file_path=output_path,
            source_type="generated",
            category = category
        )
        db.session.add(user_file_record)

        db.session.commit()

        file_name_for_browser = quote(file_name_safe)

        # return send_file(output_path, as_attachment=True)
        return send_file(
            output_path,
            as_attachment=True,
            # download_name=file_name,
            download_name=file_name_for_browser,
            mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

    except Exception as e:
        print("❌ Error in generate_docx:", str(e))
        traceback.print_exc()
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

    
@app.route("/upload-file", methods=["POST"])
@jwt_required()
def upload_file():
    try:
        current_user_id = int(get_jwt_identity())
        if "file" not in request.files:
            return {"error": "No file uploaded"}, 400
        
        file = request.files["file"]
        if file.filename == "":
            return {"error": "No file selected"}, 400
        
        category = request.form.get("category")
        if not category:
            return {"error": "Category is required"}, 400
        
        # Save the file
        user_dir = os.path.join("uploads", str(current_user_id))
        os.makedirs(user_dir, exist_ok=True)
        file_path = os.path.join(user_dir, file.filename)
        file.save(file_path)
        
        # Read file temporarily to validate columns
        # df = (
        #     pd.read_excel(file)
        #     # if file.filename.endswith(".xlsx")
        #     if file.filename.endswith(".xlsm")
        #     else pd.read_csv(file)
        # )

        # Detect file extension
        ext = file.filename.lower().split(".")[-1]

        # Read file into DataFrame
        if ext in ["xlsm", "xlsx", "xls"]:
            df = pd.read_excel(file_path, engine="openpyxl")
        elif ext == "csv":
            try:
                df = pd.read_csv(file_path, encoding="utf-8")
            except UnicodeDecodeError:
                df = pd.read_csv(file_path, encoding="latin1")
        else:
            return {"error": f"Unsupported file type: {ext}"}, 400

        df.columns = [c.strip().replace(" ", "_").replace("/", "_") for c in df.columns]

        # Validate against category config
        required_cols = CATEGORY_COLUMNS.get(category, [])
        missing = [col for col in required_cols if col not in df.columns]
        if missing:
            return {
                "error": f"Uploaded file does not match expected format for {category}. Missing columns: {missing}"
            }, 400

        # Record in DB
        user_file = UserFile(
            user_id=current_user_id,
            file_name=file.filename,
            file_path=file_path,
            source_type="uploaded",
            category=category
        )
        db.session.add(user_file)
        db.session.commit()

        return {"message": "File uploaded successfully", "file_id": user_file.id}

    except Exception as e:
        db.session.rollback()
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

#         # Read file dynamically
#         # df = (
#         #     pd.read_excel(user_file.file_path)
#         #     if user_file.file_path.endswith(".xlsx")
#         #     else pd.read_csv(user_file.file_path)
#         # )

#         # Detect extension
#         ext = user_file.file_path.lower().split(".")[-1]

#         # Read file dynamically
#         if ext in ["xlsm", "xlsx"]:
#             df = pd.read_excel(user_file.file_path, engine="openpyxl")
#         elif ext == "xls":
#             df = pd.read_excel(user_file.file_path, engine="xlrd")  # if supported
#         elif ext == "csv":
#             try:
#                 df = pd.read_csv(user_file.file_path, encoding="utf-8")
#             except UnicodeDecodeError:
#                 df = pd.read_csv(user_file.file_path, encoding="latin1")
#         else:
#             return {"error": f"Unsupported file type: {ext}"}, 400

#         df.columns = [c.strip().replace(" ", "_").replace("/", "_") for c in df.columns]

#         df.reset_index(inplace=True)
#         df.rename(columns={"index": "id"}, inplace=True)
#         df["id"] = df["id"] + 1

#         if "certification_audit_conducted" in df.columns:
#             if pd.api.types.is_datetime64_any_dtype(df["certification_audit_conducted"]):
#                 df["certification_audit_conducted"] = df["certification_audit_conducted"].dt.strftime("%b-%y")

#         # Mark rows already generated
#         # generated_rows = {g.row_id for g in GeneratedDoc.query.all()}
#         # generated_rows = {g.row_id for g in GeneratedDoc.query.filter_by(user_id=current_user_id).all()}
#         generated_rows = {
#             g.row_id
#             for g in GeneratedDoc.query.filter_by(
#                 user_id=current_user_id,
#                 category=user_file.category   # ensure same category
#             ).all()
#         }

#         checklist_rows = {
#             c.row_id
#             for c in ChecklistDoc.query.filter_by(
#                 user_id=current_user_id,
#                 category=user_file.category
#             ).all()
#         }

#         df["Status"] = df["id"].apply(lambda x: "Generated" if x in generated_rows else "Pending")
#         df["ChecklistGenerated"] = df["id"].apply(lambda x: x in checklist_rows)

#         df = df.replace({np.nan: None, np.inf: None, -np.inf: None})

#         return jsonify(df.to_dict(orient="records"))

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
        category = user_file.category.upper()
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
        generated_rows = {
            g.row_id
            for g in GeneratedDoc.query.filter_by(user_id=current_user_id, category=user_file.category).all()
        }

        df_master["Status"] = df_master["id"].apply(lambda x: "Generated" if x in generated_rows else "Pending")

        generated_checklists = {
            c.row_id
            for c in ChecklistDoc.query.filter_by(user_id=current_user_id, category=user_file.category).all()
        }
        
        df_master["ChecklistGenerated"] = df_master["id"].apply(lambda x: x in generated_checklists)

        df_master = df_master.replace({np.nan: None, np.inf: None, -np.inf: None})

        return jsonify(df_master.to_dict(orient="records"))

    except Exception as e:
        return {"error": str(e)}, 500


    
# @app.route("/generated-docs", methods=["GET"])
# @jwt_required()
# def get_generated_docs():
#     current_user_id = int(get_jwt_identity())
#     docs = GeneratedDoc.query.filter_by(user_id=current_user_id).order_by(GeneratedDoc.created_at.desc()).all()
#     return jsonify([
#         {
#             "id": d.id,
#             "row_id": d.row_id,
#             "file_name": d.file_name,
#             "created_at": d.created_at.strftime("%Y-%m-%d %H:%M:%S")
#         } for d in docs
#     ])

@app.route("/generated-docs", methods=["GET"])
@jwt_required()
def get_generated_docs():
    current_user_id = int(get_jwt_identity())
    category = request.args.get("category", None)

    query = GeneratedDoc.query.filter_by(user_id=current_user_id)

    if category:
        query = query.filter(GeneratedDoc.category.ilike(category))

    print("Requested category:", category)

    docs = query.order_by(GeneratedDoc.created_at.desc()).all()

    return jsonify([
        {
            "id": d.id,
            "row_id": d.row_id,
            "file_name": d.file_name,
            "category": d.category,
            "created_at": d.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "source": "GeneratedDoc"
        } for d in docs
    ])

# @app.route("/download-generated-file/<file_name>", methods=["GET"])
# @jwt_required()
# def download_generated_file(file_name):
#     current_user_id = int(get_jwt_identity())
#     doc = GeneratedDoc.query.filter_by(file_name=file_name, user_id=current_user_id).first()
#     if not doc:
#         return {"error": "File not found or access denied"}, 404

#     file_path = os.path.join(OUTPUT_DIR, file_name)
#     return send_file(file_path, as_attachment=True)

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

# @app.route("/categories", methods=["GET"])
# def get_categories():
#     return jsonify({
#         name: {
#             "excel_columns": cfg["excel_columns"],
#             "mandays": list(cfg["templates"].keys())
#         }
#         for name, cfg in CATEGORY_CONFIG.items()
#     })


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

    user_id = request.args.get("user_id")  # optional filter
    files_data = []

    if user_id:
        # user_files = UserFile.query.filter_by(user_id=user_id).all()
        generated_files = GeneratedDoc.query.filter_by(user_id=user_id).all()
    else:
        # user_files = UserFile.query.all()
        generated_files = GeneratedDoc.query.all()

    # for f in user_files:
    #     files_data.append({
    #         "id": f.id,
    #         "file_name": f.file_name,
    #         "category": f.category,
    #         "uploaded_at": f.uploaded_at,
    #         "user": f.user.username,
    #         "source": "uploaded"
    #     })

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

    # ✅ Only admins can download all files
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

# @app.route("/generate-checklist/<int:file_id>/<int:row_id>", methods=["GET"])
# @jwt_required()
# def generate_checklist(file_id, row_id):
#     try:
#         current_user_id = int(get_jwt_identity())

#         # --- Find the uploaded file ---
#         user_file = UserFile.query.filter_by(
#             id=file_id,
#             user_id=current_user_id,
#             source_type="uploaded"
#         ).first()
#         if not user_file:
#             return jsonify({"error": "File not found or access denied"}), 404

#         category = user_file.category.upper()  # QMS, EMS, OHSAS

#         # --- Pick checklist template for category ---
#         template_file = CATEGORY_CHECKLIST_TEMPLATES.get(category)
#         if not template_file or not os.path.exists(template_file):
#             return jsonify({"error": f"Checklist template not found for {category}"}), 400

#         # --- Load Excel or CSV ---
#         ext = user_file.file_path.lower().split(".")[-1]
#         if ext in ["xlsm", "xlsx"]:
#             xl = pd.ExcelFile(user_file.file_path, engine="openpyxl")
#         elif ext == "xls":
#             xl = pd.ExcelFile(user_file.file_path, engine="xlrd")
#         elif ext == "csv":
#             df_checklist = pd.read_csv(user_file.file_path)
#             xl = None
#         else:
#             return jsonify({"error": f"Unsupported file type: {ext}"}), 400

#         # --- Load checklist sheet ---
#         if xl:
#             # find the checklist sheet dynamically
#             sheet_candidates = [s for s in xl.sheet_names if category in s and "Checklist" in s]
#             if not sheet_candidates:
#                 return jsonify({"error": f"No checklist sheet found for {category}"}), 404
#             sheet_name = sheet_candidates[0]
#             df_checklist = xl.parse(sheet_name=sheet_name)

#         df_checklist.columns = [c.strip().replace(" ", "_").replace("/", "_") for c in df_checklist.columns]
#         df_checklist.reset_index(inplace=True)
#         df_checklist.rename(columns={"index": "id"}, inplace=True)
#         df_checklist["id"] = df_checklist["id"] + 1

#         # --- Fetch the specific row from checklist ---
#         row = df_checklist[df_checklist["id"] == row_id].to_dict(orient="records")
#         if not row:
#             return jsonify({"error": "Row not found in checklist sheet"}), 404
#         row_data = row[0]

#         # --- Load category-specific master sheet ---
#         if xl:
#             sheet_name_map = {
#                 "QMS": "QMS 2025",
#                 "EMS": "EMS 2025",
#                 "OHSMS": "OHSMS 2025"
#             }
#             df_master = xl.parse(sheet_name=sheet_name_map.get(category, "Sheet1"))
#             df_master.columns = [c.strip().replace(" ", "_").replace("/", "_") for c in df_master.columns]
#         else:
#             df_master = pd.DataFrame()  # CSV case

#         # --- Merge master sheet data if matching ---
#         if not df_master.empty:
#             certificate_no = row_data.get("Certificate_No")
#             master_row = df_master[df_master["Certificate_No"] == certificate_no].to_dict(orient="records")
#             master_data = master_row[0] if master_row else {}
#         else:
#             master_data = {}

#         # --- Prepare context ---
#         context = {}

#         org_name = master_data.get("Organization_Name") or row_data.get("Organization_Name") or f"record_{file_id}_{row_id}"
#         context["Organization_Name"] = org_name

#         # Master sheet columns first
#         for col in CATEGORY_COLUMNS.get(category, []):
#             context[col] = row_data.get(col) or master_data.get(col) or "NA"
#             if isinstance(context[col], pd.Timestamp):
#                 context[col] = context[col].strftime("%d-%m-%Y")

#         # Checklist-specific columns (add if not already present)
#         for col in df_checklist.columns:
#             if col not in context:
#                 context[col] = row_data.get(col, "NA")
#                 if isinstance(context[col], pd.Timestamp):
#                     context[col] = context[col].strftime("%d-%m-%Y")

#         # --- Render template ---
#         doc = DocxTemplate(template_file)
#         doc.render(context)

#         # --- Save output ---
#         # org_name = context.get("Organization_Name", f"record_{file_id}_{row_id}")
#         # base_name = make_browser_safe_filename(org_name, category)
#         # file_name_safe = f"{base_name}_{category}_checklist.docx"
#         # output_path = os.path.join(OUTPUT_DIR, file_name_safe)
#         # doc.save(output_path)

#         print("Checklist columns:", df_checklist.columns.tolist())
#         print("Row data fetched:", row_data)
#         print("Org name value:", row_data.get("Organization_Name"))


#         # org_name = context.get("Organization_Name", f"record_{file_id}_{row_id}")
#         # # org_name = context.get("Organization_Name")
#         # print(org_name)

#         # sanitize org_name (replace spaces and unsafe chars with "_")
#         org_name_safe = re.sub(r"[^\w]", "_", org_name)
#         org_name_safe = re.sub(r"_+", "_", org_name_safe).strip("_")
#         print(org_name_safe)

#         # ✅ Final checklist filename
#         file_name_safe = f"{org_name_safe}_{category}_checklist.docx"
#         print(file_name_safe)
#         output_path = os.path.join(OUTPUT_DIR, file_name_safe)
#         doc.save(output_path)

#         # --- Save to DB ---
#         with open(output_path, "rb") as f:
#             new_record = ChecklistDoc(
#                 row_id=row_id,
#                 file_name=file_name_safe,
#                 file_data=f.read(),
#                 user_id=current_user_id,
#                 category=category
#             )
#             db.session.add(new_record)
#             db.session.commit()

#         return send_file(
#             output_path,
#             as_attachment=True,
#             download_name=file_name_safe,
#             mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
#         )

#     except Exception as e:
#         print("❌ Error in generate_checklist:", str(e))
#         traceback.print_exc()
#         db.session.rollback()
#         return jsonify({"error": str(e)}), 500

# @app.route("/generate-checklist/<int:file_id>/<int:row_id>", methods=["GET"])
# @jwt_required()
# def generate_checklist(file_id, row_id):
#     try:
#         current_user_id = int(get_jwt_identity())

#         # --- Find the uploaded file ---
#         user_file = UserFile.query.filter_by(
#             id=file_id,
#             user_id=current_user_id,
#             source_type="uploaded"
#         ).first()
#         if not user_file:
#             return jsonify({"error": "File not found or access denied"}), 404

#         category = user_file.category.upper()  # QMS, EMS, OHSMS

#         # --- Pick checklist template ---
#         # template_file = CATEGORY_CHECKLIST_TEMPLATES.get(category)
#         # if not template_file or not os.path.exists(template_file):
#         #     return jsonify({"error": f"Checklist template not found for {category}"}), 400

#         template_candidates = CATEGORY_CHECKLIST_TEMPLATES.get(category, [])
#         if not template_candidates:
#             return jsonify({"error": f"No checklist templates found for {category}"}), 400

#         template_file = random.choice(template_candidates)  # ✅ random selection
#         if not os.path.exists(template_file):
#             return jsonify({"error": f"Template file not found: {template_file}"}), 400

#         # --- Load Excel ---
#         xl = pd.ExcelFile(user_file.file_path, engine="openpyxl")
        
#         # ✅ Load master sheet (e.g. QMS 2025)
#         sheet_name_map = {
#             "QMS": "QMS 2025",
#             "EMS": "EMS 2025",
#             "OHSMS": "OHSMS 2025"
#         }
#         df_master = xl.parse(sheet_name_map.get(category, "Sheet1"))
#         df_master.columns = [c.strip().replace(" ", "_").replace("/", "_") for c in df_master.columns]

#         # ✅ Load checklist sheet
#         sheet_candidates = [s for s in xl.sheet_names if category in s and "Checklist" in s]
#         if not sheet_candidates:
#             return jsonify({"error": f"No checklist sheet found for {category}"}), 404
#         df_checklist = xl.parse(sheet_candidates[0])
#         df_checklist.columns = [c.strip().replace(" ", "_").replace("/", "_") for c in df_checklist.columns]

#         # --- Get row from doc sheet by row_id ---
#         master_row = df_master.reset_index()
#         master_row.rename(columns={"index": "id"}, inplace=True)
#         master_row["id"] = master_row["id"] + 1

#         selected_row = master_row[master_row["id"] == row_id].to_dict(orient="records")
#         if not selected_row:
#             return jsonify({"error": "Row not found in doc sheet"}), 404

#         master_data = selected_row[0]
#         certificate_no = master_data.get("Certificate_No")

#         # --- Match checklist row by Certificate_No ---
#         checklist_row = df_checklist[df_checklist["Certificate_No"] == certificate_no].to_dict(orient="records")
#         if not checklist_row:
#             return jsonify({"error": f"No checklist entry found for Certificate_No {certificate_no}"}), 404

#         row_data = checklist_row[0]

#         # --- Merge master + checklist ---
#         context = {**master_data, **row_data}
#         for k, v in context.items():
#             if isinstance(v, pd.Timestamp):
#                 context[k] = v.strftime("%d-%m-%Y")
#             elif pd.isna(v):
#                 context[k] = "NA"

#         # --- Render checklist doc ---
#         doc = DocxTemplate(template_file)
#         doc.render(context)

#         org_name = context.get("Organization_Name", f"record_{file_id}_{row_id}")
#         org_name_safe = re.sub(r"[^\w]", "_", org_name).strip("_")
#         file_name_safe = f"{org_name_safe}_{category}_checklist.docx"

#         output_path = os.path.join(OUTPUT_DIR, file_name_safe)
#         doc.save(output_path)

#         # --- Save in DB ---
#         with open(output_path, "rb") as f:
#             new_record = ChecklistDoc(
#                 row_id=row_id,
#                 file_name=file_name_safe,
#                 file_data=f.read(),
#                 user_id=current_user_id,
#                 category=category
#             )
#             db.session.add(new_record)
#             db.session.commit()

#         return send_file(output_path, as_attachment=True, download_name=file_name_safe)

#     except Exception as e:
#         traceback.print_exc()
#         db.session.rollback()
#         return jsonify({"error": str(e)}), 500

# @app.route("/generate-checklist/<int:file_id>/<int:row_id>", methods=["GET"])
# @jwt_required()
# def generate_checklist(file_id, row_id):
#     try:
#         current_user_id = int(get_jwt_identity())

#         # --- Find the uploaded file ---
#         user_file = UserFile.query.filter_by(
#             id=file_id,
#             user_id=current_user_id,
#             source_type="uploaded"
#         ).first()
#         if not user_file:
#             return jsonify({"error": "File not found or access denied"}), 404

#         category = user_file.category.upper()

#         # --- Pick checklist template ---
#         template_candidates = CATEGORY_CHECKLIST_TEMPLATES.get(category, [])
#         if not template_candidates:
#             return jsonify({"error": f"No checklist templates found for {category}"}), 400
#         template_file = random.choice(template_candidates)
#         if not os.path.exists(template_file):
#             return jsonify({"error": f"Template file not found: {template_file}"}), 400

#         # --- Load Excel ---
#         xl = pd.ExcelFile(user_file.file_path, engine="openpyxl")
#         sheet_name_map = {"QMS": "QMS 2025", "EMS": "EMS 2025", "OHSMS": "OHSMS 2025"}
#         df_master = xl.parse(sheet_name_map.get(category, "Sheet1"))
#         df_master.columns = [c.strip().replace(" ", "_").replace("/", "_") for c in df_master.columns]

#         sheet_candidates = [s for s in xl.sheet_names if category in s and "Checklist" in s]
#         if not sheet_candidates:
#             return jsonify({"error": f"No checklist sheet found for {category}"}), 404
#         df_checklist = xl.parse(sheet_candidates[0])
#         df_checklist.columns = [c.strip().replace(" ", "_").replace("/", "_") for c in df_checklist.columns]

#         # --- Get row from master sheet ---
#         master_row = df_master.reset_index()
#         master_row.rename(columns={"index": "id"}, inplace=True)
#         master_row["id"] = master_row["id"] + 1

#         selected_row = master_row[master_row["id"] == row_id].to_dict(orient="records")
#         if not selected_row:
#             return jsonify({"error": "Row not found in master sheet"}), 404
#         master_data = selected_row[0]
#         certificate_no = master_data.get("Certificate_No")

#         # --- Match checklist row by Certificate_No ---
#         checklist_row = df_checklist[df_checklist["Certificate_No"] == certificate_no].to_dict(orient="records")
#         if not checklist_row:
#             return jsonify({"error": f"No checklist entry found for Certificate_No {certificate_no}"}), 404
#         row_data = checklist_row[0]

#         # --- Merge master + checklist ---
#         context = {**master_data, **row_data}
#         for k, v in context.items():
#             if isinstance(v, pd.Timestamp):
#                 context[k] = v.strftime("%d-%m-%Y")
#             elif pd.isna(v):
#                 context[k] = "NA"
#             elif isinstance(v, str):
#                 # Only replace & with &amp; so Word can render it
#                 context[k] = v.replace("&", "&amp;")

#         # --- Render checklist doc ---
#         doc = DocxTemplate(template_file)
#         doc.render(context)

#         org_name = context.get("Organization_Name", f"record_{file_id}_{row_id}")
#         org_name_safe = re.sub(r"[^\w]", "_", org_name).strip("_")
#         file_name_safe = f"{org_name_safe}_{category}_checklist.docx"

#         output_path = os.path.join(OUTPUT_DIR, file_name_safe)
#         doc.save(output_path)

#         # --- Save in DB ---
#         with open(output_path, "rb") as f:
#             new_record = ChecklistDoc(
#                 row_id=row_id,
#                 file_name=file_name_safe,
#                 file_data=f.read(),
#                 user_id=current_user_id,
#                 category=category
#             )
#             db.session.add(new_record)
#             db.session.commit()

#         return send_file(output_path, as_attachment=True, download_name=file_name_safe)

#     except Exception as e:
#         traceback.print_exc()
#         db.session.rollback()
#         return jsonify({"error": str(e)}), 500

@app.route("/generate-checklist/<int:file_id>/<int:row_id>", methods=["GET"])
@jwt_required()
def generate_checklist(file_id, row_id):
    try:
        current_user_id = int(get_jwt_identity())

        # --- Find the uploaded file ---
        user_file = UserFile.query.filter_by(
            id=file_id,
            user_id=current_user_id,
            source_type="uploaded"
        ).first()
        if not user_file:
            return jsonify({"error": "File not found or access denied"}), 404

        category = user_file.category.upper()

        # --- Pick checklist template ---
        template_candidates = CATEGORY_CHECKLIST_TEMPLATES.get(category, [])
        if not template_candidates:
            return jsonify({"error": f"No checklist templates found for {category}"}), 400
        template_file = random.choice(template_candidates)
        if not os.path.exists(template_file):
            return jsonify({"error": f"Template file not found: {template_file}"}), 400

        # --- Load Excel ---
        xl = pd.ExcelFile(user_file.file_path, engine="openpyxl")

        # Include IMS in sheet name map
        sheet_name_map = {
            "QMS": "QMS 2025",
            "EMS": "EMS 2025",
            "OHSMS": "OHSMS 2025",
            "IMS": "IMS 2025"
        }

        print("Sheets found in Excel:", xl.sheet_names)

        df_master = xl.parse(sheet_name_map.get(category, "Sheet1"))
        df_master.columns = [c.strip().replace(" ", "_").replace("/", "_") for c in df_master.columns]

        # --- Find Checklist Sheet ---
        sheet_candidates = [s for s in xl.sheet_names if category in s and "Checklist" in s]
        if not sheet_candidates:
            return jsonify({"error": f"No checklist sheet found for {category}"}), 404

        df_checklist = xl.parse(sheet_candidates[0])
        df_checklist.columns = [c.strip().replace(" ", "_").replace("/", "_") for c in df_checklist.columns]

        # --- Get master row ---
        master_row = df_master.reset_index()
        master_row.rename(columns={"index": "id"}, inplace=True)
        master_row["id"] = master_row["id"] + 1

        selected_row = master_row[master_row["id"] == row_id].to_dict(orient="records")
        if not selected_row:
            return jsonify({"error": "Row not found in master sheet"}), 404

        master_data = selected_row[0]

        # --- Determine Certificate No based on category ---
        if category == "IMS":
            match_column = "Certificate_No_QMS"
            certificate_no = master_data.get(match_column)
        else:
            match_column = "Certificate_No"
            certificate_no = master_data.get(match_column)

        if not certificate_no or str(certificate_no).strip().lower() in ["", "none", "null"]:
            return jsonify({"error": f"No valid certificate number found for {category}"}), 400

        # --- Match checklist row ---
        if match_column not in df_checklist.columns:
            return jsonify({"error": f"Checklist sheet missing expected column {match_column}"}), 400

        checklist_row = df_checklist[df_checklist[match_column] == certificate_no].to_dict(orient="records")
        if not checklist_row:
            return jsonify({"error": f"No checklist entry found for {match_column} = {certificate_no}"}), 404

        row_data = checklist_row[0]

        # --- Merge data ---
        context = {**master_data, **row_data}
        for k, v in context.items():
            if isinstance(v, pd.Timestamp):
                context[k] = v.strftime("%d-%m-%Y")
            elif pd.isna(v) or str(v).strip().lower() == "null":
                context[k] = "NA"
            elif isinstance(v, str):
                context[k] = v.replace("&", "&amp;")

        # --- Render DOCX ---
        doc = DocxTemplate(template_file)
        doc.render(context)

        org_name = context.get("Organization_Name", f"record_{file_id}_{row_id}")
        org_name_safe = re.sub(r"[^\w]", "_", org_name).strip("_")
        file_name_safe = f"{org_name_safe}_{category}_checklist.docx"
        output_path = os.path.join(OUTPUT_DIR, file_name_safe)
        doc.save(output_path)

        # --- Save to DB ---
        with open(output_path, "rb") as f:
            new_record = ChecklistDoc(
                row_id=row_id,
                file_name=file_name_safe,
                file_data=f.read(),
                user_id=current_user_id,
                category=category
            )
            db.session.add(new_record)
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
        category = category.upper()  # ensure consistent casing

        # Find generated document(s) for this row by this user and category
        docs = GeneratedDoc.query.filter_by(row_id=row_id, user_id=current_user_id, category=category).all()
        if not docs:
            return jsonify({"error": "Generated document not found"}), 404

        for doc in docs:
            # Delete the file from disk
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
        category = category.upper()  # ensure consistent casing

        # Delete Checklist documents for this row, user, and category
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

# @app.route("/generated-checklists", methods=["GET"])
# @jwt_required()
# def get_generated_checklists():
#     current_user_id = int(get_jwt_identity())
#     docs = ChecklistDoc.query.filter_by(user_id=current_user_id).order_by(ChecklistDoc.created_at.desc()).all()
#     return jsonify([
#         {
#             "id": d.id,
#             "row_id": d.row_id,
#             "file_name": d.file_name,
#             "created_at": d.created_at.strftime("%Y-%m-%d %H:%M:%S")
#         } for d in docs
#     ])


@app.route("/generated-checklists", methods=["GET"])
@jwt_required()
def get_generated_checklists():
    current_user_id = int(get_jwt_identity())
    category = request.args.get("category", None)

    query = ChecklistDoc.query.filter_by(user_id=current_user_id)

    if category:
        # Case-insensitive and space-trimmed comparison
        query = query.filter(db.func.lower(db.func.trim(ChecklistDoc.category)) == category.strip().lower())

    print("Requested checklist category:", category)

    docs = query.order_by(ChecklistDoc.created_at.desc()).all()

    return jsonify([
        {
            "id": d.id,
            "row_id": d.row_id,
            "file_name": d.file_name,
            "category": d.category,
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