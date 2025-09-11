from flask import Flask, request, jsonify, send_file
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

# EXCEL_FILE = "D:/Anurag/Office/KVQA KAF Data Upload Application/Data1.xlsx"     # path to your Excel file
# SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/1fzYnnOKHt3houEzNolPJKEw9PIKJkvDJbfcmKgUIjQs/export?format=csv&gid=0"     # path to your SPREADSHEET file
TEMPLATE_FILE = "D:/Anurag/Office/KVQA KAF Data Upload Application/backend/templates/template.docx"  # path to your Word template
OUTPUT_DIR = "generated_docs"

os.makedirs(OUTPUT_DIR, exist_ok=True)

@app.route('/')
def home():
    return "KVQA KAF Data Entry Application Started"

@app.route("/register", methods=["POST"])
def register():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return {"error": "Username and password required"}, 400

    if User.query.filter_by(username=username).first():
        return {"error": "User already exists"}, 400

    new_user = User(username=username)
    new_user.set_password(password)

    db.session.add(new_user)
    db.session.commit()

    return {"message": "User registered successfully"}, 201


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
    return jsonify(access_token=access_token)


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
    return jsonify([{"id": u.id, "username": u.username} for u in users])

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

@app.route("/generate-docx/<int:file_id>/<int:row_id>", methods=["GET"])
@jwt_required()
def generate_docx(file_id, row_id):
    try:
        current_user_id = int(get_jwt_identity())
        template_type = request.args.get("template_type", "template1")

        # Pick template file
        if template_type == "template1":
            template_file = "D:/Anurag/Office/KVQA KAF Data Upload Application/backend/templates/template1.docx"
        else:
            template_file = "D:/Anurag/Office/KVQA KAF Data Upload Application/backend/templates/template2.docx"

        # Find the uploaded file for this user
        user_file = UserFile.query.filter_by(
            id=file_id,
            user_id=current_user_id,
            source_type="uploaded"
        ).first()

        if not user_file:
            return jsonify({"error": "File not found or access denied"}), 404

        # Load Excel/CSV
        df = (
            pd.read_excel(user_file.file_path)
            if user_file.file_path.endswith(".xlsx")
            else pd.read_csv(user_file.file_path)
        )
        df.columns = [c.strip().replace(" ", "_").replace("/", "_") for c in df.columns]

        df.reset_index(inplace=True)
        df.rename(columns={"index": "id"}, inplace=True)
        df["id"] = df["id"] + 1

        if "certification_audit_conducted" in df.columns:
            if pd.api.types.is_datetime64_any_dtype(df["certification_audit_conducted"]):
                df["certification_audit_conducted"] = df["certification_audit_conducted"].dt.strftime("%b-%y")

        # Get row by ID
        row = df[df["id"] == row_id].to_dict(orient="records")
        if not row:
            return jsonify({"error": "Row not found"}), 404

        row_data = row[0]

        # Convert dates and handle NaN
        for k, v in row_data.items():
            if isinstance(v, pd.Timestamp):
                row_data[k] = v.strftime("%d-%m-%Y")
            elif pd.isna(v):
                row_data[k] = "NA"

        if "INTERNAL_ISSUE_NO" in row_data and isinstance(row_data["INTERNAL_ISSUE_NO"], str):
            row_data["INTERNAL_ISSUE_NO"] = escape(row_data["INTERNAL_ISSUE_NO"])


        # Render Word doc
        doc = DocxTemplate(template_file)
        doc.render(row_data)

        # file_name = f"record_{file_id}_{row_id}_{template_type}.docx"
        # output_path = os.path.join(OUTPUT_DIR, file_name)
        # doc.save(output_path)

        org_name = row_data.get("Organization_Name", f"record_{file_id}_{row_id}")
        safe_org_name = "".join(c if c.isalnum() or c in (" ", "_", "-") else "_" for c in org_name).strip()
        file_name = f"{safe_org_name}.docx"

        output_path = os.path.join(OUTPUT_DIR, file_name)
        doc.save(output_path)

        # Save in DB
        new_record = GeneratedDoc(
            row_id=row_id,
            file_name=file_name,
            user_id=current_user_id
        )
        db.session.add(new_record)

        # Also record in UserFile for tracking
        user_file_record = UserFile(
            user_id=current_user_id,
            file_name=file_name,
            file_path=output_path,
            source_type="generated"
        )
        db.session.add(user_file_record)

        db.session.commit()

        return send_file(output_path, as_attachment=True)

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

        # Save the file
        user_dir = os.path.join("uploads", str(current_user_id))
        os.makedirs(user_dir, exist_ok=True)
        file_path = os.path.join(user_dir, file.filename)
        file.save(file_path)

        # Record in DB
        user_file = UserFile(
            user_id=current_user_id,
            file_name=file.filename,
            file_path=file_path,
            source_type="uploaded"
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


@app.route("/excel-rows/<int:file_id>", methods=["GET"])
@jwt_required()
def get_excel_rows(file_id):
    try:
        current_user_id = int(get_jwt_identity())
        user_file = UserFile.query.filter_by(id=file_id, user_id=current_user_id).first()
        if not user_file:
            return {"error": "File not found or access denied"}, 404

        # Read file dynamically
        df = (
            pd.read_excel(user_file.file_path)
            if user_file.file_path.endswith(".xlsx")
            else pd.read_csv(user_file.file_path)
        )
        df.columns = [c.strip().replace(" ", "_").replace("/", "_") for c in df.columns]

        df.reset_index(inplace=True)
        df.rename(columns={"index": "id"}, inplace=True)
        df["id"] = df["id"] + 1

        if "certification_audit_conducted" in df.columns:
            if pd.api.types.is_datetime64_any_dtype(df["certification_audit_conducted"]):
                df["certification_audit_conducted"] = df["certification_audit_conducted"].dt.strftime("%b-%y")

        # Mark rows already generated
        # generated_rows = {g.row_id for g in GeneratedDoc.query.all()}
        generated_rows = {g.row_id for g in GeneratedDoc.query.filter_by(user_id=current_user_id).all()}
        df["Status"] = df["id"].apply(lambda x: "Generated" if x in generated_rows else "Pending")

        df = df.replace({np.nan: None, np.inf: None, -np.inf: None})

        return jsonify(df.to_dict(orient="records"))

    except Exception as e:
        return {"error": str(e)}, 500

    
@app.route("/generated-docs", methods=["GET"])
@jwt_required()
def get_generated_docs():
    current_user_id = int(get_jwt_identity())
    docs = GeneratedDoc.query.filter_by(user_id=current_user_id).order_by(GeneratedDoc.created_at.desc()).all()
    return jsonify([
        {
            "id": d.id,
            "row_id": d.row_id,
            "file_name": d.file_name,
            "created_at": d.created_at.strftime("%Y-%m-%d %H:%M:%S")
        } for d in docs
    ])


@app.route("/download-generated-file/<file_name>", methods=["GET"])
@jwt_required()
def download_generated_file(file_name):
    current_user_id = int(get_jwt_identity())
    doc = GeneratedDoc.query.filter_by(file_name=file_name, user_id=current_user_id).first()
    if not doc:
        return {"error": "File not found or access denied"}, 404

    file_path = os.path.join(OUTPUT_DIR, file_name)
    return send_file(file_path, as_attachment=True)

@app.route("/init-db")
def init_db():
    try:
        db.create_all()
        return {"message": "Database initialized successfully!"}
    except Exception as e:
        return {"error": str(e)}, 500


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)