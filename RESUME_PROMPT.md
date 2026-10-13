# CRIMENET-X — Resume Prompt for Future Sessions

If resuming work on CRIMENET-X in a subsequent session:

1. **Do NOT rebuild from scratch**.
2. Run backend: `python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000`.
3. Verify `http://localhost:8000/api/health`.
4. Inspect `PROJECT_STATUS.md` for current feature status and immediate next tasks.
5. All 9 frontend pages in `frontend/pages/` are operational.
6. Edge simulation exists in `esp32/esp32_simulator.py`.
7. Synthetic datasets exist in `data/synthetic_events.csv`.
8. Adhere strictly to the academic ethical guidelines (Synthetic Data Only, Analytical Pattern Scores, Requires Certified Human Review).
