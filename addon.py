from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Callable, Iterable, Optional


def _log(cb: Optional[Callable[[str], None]], msg: str) -> None:
    """Log helper: callback si fourni, sinon print."""
    if cb:
        cb(msg)
    else:
        print(msg)


def _safe_copy_file(src: Path, dst: Path) -> None:
    """Copie un fichier en créant les dossiers si besoin."""
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def _copy_tree_merge(src_dir: Path, dst_dir: Path) -> None:
    """
    Copie un dossier vers un autre en fusionnant (sans effacer ce qui existe déjà).
    """
    if not src_dir.exists():
        return

    for root, _, files in os.walk(src_dir):
        root_p = Path(root)
        rel = root_p.relative_to(src_dir)
        out_root = dst_dir / rel
        out_root.mkdir(parents=True, exist_ok=True)

        for f in files:
            _safe_copy_file(root_p / f, out_root / f)


def _find_folder_recursive(base: Path, folder_name: str) -> list[Path]:
    """
    Cherche récursivement tous les dossiers dont le nom correspond à folder_name
    sous base. Retourne la liste des chemins trouvés.
    """
    results = []
    for root, dirs, _ in os.walk(base):
        for d in dirs:
            if d.lower() == folder_name.lower():
                results.append(Path(root) / d)
    return results


def _copy_model_folder(
    src_models_base: Path,
    dst_models_base: Path,
    model_name: str,
    cb: Optional[Callable[[str], None]] = None,
) -> int:
    """
    Cherche récursivement <model_name> sous src_models_base et copie en
    préservant la structure relative depuis src_models_base.

    Exemple :
      src_models_base = garrysmod/models
      model_name      = winterfell
      trouvé dans     = garrysmod/models/kera/winterfell/
      copié vers      = addon/models/kera/winterfell/
    """
    matches = _find_folder_recursive(src_models_base, model_name)

    if not matches:
        _log(cb, f"[WARN] Models introuvable: '{model_name}' sous {src_models_base}")
        return 0

    copied = 0
    for src_dir in matches:
        rel = src_dir.relative_to(src_models_base)
        dst_dir = dst_models_base / rel
        _log(cb, f"[INFO] Copie models: {src_dir} -> {dst_dir}")
        _copy_tree_merge(src_dir, dst_dir)
        copied += 1
    return copied


def _copy_materials_folder(
    src_materials_base: Path,
    dst_materials_base: Path,
    model_name: str,
    cb: Optional[Callable[[str], None]] = None,
) -> int:
    """
    Cherche récursivement <model_name> sous src_materials_base et copie en
    préservant la structure relative depuis src_materials_base.

    Exemple :
      src_materials_base = garrysmod/materials
      model_name         = winterfell
      trouvé dans        = garrysmod/materials/models/kera/winterfell/
      copié vers         = addon/materials/models/kera/winterfell/
    """
    matches = _find_folder_recursive(src_materials_base, model_name)

    if not matches:
        _log(cb, f"[WARN] Materials introuvable: '{model_name}' sous {src_materials_base}")
        return 0

    copied = 0
    for src_dir in matches:
        rel = src_dir.relative_to(src_materials_base)
        dst_dir = dst_materials_base / rel
        _log(cb, f"[INFO] Copie materials: {src_dir} -> {dst_dir}")
        _copy_tree_merge(src_dir, dst_dir)
        copied += 1
    return copied



def create_addon(
    model_names: Iterable[str],
    workshop_folder_name: str,
    source_materials_base: str,
    source_models_base: str,
    workshop_base: str,
    cb: Optional[Callable[[str], None]] = None,
) -> Path:
    """
    Crée un addon "déplié" (pas de .gma) dans un dossier Workshop.

    Paramètres:
      - model_names: liste de noms de dossiers de modèles (ex: ["winterfell", "targ_07"])
      - workshop_folder_name: nom du dossier addon final (ex: "winterfell_pack")
      - source_materials_base: chemin vers .../garrysmod/materials  (racine materials)
      - source_models_base: chemin vers .../garrysmod/models         (racine models)
      - workshop_base: dossier où stocker les addons (ex: E:/Gmod/Workshop)
      - cb: callback de log optionnel

    Sortie:
      <workshop_base>/<workshop_folder_name>/
        materials/<chemin_relatif_trouvé>/<model>/*
        models/<chemin_relatif_trouvé>/<model>/*

    La recherche est récursive : n'importe quel sous-dossier sous materials/ ou
    models/ sera trouvé et sa structure préservée dans l'addon.
    """
    models = [m.strip() for m in model_names if m and str(m).strip()]
    if not models:
        raise ValueError("Aucun modèle fourni.")

    workshop_folder_name = workshop_folder_name.strip()
    if not workshop_folder_name:
        raise ValueError("Nom de dossier Workshop vide.")

    src_mat = Path(source_materials_base).resolve()
    src_mod = Path(source_models_base).resolve()
    ws_base = Path(workshop_base).resolve()

    if not src_mat.exists():
        raise FileNotFoundError(f"Chemin source materials invalide: {src_mat}")
    if not src_mod.exists():
        raise FileNotFoundError(f"Chemin source models invalide: {src_mod}")

    ws_base.mkdir(parents=True, exist_ok=True)

    addon_root = ws_base / workshop_folder_name
    addon_root.mkdir(parents=True, exist_ok=True)

    # Les destinations sont à la racine de l'addon, la structure relative
    # sera reconstruite automatiquement par _copy_materials_folder/_copy_model_folder
    dst_materials_base = addon_root / "materials"
    dst_models_base = addon_root / "models"

    _log(cb, f"[INFO] Addon root: {addon_root}")
    _log(cb, "[INFO] Sources:")
    _log(cb, f"       - materials: {src_mat}")
    _log(cb, f"       - models   : {src_mod}")
    _log(cb, f"[INFO] Models à pack: {', '.join(models)}")

    copied_any = False

    for model in models:
        copied_m = _copy_materials_folder(src_mat, dst_materials_base, model, cb=cb)
        copied_md = _copy_model_folder(src_mod, dst_models_base, model, cb=cb)
        if copied_m or copied_md:
            copied_any = True

    if not copied_any:
        raise RuntimeError("Rien n'a été copié (vérifie tes chemins source et noms de modèles).")

    _log(cb, "[TERMINE] Addon généré (dossier prêt).")

    return addon_root


# Optionnel: test rapide en ligne de commande
if __name__ == "__main__":
    # Exemple:
    # python addon.py "winterfell,targ_07" "winterfell_pack" "C:/.../materials/models/kera" "C:/.../models/kera" "E:/Gmod/Workshop"
    import sys

    if len(sys.argv) < 6:
        print("Usage:")
        print('  python addon.py "model1,model2" "workshop_folder" "source_materials_base" "source_models_base" "workshop_base"')
        raise SystemExit(1)

    models_arg = sys.argv[1]
    workshop_folder = sys.argv[2]
    source_mat = sys.argv[3]
    source_mod = sys.argv[4]
    workshop_base = sys.argv[5]

    models_list = [m.strip() for m in models_arg.split(",") if m.strip()]

    addon_path = create_addon(
        model_names=models_list,
        workshop_folder_name=workshop_folder,
        source_materials_base=source_mat,
        source_models_base=source_mod,
        workshop_base=workshop_base,
        cb=print,
    )
    print(f"Addon créé: {addon_path}")