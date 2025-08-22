from flask import Flask, render_template, request, jsonify, session, abort
from uuid import uuid4
import requests
from werkzeug.middleware.proxy_fix import ProxyFix
from config import settings

app = Flask(__name__)
app.config['SECRET_KEY'] = settings.SECRET_KEY
app.wsgi_app = ProxyFix(app.wsgi_app)

AGENTS = [
    {
        "id": "agent_a",
        "name": "Mr.Sutat",
        "description": "หน่วยทะเบียนและประมวลผล",
        "image_url": "/static/img/sutat_pic.png",
        "webhook": settings.N8N_AGENT_A_URL,
        "enabled": False,  # ← ปิด (ห้ามเข้า)
        # "auth_header": settings.N8N_AGENT_A_AUTH,
    },
    {
        "id": "agent_b",
        "name": "P.Mee Mai",
        "description": "หน่วยจัดการและพัฒนาหลักสูตร",
        "image_url": "/static/img/mee_mai.png",
        "webhook": settings.N8N_AGENT_B_URL,
        "enabled": False,  # ← ปิด (ห้ามเข้า)
        # "auth_header": settings.N8N_AGENT_B_AUTH,
    },
    {
        "id": "agent_c",
        "name": "Mrs. Lord",
        "description": "หน่วยบัณฑิตศึกษา",
        "image_url": "/static/img/lord.png",
        "webhook": settings.N8N_AGENT_C_URL,
        "enabled": True,  # ← ปิด (ห้ามเข้า)
        # "auth_header": settings.N8N_AGENT_C_AUTH,
    },
]

AGENT_MAP = {a["id"]: a for a in AGENTS}


def get_session_id():
    if 'sid' not in session:
        session['sid'] = str(uuid4())
    return session['sid']


@app.route('/')
def home():
    return render_template('index.html', agents=AGENTS)


@app.route('/chat/<agent_id>')
def chat(agent_id):
    agent = AGENT_MAP.get(agent_id)
    if not agent:
        abort(404)
    sid = get_session_id()
    session.setdefault('history', {})
    session['history'].setdefault(agent_id, [])
    session.modified = True
    return render_template('chat.html', agent=agent, sid=sid)


@app.route('/api/chat/<agent_id>', methods=['POST'])
def api_chat(agent_id):
    agent = AGENT_MAP.get(agent_id)
    if not agent:
        return jsonify({"error": "Unknown agent"}), 404

    data = request.get_json(force=True)
    user_message = (data or {}).get('message', '').strip()
    if not user_message:
        return jsonify({"error": "Empty message"}), 400
    
    



    session.setdefault('history', {})
    history = session['history'].setdefault(agent_id, [])
  
    payload = {
        "message": user_message,
  
    }

    headers = {"Content-Type": "application/json"}
    if agent.get("auth_header"):
        headers.update(agent["auth_header"])

    try:
        resp = requests.post(agent['webhook'], json=payload, headers=headers, timeout=60)
        resp.raise_for_status()
        data = resp.json() if resp.headers.get('Content-Type','').startswith('application/json') else {"reply": resp.text}
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"n8n request failed: {e}"}), 502

    bot_reply = data.get('reply') if isinstance(data, dict) else None
    new_history = data.get('history') if isinstance(data, dict) else None

    history.append({"role": "user", "content": user_message})
    if bot_reply:
        history.append({"role": "assistant", "content": bot_reply})
    if new_history and isinstance(new_history, list):
        history = new_history
    session['history'][agent_id] = history
    session.modified = True

    return jsonify({"reply": bot_reply or "(No reply returned from n8n)"})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
