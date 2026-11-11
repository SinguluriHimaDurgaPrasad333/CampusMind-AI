#!/bin/bash
PORT="${PORT:-8501}"
python -m streamlit run app.py --server.port "$PORT" --server.address 0.0.0.0 --server.headless true --server.enableCORS false --server.enableXsrfProtection false
