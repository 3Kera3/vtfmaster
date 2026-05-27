import os
import re
import sys

# ============================================================
# Helpers D/N token support (identique)
# ============================================================

DN_TOKEN_RE = re.compile(r'_(d|n)(?=_)', re.IGNORECASE)  # match "_D_" or "_N_" (token au milieu)

def detect_map_type(name_no_ext_lower: str, diffuse_suffixes, normal_suffixes):
    """
    Retourne "diffuse", "normal" ou None selon:
    - token _D_ / _N_ n'importe où dans le nom
    - ou suffixes classiques en fin de nom (_d, _n, etc.)
    """
    m = DN_TOKEN_RE.search(name_no_ext_lower)
    if m:
        return "diffuse" if m.group(1) == "d" else "normal"

    for s in diffuse_suffixes:
        if s and name_no_ext_lower.endswith(s):
            return "diffuse"
    for s in normal_suffixes:
        if s and name_no_ext_lower.endswith(s):
            return "normal"

    return None


def make_pair_key(name_no_ext_lower: str, diffuse_suffixes, normal_suffixes):
    """
    Fabrique une clé stable pour associer diffuse/normal:
    - supprime le token _D_/_N_ (au milieu)
    - sinon supprime un suffixe connu en fin de nom (_d/_n/_diffuse/_normal/etc.)
    """
    if DN_TOKEN_RE.search(name_no_ext_lower):
        key = DN_TOKEN_RE.sub("", name_no_ext_lower)
        key = re.sub(r"__+", "_", key).strip("_")
        return key

    for s in diffuse_suffixes + normal_suffixes:
        if s and name_no_ext_lower.endswith(s):
            return name_no_ext_lower[:-len(s)]
    return name_no_ext_lower


# ============================================================
# VMT Template support (preset éditable via vmt_template.py)
# ============================================================

# On ignore dans le template les lignes base/bump (car regénérées)
BASE_RE = re.compile(r'^\s*"\$basetexture"\s*".*"\s*$', re.IGNORECASE)
BUMP_RE = re.compile(r'^\s*"\$bumpmap"\s*".*"\s*$', re.IGNORECASE)

def _load_template_text(preset_name="props"):
    """
    Charge le preset depuis vmt_template.py.
    """
    try:
        from vmt_template import load_vmt_template
        # On essaie d'abord de charger via le dossier du script courant
        script_dir = os.path.dirname(os.path.abspath(__file__))
        return load_vmt_template(preset_name=preset_name, base_dir=script_dir)
    except Exception as e:
        try:
            from vmt_template import DEFAULT_TEMPLATES, DEFAULT_PROPS_TEMPLATE
            return DEFAULT_TEMPLATES.get(preset_name, DEFAULT_PROPS_TEMPLATE)
        except Exception as e2:
            raise ImportError(
                f"Impossible de charger le preset VMT depuis vmt_template.py. "
                f"Erreur d'origine: {e}, Erreur fallback: {e2}"
            ) from e2


def _sanitize_template(template_text: str):
    """
    Retourne (shader_name, body_lines) en supprimant :
    - la ligne $basetexture
    - la ligne $bumpmap
    - les braces { } existantes
    Le shader reste configurable (VertexLitGeneric par défaut).
    """
    lines = template_text.replace("\r\n", "\n").split("\n")

    shader = "VertexLitGeneric"
    i = 0
    while i < len(lines) and not lines[i].strip():
        i += 1
    if i < len(lines):
        first = lines[i].strip()
        if first.startswith('"') and first.endswith('"'):
            shader = first.strip('"')

    body = []
    for line in lines:
        s = line.strip()

        # ignore shader line
        if s.startswith('"') and s.endswith('"') and s.strip('"').lower() == shader.lower():
            continue

        # ignore braces
        if s in ("{", "}"):
            continue

        # ignore base/bump lines from user template (car on les regénère)
        if BASE_RE.match(s) or BUMP_RE.match(s):
            continue

        body.append(line)

    # Trim
    while body and not body[0].strip():
        body.pop(0)
    while body and not body[-1].strip():
        body.pop()

    return shader, body


def _build_vmt_content(
    model_dir: str,
    diffuse_name: str,
    normal_name: str | None,
    template_text: str,
    nocull: bool | None = None,
    alphatest: bool | None = None,
    translucent: bool | None = None,
) -> str:
    shader, body = _sanitize_template(template_text)

    # Filtrer les options gérées par l'interface si elles ne sont pas None
    filtered_body = []
    for line in body:
        s = line.strip()
        if nocull is not None and re.match(r'^\s*"\$nocull"\s*".*"\s*$', s, re.IGNORECASE):
            continue
        if alphatest is not None and re.match(r'^\s*"\$alphatest"\s*".*"\s*$', s, re.IGNORECASE):
            continue
        if translucent is not None and re.match(r'^\s*"\$translucent"\s*".*"\s*$', s, re.IGNORECASE):
            continue
        filtered_body.append(line)

    out = []
    out.append(f'"{shader}"')
    out.append("{")
    # ✅ LIGNES AUTO (toujours générées)
    out.append(f'\t"$basetexture" "{model_dir}/{diffuse_name}"')
    if normal_name:
        out.append(f'\t"$bumpmap"     "{model_dir}/{normal_name}"')

    # ✅ Options VMT explicites
    if nocull is True:
        out.append('\t"$nocull" "1"')
    if alphatest is True:
        out.append('\t"$alphatest" "1"')
    if translucent is True:
        out.append('\t"$translucent" "1"')

    out.append("")

    # ✅ Le reste vient du template éditable
    out.extend(filtered_body)

    # fermer proprement
    if not out or out[-1].strip() != "}":
        out.append("}")

    return "\n".join(out) + "\n"


# ============================================================
# VMT creation
# ============================================================

def create_vmt_file(
    vtf_diffuse,
    vtf_normal,
    output_dir,
    model_dir,
    preset_name="props",
    nocull: bool | None = None,
    alphatest: bool | None = None,
    translucent: bool | None = None,
):
    diffuse_name = os.path.splitext(os.path.basename(vtf_diffuse))[0]
    normal_name  = os.path.splitext(os.path.basename(vtf_normal))[0]

    os.makedirs(output_dir, exist_ok=True)

    template_text = _load_template_text(preset_name)
    vmt_content = _build_vmt_content(
        model_dir,
        diffuse_name,
        normal_name,
        template_text,
        nocull=nocull,
        alphatest=alphatest,
        translucent=translucent,
    )

    vmt_file = os.path.join(output_dir, f"{diffuse_name}.vmt")
    with open(vmt_file, "w", encoding="utf-8") as f:
        f.write(vmt_content)

    print(f"Fichier VMT créé : {vmt_file}")


def create_vmt_file_without_normal(
    vtf_diffuse,
    output_dir,
    model_dir,
    preset_name="props",
    nocull: bool | None = None,
    alphatest: bool | None = None,
    translucent: bool | None = None,
):
    diffuse_name = os.path.splitext(os.path.basename(vtf_diffuse))[0]
    os.makedirs(output_dir, exist_ok=True)

    template_text = _load_template_text(preset_name)
    vmt_content = _build_vmt_content(
        model_dir,
        diffuse_name,
        None,
        template_text,
        nocull=nocull,
        alphatest=alphatest,
        translucent=translucent,
    )

    vmt_file = os.path.join(output_dir, f"{diffuse_name}.vmt")
    with open(vmt_file, "w", encoding="utf-8") as f:
        f.write(vmt_content)

    print(f"Fichier VMT créé (sans normal map) : {vmt_file}")


# ============================================================
# Folder processing (identique)
# ============================================================

def process_vtf_directory(base_dir, target_folder):
    vtf_dir = os.path.join(base_dir, target_folder)
    output_dir = vtf_dir
    model_dir = f"models/kera/{target_folder}"

    if not os.path.isdir(vtf_dir):
        print(f"Le répertoire {vtf_dir} n'existe pas.")
        return

    vtf_files = [f for f in os.listdir(vtf_dir) if f.lower().endswith(".vtf")]
    if not vtf_files:
        print(f"Aucun fichier VTF trouvé dans le répertoire {vtf_dir}")
        return

    diffuse_suffixes = ["_d", "_diffuse", "_color", "_albedo", "_c", "_base", "_basecolor"]
    normal_suffixes  = ["_n", "_normal", "_nrm", "_norm"]

    diffuse_by_key = {}
    normal_by_key  = {}

    for filename in vtf_files:
        name_no_ext = os.path.splitext(filename)[0]
        name_lower  = name_no_ext.lower()

        map_type = detect_map_type(name_lower, diffuse_suffixes, normal_suffixes)
        key = make_pair_key(name_lower, diffuse_suffixes, normal_suffixes)

        if map_type == "normal":
            normal_by_key[key] = filename
        else:
            diffuse_by_key[key] = filename

    vmt_created = 0

    for key, diffuse_file in diffuse_by_key.items():
        diffuse_path = os.path.join(vtf_dir, diffuse_file)
        normal_file = normal_by_key.get(key)

        if normal_file:
            normal_path = os.path.join(vtf_dir, normal_file)
            create_vmt_file(diffuse_path, normal_path, output_dir, model_dir)
        else:
            create_vmt_file_without_normal(diffuse_path, output_dir, model_dir)

        vmt_created += 1

    print(f"\n{vmt_created} fichier(s) VMT créé(s) avec succès dans {output_dir}")


def process_vtf_folder(
    vtf_dir,
    model_dir,
    vtf_files_to_process=None,
    preset_name="props",
    nocull: bool | None = None,
    alphatest: bool | None = None,
    translucent: bool | None = None,
    callback=None,
):
    def log(msg: str):
        if callback:
            callback(msg)
        else:
            print(msg)

    if not os.path.isdir(vtf_dir):
        raise FileNotFoundError(f"Le répertoire {vtf_dir} n'existe pas.")

    output_dir = vtf_dir

    vtf_files = [f for f in os.listdir(vtf_dir) if f.lower().endswith(".vtf")]
    if not vtf_files:
        log(f"Aucun fichier VTF trouvé dans le répertoire {vtf_dir}")
        return 0

    diffuse_suffixes = ["_d", "_diffuse", "_color", "_albedo", "_c", "_base", "_basecolor"]
    normal_suffixes  = ["_n", "_normal", "_nrm", "_norm"]

    diffuse_by_key = {}
    normal_by_key  = {}

    for filename in vtf_files:
        name_no_ext = os.path.splitext(filename)[0]
        name_lower  = name_no_ext.lower()

        map_type = detect_map_type(name_lower, diffuse_suffixes, normal_suffixes)
        key = make_pair_key(name_lower, diffuse_suffixes, normal_suffixes)

        if map_type == "normal":
            normal_by_key[key] = filename
        else:
            diffuse_by_key[key] = filename

    processed_keys = None
    if vtf_files_to_process is not None:
        processed_keys = set()
        for f in vtf_files_to_process:
            name_no_ext = os.path.splitext(f)[0]
            name_lower = name_no_ext.lower()
            key = make_pair_key(name_lower, diffuse_suffixes, normal_suffixes)
            processed_keys.add(key)

    vmt_created = 0

    for key, diffuse_file in diffuse_by_key.items():
        if processed_keys is not None and key not in processed_keys:
            continue
        diffuse_path = os.path.join(vtf_dir, diffuse_file)
        normal_file = normal_by_key.get(key)

        if normal_file:
            normal_path = os.path.join(vtf_dir, normal_file)
            create_vmt_file(
                diffuse_path,
                normal_path,
                output_dir,
                model_dir,
                preset_name=preset_name,
                nocull=nocull,
                alphatest=alphatest,
                translucent=translucent,
            )
            log(f"VMT: {os.path.splitext(diffuse_file)[0]}.vmt (avec normal)")
        else:
            create_vmt_file_without_normal(
                diffuse_path,
                output_dir,
                model_dir,
                preset_name=preset_name,
                nocull=nocull,
                alphatest=alphatest,
                translucent=translucent,
            )
            log(f"VMT: {os.path.splitext(diffuse_file)[0]}.vmt (sans normal)")

        vmt_created += 1

    log(f"{vmt_created} fichier(s) VMT créé(s) dans {output_dir}")
    return vmt_created


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Erreur : Aucun dossier cible spécifié.")
        sys.exit(1)

    target_folder = sys.argv[1]
    base_dir = r"C:\Program Files (x86)\Steam\steamapps\common\GarrysMod\garrysmod\materials\models\kera"
    process_vtf_directory(base_dir, target_folder)