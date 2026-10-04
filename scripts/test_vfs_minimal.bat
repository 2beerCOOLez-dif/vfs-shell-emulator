@echo off
echo Test 5: Minimal VFS with all commands
python -m src.main --vfs-path data/minimal.json --script scripts/all_commands.sh
pause