import sys
from PyQt5 import QtWidgets

try:
    from src.widgets.gantt_chart_widget import EditableGanttWidget
    print("✅ EditableGanttWidget imported successfully")
except ImportError as e:
    print(f"❌ Import error: {e}")
    
    # بررسی وجود فایل
    import os
    if os.path.exists("src/widgets/gantt_chart_widget.py"):
        print("✅ File exists")
    else:
        print("❌ File not found at src/widgets/gantt_chart_widget.py")