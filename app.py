from flask import Flask, request, jsonify, render_template

from graph.builder import build_graph
from config import LLM_PROVIDER, MODEL_NAME, PORT

app = Flask(__name__)
agent = build_graph()


@app.route("/", methods=["GET"])
def index():
    return render_template(
        "index.html",
        provider=LLM_PROVIDER,
        model=MODEL_NAME,
        port=PORT
    )


@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "online",
        "service": "papermind-ai",
        "provider": LLM_PROVIDER,
        "model": MODEL_NAME,
        "port": PORT,

        "endpoints": {
            "POST /analyze": {
                "body": {"paper_url": "https://arxiv.org/abs/1706.03762"}
            }
        }
    })



@app.route("/analyze", methods=["POST"])
def analyze():
    paper_url = None
    pdf_bytes = None
    filename = None

    # 1. Check if multipart/form-data (File Upload or Form field)
    if "file" in request.files:
        uploaded_file = request.files["file"]
        if uploaded_file and uploaded_file.filename:
            filename = uploaded_file.filename
            pdf_bytes = uploaded_file.read()
            paper_url = filename
    
    if not pdf_bytes:
        # Check form data or JSON body
        if request.form and "paper_url" in request.form:
            paper_url = request.form.get("paper_url")
        elif request.is_json:
            data = request.get_json(silent=True) or {}
            paper_url = data.get("paper_url")

    if not paper_url and not pdf_bytes:
        return jsonify({"error": "Please provide either a 'paper_url' or upload a PDF 'file'."}), 400

    initial_state = {
        "attempt": 0,
        "paper_url": paper_url,
    }
    if pdf_bytes:
        initial_state["pdf_bytes"] = pdf_bytes
        initial_state["filename"] = filename

    try:
        result = agent.invoke(initial_state)
        # Remove raw bytes from response payload
        if "pdf_bytes" in result:
            del result["pdf_bytes"]
        return jsonify(result)
    except Exception as e:
        return jsonify({
            "error": str(e),
            "paper_url": paper_url,
            "status": "failed"
        }), 500



if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=PORT)


