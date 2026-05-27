from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import threading

from lang import tr


def get_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def get_bundle_dir() -> Path:
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        return Path(meipass).resolve()
    return get_base_dir()


def find_bundled_path(filename: str) -> Path:
    candidates = [
        get_bundle_dir() / filename,
        get_base_dir() / filename,
        get_base_dir() / "_internal" / filename,
    ]
    for p in candidates:
        if p.exists():
            return p
    return candidates[0]


def compute_vmt_relative(dest_dir: str) -> str:
    dest = Path(dest_dir)
    parts_lower = [p.lower() for p in dest.parts]

    try:
        idx = parts_lower.index("materials")
        rel_parts = dest.parts[idx + 1:]
        if not rel_parts:
            return ""
        return Path(*rel_parts).as_posix()
    except ValueError:
        return dest.name


def get_config_path() -> Path:
    base_dir = get_base_dir()
    portable = base_dir / "config.json"
    if portable.exists():
        return portable

    appdata = os.environ.get("APPDATA")
    if not appdata:
        return portable

    return Path(appdata) / "VTFMaster" / "config.json"


class VTFMasterGUI:
    def configurer_style(self):
        style = ttk.Style()
        style.theme_use("clam")
        bg_color = "#f5f5f5"
        accent_color = "#3498db"
        action_color = "#2ecc71"
        text_color = "#2c3e50"

        style.configure("TFrame", background=bg_color)
        style.configure("TLabel", background=bg_color, foreground=text_color)
        style.configure("TLabelframe", background=bg_color)
        style.configure(
            "TLabelframe.Label",
            background=bg_color,
            foreground=text_color,
            font=("Helvetica", 9, "bold"),
        )
        style.configure("TButton", font=("Helvetica", 9))

        style.configure("Action.TButton", background=action_color, foreground="white")
        style.map(
            "Action.TButton",
            background=[("active", "#27ae60"), ("pressed", "#27ae60")],
            foreground=[("active", "white"), ("pressed", "white")],
        )

        style.configure("Accent.TButton", background=accent_color, foreground="white")
        style.map(
            "Accent.TButton",
            background=[("active", "#2980b9"), ("pressed", "#2980b9")],
            foreground=[("active", "white"), ("pressed", "white")],
        )

        style.configure("Custom.TEntry", padding=5)
        style.configure("Custom.TCheckbutton", background=bg_color, font=("Helvetica", 9))
        self.root.configure(background=bg_color)

    def __init__(self, root):
        self.root = root
        self.base_dir = get_base_dir()
        self.bundle_dir = get_bundle_dir()
        self.root.title("VTF Master - Convertisseur VTF/VMT")

        try:
            icon_path = find_bundled_path("vtfmaster.ico")
            if icon_path.exists():
                self.root.iconbitmap(str(icon_path))
        except Exception:
            pass

        self.root.minsize(600, 700)
        self.root.geometry("700x800")
        self.configurer_style()

        required_files = {
            "VTFCmd.exe": "VTFCmd.exe est manquant",
            "VTFLib.dll": "VTFLib.dll est manquant",
            "DevIL.dll": "DevIL.dll est manquant",
            "HLLib.dll": "HLLib.dll est manquant",
        }

        missing_files = []
        for file, message in required_files.items():
            p = find_bundled_path(file)
            if not p.exists():
                missing_files.append(
                    f"{message}\n"
                    f"  - cherché dans: {self.bundle_dir}\n"
                    f"  - et aussi: {self.base_dir}"
                )

        if missing_files:
            error_message = "Fichiers manquants :\n" + "\n".join(missing_files)
            messagebox.showerror("Erreur", error_message)
            root.destroy()
            return

        try:
            self.charger_configuration()
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du chargement de la configuration : {str(e)}")
            root.destroy()
            return

        # Traductions basées sur la langue chargée
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.vtf_frame = ttk.Frame(self.notebook)
        self.vmt_edit_frame = ttk.Frame(self.notebook)
        self.addon_frame = ttk.Frame(self.notebook)
        self.config_frame = ttk.Frame(self.notebook)
        self.about_frame = ttk.Frame(self.notebook)

        self.notebook.add(self.vtf_frame, text=tr(self.language, "tab_vtf"))
        self.notebook.add(self.vmt_edit_frame, text=tr(self.language, "tab_vmt_edit"))
        self.notebook.add(self.addon_frame, text=tr(self.language, "tab_addon"))
        self.notebook.add(self.config_frame, text=tr(self.language, "tab_config"))
        self.notebook.add(self.about_frame, text=tr(self.language, "tab_about"))

        self.setup_vtf_tab()
        self.setup_vmt_edit_tab()
        self.setup_addon_tab()
        self.setup_config_tab()
        self.setup_about_tab()

    # -------------------- CONFIG --------------------

    def charger_configuration(self):
        config_path = get_config_path()
        config_path.parent.mkdir(parents=True, exist_ok=True)

        default_config = {
            "source1_base": r"C:/Program Files (x86)/Steam/steamapps/common/GarrysMod/garrysmod/materials/models/kera",
            "source2_base": r"C:/Program Files (x86)/Steam/steamapps/common/GarrysMod/garrysmod/models/kera",
            "workshop_base": r"E:/Gmod/Workshop",
            "language": "fr",
        }

        if not config_path.exists():
            with config_path.open("w", encoding="utf-8") as f:
                json.dump(default_config, f, indent=2)
            config = default_config
        else:
            try:
                with config_path.open("r", encoding="utf-8") as f:
                    config = json.load(f)
            except json.JSONDecodeError:
                config = default_config
                with config_path.open("w", encoding="utf-8") as f:
                    json.dump(config, f, indent=2)

        self.source1_base = config.get("source1_base", "")
        self.source2_base = config.get("source2_base", "")
        self.workshop_base = config.get("workshop_base", "")
        self.language = (config.get("language", "fr") or "fr").lower()

    def sauvegarder_configuration(self):
        config = {
            "source1_base": self.entry_source1.get(),
            "source2_base": self.entry_source2.get(),
            "workshop_base": self.entry_workshop_base.get(),
            "language": self.language_var.get(),
        }
        config_path = get_config_path()
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with config_path.open("w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)

        # Recharge en mémoire
        self.charger_configuration()
        self.maj_affichage_chemins()

        messagebox.showinfo(tr(self.language, "success"), tr(self.language, "lang_restart_note"))

    # -------------------- TAB VTF/VMT --------------------

    def setup_vtf_tab(self):
        title_frame = ttk.Frame(self.vtf_frame)
        title_frame.pack(fill=tk.X, pady=10)
        ttk.Label(
            title_frame,
            text=tr(self.language, "title_convert"),
            font=("Helvetica", 16, "bold"),
            foreground="#2c3e50",
        ).pack()

        ttk.Separator(self.vtf_frame, orient="horizontal").pack(fill=tk.X, padx=20, pady=5)

        paths_frame = ttk.LabelFrame(self.vtf_frame, text=tr(self.language, "paths_group"))
        paths_frame.pack(fill=tk.X, padx=10, pady=10)

        self.source_dir_var = tk.StringVar(value="")
        self.dest_dir_var = tk.StringVar(value="")
        self.vmt_relative_var = tk.StringVar(value="")

        ttk.Label(paths_frame, text=tr(self.language, "source_dir")).grid(row=0, column=0, sticky="w", padx=10, pady=6)
        self.source_entry = ttk.Entry(paths_frame, textvariable=self.source_dir_var, width=60)
        self.source_entry.grid(row=0, column=1, sticky="ew", padx=6, pady=6)
        ttk.Button(paths_frame, text=tr(self.language, "browse"), command=self.browse_source_dir).grid(row=0, column=2, padx=6, pady=6)

        ttk.Label(paths_frame, text=tr(self.language, "dest_dir")).grid(row=1, column=0, sticky="w", padx=10, pady=6)
        self.dest_entry = ttk.Entry(paths_frame, textvariable=self.dest_dir_var, width=60)
        self.dest_entry.grid(row=1, column=1, sticky="ew", padx=6, pady=6)
        ttk.Button(paths_frame, text=tr(self.language, "browse"), command=self.browse_dest_dir).grid(row=1, column=2, padx=6, pady=6)

        ttk.Label(paths_frame, text=tr(self.language, "vmt_rel")).grid(row=2, column=0, sticky="w", padx=10, pady=6)
        self.vmt_entry = ttk.Entry(paths_frame, textvariable=self.vmt_relative_var, width=60)
        self.vmt_entry.grid(row=2, column=1, sticky="ew", padx=6, pady=6)
        ttk.Button(paths_frame, text=tr(self.language, "auto"), command=self.fill_default_vmt_relative).grid(row=2, column=2, padx=6, pady=6)

        paths_frame.columnconfigure(1, weight=1)

        options_frame = ttk.LabelFrame(self.vtf_frame, text=tr(self.language, "options_group"))
        options_frame.pack(fill=tk.X, padx=10, pady=5)

        self.var_vtf = tk.BooleanVar(value=True)
        self.var_vmt = tk.BooleanVar(value=True)

        ttk.Checkbutton(options_frame, text=tr(self.language, "opt_vtf"), variable=self.var_vtf).grid(
            row=0, column=0, sticky="w", padx=10, pady=5
        )
        ttk.Checkbutton(options_frame, text=tr(self.language, "opt_vmt"), variable=self.var_vmt).grid(
            row=1, column=0, sticky="w", padx=10, pady=5
        )

        ttk.Label(options_frame, text=tr(self.language, "tex_size")).grid(row=0, column=1, sticky="e", padx=10)
        self.texture_size = tk.StringVar(value="2048x2048")
        self.texture_size_combo = ttk.Combobox(
            options_frame,
            textvariable=self.texture_size,
            values=["4096x4096", "2048x2048", "1024x1024"],
            state="readonly",
            width=10,
        )
        self.texture_size_combo.grid(row=0, column=2, padx=5)

        exec_frame = ttk.Frame(self.vtf_frame)
        exec_frame.pack(fill=tk.X, padx=10, pady=5)
        self.btn_exec = ttk.Button(exec_frame, text=tr(self.language, "run"), style="Action.TButton", command=self.executer_conversion)
        self.btn_exec.pack(side=tk.LEFT, padx=5, pady=5)

        log_frame = ttk.LabelFrame(self.vtf_frame, text=tr(self.language, "results_group"))
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.log_text = tk.Text(log_frame, height=8, wrap=tk.WORD, state=tk.NORMAL)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self.log_text.insert(tk.END, tr(self.language, "welcome"))
        self.log_text.config(state=tk.DISABLED)

    def _append_log(self, message: str):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message.rstrip() + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def log(self, message: str):
        self.root.after(0, lambda: self._append_log(message))

    def browse_source_dir(self):
        initial_dir = self.source_dir_var.get() or os.getcwd()
        selected = filedialog.askdirectory(title=tr(self.language, "source_dir"), initialdir=initial_dir)
        if selected:
            self.source_dir_var.set(selected)

    def browse_dest_dir(self):
        initial_dir = self.dest_dir_var.get() or os.getcwd()
        selected = filedialog.askdirectory(title=tr(self.language, "dest_dir"), initialdir=initial_dir)
        if selected:
            self.dest_dir_var.set(selected)
            self.fill_default_vmt_relative(force_if_empty=True)

    def fill_default_vmt_relative(self, force_if_empty: bool = False):
        dest = (self.dest_dir_var.get() or "").strip()
        if not dest:
            return

        proposed = compute_vmt_relative(dest)
        current = (self.vmt_relative_var.get() or "").strip()
        if force_if_empty and current:
            return
        self.vmt_relative_var.set(proposed)

    def executer_conversion(self):
        self.btn_exec.config(state=tk.DISABLED)
        self.log("\n" + tr(self.language, "log_convert_start"))
        t = threading.Thread(target=self._run_conversion_worker, daemon=True)
        t.start()

    def _run_conversion_worker(self):
        try:
            source_dir = (self.source_dir_var.get() or "").strip()
            dest_dir = (self.dest_dir_var.get() or "").strip()
            vmt_rel = (self.vmt_relative_var.get() or "").strip().replace("\\", "/").strip("/")

            do_vtf = bool(self.var_vtf.get())
            do_vmt = bool(self.var_vmt.get())

            if not do_vtf and not do_vmt:
                raise ValueError(tr(self.language, "need_one_option"))

            if not dest_dir:
                raise ValueError(tr(self.language, "need_dest"))
            os.makedirs(dest_dir, exist_ok=True)

            if do_vtf:
                if not source_dir:
                    raise ValueError(tr(self.language, "need_source_for_vtf"))
                if not os.path.isdir(source_dir):
                    raise FileNotFoundError(f"Dossier source introuvable: {source_dir}")

                from convert_vtf import convert_images_to_vtf, get_vtfcmd_path

                vtfcmd = get_vtfcmd_path()
                self.log(f"[INFO] VTFCmd: {vtfcmd}")
                converted = convert_images_to_vtf(
                    input_dir=source_dir,
                    output_dir=dest_dir,
                    vtfcmd_path=vtfcmd,
                    texture_size=self.texture_size.get(),
                    callback=self.log,
                )
                self.log(f"[OK] VTF: {converted} fichier(s) converti(s).")

            if do_vmt:
                if not vmt_rel:
                    vmt_rel = compute_vmt_relative(dest_dir)

                if not vmt_rel:
                    raise ValueError(tr(self.language, "cannot_compute_vmt_rel"))

                if not do_vtf:
                    vtf_files = [f for f in os.listdir(dest_dir) if f.lower().endswith(".vtf")]
                    if not vtf_files:
                        raise ValueError(tr(self.language, "missing_vtf_in_dest"))

                from create_vmt_file import process_vtf_folder
                vmt_count = process_vtf_folder(dest_dir, vmt_rel, callback=self.log)
                self.log(f"[OK] VMT: {vmt_count} fichier(s) généré(s).")

            self.log(tr(self.language, "log_done"))

        except Exception as e:
            self.log(f"[ERREUR] {e}")
        finally:
            self.root.after(0, lambda: self.btn_exec.config(state=tk.NORMAL))

    # -------------------- TAB VMT EDIT --------------------

    def setup_vmt_edit_tab(self):
        title_frame = ttk.Frame(self.vmt_edit_frame)
        title_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Label(
            title_frame,
            text=tr(self.language, "title_vmt_edit"),
            font=("Helvetica", 16, "bold"),
            foreground="#2c3e50",
        ).pack()

        ttk.Separator(self.vmt_edit_frame, orient="horizontal").pack(fill=tk.X, padx=20, pady=10)

        desc = ttk.Label(
            self.vmt_edit_frame,
            text=tr(self.language, "vmt_edit_desc"),
            justify=tk.LEFT,
            anchor="w",
        )
        desc.pack(anchor="w", padx=15)

        # Text zone
        self.vmt_template_text = tk.Text(self.vmt_edit_frame, height=22, wrap=tk.NONE)
        self.vmt_template_text.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        # Buttons
        btn_frame = ttk.Frame(self.vmt_edit_frame)
        btn_frame.pack(fill=tk.X, padx=15, pady=(0, 10))

        ttk.Button(btn_frame, text=tr(self.language, "reset_preset"), command=self.reset_vmt_preset).pack(side=tk.LEFT)
        ttk.Button(btn_frame, text=tr(self.language, "save_preset"), style="Action.TButton", command=self.save_vmt_preset).pack(side=tk.LEFT, padx=10)

        # Load preset at start
        self.load_vmt_preset_into_ui()

    def load_vmt_preset_into_ui(self):
        try:
            from vmt_template import load_vmt_template
            template = load_vmt_template(base_dir=get_base_dir())
        except Exception as e:
            self.log(f"[WARN] Erreur chargement preset: {e}")
            template = (
                '"VertexLitGeneric"\n'
                '{\n'
                '\t"$basetexture" "models/"\n'
                '\t"$bumpmap"     "models/"\n'
                '\n'
                '\t// éclairage plus doux\n'
                '\t"$halflambert" "1"\n'
                '\n'
                '\t// Relief lisible sans effet plastique\n'
                '\t"$phong" "1"\n'
                '\t"$phongalbedotint" "1"\n'
                '\t"$phongboost" "1.5"\n'
                '\t"$phongexponent" "16"\n'
                '\t"$phongfresnelranges" "[0.02 0.12 1]"\n'
                '\n'
                '\t"$nocull" "1"\n'
                '}\n'
            )

        self.vmt_template_text.delete("1.0", tk.END)
        self.vmt_template_text.insert(tk.END, template)

    def save_vmt_preset(self):
        txt = self.vmt_template_text.get("1.0", tk.END).rstrip() + "\n"
        try:
            from vmt_template import save_vmt_template
            save_vmt_template(txt, base_dir=get_base_dir())
            messagebox.showinfo(tr(self.language, "success"), tr(self.language, "preset_saved"))
        except Exception as e:
            messagebox.showerror(tr(self.language, "error"), str(e))

    def reset_vmt_preset(self):
        try:
            from vmt_template import reset_vmt_template
            reset_vmt_template(base_dir=get_base_dir())
            self.load_vmt_preset_into_ui()
            messagebox.showinfo(tr(self.language, "success"), tr(self.language, "preset_reset"))
        except Exception as e:
            messagebox.showerror(tr(self.language, "error"), str(e))

    # -------------------- TAB ADDON --------------------

    def setup_addon_tab(self):
        title_frame = ttk.Frame(self.addon_frame)
        title_frame.pack(fill=tk.X, pady=10)
        ttk.Label(
            title_frame,
            text=tr(self.language, "title_addon"),
            font=("Helvetica", 16, "bold"),
            foreground="#2c3e50",
        ).pack()

        ttk.Separator(self.addon_frame, orient="horizontal").pack(fill=tk.X, padx=20, pady=5)

        mode_frame = ttk.LabelFrame(self.addon_frame, text=tr(self.language, "mode_group"))
        mode_frame.pack(fill=tk.X, padx=10, pady=5)
        self.mode_creation = tk.StringVar(value="unique")
        ttk.Radiobutton(mode_frame, text=tr(self.language, "mode_unique"), variable=self.mode_creation, value="unique").grid(
            row=0, column=0, sticky="w", padx=10, pady=5
        )
        ttk.Radiobutton(mode_frame, text=tr(self.language, "mode_series"), variable=self.mode_creation, value="serie").grid(
            row=0, column=1, sticky="w", padx=10, pady=5
        )

        config_frame = ttk.LabelFrame(self.addon_frame, text=tr(self.language, "addon_config_group"))
        config_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(config_frame, text=tr(self.language, "models_names")).grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.entry_modeles = ttk.Entry(config_frame, width=60)
        self.entry_modeles.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(config_frame, text=tr(self.language, "workshop_folder")).grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.entry_workshop_name = ttk.Entry(config_frame, width=60)
        self.entry_workshop_name.grid(row=1, column=1, padx=5, pady=5)

        chemins_frame = ttk.LabelFrame(self.addon_frame, text=tr(self.language, "paths_configured"))
        chemins_frame.pack(fill=tk.X, padx=10, pady=10)
        chemins_text = f"Source materials : {self.source1_base}\nSource models : {self.source2_base}\nDossier Workshop : {self.workshop_base}"
        self.label_chemins_addon = ttk.Label(chemins_frame, text=chemins_text, justify=tk.LEFT)
        self.label_chemins_addon.pack(anchor="w", padx=5, pady=5)

        btn_frame = ttk.Frame(self.addon_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        self.btn_addon = tk.Button(
            btn_frame,
            text=tr(self.language, "create_addon"),
            bg="#b3e0ff",
            font=("Helvetica", 11, "bold"),
            command=self.creer_addon,
        )
        self.btn_addon.pack(pady=5)

        log_frame = ttk.LabelFrame(self.addon_frame, text=tr(self.language, "results_group"))
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.log_addon = tk.Text(log_frame, height=8, wrap=tk.WORD, state=tk.NORMAL)
        self.log_addon.pack(fill=tk.BOTH, expand=True)
        self.log_addon.config(state=tk.DISABLED)

    def _append_addon_log(self, message: str):
        self.log_addon.config(state=tk.NORMAL)
        self.log_addon.insert(tk.END, message.rstrip() + "\n")
        self.log_addon.see(tk.END)
        self.log_addon.config(state=tk.DISABLED)

    def addon_log(self, message: str):
        self.root.after(0, lambda: self._append_addon_log(message))

    def creer_addon(self):
        self.btn_addon.config(state=tk.DISABLED)
        self.addon_log("\n[INFO] Création d'addon lancée...")
        t = threading.Thread(target=self._run_addon_worker, daemon=True)
        t.start()

    def _run_addon_worker(self):
        try:
            workshop_name = (self.entry_workshop_name.get() or "").strip()
            raw_models = (self.entry_modeles.get() or "").strip()
            model_list = [m.strip() for m in raw_models.split(",") if m.strip()]

            if not workshop_name:
                raise ValueError("Veuillez renseigner le 'Nom du dossier Workshop'.")
            if not model_list:
                raise ValueError("Veuillez renseigner au moins un modèle (séparé par des virgules).")

            from addon import create_addon

            addon_root = create_addon(
                model_names=model_list,
                workshop_folder_name=workshop_name,
                source_materials_base=self.source1_base,
                source_models_base=self.source2_base,
                workshop_base=self.workshop_base,
                cb=self.addon_log,
            )
            self.addon_log(f"[OK] Addon généré dans: {addon_root}")

        except Exception as e:
            self.addon_log(f"[ERREUR] {e}")
        finally:
            self.root.after(0, lambda: self.btn_addon.config(state=tk.NORMAL))

    # -------------------- TAB CONFIG --------------------

    def setup_config_tab(self):
        title_frame = ttk.Frame(self.config_frame)
        title_frame.pack(fill=tk.X, pady=10)
        ttk.Label(
            title_frame,
            text=tr(self.language, "title_config"),
            font=("Helvetica", 16, "bold"),
            foreground="#2c3e50",
        ).pack()

        ttk.Separator(self.config_frame, orient="horizontal").pack(fill=tk.X, padx=20, pady=5)

        form_frame = ttk.Frame(self.config_frame)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=10)

        ttk.Label(form_frame, text=tr(self.language, "source_materials_base")).grid(row=0, column=0, sticky="w", pady=5)
        self.entry_source1 = ttk.Entry(form_frame, width=70)
        self.entry_source1.grid(row=0, column=1, pady=5)
        self.entry_source1.insert(0, self.source1_base)

        ttk.Label(form_frame, text=tr(self.language, "source_models_base")).grid(row=1, column=0, sticky="w", pady=5)
        self.entry_source2 = ttk.Entry(form_frame, width=70)
        self.entry_source2.grid(row=1, column=1, pady=5)
        self.entry_source2.insert(0, self.source2_base)

        ttk.Label(form_frame, text=tr(self.language, "workshop_base")).grid(row=2, column=0, sticky="w", pady=5)
        self.entry_workshop_base = ttk.Entry(form_frame, width=70)
        self.entry_workshop_base.grid(row=2, column=1, pady=5)
        self.entry_workshop_base.insert(0, self.workshop_base)

        # Langue
        ttk.Label(form_frame, text=tr(self.language, "language_label")).grid(row=3, column=0, sticky="w", pady=5)
        self.language_var = tk.StringVar(value=self.language)
        self.combo_language = ttk.Combobox(
            form_frame,
            textvariable=self.language_var,
            values=["fr", "en"],
            state="readonly",
            width=10
        )
        self.combo_language.grid(row=3, column=1, sticky="w", pady=5)

        btn_frame = ttk.Frame(self.config_frame)
        btn_frame.pack(pady=10)
        self.btn_valider = tk.Button(
            btn_frame,
            text=tr(self.language, "save"),
            bg="#4be37a",
            font=("Helvetica", 11, "bold"),
            command=self.sauvegarder_configuration,
        )
        self.btn_valider.pack(pady=5)

    def maj_affichage_chemins(self):
        if hasattr(self, "label_chemins_addon"):
            chemins_text = f"Source materials : {self.source1_base}\nSource models : {self.source2_base}\nDossier Workshop : {self.workshop_base}"
            self.label_chemins_addon.config(text=chemins_text)

    # -------------------- TAB ABOUT --------------------

    def setup_about_tab(self):
        title_frame = ttk.Frame(self.about_frame)
        title_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Label(
            title_frame,
            text=tr(self.language, "title_about"),
            font=("Helvetica", 16, "bold"),
            foreground="#2c3e50",
        ).pack()

        ttk.Separator(self.about_frame, orient="horizontal").pack(fill=tk.X, padx=20, pady=10)

        content_frame = ttk.Frame(self.about_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)

        about_text = tr(self.language, "about_text")

        lbl = ttk.Label(
            content_frame,
            text=about_text,
            justify=tk.LEFT,
            anchor="nw",
            font=("Helvetica", 10),
        )
        lbl.pack(anchor="nw", padx=20, pady=10)


def main() -> int:
    root = tk.Tk()
    _app = VTFMasterGUI(root)
    root.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())