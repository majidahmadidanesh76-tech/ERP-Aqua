@echo off
cd /d E:\ERP-Aqua
python smart_rules.py
echo %date% %time% >> smart_rules_log.txt