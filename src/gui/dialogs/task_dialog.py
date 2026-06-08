"""
دیالوگ افزودن/ویرایش وظیفه با قابلیت انتخاب از الگوهای تکراری
نسخه با چیدمان صحیح - لیبل و کامبوباکس در یک ردیف
"""

from PyQt5 import QtWidgets, QtCore
import qtawesome as qta
import mysql.connector

from ...widgets.jalali_date_edit import JalaliDateEdit
from .task_template_dialog import TaskTemplateDialog


class TaskDialog(QtWidgets.QDialog):
    def __init__(self, parent=None, plan_id=None, is_maintenance=False, task=None):
        super().__init__(parent)
        
        self.plan_id = plan_id
        self.is_maintenance = is_maintenance
        self.task = task
        self.templates = []
        
        self.setWindowTitle("➕ افزودن وظیفه جدید" if not task else "✏️ ویرایش وظیفه")
        self.setModal(True)
        self.resize(600, 680)
        
        self.load_templates_direct()
        self.setup_ui()
        if task:
            self.load_task_data()

    def get_db_connection(self):
        try:
            conn = mysql.connector.connect(
                host='localhost',
                user='root',
                password='',
                database='erp_aqua'
            )
            return conn
        except Exception as e:
            print(f"ERROR: خطا در اتصال به دیتابیس: {e}")
            return None

    def load_templates_direct(self):
        conn = self.get_db_connection()
        if conn:
            try:
                cursor = conn.cursor(dictionary=True)
                cursor.execute("SELECT * FROM task_templates ORDER BY name")
                self.templates = cursor.fetchall()
                cursor.close()
                conn.close()
                print(f"DEBUG: تعداد الگوهای بارگذاری شده: {len(self.templates)}")
            except Exception as e:
                print(f"ERROR: خطا در بارگذاری الگوها: {e}")
                self.templates = []
        else:
            self.templates = []

    def refresh_templates_combo(self):
        if not hasattr(self, 'template_combo'):
            return
            
        current_template_id = None
        if self.template_combo.currentIndex() > 0:
            current = self.template_combo.currentData()
            if current:
                current_template_id = current.get('id')
        
        self.template_combo.clear()
        self.template_combo.addItem("--- انتخاب الگو (اختیاری) ---", None)
        
        for tpl in self.templates:
            display_text = f"{tpl.get('name', '')} [{tpl.get('category', '')}]"
            self.template_combo.addItem(display_text, tpl)
        
        if current_template_id:
            for i in range(self.template_combo.count()):
                item_data = self.template_combo.itemData(i)
                if item_data and item_data.get('id') == current_template_id:
                    self.template_combo.setCurrentIndex(i)
                    break

    def execute_db_query(self, query, params=None):
        conn = self.get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                conn.commit()
                cursor.close()
                conn.close()
                return True
            except Exception as e:
                print(f"ERROR: خطا در اجرای کوئری: {e}")
                conn.close()
                return False
        return False

    def get_glass_style(self):
        return """
            QPushButton {
                background-color: rgba(60, 60, 65, 200);
                color: #C8C8C8;
                border: 1px solid rgba(86, 156, 214, 80);
                border-radius: 4px;
                font-weight: bold;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: rgba(86, 156, 214, 100);
                border-color: rgba(86, 156, 214, 150);
                color: white;
            }
        """

    def get_glass_icon_style(self):
        return """
            QToolButton {
                background-color: rgba(60, 60, 65, 180);
                border: 1px solid rgba(86, 156, 214, 80);
                border-radius: 3px;
            }
            QToolButton:hover {
                background-color: rgba(86, 156, 214, 100);
                border-color: rgba(86, 156, 214, 150);
            }
        """

    def setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        glass_style = self.get_glass_style()
        glass_icon_style = self.get_glass_icon_style()

        # ========== بخش الگوهای تکراری (در یک ردیف) ==========
        template_widget = QtWidgets.QWidget()
        template_layout = QtWidgets.QHBoxLayout(template_widget)
        template_layout.setSpacing(10)
        template_layout.setContentsMargins(0, 0, 0, 0)

        template_label = QtWidgets.QLabel("الگوهای تکراری:")
        template_label.setStyleSheet("color: #4EC9B0; font-weight: bold; min-width: 100px;")
        template_label.setAlignment(QtCore.Qt.AlignRight)
        template_layout.addWidget(template_label)

        self.template_combo = QtWidgets.QComboBox()
        self.template_combo.setMinimumWidth(320)
        self.template_combo.setFixedHeight(32)
        self.template_combo.addItem("--- انتخاب الگو (اختیاری) ---", None)
        
        for tpl in self.templates:
            display_text = f"{tpl.get('name', '')} [{tpl.get('category', '')}]"
            self.template_combo.addItem(display_text, tpl)
            
        self.template_combo.currentIndexChanged.connect(self.on_template_selected)
        template_layout.addWidget(self.template_combo, 1)
        
        # دکمه افزودن الگو
        self.add_template_btn = QtWidgets.QToolButton()
        self.add_template_btn.setIcon(qta.icon('fa5s.plus', color='#4EC9B0'))
        self.add_template_btn.setIconSize(QtCore.QSize(16, 16))
        self.add_template_btn.setToolTip("افزودن الگوی جدید")
        self.add_template_btn.setFixedSize(32, 32)
        self.add_template_btn.setStyleSheet(glass_icon_style)
        self.add_template_btn.clicked.connect(self.add_template)
        template_layout.addWidget(self.add_template_btn)
        
        # دکمه ویرایش الگو
        self.edit_template_btn = QtWidgets.QToolButton()
        self.edit_template_btn.setIcon(qta.icon('fa5s.edit', color='#569CD6'))
        self.edit_template_btn.setIconSize(QtCore.QSize(16, 16))
        self.edit_template_btn.setToolTip("ویرایش الگوی انتخاب شده")
        self.edit_template_btn.setFixedSize(32, 32)
        self.edit_template_btn.setStyleSheet(glass_icon_style)
        self.edit_template_btn.clicked.connect(self.edit_template)
        self.edit_template_btn.setEnabled(False)
        template_layout.addWidget(self.edit_template_btn)
        
        # دکمه حذف الگو
        self.delete_template_btn = QtWidgets.QToolButton()
        self.delete_template_btn.setIcon(qta.icon('fa5s.trash-alt', color='#F48771'))
        self.delete_template_btn.setIconSize(QtCore.QSize(16, 16))
        self.delete_template_btn.setToolTip("حذف الگوی انتخاب شده")
        self.delete_template_btn.setFixedSize(32, 32)
        self.delete_template_btn.setStyleSheet(glass_icon_style)
        self.delete_template_btn.clicked.connect(self.delete_template)
        self.delete_template_btn.setEnabled(False)
        template_layout.addWidget(self.delete_template_btn)
        
        layout.addWidget(template_widget)

        # ========== خط جداکننده ==========
        line = QtWidgets.QFrame()
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setStyleSheet("background-color: #3E3E42; margin: 5px 0;")
        layout.addWidget(line)

        # ========== فرم اصلی ==========
        form_widget = QtWidgets.QWidget()
        form_layout = QtWidgets.QFormLayout(form_widget)
        form_layout.setLabelAlignment(QtCore.Qt.AlignRight)
        form_layout.setSpacing(12)
        form_layout.setContentsMargins(0, 0, 0, 0)

        # عنوان وظیفه
        self.title_edit = QtWidgets.QLineEdit()
        self.title_edit.setPlaceholderText("عنوان وظیفه")
        self.title_edit.setMinimumHeight(32)
        self.title_edit.setStyleSheet("""
            QLineEdit {
                background-color: #3C3C3C;
                border: 1px solid #3E3E42;
                border-radius: 4px;
                padding: 8px;
                color: #C8C8C8;
            }
        """)
        form_layout.addRow("عنوان وظیفه:", self.title_edit)

        # توضیحات
        self.desc_edit = QtWidgets.QTextEdit()
        self.desc_edit.setMaximumHeight(80)
        self.desc_edit.setPlaceholderText("توضیحات کامل وظیفه...")
        self.desc_edit.setStyleSheet("""
            QTextEdit {
                background-color: #3C3C3C;
                border: 1px solid #3E3E42;
                border-radius: 4px;
                padding: 8px;
                color: #C8C8C8;
            }
        """)
        form_layout.addRow("توضیحات:", self.desc_edit)

        # دسته‌بندی
        self.category_combo = QtWidgets.QComboBox()
        self.category_combo.addItems(["feeding", "cleaning", "inspection", "repair", "harvest", "water_quality", "other"])
        self.category_combo.setMinimumHeight(32)
        self.category_combo.setStyleSheet("""
            QComboBox {
                background-color: #3C3C3C;
                border: 1px solid #3E3E42;
                border-radius: 4px;
                padding: 8px;
                color: #C8C8C8;
            }
        """)
        form_layout.addRow("دسته‌بندی:", self.category_combo)

        # تاریخ انجام
        self.scheduled_date = JalaliDateEdit()
        self.scheduled_date.setMinimumHeight(32)
        self.scheduled_date.setStyleSheet("""
            QDateEdit {
                background-color: #3C3C3C;
                border: 1px solid #3E3E42;
                border-radius: 4px;
                padding: 6px;
                color: #C8C8C8;
            }
        """)
        form_layout.addRow("تاریخ انجام:", self.scheduled_date)

        # ساعت شروع
        self.start_time = QtWidgets.QTimeEdit()
        self.start_time.setTime(QtCore.QTime(8, 0))
        self.start_time.setMinimumHeight(32)
        self.start_time.setStyleSheet("""
            QTimeEdit {
                background-color: #3C3C3C;
                border: 1px solid #3E3E42;
                border-radius: 4px;
                padding: 6px;
                color: #C8C8C8;
            }
        """)
        form_layout.addRow("ساعت شروع:", self.start_time)

        # مدت زمان
        self.duration = QtWidgets.QSpinBox()
        self.duration.setRange(15, 1440)
        self.duration.setSuffix(" دقیقه")
        self.duration.setValue(60)
        self.duration.setMinimumHeight(32)
        self.duration.setStyleSheet("""
            QSpinBox {
                background-color: #3C3C3C;
                border: 1px solid #3E3E42;
                border-radius: 4px;
                padding: 6px;
                color: #C8C8C8;
            }
        """)
        form_layout.addRow("مدت زمان:", self.duration)

        # مسئول
        self.responsible = QtWidgets.QLineEdit()
        self.responsible.setPlaceholderText("واحد مسئول (مثال: واحد بهره برداری)")
        self.responsible.setMinimumHeight(32)
        self.responsible.setStyleSheet("""
            QLineEdit {
                background-color: #3C3C3C;
                border: 1px solid #3E3E42;
                border-radius: 4px;
                padding: 8px;
                color: #C8C8C8;
            }
        """)
        form_layout.addRow("مسئول:", self.responsible)

        # اولویت
        self.priority = QtWidgets.QComboBox()
        self.priority.addItems(["1 - بالا", "2 - متوسط", "3 - پایین"])
        self.priority.setMinimumHeight(32)
        self.priority.setStyleSheet("""
            QComboBox {
                background-color: #3C3C3C;
                border: 1px solid #3E3E42;
                border-radius: 4px;
                padding: 8px;
                color: #C8C8C8;
            }
        """)
        form_layout.addRow("اولویت:", self.priority)

        layout.addWidget(form_widget)

        # ========== دکمه‌ها ==========
        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.setSpacing(10)
        btn_layout.addStretch()

        ok_btn = QtWidgets.QPushButton("💾 ذخیره وظیفه")
        ok_btn.setFixedSize(120, 38)
        ok_btn.setStyleSheet(glass_style)
        ok_btn.clicked.connect(self.accept)

        cancel_btn = QtWidgets.QPushButton("❌ انصراف")
        cancel_btn.setFixedSize(100, 38)
        cancel_btn.setStyleSheet(glass_style)
        cancel_btn.clicked.connect(self.reject)

        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def on_template_selected(self, index):
        template = self.template_combo.currentData()
        self.edit_template_btn.setEnabled(template is not None)
        self.delete_template_btn.setEnabled(template is not None)
        
        if template:
            self.title_edit.setText(template.get('name', ''))
            self.desc_edit.setText(template.get('description', ''))
            self.duration.setValue(template.get('default_duration_minutes', 60))
            self.responsible.setText(template.get('default_assigned_to', ''))
            category = template.get('category', 'other')
            idx = self.category_combo.findText(category)
            if idx >= 0:
                self.category_combo.setCurrentIndex(idx)

    def add_template(self):
        dialog = TaskTemplateDialog(self, db=None)
        if dialog.exec_():
            data = dialog.get_data()
            result = self.execute_db_query("""
                INSERT INTO task_templates (name, category, default_duration_minutes, default_assigned_to, description)
                VALUES (%s, %s, %s, %s, %s)
            """, (data['name'], data['category'], data['duration'], data['assigned_to'], data['description']))
            
            if result:
                self.load_templates_direct()
                self.refresh_templates_combo()
                QtWidgets.QMessageBox.information(self, "موفق", "الگوی وظیفه با موفقیت اضافه شد")

    def edit_template(self):
        template = self.template_combo.currentData()
        if template:
            dialog = TaskTemplateDialog(self, template=template, db=None)
            if dialog.exec_():
                data = dialog.get_data()
                result = self.execute_db_query("""
                    UPDATE task_templates 
                    SET name = %s, category = %s, default_duration_minutes = %s, 
                        default_assigned_to = %s, description = %s
                    WHERE id = %s
                """, (data['name'], data['category'], data['duration'], data['assigned_to'], 
                      data['description'], template['id']))
                
                if result:
                    self.load_templates_direct()
                    self.refresh_templates_combo()
                    QtWidgets.QMessageBox.information(self, "موفق", "الگوی وظیفه با موفقیت ویرایش شد")

    def delete_template(self):
        template = self.template_combo.currentData()
        if template:
            reply = QtWidgets.QMessageBox.question(self, "تأیید حذف", 
                f"آیا از حذف الگوی '{template.get('name', '')}' مطمئن هستید؟",
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            if reply == QtWidgets.QMessageBox.Yes:
                result = self.execute_db_query("DELETE FROM task_templates WHERE id = %s", (template['id'],))
                if result:
                    self.load_templates_direct()
                    self.refresh_templates_combo()
                    QtWidgets.QMessageBox.information(self, "موفق", "الگوی وظیفه با موفقیت حذف شد")

    def load_task_data(self):
        if self.task:
            self.title_edit.setText(self.task.get('task_title', ''))
            self.desc_edit.setText(self.task.get('task_description', ''))
            idx = self.category_combo.findText(self.task.get('category', 'other'))
            if idx >= 0:
                self.category_combo.setCurrentIndex(idx)
            self.scheduled_date.set_jalali_date(self.task.get('scheduled_date', ''))
            if self.task.get('scheduled_start_time'):
                self.start_time.setTime(QtCore.QTime.fromString(str(self.task['scheduled_start_time'])[:5], "hh:mm"))
            self.duration.setValue(self.task.get('estimated_duration_minutes', 60))
            self.responsible.setText(self.task.get('assigned_to_unit', '') or self.task.get('assigned_to_team', ''))
            priority_map = {"1 - بالا": 1, "2 - متوسط": 2, "3 - پایین": 3}
            for i, (text, val) in enumerate(priority_map.items()):
                if val == self.task.get('priority_level', 2):
                    self.priority.setCurrentIndex(i)
                    break

    def accept(self):
        if not self.title_edit.text().strip():
            QtWidgets.QMessageBox.warning(self, "خطا", "لطفاً عنوان وظیفه را وارد کنید")
            return
        if not self.responsible.text().strip():
            QtWidgets.QMessageBox.warning(self, "خطا", "لطفاً مسئول را وارد کنید")
            return

        priority_map = {"1 - بالا": 1, "2 - متوسط": 2, "3 - پایین": 3}
        priority = priority_map.get(self.priority.currentText(), 2)

        self.result_data = {
            "task_title": self.title_edit.text().strip(),
            "task_description": self.desc_edit.toPlainText(),
            "category": self.category_combo.currentText(),
            "scheduled_date": self.scheduled_date.get_jalali_date(),
            "scheduled_start_time": self.start_time.time().toString("hh:mm:ss"),
            "estimated_duration_minutes": self.duration.value(),
            "assigned_to_unit": self.responsible.text().strip(),
            "priority_level": priority
        }

        super().accept()