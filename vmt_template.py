from __future__ import annotations

from pathlib import Path

# Presets par défaut
DEFAULT_PROPS_TEMPLATE = (
    '"VertexLitGeneric"\n'
    '{\n'
    '\t"$basetexture" "models/"\n'
    '\t"$bumpmap"     "models/"\n'
    '\n'
    '\t// eclairage plus doux\n'
    '\t"$halflambert" "1"\n'
    '\n'
    '\t// Relief lisible sans effet plastique\n'
    '\t"$phong" "1"\n'
    '\t"$phongalbedotint" "1"\n'
    '\t"$phongboost" "1.5"\n'
    '\t"$phongexponent" "16"\n'
    '\t"$phongfresnelranges" "[0.02 0.12 1]"\n'
    '}\n'
)

DEFAULT_MAP_HAMMER_TEMPLATE = (
    '"LightmappedGeneric"\n'
    '{\n'
    '\t"$basetexture" "map/"\n'
    '\t"$bumpmap"     "map/"\n'
    '\n'
    '\t"$envmap" "env_cubemap"\n'
    '\t"$envmaptint" "[.02 .02 .02]"\n'
    '\t"$normalmapalphaenvmapmask" "1"\n'
    '\n'
    '\t// Force le rendu propre des normales\n'
    '\t"$bumpframe" "0"\n'
    '}\n'
)

DEFAULT_TEMPLATES = {
    "props": DEFAULT_PROPS_TEMPLATE,
    "map_hammer": DEFAULT_MAP_HAMMER_TEMPLATE,
}


def _resolve_preset_path(preset_name: str = "props", base_dir: str | Path | None = None) -> Path:
    """
    Où on stocke le preset édité.
    - Si base_dir fourni: base_dir/vmt_preset_<preset_name>.txt
    - Sinon: vmt_preset_<preset_name>.txt dans le dossier courant
    """
    filename = f"vmt_preset_{preset_name}.txt"
    if base_dir is None:
        return Path(filename).resolve()
    return Path(base_dir).resolve() / filename


def load_vmt_template(preset_name: str = "props", base_dir: str | Path | None = None) -> str:
    """
    Charge le preset utilisateur s'il existe, sinon renvoie le preset par défaut.
    """
    path = _resolve_preset_path(preset_name, base_dir)
    if path.exists():
        try:
            return path.read_text(encoding="utf-8")
        except Exception:
            pass
    return DEFAULT_TEMPLATES.get(preset_name, DEFAULT_PROPS_TEMPLATE)


def save_vmt_template(text: str, preset_name: str = "props", base_dir: str | Path | None = None) -> Path:
    """
    Sauvegarde le preset utilisateur et retourne le chemin écrit.
    """
    path = _resolve_preset_path(preset_name, base_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def reset_vmt_template(preset_name: str = "props", base_dir: str | Path | None = None) -> None:
    """
    Supprime le fichier preset utilisateur s'il existe.
    load_vmt_template retournera alors le preset par défaut en mémoire.
    """
    path = _resolve_preset_path(preset_name, base_dir)
    if path.exists():
        path.unlink()