# Installation Guide

## Requirements
- Python 3.10+
- pip
- Windows 10/11 (primary), Linux (secondary)

## Setup Steps
1. Open terminal in project root.
2. Create virtual environment:
   - `python -m venv .venv`
3. Activate:
   - Windows: `.venv\\Scripts\\activate`
   - Linux: `source .venv/bin/activate`
4. Install packages:
   - `pip install -r requirements.txt`
5. Launch:
   - `python main.py`

## Optional
- Install `pytest` test tooling from `requirements.txt`.
- Run tests using `pytest`.
