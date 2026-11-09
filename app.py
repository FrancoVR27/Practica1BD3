import os
import uuid
from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for, flash
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret-key")

ASTRA_DB_SECURE_CONNECT_BUNDLE = os.getenv("ASTRA_DB_SECURE_CONNECT_BUNDLE")
ASTRA_DB_CLIENT_ID = os.getenv("ASTRA_DB_CLIENT_ID")
ASTRA_DB_CLIENT_SECRET = os.getenv("ASTRA_DB_CLIENT_SECRET")
ASTRA_DB_KEYSPACE = os.getenv("ASTRA_DB_KEYSPACE", "app_keyspace")

_cluster = None
_session = None


def get_session():
    global _cluster, _session
    if _session is None:
        cloud_config = {"secure_connect_bundle": ASTRA_DB_SECURE_CONNECT_BUNDLE}
        auth_provider = PlainTextAuthProvider(ASTRA_DB_CLIENT_ID, ASTRA_DB_CLIENT_SECRET)
        _cluster = Cluster(cloud=cloud_config, auth_provider=auth_provider)
        _session = _cluster.connect()
        _session.set_keyspace(ASTRA_DB_KEYSPACE)
    return _session


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/registro", methods=["POST"])
def registro():
    nombre = (request.form.get("nombre") or "").strip()
    if not nombre:
        flash("El nombre es requerido", "error")
        return redirect(url_for("index"))

    session = get_session()
    session.execute(
        "INSERT INTO usuarios (id, nombre, fecha) VALUES (%s, %s, %s)",
        (uuid.uuid4(), nombre, datetime.utcnow()),
    )
    flash(f"Usuario '{nombre}' registrado correctamente", "success")
    return redirect(url_for("index"))


@app.route("/usuarios", methods=["GET"])
def usuarios():
    session = get_session()
    rows = session.execute("SELECT id, nombre, fecha FROM usuarios")
    data = [
        {"id": str(r.id), "nombre": r.nombre, "fecha": str(r.fecha)} for r in rows
    ]
    return render_template("usuarios.html", usuarios=data, count=len(data))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5001)), debug=True)
