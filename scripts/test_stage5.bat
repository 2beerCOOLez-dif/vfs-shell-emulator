@echo off
echo Test 12: Stage 5 cp command with deep VFS
python -m src.main --vfs-path data/deep.json --script scripts/stage5_commands.sh
pause