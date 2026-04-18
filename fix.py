import os
import shutil

# Path to the Guest app
guest_path = os.path.join(os.getcwd(), 'Guest')
# The "broken" folder name from your screenshot
broken_folder = os.path.join(guest_path, 'templates \ Guest')
# The correct path we want
correct_folder = os.path.join(guest_path, 'templates', 'Guest')

if os.path.exists(broken_folder):
    print(f"Fixing structure in {guest_path}...")
    # Create the nested directory correctly
    os.makedirs(correct_folder, exist_ok=True)
    
    # Move all files from broken folder to correct folder
    for item in os.listdir(broken_folder):
        s = os.path.join(broken_folder, item)
        d = os.path.join(correct_folder, item)
        shutil.move(s, d)
    
    # Remove the old folder
    os.rmdir(broken_folder)
    print("Success! Folders reorganized.")
else:
    print("Could not find the 'templates \\ Guest' folder. Check the folder name manually.")