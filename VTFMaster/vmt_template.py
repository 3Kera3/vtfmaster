from __future__ import annotations

from pathlib import Path

# Preset par défaut (celui affiché dans ton onglet VMT Edit)
DEFAULT_VMT_TEMPLATE = (
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

# Nom du fichier preset sauvegardé (à côté de l'exe si possible)
TEMPLATE_FILENAME = "vmt_preset.txt"


def _resolve_preset_path(base_dir: str | Path | None = None) -> Path:
    """
    Où on stocke le preset édité.
    - Si base_dir fourni: base_dir/vmt_preset.txt
    - Sinon: vmt_preset.txt dans le dossier courant
    """
    if base_dir is None:
        return Path(TEMPLATE_FILENAME).resolve()
    return Path(base_dir).resolve() / TEMPLATE_FILENAME


def load_vmt_template(base_dir: str | Path | None = None) -> str:
    """
    Charge le preset utilisateur s'il existe, sinon renvoie le preset par défaut.
    Compatible avec:
      - load_vmt_template()
      - load_vmt_template(base_dir=...)
      - load_vmt_template(Path(...))
    """
    path = _resolve_preset_path(base_dir)
    if path.exists():
        try:
            return path.read_text(encoding="utf-8")
        except Exception:
            # Si le fichier est illisible, on retombe sur le défaut
            return DEFAULT_VMT_TEMPLATE
    return DEFAULT_VMT_TEMPLATE


def save_vmt_template(text: str, base_dir: str | Path | None = None) -> Path:
    """
    Sauvegarde le preset utilisateur et retourne le chemin écrit.
    """
    path = _resolve_preset_path(base_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def reset_vmt_template(base_dir: str | Path | None = None) -> Path:
    """
    Remet le preset par défaut (écrit dans le fichier).
    """
    return save_vmt_template(DEFAULT_VMT_TEMPLATE, base_dir=base_dir)