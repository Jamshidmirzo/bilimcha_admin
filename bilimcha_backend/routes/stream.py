from flask import Blueprint, request, Response, jsonify
import requests
from services.youtube import get_fresh_video_url

stream_bp = Blueprint("stream", __name__)

@stream_bp.route("/<youtube_id>", methods=["GET", "HEAD"])
def stream(youtube_id):
    try:
        video_url = get_fresh_video_url(youtube_id)
        headers = {}
        if rng := request.headers.get("Range"):
            headers["Range"] = rng
        # forward request (stream=True)
        r = requests.get(video_url, headers=headers, stream=True, timeout=30)
        resp_headers = {
            "Content-Type": r.headers.get("Content-Type", "video/mp4"),
            "Content-Length": r.headers.get("Content-Length"),
            "Accept-Ranges": r.headers.get("Accept-Ranges"),
            "Cache-Control": "no-store",
        }
        if cr := r.headers.get("Content-Range"):
            resp_headers["Content-Range"] = cr
        return Response(r.iter_content(chunk_size=8192), status=r.status_code, headers=resp_headers)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
