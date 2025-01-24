import os
import shutil
import sys

def organize_files(new_subfolder):
    # Get the current working directory
    parent_dir = os.getcwd()

    # List all subfolders in the parent directory
    subfolders = [f.path for f in os.scandir(parent_dir) if f.is_dir()]

    for subfolder in subfolders:
        # Create the new subfolder inside each subfolder
        new_subfolder_path = os.path.join(subfolder, new_subfolder)
        os.makedirs(new_subfolder_path, exist_ok=True)

        # Move all files from the current subfolder to the new subfolder
        for item in os.listdir(subfolder):
            item_path = os.path.join(subfolder, item)
            if os.path.isfile(item_path):
                shutil.move(item_path, new_subfolder_path)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script_name.py <new_subfolder_name>")
        sys.exit(1)

    new_subfolder_name = sys.argv[1]
    organize_files(new_subfolder_name)
