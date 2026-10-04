@echo off
echo Test 7: Deep 3-level VFS with all commands
python -m src.main --vfs-path data/deep.json --script scripts/all_commands.sh
pause