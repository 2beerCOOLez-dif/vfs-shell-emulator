@echo off
echo Test 8: Missing VFS file error handling
python -m src.main --vfs-path data/missing.json
pause