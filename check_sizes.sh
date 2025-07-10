#!/bin/bash
cd backend
uv pip install --dry-run -r ../requirements.txt 2>&1 | grep -E "━|MB|GB" | head -30