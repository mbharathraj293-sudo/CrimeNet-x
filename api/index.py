"""
Vercel Serverless Function entry point for CRIMENET-X FastAPI application.
Exposes the ASGI app instance for Vercel's Python runtime.
"""
import os
import sys

# Ensure repository root is on sys.path so 'backend' modules import seamlessly
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from backend.main import app
