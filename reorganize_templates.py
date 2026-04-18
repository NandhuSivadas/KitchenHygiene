import os
import shutil

# Root path
root = os.getcwd()

# New master templates folder
master_templates = os.path.join(root, 'templates')
os.makedirs(master_templates, exist_ok=True)

apps = ['Admin', 'Guest', 'User']

for app in apps:
    # Path to original app templates
    app_templates_path = os.path.join(root, app, 'templates', app)
    
    # Path to new master destination
    dest_path = os.path.join(master_templates, app)
    
    if os.path.exists(app_templates_path):
        print(f"Moving {app} templates to master folder...")
        if os.path.exists(dest_path):
            shutil.rmtree(dest_path) # Clean start
        shutil.copytree(app_templates_path, dest_path)
        print(f"SUCCESS: {app} templates moved.")
    else:
        print(f"WARNING: Could not find templates for {app} at {app_templates_path}")

print("\nDone! Templates reorganized! Now update settings.py.")
