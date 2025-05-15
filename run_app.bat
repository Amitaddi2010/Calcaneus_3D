@echo off
set PYTHONPATH=%PYTHONPATH%;%CD%
python init_db.py
python -m streamlit run app.py --server.port 8503 --server.address localhost 