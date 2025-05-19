# FILE: app.py

import logging
import uuid
import os
import csv
from quart import (
    Quart, render_template, request, g,
    Response, redirect, url_for, jsonify
)

from flexiai.config.logging_config import setup_logging
from flexiai.controllers.quart_chat_controller import chat_bp, QuartChatController

# ─── Logging Configuration ───────────────────────────────────────────────
setup_logging(
    root_level=logging.DEBUG,
    file_level=logging.DEBUG,
    console_level=logging.ERROR,
    enable_file_logging=True,
    enable_console_logging=True
)
logger = logging.getLogger(__name__)
logger.info("⏱️  Starting Quart app...")

# ─── Create Quart App ────────────────────────────────────────────────────
app = Quart(
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/static"
)

# Mount all chat‐related routes under /chat
app.register_blueprint(chat_bp, url_prefix="/chat")
logger.debug("✔️  Registered chat Blueprint at /chat")

# ─── Global State ───────────────────────────────────────────────────────
ASSISTANT_ID: str | None = None

# ─── One‐time Controller Initialization ─────────────────────────────────
@app.before_serving
async def initialize_controller() -> None:
    """
    One‐time initialization of the QuartChatController singleton.
    """
    import flexiai.controllers.quart_chat_controller as qcc

    if qcc.controller_instance is not None:
        logger.debug("Controller already initialized, skipping.")
        return

    # Choose your assistant ID here (or pull from ENV, config, etc.)
    selected_assistant = 'asst_SbnReaK3gT3h2V19X1cJKXqk'

    logger.info("Initializing QuartChatController for '%s' …", selected_assistant)
    controller = await QuartChatController.create_async(selected_assistant)
    qcc.controller_instance = controller

    global ASSISTANT_ID
    ASSISTANT_ID = controller.assistant_id
    logger.info("✅  Controller initialized for assistant '%s'", ASSISTANT_ID)

# ─── Per‐request User ID Management ──────────────────────────────────────
@app.before_request
async def load_user() -> None:
    """
    Ensure each request has a user_id, loading from cookie or generating a new UUID.
    """
    uid = request.cookies.get("user_id")
    if not uid:
        uid = str(uuid.uuid4())
    g.user_id = uid

@app.after_request
async def save_user(response: Response) -> Response:
    """
    If we generated a new user_id this request, set it as a cookie.
    """
    if not request.cookies.get("user_id"):
        response.set_cookie("user_id", g.user_id, httponly=True)
    return response

# ─── Template Context ───────────────────────────────────────────────────
@app.context_processor
def inject_ids():
    """
    Inject user_id and assistant_id into every template context.
    """
    return {
        "user_id": g.user_id,
        "assistant_id": ASSISTANT_ID
    }

# ─── Public Landing Page ─────────────────────────────────────────────────
@app.route("/", methods=["GET"])
async def home():
    """
    Render the public landing page.
    """
    logger.debug("Rendering index.html (assistant_id=%s)", ASSISTANT_ID)
    return await render_template("index.html")

# ─── Error Handlers ──────────────────────────────────────────────────────
@app.errorhandler(404)
async def handle_404(err):
    logger.info("404 Not Found: %s", request.path)
    # logger.warning("404 Not Found: %s", err)
    return "Page not found", 404

@app.errorhandler(500)
async def handle_500(err):
    logger.exception("💥 Internal Server Error: %s", err)
    return "Internal server error", 500


# ─── User Info Submission Endpoint ───────────────────────────────────────
@app.route("/submit_user_info", methods=["POST"])
async def submit_user_info():
    """
    Accept either:
      - AJAX POST with JSON (application/json)
      - Classic form POST (application/x-www-form-urlencoded)

    Saves first_name, last_name, radio_choice, checkbox_choice, text_area
    into flexiai/toolsmith/data/csv/user_submissions.csv. Returns JSON on AJAX,
    or redirects back to chat on classic form submit.
    """
    logger.info("[submit_user_info] Called")
    content_type = request.headers.get("Content-Type", "")
    is_ajax = content_type.startswith("application/json")

    # 1) Parse payload
    if is_ajax:
        payload = await request.get_json()
    else:
        form = await request.form
        payload = form

    logger.debug("[submit_user_info] Payload: %s", payload)

    first    = payload.get("first_name", "").strip()
    last     = payload.get("last_name", "").strip()
    radio    = payload.get("radio_choice", "")
    checkbox = payload.get("checkbox_choice", "")
    notes    = payload.get("text_area", "")

    # 2) Validate
    if not first or not last:
        msg = "Both first and last name are required."
        logger.warning("[submit_user_info] Validation failed: %s", msg)
        if is_ajax:
            return jsonify(status=False, message=msg), 400
        return msg, 400

    # 3) Build CSV path under flexiai/toolsmith/data/csv
    csv_dir  = os.path.join(os.getcwd(), "flexiai", "toolsmith", "data", "csv")
    os.makedirs(csv_dir, exist_ok=True)
    csv_path = os.path.join(csv_dir, "user_submissions.csv")
    logger.debug("[submit_user_info] Writing to CSV at %s", csv_path)

    # 4) Write header if new
    if not os.path.isfile(csv_path):
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f, lineterminator="\n")
            writer.writerow([
                "first_name",
                "last_name",
                "radio_choice",
                "checkbox_choice",
                "text_area"
            ])
        logger.info("[submit_user_info] Created new CSV with header")

    # 5) Append submission
    with open(csv_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerow([first, last, radio, checkbox, notes])
    logger.info("[submit_user_info] Appended submission for %s %s", first, last)

    # 6) Respond
    if is_ajax:
        return jsonify(status=True, message="Thanks, we got it!"), 200

    # classic form: go back into the chat UI
    return redirect(url_for("chat.render_chat_page"))



# ─── Entrypoint ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True, use_reloader=False)
