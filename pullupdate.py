import os
import shutil
import subprocess
import tempfile
import argparse
import sys

def read_gitignore():
    ignore_list = set()
    if os.path.isfile(".gitignore"):
        with open(".gitignore", "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    ignore_list.add(line)
    return ignore_list

def copy_all(src, dst, ignored):
    for root, dirs, files in os.walk(src):
        rel_path = os.path.relpath(root, src)
        dst_root = os.path.join(dst, rel_path) if rel_path != '.' else dst

        os.makedirs(dst_root, exist_ok=True)

        for file in files:
            rel_file = os.path.normpath(os.path.join(rel_path, file))
            if any(rel_file.startswith(pattern) for pattern in ignored):
                continue
            shutil.copy2(os.path.join(root, file), os.path.join(dst_root, file))

def main():
    parser = argparse.ArgumentParser(description="Update current folder from a GitHub repo.")
    parser.add_argument("repo", help="Git repository URL to pull from")
    args = parser.parse_args()

    print("WARNING: This will overwrite any files in the current directory unless they are listed in .gitignore.")
    input("Press Enter to continue or Ctrl+C to cancel...")
    
    tmp_dir = tempfile.mkdtemp()
    try:
        print(f"Chaning active directory to {os.path.dirname(os.path.abspath(__file__))}")
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        print("Cloning repo...")
        subprocess.run(["git", "clone", "--depth", "1", args.repo, tmp_dir], check=True)

        print("Copying files (ignoring .gitignore patterns)...")
        ignore_patterns = read_gitignore()
        copy_all(tmp_dir, ".", ignore_patterns)

        print("Update complete.")
    except subprocess.CalledProcessError:
        print("❌ Failed to clone the repo. Make sure Git is installed and the URL is correct.")
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

if __name__ == "__main__":
    main()
