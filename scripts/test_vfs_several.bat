@echo off
echo Test 6: Several files VFS with all commands
python -m src.main --vfs-path data/several_files.json --script scripts/all_commands.sh
pause