"""
Flask Application — Azure Blob Storage CRUD
Peut être testé localement avant déploiement sur la VM.
"""
import os
import uuid
from datetime import datetime

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
    "DATABASE_URL", "sqlite:///local_dev.db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# ─── Modèle ───────────────────────────────────────────────────────────────────
class FileMetadata(db.Model):
    __tablename__ = "file_metadata"

    id          = db.Column(db.String(36), primary_key=True,
                            default=lambda: str(uuid.uuid4()))
    filename    = db.Column(db.String(255), nullable=False)
    blob_url    = db.Column(db.Text)
    size_bytes  = db.Column(db.Integer)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    description = db.Column(db.Text)

    def to_dict(self):
        return {
            "id":          self.id,
            "filename":    self.filename,
            "blob_url":    self.blob_url,
            "size_bytes":  self.size_bytes,
            "uploaded_at": self.uploaded_at.isoformat(),
            "description": self.description,
        }


# ─── Helpers Azure ────────────────────────────────────────────────────────────
def get_container_client():
    account  = os.getenv("AZURE_STORAGE_ACCOUNT")
    key      = os.getenv("AZURE_STORAGE_KEY")
    conn_str = (
        f"DefaultEndpointsProtocol=https;"
        f"AccountName={account};"
        f"AccountKey={key};"
        f"EndpointSuffix=core.windows.net"
    )
    blob_service = BlobServiceClient.from_connection_string(conn_str)
    return blob_service.get_container_client(
        os.getenv("AZURE_CONTAINER_NAME", "static-files")
    )


# ─── Routes ───────────────────────────────────────────────────────────────────

@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status":  "ok",
        "message": "Flask app running",
        "time":    datetime.utcnow().isoformat(),
    }), 200


# CREATE – Upload fichier vers Azure Blob + enregistrement métadonnées
@app.route("/files", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file part in request"}), 400

    file        = request.files["file"]
    description = request.form.get("description", "")

    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    file_content = file.read()
    blob_name    = f"{uuid.uuid4()}_{file.filename}"
    container    = os.getenv("AZURE_CONTAINER_NAME", "static-files")
    account      = os.getenv("AZURE_STORAGE_ACCOUNT")

    container_client = get_container_client()
    container_client.upload_blob(name=blob_name, data=file_content, overwrite=True)

    blob_url = (
        f"https://{account}.blob.core.windows.net/{container}/{blob_name}"
    )

    meta = FileMetadata(
        filename    = file.filename,
        blob_url    = blob_url,
        size_bytes  = len(file_content),
        description = description,
    )
    db.session.add(meta)
    db.session.commit()

    return jsonify(meta.to_dict()), 201


# READ – Lister tous les fichiers
@app.route("/files", methods=["GET"])
def list_files():
    files = FileMetadata.query.order_by(
        FileMetadata.uploaded_at.desc()
    ).all()
    return jsonify([f.to_dict() for f in files]), 200


# READ – Obtenir un fichier par son ID
@app.route("/files/<file_id>", methods=["GET"])
def get_file(file_id):
    meta = db.session.get(FileMetadata, file_id)
    if not meta:
        return jsonify({"error": "File not found"}), 404
    return jsonify(meta.to_dict()), 200


# UPDATE – Modifier la description d'un fichier
@app.route("/files/<file_id>", methods=["PUT"])
def update_file(file_id):
    meta = db.session.get(FileMetadata, file_id)
    if not meta:
        return jsonify({"error": "File not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON body"}), 400

    if "description" in data:
        meta.description = data["description"]

    db.session.commit()
    return jsonify(meta.to_dict()), 200


# DELETE – Supprimer blob Azure + métadonnées BD
@app.route("/files/<file_id>", methods=["DELETE"])
def delete_file(file_id):
    meta = db.session.get(FileMetadata, file_id)
    if not meta:
        return jsonify({"error": "File not found"}), 404

    blob_name = meta.blob_url.split("/")[-1]
    container_client = get_container_client()
    container_client.delete_blob(blob_name)

    db.session.delete(meta)
    db.session.commit()

    return jsonify({"message": f"File {file_id} deleted successfully"}), 200


# ─── Point d'entrée ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=5000, debug=False)
