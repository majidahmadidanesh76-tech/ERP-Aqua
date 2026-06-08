"""
دیالوگ افزودن/ویرایش وظیفه برای برنامه پرورش و نت
"""

from PyQt5 import QtWidgets, QtCore
import qtawesome as qta

from ...widgets.jalali_date_edit import JalaliDateEdit
from ...database.db_handler import DatabaseHandler
from .task_template_dialog import TaskTemplateDialog


class TaskDialog(QtWidgets.QDialog):
    def __init__(self, parent=None, plan_id=None, is_maintenance=False, task=None):
        super().__init__(parent)
        
        self.db = DatabaseHandler()
        self.plan_id = plan_id
        self.is_maintenance = is_maintenance
        self.task = task
        self.templates = []
        
        self.setWindowTitle("➕ افزودن وظیفه جدید" if not task else "✏️ ویرایش وظیفه")
        self.setModal(True)
        self.resize(540, 580)
        
        self.load_templates()
        self.setup_ui()
        if task:
            self.load_task_data()

    def load_templates(self):
        """بارگذاری الگوهای وظایف از دیتابیس"""
        self.templates = self.db.fetch_all("SELECT * FROM task_templates ORDER BY name")

    def refresh_templates_combo(self):
        """بازخوانی کامبوباکس الگوها"""
        if not hasattr(self, 'template_combo'):
            return
            
        current_data = self.template_combo.currentData()
        self.template_combo.clear()
        self.template_combo.addItem("--- انتخاب الگو ---", None)
        
        for tpl in self.templates:
            self.template_combo.addItem(tpl.get('name', ''), tpl)
        
        if current_data:
            for i in range(self.template_combo.count()):
                if self.template_combo.itemData(i) == current_data:
                    self.template_combo.setCurrentIndex(i)
                    break

    def setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        field_style = """
            QLineEdit, QTextEdit, QComboBox, QSpinBox, QTimeEdit {
                background-color: #3C3C3F;
                border: 1px solid #4A4A4F;
                border-radius: 4px;
                padding: 7px 10px;
                color: #FFFFFF;
                font-size: 12px;
                min-height: 32px;
            }
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QSpinBox:focus, QTimeEdit:focus {
                border-color: #569CD6;
                background-color: #45454A;
            }
            QTextEdit {
                min-height: 70px;
                max-height: 70px;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox QAbstractItemView {
                background-color: #3C3C3F;
                color: #FFFFFF;
                selection-background-color: #0E639C;
            }
            QSpinBox::up-button, QSpinBox::down-button,
            QTimeEdit::up-button, QTimeEdit::down-button {
                width: 18px;
                background-color: #3C3C3F;
            }
            QSpinBox::up-button:hover, QSpinBox::down-button:hover,
            QTimeEdit::up-button:hover, QTimeEdit::down-button:hover {
                background-color: #569CD6;
            }
        """
        
        label_style = """
            QLabel {
                color: #C8C8C8;
                font-size: 12px;
                background-color: transparent;
                border: none;
            }
        """
        
        btn_style = """
            QPushButton {
                background-color: #3C3C3F;
                color: #C8C8C8;
                border: 1px solid #4A4A4F;
                border-radius: 4px;
                font-weight: bold;
                padding: 7px 14px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #4A4A4F;
                border-color: #569CD6;
                color: white;
            }
        """
        
        cancel_btn_style = """
            QPushButton {
                background-color: #3C3C3F;
                color: #C8C8C8;
                border: 1px solid #4A4A4F;
                border-radius: 4px;
                font-weight: bold;
                padding: 7px 14px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #4A4A4F;
                border-color: #F48771;
                color: #F48771;
            }
        """
        
        icon_style = """
            QToolButton {
                background-color: #3C3C3F;
                border: 1px solid #4A4A4F;
                border-radius: 3px;
            }
            QToolButton:hover {
                background-color: #4A4A4F;
                border-color: #569CD6;
            }
        """

        # ========== بخش الگوهای تکراری ==========
        template_widget = QtWidgets.QWidget()
        template_widget.setStyleSheet("background-color: transparent;")
        template_layout = QtWidgets.QHBoxLayout(template_widget)
        template_layout.setSpacing(8)
        template_layout.setContentsMargins(0, 0, 0, 0)

        template_label = QtWidgets.QLabel("الگو:")
        template_label.setStyleSheet("color: #4EC9B0; font-weight: bold; min-width: 40px; background-color: transparent;")
        template_label.setAlignment(QtCore.Qt.AlignRight)
        template_layout.addWidget(template_label)

        self.template_combo = QtWidgets.QComboBox()
        self.template_combo.setMinimumWidth(280)
        self.template_combo.setStyleSheet(field_style)
        self.template_combo.addItem("--- انتخاب الگو ---", None)
        for tpl in self.templates:
            self.template_combo.addItem(tpl.get('name', ''), tpl)
        self.template_combo.currentIndexChanged.connect(self.on_template_selected)
        template_layout.addWidget(self.template_combo, 1)
        
        self.add_template_btn = QtWidgets.QToolButton()
        self.add_template_btn.setIcon(qta.icon('fa5s.plus', color='#4EC9B0'))
        self.add_template_btn.setIconSize(QtCore.QSize(14, 14))
        self.add_template_btn.setToolTip("افزودن الگو")
        self.add_template_btn.setFixedSize(28, 28)
        self.add_template_btn.setStyleSheet(icon_style)
        self.add_template_btn.clicked.connect(self.add_template)
        template_layout.addWidget(self.add_template_btn)
        
        self.edit_template_btn = QtWidgets.QToolButton()
        self.edit_template_btn.setIcon(qta.icon('fa5s.edit', color='#569CD6'))
        self.edit_template_btn.setIconSize(QtCore.QSize(14, 14))
        self.edit_template_btn.setToolTip("ویرایش الگو")
        self.edit_template_btn.setFixedSize(28, 28)
        self.edit_template_btn.setStyleSheet(icon_style)
        self.edit_template_btn.clicked.connect(self.edit_template)
        self.edit_template_btn.setEnabled(False)
        template_layout.addWidget(self.edit_template_btn)
        
        self.delete_template_btn = QtWidgets.QToolButton()
        self.delete_template_btn.setIcon(qta.icon('fa5s.trash-alt', color='#F48771'))
        self.delete_template_btn.setIconSize(QtCore.QSize(14, 14))
        self.delete_template_btn.setToolTip("حذف الگو")
        self.delete_template_btn.setFixedSize(28, 28)
        self.delete_template_btn.setStyleSheet(icon_style)
        self.delete_template_btn.clicked.connect(self.delete_template)
        self.delete_template_btn.setEnabled(False)
        template_layout.addWidget(self.delete_template_btn)
        
        layout.addWidget(template_widget)

        # ========== خط جداکننده ==========
        line = QtWidgets.QFrame()
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setStyleSheet("background-color: #4A4A4F; margin: 8px 0;")
        layout.addWidget(line)

        # ========== فرم اصلی ==========
        form_widget = QtWidgets.QWidget()
        form_widget.setStyleSheet("background-color: transparent;")
        form_layout = QtWidgets.QFormLayout(form_widget)
        form_layout.setLabelAlignment(QtCore.Qt.AlignRight)
        form_layout.setSpacing(12)
        form_layout.setContentsMargins(0, 0, 0, 0)

        self.title_edit = QtWidgets.QLineEdit()
        self.title_edit.setPlaceholderText("عنوان وظیفه")
        self.title_edit.setStyleSheet(field_style)
        form_layout.addRow("عنوان:", self.title_edit)

        self.desc_edit = QtWidgets.QTextEdit()
        self.desc_edit.setPlaceholderText("توضیحات...")
        self.desc_edit.setStyleSheet(field_style)
        form_layout.addRow("توضیحات:", self.desc_edit)

        self.scheduled_date = JalaliDateEdit()
        form_layout.addRow("تاریخ:", self.scheduled_date)

        self.start_time = QtWidgets.QTimeEdit()
        self.start_time.setTime(QtCore.QTime(8, 0))
        self.start_time.setDisplayFormat("HH:mm")
        self.start_time.setWrapping(True)
        self.start_time.setMinimumTime(QtCore.QTime(0, 0))
        self.start_time.setMaximumTime(QtCore.QTime(23, 59))
        self.start_time.setAlignment(QtCore.Qt.AlignCenter)
        self.start_time.setStyleSheet(field_style)
        form_layout.addRow("ساعت:", self.start_time)

        self.duration = QtWidgets.QSpinBox()
        self.duration.setRange(15, 1440)
        self.duration.setSuffix(" دقیقه")
        self.duration.setValue(60)
        self.duration.setAlignment(QtCore.Qt.AlignCenter)
        self.duration.setStyleSheet(field_style)
        form_layout.addRow("مدت:", self.duration)

        self.responsible = QtWidgets.QLineEdit()
        self.responsible.setPlaceholderText("واحد مسئول")
        self.responsible.setStyleSheet(field_style)
        form_layout.addRow("مسئول:", self.responsible)

        self.priority = QtWidgets.QComboBox()
        self.priority.addItems(["1 - بالا", "2 - متوسط", "3 - پایین"])
        self.priority.setStyleSheet(field_style)
        form_layout.addRow("اولویت:", self.priority)

        layout.addWidget(form_widget)

        # ========== دکمه‌ها ==========
        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.setSpacing(12)
        btn_layout.addStretch()

        ok_btn = QtWidgets.QPushButton("ذخیره")
        ok_btn.setFixedSize(90, 34)
        ok_btn.setStyleSheet(btn_style)
        ok_btn.clicked.connect(self.accept)

        cancel_btn = QtWidgets.QPushButton("انصراف")
        cancel_btn.setFixedSize(90, 34)
        cancel_btn.setStyleSheet(cancel_btn_style)
        cancel_btn.clicked.connect(self.reject)

        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

        for i in range(form_layout.rowCount()):
            label_item = form_layout.itemAt(i, form_layout.LabelRole)
            if label_item and label_item.widget():
                label_item.widget().setStyleSheet(label_style)

    def on_template_selected(self, index):
        template = self.template_combo.currentData()
        self.edit_template_btn.setEnabled(template is not None)
        self.delete_template_btn.setEnabled(template is not None)
        
        if template:
            self.title_edit.setText(template.get('name', ''))
            self.desc_edit.setText(template.get('description', ''))
            self.duration.setValue(template.get('default_duration_minutes', 60))
            self.responsible.setText(template.get('default_assigned_to', ''))

    def add_template(self):
        dialog = TaskTemplateDialog(self, db=self.db)
        if dialog.exec_():
            data = dialog.get_data()
            try:
                self.db.execute_query("""
                    INSERT INTO task_templates (name, category, default_duration_minutes, default_assigned_to, description)
                    VALUES (%s, %s, %s, %s, %s)
                """, (data['name'], data['category'], data['duration'], data['assigned_to'], data['description']))
                self.load_templates()
                self.refresh_templates_combo()
                QtWidgets.QMessageBox.information(self, "موفق", "الگوی وظیفه اضافه شد")
            except Exception as e:
                QtWidgets.QMessageBox.warning(self, "خطا", f"خطا در ذخیره الگو:\n{str(e)}")

    def edit_template(self):
        template = self.template_combo.currentData()
        if template:
            dialog = TaskTemplateDialog(self, template=template, db=self.db)
            if dialog.exec_():
                data = dialog.get_data()
                try:
                    self.db.execute_query("""
                        UPDATE task_templates 
                        SET name = %s, category = %s, default_duration_minutes = %s, 
                            default_assigned_to = %s, description = %s
                        WHERE id = %s
                    """, (data['name'], data['category'], data['duration'], 
                          data['assigned_to'], data['description'], template['id']))
                    self.load_templates()
                    self.refresh_templates_combo()
                    QtWidgets.QMessageBox.information(self, "موفق", "الگوی وظیفه ویرایش شد")
                except Exception as e:
                    QtWidgets.QMessageBox.warning(self, "خطا", f"خطا در ویرایش الگو:\n{str(e)}")

    def delete_template(self):
        template = self.template_combo.currentData()
        if template:
            reply = QtWidgets.QMessageBox.question(self, "تأیید حذف", 
                f"آیا از حذف الگوی '{template.get('name', '')}' مطمئن هستید؟",
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            if reply == QtWidgets.QMessageBox.Yes:
                try:
                    self.db.execute_query("DELETE FROM task_templates WHERE id = %s", (template['id'],))
                    self.load_templates()
                    self.refresh_templates_combo()
                    QtWidgets.QMessageBox.information(self, "موفق", "الگوی وظیفه حذف شد")
                except Exception as e:
                    QtWidgets.QMessageBox.warning(self, "خطا", f"خطا در حذف الگو:\n{str(e)}")

    def load_task_data(self):
        if self.task:
            self.title_edit.setText(self.task.get('task_title', ''))
            self.desc_edit.setText(self.task.get('task_description', ''))
            
            scheduled_date = self.task.get('scheduled_date', '')
            if scheduled_date and hasattr(scheduled_date, 'strftime'):
                scheduled_date = scheduled_date.strftime('%Y/%m/%d')
            elif scheduled_date and isinstance(scheduled_date, str) and '-' in scheduled_date:
                scheduled_date = scheduled_date.replace('-', '/')
            else:
                scheduled_date = str(scheduled_date) if scheduled_date else ''
            
            self.scheduled_date.set_jalali_date(scheduled_date)
            
            if self.task.get('scheduled_start_time'):
                time_str = str(self.task['scheduled_start_time'])[:5]
                self.start_time.setTime(QtCore.QTime.fromString(time_str, "HH:mm"))
            self.duration.setValue(self.task.get('estimated_duration_minutes', 60))
            self.responsible.setText(self.task.get('assigned_to_unit', '') or self.task.get('assigned_to_team', ''))
            
            priority_map = {1: "1 - بالا", 2: "2 - متوسط", 3: "3 - پایین"}
            priority_text = priority_map.get(self.task.get('priority_level', 2), "2 - متوسط")
            self.priority.setCurrentText(priority_text)

    def accept(self):
        if not self.title_edit.text().strip():
            QtWidgets.QMessageBox.warning(self, "خطا", "لطفاً عنوان وظیفه را وارد کنید")
            return
        if not self.responsible.text().strip():
            QtWidgets.QMessageBox.warning(self, "خطا", "لطفاً مسئول را وارد کنید")
            return

        priority_map = {"1 - بالا": 1, "2 - متوسط": 2, "3 - پایین": 3}
        priority = priority_map.get(self.priority.currentText(), 2)

        scheduled_date = self.scheduled_date.get_jalali_date()

        self.result_data = {
            "task_title": self.title_edit.text().strip(),
            "task_description": self.desc_edit.toPlainText(),
            "category": "other",
            "scheduled_date": scheduled_date,
            "scheduled_start_time": self.start_time.time().toString("hh:mm:ss"),
            "estimated_duration_minutes": self.duration.value(),
            "assigned_to_unit": self.responsible.text().strip(),
            "priority_level": priority
        }

        super().accept()