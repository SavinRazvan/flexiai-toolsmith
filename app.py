# FILE: app.py

import logging
import uuid
import os
import csv
from quart import (
    Quart, render_template, request, g,
    Response, redirect, url_for, jsonify
)

from flexiai.config.models import GeneralSettings
from flexiai.config.logging_config import setup_logging
import flexiai.controllers.quart_chat_controller as qcc

# ─── Logging Configuration ───────────────────────────────────────────────
setup_logging(
    root_level=logging.DEBUG,
    file_level=logging.DEBUG,
    console_level=logging.ERROR,
    enable_file_logging=True,
    enable_console_logging=True
)
logger = logging.getLogger(__name__)
logger.info("⏱️ [app.py] Starting Quart app...")

# ─── Load & validate environment settings ───────────────────────────────
settings = GeneralSettings()

# ─── Create Quart App ────────────────────────────────────────────────────
app = Quart(
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/static"
)

# ─── Mount chat Blueprint ────────────────────────────────────────────────
app.register_blueprint(qcc.chat_bp, url_prefix="/chat")
logger.debug("✔️ [app.py] Registered chat Blueprint at /chat")

# ─── One‐time Controller Initialization ─────────────────────────────────
@app.before_serving
async def initialize_controller() -> None:
    """
    One‐time initialization of the QuartChatController singleton.
    """
    if qcc.controller_instance is not None:
        logger.debug("[initialize_controller] Controller already initialized, skipping.")
        return

    assistant_id = settings.ASSISTANT_ID
    logger.info("[initialize_controller] Initializing QuartChatController for '%s'.", assistant_id)

    # create_async reads settings.ASSISTANT_ID internally
    controller = await qcc.QuartChatController.create_async()
    qcc.controller_instance = controller

    logger.info("✅ [initialize_controller] Controller initialized for assistant '%s'", assistant_id)

# ─── Per‐request User ID Management ──────────────────────────────────────
@app.before_request
async def load_user() -> None:
    """
    Determine user_id for this session:
      1) If USER_ID is set in .env, always use that.
      2) Otherwise, look for a cookie.
      3) If neither, generate a new UUID.
    """
    if settings.USER_ID:
        g.user_id = settings.USER_ID
    else:
        uid = request.cookies.get("user_id")
        if not uid:
            uid = str(uuid.uuid4())
        g.user_id = uid

@app.after_request
async def save_user(response: Response) -> Response:
    """
    Persist cookie-based user_id if USER_ID is not set in .env.
    """
    if not settings.USER_ID and not request.cookies.get("user_id"):
        response.set_cookie("user_id", g.user_id, httponly=True)
    return response

# ─── Template Context ───────────────────────────────────────────────────
@app.context_processor
def inject_ids():
    """
    Inject user_id and assistant_id into every template context.
    """
    return {
        "user_id":      g.user_id,
        "assistant_id": settings.ASSISTANT_ID
    }

# ─── Public Landing Page ─────────────────────────────────────────────────
@app.route("/", methods=["GET"])
async def home():
    """
    Render the public landing page.
    """
    logger.debug("[home] Rendering index.html (assistant_id=%s)", settings.ASSISTANT_ID)
    return await render_template("index.html")

# ─── Error Handlers ──────────────────────────────────────────────────────
@app.errorhandler(404)
async def handle_404(err):
    logger.info("[handle_404] 404 Not Found: %s", request.path)
    return "Page not found", 404

@app.errorhandler(500)
async def handle_500(err):
    logger.exception("💥 [handle_500] Internal Server Error: %s", err)
    return "Internal server error", 500

# ─── User Info Submission Endpoint ───────────────────────────────────────
@app.route("/submit_user_info", methods=["POST"])
async def submit_user_info():
    """
    Accept either AJAX JSON or form-encoded POST and append to CSV.
    """
    logger.info("[submit_user_info] Called")
    is_ajax = request.headers.get("Content-Type", "").startswith("application/json")
    payload = await request.get_json() if is_ajax else await request.form

    first = payload.get("first_name", "").strip()
    last = payload.get("last_name", "").strip()
    radio = payload.get("radio_choice", "")
    # Normalize checkbox to always be "true" or "false"
    raw_checkbox = payload.get("checkbox_choice")
    checkbox = "true" if str(raw_checkbox).lower() == "true" else "false"
    notes = payload.get("text_area", "")

    if not first or not last:
        msg = "Both first and last name are required."
        logger.warning("[submit_user_info] Validation failed: %s", msg)
        if is_ajax:
            return jsonify(status=False, message=msg), 400
        return msg, 400

    csv_dir = os.path.join(os.getcwd(), "flexiai", "toolsmith", "data", "csv")
    os.makedirs(csv_dir, exist_ok=True)
    csv_path = os.path.join(csv_dir, "user_submissions.csv")

    # Create file with header if it doesn't exist, quoting all fields
    if not os.path.isfile(csv_path):
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(
                f,
                lineterminator="\n",
                quoting=csv.QUOTE_ALL
            )
            writer.writerow([
                "first_name",
                "last_name",
                "radio_choice",
                "checkbox_choice",
                "text_area"
            ])
        logger.info("[submit_user_info] Created new CSV with header")

    # Append data row, quoting all fields
    with open(csv_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(
            f,
            lineterminator="\n",
            quoting=csv.QUOTE_ALL
        )
        writer.writerow([first, last, radio, checkbox, notes])
    logger.info("[submit_user_info] Appended submission for %s %s", first, last)

    if is_ajax:
        return jsonify(status=True, message="Thanks, we got it!"), 200
    return redirect(url_for("chat.render_chat_page"))

# ─── Entrypoint ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True, use_reloader=False)
