@echo off
echo Test 10: Stage 4 commands with deep VFS
python -m src.main --vfs-path data/deep.json --script scripts/stage4_commands.sh
pause