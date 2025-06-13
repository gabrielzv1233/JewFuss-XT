import subprocess, argparse, sys, os, shutil, pathlib
cwd = pathlib.Path(__file__).resolve().parent
os.chdir(cwd)

git_path = shutil.which("git")
if git_path is None or not pathlib.Path(git_path).is_file():
    sys.exit("Git is not installed or not on PATH.")

def run(cmd):
    subprocess.run(cmd, check=True)

def ensure_repo(url: str):
    if not (cwd / ".git").is_dir():
        run(["git", "init"])
        run(["git", "remote", "add", "origin", url])
    current = subprocess.check_output(
        ["git", "config", "--get", "remote.origin.url"], text=True
    ).strip()
    if current != url:
        run(["git", "remote", "set-url", "origin", url])

def update(branch: str):
    dirty = (
        subprocess.run(["git", "diff", "--quiet"]).returncode != 0
        or subprocess.run(
            ["git", "ls-files", "--others", "--exclude-standard", "--error-unmatch", "."],
            stdout=subprocess.DEVNULL,
        ).returncode
        == 0
    )
    if dirty:
        run(["git", "stash", "--include-untracked"])

    run(["git", "fetch", "origin", branch])
    try:
        run(["git", "merge", "--ff-only", "--no-edit", "FETCH_HEAD"])
    except subprocess.CalledProcessError:
        run(["git", "merge", "--no-edit", "FETCH_HEAD"])

    if dirty:
        run(["git", "stash", "pop"])

ap = argparse.ArgumentParser(
    description="Pull updates like 'git pull', auto-init repo if needed."
)
ap.add_argument("repo", help="Git repo URL")
ap.add_argument("-b", "--branch", default="main", help="Branch to track (default: main)")
args = ap.parse_args()

ensure_repo(args.repo)
update(args.branch)
print("Changes pulled successfully.")