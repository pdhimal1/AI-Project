"""
Stock Predictor GUI Launcher
This file launches the modern Stock Predictor GUI.

For the new modern interface, use: python stock_predictor_gui.py
"""

import sys
import os

# Import and run the new modern GUI
try:
    import stock_predictor_gui
    stock_predictor_gui.main()
except ImportError as e:
    print(f"Error loading GUI: {e}")
    print("\nPlease ensure all dependencies are installed:")
    print("  pip install -r requirements.txt")
    sys.exit(1)
