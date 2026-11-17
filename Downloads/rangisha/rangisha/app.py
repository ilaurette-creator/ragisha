import hmac, json, os, sqlite3
from datetime import datetime
from flask import Flask, flash, redirect, render_template, request, session, url_for
from translations import TEXT

app = Flask(__name__)
app.secret_key = os.environ.get("RANGISHA_SECRET", os.urandom(24))
ADMIN_PASSWORD = os.environ.get("RANGISHA_ADMIN_PASSWORD", "change-me")
DB = "rangisha.db"
DOC_TYPES = ["d_id", "d_permit", "d_passport", "d_certificate", "d_other"]

# Each field: (name, label, input type, required)
LOST = [("name", "your_name", "text", True), ("phone", "phone", "tel", True),
        ("doc_type", "doc_type", "select", True), ("place", "lost_place", "text", True),
        ("details", "details", "textarea", False)]
FOUND = [("name", "your_name", "text", True), ("phone", "phone", "tel", True),
         ("doc_type", "doc_type", "select", True), ("place", "handed_to", "text", True),
         ("details", "details", "textarea", False)]
HELP = [("name", "your_name", "text", True), ("phone", "phone", "tel", True),
        ("question", "question", "textarea", True)]
ADMIN_ADD = [("doc_type", "doc_type", "select", True), ("owner", "owner_name", "text", True),
             ("place", "kept_at", "text", True)]


def db():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    return con


with db() as con:
    con.execute("CREATE TABLE IF NOT EXISTS entries "
                "(id INTEGER PRIMARY KEY, kind TEXT, data TEXT, created TEXT)")


def save(kind, data):
    with db() as con:
        con.execute("INSERT INTO entries (kind, data, created) VALUES (?, ?, ?)",
                    (kind, json.dumps(data), datetime.now().strftime("%Y-%m-%d")))


def load(kind):
    with db() as con:
        rows = con.execute("SELECT * FROM entries WHERE kind = ? ORDER BY id DESC", (kind,)).fetchall()
    return [dict(json.loads(r["data"]), created=r["created"]) for r in rows]


def tr(key):
    return TEXT[session.get("lang", "en")].get(key, key)


@app.context_processor
def inject():
    return {"t": tr, "lang": session.get("lang", "en"), "doc_types": DOC_TYPES}


@app.before_request
def need_language():
    if "lang" not in session and request.endpoint not in ("choose", "set_lang", "static"):
        return redirect(url_for("choose"))


def form_page(kind, title, fields):
    if request.method == "POST":
        data = {f[0]: request.form.get(f[0], "").strip()[:500] for f in fields}
        if all(data[f[0]] for f in fields if f[3]):
            save(kind, data)
            flash(tr("thanks"))
            return redirect(request.path)
        flash(tr("required"))
    return render_template("form.html", title=title, fields=fields)


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/choose")
def choose():
    return render_template("choose.html")


@app.route("/lang/<code>")
def set_lang(code):
    if code in TEXT:
        session["lang"] = code
    back = request.referrer
    return redirect(back if back and "/choose" not in back else url_for("home"))


@app.route("/found")
def found():
    docs = load("found_doc")
    for d in docs:  # hide the owner's name: "Jean Kamali" -> "J*** K***"
        d["owner"] = " ".join(w[0] + "***" for w in d["owner"].split())
    return render_template("found.html", docs=docs)


@app.route("/report-lost", methods=["GET", "POST"])
def report_lost():
    return form_page("lost", "report_lost", LOST)


@app.route("/report-found", methods=["GET", "POST"])
def report_found():
    return form_page("found", "report_found", FOUND)


@app.route("/help", methods=["GET", "POST"])
def help_desk():
    return form_page("help", "help", HELP)


@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        if hmac.compare_digest(request.form.get("password", "").encode(), ADMIN_PASSWORD.encode()):
            session["admin"] = True
        else:
            flash(tr("wrong_password"))
        return redirect(url_for("admin"))
    if not session.get("admin"):
        return render_template("admin.html", logged_in=False)
    groups = [("lost_reports", load("lost")), ("found_reports", load("found")),
              ("help_questions", load("help"))]
    return render_template("admin.html", logged_in=True, groups=groups)


@app.route("/admin/add", methods=["GET", "POST"])
def admin_add():
    if not session.get("admin"):
        return redirect(url_for("admin"))
    return form_page("found_doc", "add_found", ADMIN_ADD)


@app.route("/admin/logout")
def admin_logout():
    session.pop("admin", None)
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run()
