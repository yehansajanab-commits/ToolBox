from flask import Flask
from flask import jsonify
from flask import request
from flask import url_for
from flask import send_from_directory
from flask_cors import CORS
import os

# delay importing detector until runtime to avoid hard crash at startup
# (helps the app start even if system CV libs are missing; errors handled per-request)
process_image = None
from database import (
    init_db,
    add_items,
    get_items,
    update_missing,
    get_all_boxes,
    delete_box,
    get_box_count,
    get_item_count,
)

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

init_db()


@app.route("/")
def root():
    return jsonify({
        "name": "ToolBox API",
        "status": "ok",
        "routes": [
            "/api/boxes",
            "/api/inventory",
            "/api/handover",
            "/api/receive",
            "/api/clear_box",
        ],
    })


@app.route("/api/boxes")
def api_boxes():
    return jsonify({
        "box_count": get_box_count(),
        "item_count": get_item_count(),
    })



#######################################################
# HANDOVER
#######################################################

@app.route("/api/handover", methods=["POST"])
def api_handover():
    if "image" not in request.files:
        return jsonify({"error": "Missing image file."}), 400

    image = request.files["image"]
    filepath = os.path.join(UPLOAD_FOLDER, image.filename)
    image.save(filepath)

    global process_image
    if process_image is None:
        try:
            from detector import process_image as _proc
            process_image = _proc
        except Exception as e:
            return jsonify({"error": "Image processing unavailable: %s" % str(e)}), 500

    box_no, items, segmented_path = process_image(filepath)
    add_items(box_no, items)

    result = {
        "box_no": box_no,
        "items": items,
        "segmented_url": None,
    }

    if segmented_path:
        result["segmented_url"] = url_for("uploaded_file", filename=segmented_path, _external=True)

    return jsonify(result)


#######################################################
# RECEIVE
#######################################################

@app.route("/api/receive", methods=["POST"])
def api_receive():
    if "image" not in request.files:
        return jsonify({"error": "Missing image file."}), 400

    image = request.files["image"]
    filepath = os.path.join(UPLOAD_FOLDER, image.filename)
    image.save(filepath)

    global process_image
    if process_image is None:
        try:
            from detector import process_image as _proc
            process_image = _proc
        except Exception as e:
            return jsonify({"error": "Image processing unavailable: %s" % str(e)}), 500

    box_no, items, segmented_path = process_image(filepath)
    stored = get_items(box_no)

    missing = list(set(stored) - set(items))
    update_missing(box_no, missing)
    cleared = len(missing) == 0

    result = {
        "box_no": box_no,
        "missing": missing,
        "cleared": cleared,
        "segmented_url": None,
    }

    if segmented_path:
        result["segmented_url"] = url_for("uploaded_file", filename=segmented_path, _external=True)

    return jsonify(result)


#######################################################
# INVENTORY PAGE
#######################################################

@app.route("/api/inventory")
def api_inventory():

    rows = get_all_boxes()
    data = {}

    for box_no, item in rows:
        data.setdefault(box_no, []).append(item)

    return jsonify(data)


@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


@app.route("/api/clear_box", methods=["POST"])
def api_clear_box():
    payload = request.get_json(silent=True) or request.form
    box_no = payload.get("box_no")

    if not box_no:
        return jsonify({"error": "Missing box_no."}), 400

    delete_box(box_no)
    return jsonify({"success": True})


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )