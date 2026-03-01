from __future__ import annotations

import json
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


def _copy_model_folder(
    src_models_base: Path,
    dst_models_base: Path,
    model_name: str,
    cb: Optional[Callable[[str], None]] = None,
) -> int:
    """
    Copie les fichiers modèles GMod :
      <src_models_base>/<model_name>/** -> <dst_models_base>/<model_name>/**
    Exemple sources:
      garrysmod/models/kera/<model_name>/
    Exemple destination:
      addon/models/kera/<model_name>/
    """
    src_dir = src_models_base / model_name
    dst_dir = dst_models_base / model_name

    if not src_dir.exists():
        _log(cb, f"[WARN] Models introuvable: {src_dir}")
        return 0

    _log(cb, f"[INFO] Copie models: {src_dir} -> {dst_dir}")
    _copy_tree_merge(src_dir, dst_dir)
    return 1


def _copy_materials_folder(
    src_materials_base: Path,
    dst_materials_base: Path,
    model_name: str,
    cb: Optional[Callable[[str], None]] = None,
) -> int:
    """
    Copie les matériaux GMod :
      <src_materials_base>/<model_name>/** -> <dst_materials_base>/<model_name>/**
    Exemple sources:
      garrysmod/materials/models/kera/<model_name>/
    Exemple destination:
      addon/materials/models/kera/<model_name>/
    """
    src_dir = src_materials_base / model_name
    dst_dir = dst_materials_base / model_name

    if not src_dir.exists():
        _log(cb, f"[WARN] Materials introuvable: {src_dir}")
        return 0

    _log(cb, f"[INFO] Copie materials: {src_dir} -> {dst_dir}")
    _copy_tree_merge(src_dir, dst_dir)
    return 1


def _write_addon_json(addon_root: Path, title: str, tags: Optional[list[str]] = None) -> None:
    """
    Ecrit addon.json à la racine de l'addon.
    """
    data = {
        "title": title,
        "type": "model",
        "tags": tags or ["model"],
        "ignore": [
            "*.psd",
            "*.blend",
            "*.fbx",
            "*.spp",
            "*.png",
            "*.tga",
            "*.jpg",
            "*.jpeg",
        ],
    }
    (addon_root / "addon.json").write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


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
      - source_materials_base: chemin vers .../garrysmod/materials/models/kera
      - source_models_base: chemin vers .../garrysmod/models/kera
      - workshop_base: dossier où stocker les addons (ex: E:/Gmod/Workshop)
      - cb: callback de log optionnel

    Sortie:
      <workshop_base>/<workshop_folder_name>/
        addon.json
        materials/models/kera/<model>/*
        models/kera/<model>/*
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

    dst_materials_base = addon_root / "materials" / "models" / "kera"
    dst_models_base = addon_root / "models" / "kera"

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

    _write_addon_json(addon_root, title=workshop_folder_name, tags=["model"])
    _log(cb, "[OK] addon.json créé.")
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