import os
import subprocess
import sys
import re


# ==========================================================
# CONFIGURATION
# ==========================================================

def charger_configuration():
    """
    Charge la configuration depuis le fichier config.txt.

    :return: Tuple contenant (chemin_modeles, chemin_materials)
    """
    chemin_modeles = None
    chemin_materials = None

    try:
        # Lire les valeurs depuis le fichier config.txt
        with open("config.txt", "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if line.startswith("chemin_modeles="):
                    chemin_modeles = line.split("=", 1)[1].strip()
                elif line.startswith("chemin_materials="):
                    chemin_materials = line.split("=", 1)[1].strip()
    except FileNotFoundError:
        raise FileNotFoundError("Fichier config.txt non trouvé.")

    if not chemin_modeles or not chemin_materials:
        raise ValueError("La configuration n'est pas complète. Assurez-vous que les chemins sont définis dans config.txt.")

    return chemin_modeles, chemin_materials


# ==========================================================
# LOCALISATION VTFCMD (PyInstaller compatible)
# ==========================================================

def get_vtfcmd_path():
    """
    Détermine le chemin vers VTFCmd.exe.

    :return: Chemin complet vers VTFCmd.exe
    """
    meipass = getattr(sys, "_MEIPASS", None)

    candidates = []
    if meipass:
        candidates.append(os.path.join(meipass, "VTFCmd.exe"))

    exe_dir = os.path.dirname(sys.executable) if getattr(sys, "frozen", False) else os.path.dirname(os.path.abspath(__file__))
    candidates.extend(
        [
            os.path.join(exe_dir, "VTFCmd.exe"),
            os.path.join(exe_dir, "_internal", "VTFCmd.exe"),
        ]
    )

    for p in candidates:
        if os.path.isfile(p):
            return p

    raise FileNotFoundError("VTFCmd.exe introuvable. Emplacements testés:\n- " + "\n- ".join(candidates))


# ==========================================================
# RECHERCHE DU DOSSIER TEXTURES
# ==========================================================

def find_texture_directory(model_path):
    """
    Recherche le répertoire de textures dans le chemin du modèle.
    Vérifie plusieurs variantes de noms (texture, textures, Texture, Textures).

    :param model_path: Chemin du modèle
    :return: Chemin complet vers le répertoire de textures
    """
    texture_dir_variants = ["texture", "textures", "Texture", "Textures"]

    for variant in texture_dir_variants:
        texture_dir = os.path.join(model_path, variant)
        if os.path.isdir(texture_dir):
            return texture_dir

    raise FileNotFoundError(f"Aucun répertoire de textures trouvé dans {model_path}")


# ==========================================================
# DÉTECTION NORMAL MAP (support _N_ au milieu)
# ==========================================================

NORMAL_TOKEN_RE = re.compile(r'_(n|normal)(?=_)', re.IGNORECASE)

def is_normal_map_filename(filename: str) -> bool:
    """
    Détection robuste normal map :
    - token au milieu : ..._N_... ou ..._NORMAL_...
    - suffix fin : ..._n / ..._normal
    """
    name_no_ext = os.path.splitext(filename)[0]
    name_lower = name_no_ext.lower()

    if NORMAL_TOKEN_RE.search(name_lower):
        return True

    return name_lower.endswith("_n") or name_lower.endswith("_normal")


# ==========================================================
# CONVERSION IMAGES -> VTF (options proches VTFEdit default)
# ==========================================================

def convert_images_to_vtf(input_dir, output_dir, vtfcmd_path, texture_size="2048x2048", callback=None):
    """
    Convertit toutes les images compatibles d'un répertoire en fichiers VTF.

    Compatible avec VTFCmd (version où -mipmaps n'existe pas).
    Par défaut, VTFCmd génère des mipmaps sauf si on passe -nomipmaps.
    Donc on NE met PAS -mipmaps.
    """
    if not os.path.isdir(input_dir):
        raise FileNotFoundError(f"Le répertoire d'entrée n'existe pas : {input_dir}")

    os.makedirs(output_dir, exist_ok=True)
    converted_files = 0

    def log(message: str):
        if callback:
            callback(message)
        else:
            print(message)

    log(f"Conversion des images de {input_dir} vers {output_dir}")

    width, height = texture_size.split('x')
    width = str(width).strip()
    height = str(height).strip()

    for file in os.listdir(input_dir):
        path = os.path.join(input_dir, file)

        if not os.path.isfile(path):
            continue

        if not path.lower().endswith(("png", "jpeg", "jpg", "bmp", "tga", "dds")):
            continue

        output_vtf_path = os.path.join(output_dir, os.path.splitext(file)[0] + ".vtf")
        log(f"Conversion de {path} vers {output_vtf_path}")

        is_normal_map = is_normal_map_filename(file)

        # ✅ Commande proche defaults VTFEdit, sans -mipmaps (car inexistant)
        cmd_args = [
            vtfcmd_path,
            "-file", path,
            "-output", output_dir,

            "-resize",
            "-rclampwidth", width,
            "-rclampheight", height,
            "-rfilter", "TRIANGLE",
        ]

        # Normal map flag
        if is_normal_map:
            cmd_args += ["-normal"]

        log(f"Commande exécutée : {' '.join(cmd_args)}")

        try:
            creationflags = 0
            startupinfo = None
            if os.name == "nt":
                creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

            subprocess.run(
                cmd_args,
                check=True,
                capture_output=True,
                text=True,
                creationflags=creationflags,
                startupinfo=startupinfo,
            )

            log(f"✓ Conversion réussie : {file}")
            converted_files += 1

        except subprocess.CalledProcessError as e:
            error_msg = e.stderr if e.stderr else e.stdout if e.stdout else str(e)
            log(f"✗ Erreur de conversion : {file}")
            log(f"Détails de l'erreur : {error_msg}")

        except Exception as e:
            log(f"✗ Erreur inattendue : {file}")
            log(f"Détails de l'erreur : {str(e)}")

    log(f"Conversion terminée. {converted_files} fichier(s) converti(s).")
    return converted_files


# ==========================================================
# PIPELINE CONVERSION PAR MODÈLE
# ==========================================================

def convert_vtf(model_name, chemin_modeles=None, chemin_materials=None, texture_size="2048x2048", callback=None):
    """
    Convertit les images d'un modèle en fichiers VTF.

    :param model_name: Nom du modèle à convertir
    :param chemin_modeles: Chemin vers le répertoire des modèles (si None, chargé depuis config.txt)
    :param chemin_materials: Chemin vers le répertoire des matériaux (si None, chargé depuis config.txt)
    :param texture_size: Taille max clamp (ex: "4096x4096", "2048x2048", "1024x1024")
    :param callback: Fonction de rappel pour les messages (optionnel)
    :return: Nombre de fichiers convertis
    """
    if chemin_modeles is None or chemin_materials is None:
        chemin_modeles, chemin_materials = charger_configuration()

    vtfcmd_path = get_vtfcmd_path()

    model_path = os.path.join(chemin_modeles, model_name)

    input_dir = find_texture_directory(model_path)

    output_dir = os.path.join(chemin_materials, model_name)

    return convert_images_to_vtf(input_dir, output_dir, vtfcmd_path, texture_size, callback)


# ==========================================================
# MAIN
# ==========================================================

if __name__ == "__main__":
    try:
        if len(sys.argv) < 2:
            print("[ERROR] Aucun sous-dossier spécifié.")
            sys.exit(1)

        model_name = sys.argv[1]
        print(f"Conversion du modèle : {model_name}")

        num_converted = convert_vtf(model_name)

        print(f"Conversion terminée. {num_converted} fichier(s) converti(s).")
        sys.exit(0)

    except Exception as e:
        print(f"[ERROR] {str(e)}")
        sys.exit(1)