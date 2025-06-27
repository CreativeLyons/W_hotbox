#!/usr/bin/env python3
"""
Script to copy the fixed W_hotbox files to the studio pipeline location.
This script copies W_hotbox.py and W_hotboxManager.py from the current directory
to /mnt/studio/pipeline/packages/nuke_w_hotbox/nuke16/bin/
"""

import os
import shutil
import sys

def copy_hotbox_files():
    # Source directory (current working directory)
    source_dir = os.path.join(os.getcwd(), "W_hotbox_v1.9")
    
    # Destination directory
    dest_dir = "/mnt/studio/pipeline/packages/nuke_w_hotbox/nuke16/bin"
    
    # Files to copy
    files_to_copy = ["W_hotbox.py", "W_hotboxManager.py"]
    
    print(f"Source directory: {source_dir}")
    print(f"Destination directory: {dest_dir}")
    print("-" * 50)
    
    # Check if source directory exists
    if not os.path.exists(source_dir):
        print(f"ERROR: Source directory does not exist: {source_dir}")
        return False
    
    # Check if destination directory exists
    if not os.path.exists(dest_dir):
        print(f"ERROR: Destination directory does not exist: {dest_dir}")
        return False
    
    # Copy each file
    success_count = 0
    for filename in files_to_copy:
        source_file = os.path.join(source_dir, filename)
        dest_file = os.path.join(dest_dir, filename)
        
        if not os.path.exists(source_file):
            print(f"WARNING: Source file not found: {source_file}")
            continue
        
        try:
            # Create backup of existing file if it exists
            if os.path.exists(dest_file):
                backup_file = dest_file + ".backup"
                shutil.copy2(dest_file, backup_file)
                print(f"Created backup: {backup_file}")
            
            # Copy the file
            shutil.copy2(source_file, dest_file)
            print(f"✓ Copied: {filename}")
            success_count += 1
            
        except PermissionError:
            print(f"ERROR: Permission denied copying {filename}")
            print("You may need to run this script with appropriate permissions")
        except Exception as e:
            print(f"ERROR: Failed to copy {filename}: {str(e)}")
    
    print("-" * 50)
    print(f"Successfully copied {success_count} out of {len(files_to_copy)} files")
    
    if success_count == len(files_to_copy):
        print("All files copied successfully!")
        return True
    else:
        print("Some files failed to copy. Check the errors above.")
        return False

if __name__ == "__main__":
    print("W_Hotbox File Copy Script")
    print("=" * 50)
    
    # Check if running from the correct directory
    current_dir = os.getcwd()
    if not os.path.exists(os.path.join(current_dir, "W_hotbox_v1.9")):
        print("ERROR: This script should be run from the directory containing W_hotbox_v1.9/")
        print(f"Current directory: {current_dir}")
        sys.exit(1)
    
    success = copy_hotbox_files()
    
    if success:
        print("\nFiles have been copied successfully!")
        print("The fixed W_hotbox files are now in the studio pipeline location.")
    else:
        print("\nSome errors occurred during the copy operation.")
        sys.exit(1) 