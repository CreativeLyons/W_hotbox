import os

# Copies W_hotbox.py and W_hotboxManager.py to the production directory

prod_dir="/mnt/studio/pipeline/packages/nuke_w_hotbox/nuke16/bin"

os.system(f"cp W_hotbox.py {prod_dir}")
os.system(f"cp W_hotboxManager.py {prod_dir}")

print("Files copied to production directory")  

