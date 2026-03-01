# lang.py
from __future__ import annotations

from typing import Dict

DEFAULT_LANG = "fr"

TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "fr": {
        # Tabs
        "tab_vtf": "VTF/VMT",
        "tab_vmt_edit": "VMT Edit",
        "tab_addon": "Addon Gmod",
        "tab_config": "Paramètres",
        "tab_about": "À propos",

        # Global
        "browse": "Parcourir...",
        "auto": "Auto",
        "run": "Exécuter",
        "save": "Valider",
        "success": "Succès",
        "error": "Erreur",
        "info": "Info",

        # VTF/VMT tab
        "title_convert": "Conversion VTF et VMT",
        "paths_group": "Chemins (mode dossiers)",
        "source_dir": "Dossier source (textures) :",
        "dest_dir": "Dossier destination :",
        "vmt_rel": "Chemin VMT relatif (dans le jeu) :",
        "options_group": "Options",
        "opt_vtf": "Convertir les fichiers en VTF",
        "opt_vmt": "Créer les fichiers VMT",
        "tex_size": "Taille des textures VTF :",
        "results_group": "Résultats",

        # Addon tab
        "title_addon": "Création d'Addon Gmod",
        "mode_group": "Mode de création",
        "mode_unique": "Modèle unique",
        "mode_series": "Série de modèles",
        "addon_config_group": "Configuration",
        "models_names": "Nom des modèles (séparés par des virgules) :",
        "workshop_folder": "Nom du dossier Workshop :",
        "paths_configured": "Chemins configurés",
        "create_addon": "Créer Addon(s)",

        # Config tab
        "title_config": "Configuration des chemins",
        "source_materials_base": "Chemin source materials :",
        "source_models_base": "Chemin source models :",
        "workshop_base": "Dossier Workshop :",
        "language_label": "Langue du logiciel :",
        "lang_restart_note": "Langue enregistrée. Redémarre le logiciel pour tout traduire.",

        # VMT Edit tab
        "title_vmt_edit": "Éditeur de preset VMT",
        "vmt_edit_desc": "Modifie le preset utilisé pour générer les VMT.\n"
                        "⚠ Les lignes $basetexture et $bumpmap seront toujours remplacées automatiquement.",
        "reset_preset": "Reset preset",
        "save_preset": "Sauvegarder preset",
        "preset_saved": "Preset sauvegardé.",
        "preset_reset": "Preset remis par défaut.",

        # About tab
        "title_about": "À propos",
        "welcome": "Bienvenue dans VTF Master!\nConfigurez vos options et cliquez sur 'Exécuter' pour démarrer la conversion.\n",

        # Messages / logs
        "log_convert_start": "[INFO] Conversion lancée...",
        "log_done": "[TERMINE] Opération terminée.",
        "need_one_option": "Coche au moins une option : VTF et/ou VMT.",
        "need_dest": "Veuillez renseigner le dossier destination.",
        "need_source_for_vtf": "Veuillez renseigner le dossier source (textures) pour convertir en VTF.",
        "missing_vtf_in_dest": "Aucun .vtf trouvé dans le dossier destination.\n"
                               "→ Soit coche 'Convertir les fichiers en VTF', soit mets tes .vtf dans le dossier destination.",
        "cannot_compute_vmt_rel": "Impossible de calculer le chemin VMT relatif automatiquement.\n"
                                  "Choisis un dossier destination sous 'materials'.",
        
        "about_text": (
            "VTF Master\n"
            "Auteur : Kera\n"
            "Version : 3.0.0\n\n"
            "Nouveautés (3.0.0) :\n"
            "• Onglet VMT Edit : preset VMT modifiable + bouton Reset\n"
            "• Preset appliqué à la génération (hors $basetexture / $bumpmap auto)\n"
            "• Détection diffuse/normal améliorée (_D_/_N_ + suffixes)\n"
            "• Chemin VMT relatif auto depuis 'materials'\n"
            "• Option VMT-only : pas besoin de dossier source si VTF décoché\n"
            "• Support multi-langue (FR/EN) + sauvegarde dans config\n\n"
            "Fonctions principales :\n"
            "• Conversion d’images (PNG/JPG/TGA/BMP/DDS) en VTF via VTFCmd\n"
            "• Génération automatique des VMT (diffuse + normal map si trouvée)\n"
            "• Création d’addons GMod (structure models/ & materials/ + addon.json)\n\n"
            "Dépendances incluses :\n"
            "• VTFCmd.exe\n"
            "• VTFLib.dll / DevIL.dll / HLLib.dll\n\n"
            "Astuce :\n"
            "• Mets le dossier destination dans .../garrysmod/materials/... pour auto-remplir le chemin VMT relatif.\n"
        ),
    },

    "en": {
        # Tabs
        "tab_vtf": "VTF/VMT",
        "tab_vmt_edit": "VMT Edit",
        "tab_addon": "Gmod Addon",
        "tab_config": "Settings",
        "tab_about": "About",

        # Global
        "browse": "Browse...",
        "auto": "Auto",
        "run": "Run",
        "save": "Save",
        "success": "Success",
        "error": "Error",
        "info": "Info",

        # VTF/VMT tab
        "title_convert": "VTF and VMT Conversion",
        "paths_group": "Paths (folder mode)",
        "source_dir": "Source folder (textures):",
        "dest_dir": "Destination folder:",
        "vmt_rel": "Relative VMT path (in-game):",
        "options_group": "Options",
        "opt_vtf": "Convert files to VTF",
        "opt_vmt": "Generate VMT files",
        "tex_size": "VTF texture size:",
        "results_group": "Results",

        # Addon tab
        "title_addon": "Gmod Addon Builder",
        "mode_group": "Creation mode",
        "mode_unique": "Single model",
        "mode_series": "Multiple models",
        "addon_config_group": "Configuration",
        "models_names": "Model names (comma-separated):",
        "workshop_folder": "Workshop folder name:",
        "paths_configured": "Configured paths",
        "create_addon": "Create Addon(s)",

        # Config tab
        "title_config": "Paths configuration",
        "source_materials_base": "Materials source path:",
        "source_models_base": "Models source path:",
        "workshop_base": "Workshop folder:",
        "language_label": "Software language:",
        "lang_restart_note": "Language saved. Restart the software to translate everything.",

        # VMT Edit tab
        "title_vmt_edit": "VMT preset editor",
        "vmt_edit_desc": "Edit the preset used to generate VMT files.\n"
                        "⚠ $basetexture and $bumpmap lines are always auto-generated.",
        "reset_preset": "Reset preset",
        "save_preset": "Save preset",
        "preset_saved": "Preset saved.",
        "preset_reset": "Preset reset to default.",

        # About tab
        "title_about": "About",
        "welcome": "Welcome to VTF Master!\nConfigure your options then click 'Run' to start.\n",

        # Messages / logs
        "log_convert_start": "[INFO] Conversion started...",
        "log_done": "[DONE] Operation finished.",
        "need_one_option": "Select at least one option: VTF and/or VMT.",
        "need_dest": "Please choose a destination folder.",
        "need_source_for_vtf": "Please choose a source folder (textures) to convert to VTF.",
        "missing_vtf_in_dest": "No .vtf found in destination.\n"
                               "→ Either enable VTF conversion, or place your .vtf files in destination.",
        "cannot_compute_vmt_rel": "Cannot compute relative VMT path automatically.\n"
                                  "Choose a destination under 'materials'.",
        
        "about_text": (
            "VTF Master\n"
            "Author: Kera\n"
            "Version: 3.0.0\n\n"
            "What's new (3.0.0):\n"
            "• VMT Edit tab: editable VMT preset + Reset button\n"
            "• Preset is applied on generation (except auto $basetexture / $bumpmap)\n"
            "• Improved diffuse/normal detection (_D_/_N_ tokens + suffixes)\n"
            "• Auto relative VMT path from 'materials'\n"
            "• VMT-only mode: no source folder needed when VTF is unchecked\n"
            "• Multi-language support (FR/EN) + saved in config\n\n"
            "Main features:\n"
            "• Convert images (PNG/JPG/TGA/BMP/DDS) to VTF using VTFCmd\n"
            "• Auto-generate VMT files (diffuse + normal map if found)\n"
            "• Create GMod addons (models/ & materials/ structure + addon.json)\n\n"
            "Included dependencies:\n"
            "• VTFCmd.exe\n"
            "• VTFLib.dll / DevIL.dll / HLLib.dll\n\n"
            "Tip:\n"
            "• Put destination folder inside .../garrysmod/materials/... to auto-fill the relative VMT path.\n"
        ),
    },
}


def tr(lang: str, key: str, **fmt) -> str:
    lang = (lang or DEFAULT_LANG).lower()
    table = TRANSLATIONS.get(lang, TRANSLATIONS[DEFAULT_LANG])
    text = table.get(key) or TRANSLATIONS[DEFAULT_LANG].get(key) or key
    if fmt:
        try:
            return text.format(**fmt)
        except Exception:
            return text
    return text