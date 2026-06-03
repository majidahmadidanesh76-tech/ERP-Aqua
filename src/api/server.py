"""
سرور API سبک برای ارتباط با موبایل و کارتابل پرسنل
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import json
import os
import hashlib
from datetime import datetime
import threading

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, 'data')
TASKS_FILE = os.path.join(DATA_DIR, 'mobile_tasks.json')
REPORTS_FILE = os.path.join(DATA_DIR, 'mobile_reports.json')
USERS_FILE = os.path.join(DATA_DIR, 'mobile_users.json')

os.makedirs(DATA_DIR, exist_ok=True)

def load_json_file(file_path, default=None):
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return default or []
    return default or []

def save_json_file(file_path, data):
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_tasks():
    return load_json_file(TASKS_FILE, [])

def save_tasks(tasks):
    save_json_file(TASKS_FILE, tasks)

def load_reports():
    return load_json_file(REPORTS_FILE, [])

def save_reports(reports):
    save_json_file(REPORTS_FILE, reports)

def load_users():
    users = load_json_file(USERS_FILE, [])
    if not users:
        users = [
            {"id": 1, "username": "tech1", "password": hashlib.md5("1234".encode()).hexdigest(), "name": "احمدی", "role": "technician", "role_name": "تکنسین تعمیرات"},
            {"id": 2, "username": "op1", "password": hashlib.md5("1234".encode()).hexdigest(), "name": "کریمی", "role": "operator", "role_name": "اپراتور پرورش"},
            {"id": 3, "username": "manager", "password": hashlib.md5("1234".encode()).hexdigest(), "name": "مدیر", "role": "manager", "role_name": "مدیر مزرعه"}
        ]
        save_json_file(USERS_FILE, users)
    return users

def init_sample_tasks():
    tasks = load_tasks()
    if not tasks:
        tasks = [
            {"id": 1, "title": "سرویس ماهانه قفس شماره 3", "description": "بازدید و سرویس سیستم هوادهی قفس 3", "assigned_to": "tech1", "status": "pending", "priority": "high", "due_date": "2026-06-10", "location": "قفس 3", "form_type": "maintenance_report"},
            {"id": 2, "title": "ثبت تلفات روزانه قفس 1", "description": "ثبت آمار تلفات روزانه", "assigned_to": "op1", "status": "pending", "priority": "normal", "due_date": "2026-06-05", "location": "قفس 1", "form_type": "mortality_report"},
            {"id": 3, "title": "نمونه‌برداری از آب قفس 2", "description": "اندازه‌گیری پارامترهای آب", "assigned_to": "op1", "status": "pending", "priority": "normal", "due_date": "2026-06-06", "location": "قفس 2", "form_type": "water_quality_report"},
            {"id": 4, "title": "تعمیر پمپ هوادهی", "description": "پمپ هوادهی قفس 3 دچار مشکل شده", "assigned_to": "tech1", "status": "doing", "priority": "urgent", "due_date": "2026-06-04", "location": "قفس 3", "form_type": "maintenance_report"}
        ]
        save_tasks(tasks)

init_sample_tasks()

@app.route('/mobile')
@app.route('/mobile_app.html')
def serve_mobile_app():
    mobile_file = os.path.join(BASE_DIR, 'mobile_app.html')
    if os.path.exists(mobile_file):
        return send_from_directory(BASE_DIR, 'mobile_app.html')
    return "فایل mobile_app.html یافت نشد"

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    users = load_users()
    hashed_password = hashlib.md5(password.encode()).hexdigest() if password else ""
    for user in users:
        if user['username'] == username and user['password'] == hashed_password:
            return jsonify({"success": True, "user": {"id": user['id'], "name": user['name'], "role": user['role'], "role_name": user['role_name']}})
    return jsonify({"success": False, "message": "نام کاربری یا رمز عبور اشتباه است"})

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    username = request.args.get('username')
    if not username:
        return jsonify({"success": False, "message": "نام کاربری مشخص نشده است"}), 400
    tasks = load_tasks()
    user_tasks = [t for t in tasks if t.get('assigned_to') == username]
    status_map = {'pending': 'در انتظار', 'doing': 'در حال انجام', 'done': 'انجام شده'}
    for task in user_tasks:
        task['status_text'] = status_map.get(task.get('status', 'pending'), 'در انتظار')
    return jsonify({"success": True, "tasks": user_tasks})

@app.route('/api/tasks/<int:task_id>/start', methods=['POST'])
def start_task(task_id):
    tasks = load_tasks()
    for task in tasks:
        if task['id'] == task_id:
            task['status'] = 'doing'
            save_tasks(tasks)
            return jsonify({"success": True, "message": "وظیفه شروع شد"})
    return jsonify({"success": False, "message": "وظیفه یافت نشد"}), 404

@app.route('/api/tasks/<int:task_id>/complete', methods=['POST'])
def complete_task(task_id):
    tasks = load_tasks()
    for task in tasks:
        if task['id'] == task_id:
            task['status'] = 'done'
            save_tasks(tasks)
            return jsonify({"success": True, "message": "وظیفه تکمیل شد"})
    return jsonify({"success": False, "message": "وظیفه یافت نشد"}), 404

@app.route('/api/reports', methods=['POST'])
def submit_report():
    data = request.json
    reports = load_reports()
    new_report = {"id": len(reports) + 1, "task_id": data.get('task_id'), "user": data.get('user'), "form_type": data.get('form_type'), "data": data.get('data'), "submitted_at": datetime.now().isoformat()}
    reports.append(new_report)
    save_reports(reports)
    if new_report['task_id']:
        tasks = load_tasks()
        for task in tasks:
            if task['id'] == new_report['task_id']:
                task['status'] = 'done'
                save_tasks(tasks)
                break
    print(f"📱 گزارش جدید: {new_report['form_type']} توسط {new_report['user']}")
    return jsonify({"success": True, "message": "گزارش ثبت شد", "report_id": new_report['id']})

@app.route('/api/forms/<form_type>', methods=['GET'])
def get_form_template(form_type):
    templates = {
        "maintenance_report": {"title": "گزارش تعمیرات", "fields": [{"name": "equipment", "label": "نام تجهیز", "type": "text", "required": True}, {"name": "issue", "label": "شرح مشکل", "type": "textarea", "required": True}, {"name": "action_taken", "label": "اقدام انجام شده", "type": "textarea", "required": True}, {"name": "cost", "label": "هزینه", "type": "number"}]},
        "mortality_report": {"title": "گزارش تلفات", "fields": [{"name": "cage_id", "label": "شماره قفس", "type": "select", "options": ["1", "2", "3"], "required": True}, {"name": "count", "label": "تعداد تلفات", "type": "number", "required": True}, {"name": "cause", "label": "علت", "type": "select", "options": ["بیماری", "کمبود اکسیژن", "دمای بالا", "نامشخص"], "required": True}]},
        "water_quality_report": {"title": "گزارش کیفیت آب", "fields": [{"name": "cage_id", "label": "شماره قفس", "type": "select", "options": ["1", "2", "3"], "required": True}, {"name": "temperature", "label": "دما", "type": "number", "required": True}, {"name": "dissolved_oxygen", "label": "اکسیژن", "type": "number", "required": True}, {"name": "ph", "label": "pH", "type": "number", "required": True}]}
    }
    template = templates.get(form_type)
    if template:
        return jsonify({"success": True, "form": template})
    return jsonify({"success": False, "message": "فرم یافت نشد"}), 404

def run_server(host='0.0.0.0', port=5000):
    print(f"🚀 سرور API در http://{host}:{port}")
    print(f"📱 موبایل: http://{host}:{port}/mobile")
    app.run(host=host, port=port, debug=False, use_reloader=False, threaded=True)

def start_api_server(host='0.0.0.0', port=5000):
    server_thread = threading.Thread(target=run_server, args=(host, port), daemon=True)
    server_thread.start()
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        print(f"\n📱 از موبایل: http://{local_ip}:{port}/mobile")
        print(f"   کاربران: tech1 / op1 / manager | رمز: 1234\n")
    except:
        pass