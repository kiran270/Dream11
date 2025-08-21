#!/usr/bin/env python3
"""
Script to fix the corrupted checkapp_backup.py file by replacing the getTeams function
"""

# Read the original working getTeams function
with open('original_getTeams.py', 'r') as f:
    clean_function = f.read()

# Read the current checkapp_backup.py file
with open('checkapp_backup.py', 'r') as f:
    lines = f.readlines()

# Find the start and end of the getTeams function
start_line = None
end_line = None

for i, line in enumerate(lines):
    if line.strip().startswith('def getTeams('):
        start_line = i
    elif start_line is not None and line.strip().startswith('def save_teams_to_file('):
        end_line = i
        break

if start_line is not None and end_line is not None:
    print(f"Found getTeams function from line {start_line + 1} to {end_line}")
    
    # Replace the corrupted function with the clean one
    new_lines = (
        lines[:start_line] +  # Everything before getTeams
        [clean_function + '\n\n'] +  # Clean getTeams function
        lines[end_line:]  # Everything after getTeams (starting with save_teams_to_file)
    )
    
    # Write the fixed file
    with open('checkapp_backup.py', 'w') as f:
        f.writelines(new_lines)
    
    print("✅ Successfully replaced the corrupted getTeams function in checkapp_backup.py!")
    print("🎯 The backup file should now work without syntax errors")
else:
    print("❌ Could not find the getTeams function boundaries")