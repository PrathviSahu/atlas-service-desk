from flask import Blueprint, jsonify, request as flask_request
from ..services.request_service import (
    get_all_requests,
    get_request_by_id,
    create_request,
    update_request,
    get_duplicate_candidates,
    get_priority_suggestion,
)

requests_bp = Blueprint("requests", __name__)


@requests_bp.route("/requests", methods=["GET"])
def list_requests():
    filters = {
        "status": flask_request.args.get("status"),
        "priority": flask_request.args.get("priority"),
        "flag": flask_request.args.get("flag"),
    }
    return jsonify(get_all_requests(filters)), 200


@requests_bp.route("/requests/<request_id>", methods=["GET"])
def get_request(request_id):
    req = get_request_by_id(request_id)
    if not req:
        return jsonify({"error": f"Request {request_id} not found"}), 404
    return jsonify(req), 200


@requests_bp.route("/requests", methods=["POST"])
def create_new_request():
    data = flask_request.get_json()
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400
    try:
        created = create_request(data)
        return jsonify(created), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@requests_bp.route("/requests/<request_id>", methods=["PATCH"])
def update_existing_request(request_id):
    data = flask_request.get_json()
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400
    try:
        updated = update_request(request_id, data)
        if not updated:
            return jsonify({"error": f"Request {request_id} not found"}), 404
        return jsonify(updated), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@requests_bp.route("/requests/<request_id>/duplicates", methods=["GET"])
def get_duplicates(request_id):
    req = get_request_by_id(request_id)
    if not req:
        return jsonify({"error": f"Request {request_id} not found"}), 404
    candidates = get_duplicate_candidates(request_id)
    return jsonify(candidates), 200


@requests_bp.route("/priority-suggestion", methods=["POST"])
def priority_suggestion():
    data = flask_request.get_json()
    if not data or "message" not in data:
        return jsonify({"error": "message field required"}), 400
    return jsonify(get_priority_suggestion(data["message"])), 200
