# -*- coding: utf-8 -*-
import sys
import os
import json
import urllib.parse
import xbmcgui
import xbmcplugin

handle = int(sys.argv[1])
addon_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
traits_data_path = os.path.join(addon_path, 'resources', 'data', 'Traits.json')
traits_images_path = os.path.join(addon_path, 'resources', 'images', 'Traits')
brainrots_images_path = os.path.join(addon_path, 'resources', 'images', 'Brainrots')
brainrots_data_path = os.path.join(addon_path, 'resources', 'data', 'BrainrotsCatalogue.json')
bases_data_path = os.path.join(addon_path, 'resources', 'data', 'Bases.json')
mutations_data_path = os.path.join(addon_path, 'resources', 'data', 'Mutations.json')
    
# --- Utilitaire pour convertir les grands nombres ($90M, $6T, etc.) ---
def format_money(value):
    try:
        value = float(value)
    except (TypeError, ValueError):
        return str(value)

    suffixes = ['', 'K', 'M', 'B', 'T']
    magnitude = 0
    while abs(value) >= 1000 and magnitude < len(suffixes) - 1:
        magnitude += 1
        value /= 1000.0
    # Supprime les zéros inutiles
    return f"${value:.1f}".rstrip('0').rstrip('.') + suffixes[magnitude]

def build_url(query):
    """Construit une URL interne pour naviguer dans le plugin"""
    return sys.argv[0] + '?' + urllib.parse.urlencode(query)

def show_menu():
    """Affiche le menu principal"""
    xbmcplugin.setPluginCategory(handle, "Brainrot Manager")
    xbmcplugin.setContent(handle, "videos")

    menu_items = [
        ("Mes Bases", "mes_bases", "🧱"),
        ("Tous les Traits", "tous_les_traits", "🧬"),
        ("Toutes les Brainrots", "toutes_les_brainrots", "🧠")
    ]

    for label, action, icon in menu_items:
        url = build_url({'action': action})
        li = xbmcgui.ListItem(label=f"{icon} {label}")
        xbmcplugin.addDirectoryItem(handle=handle, url=url, listitem=li, isFolder=True)

    xbmcplugin.endOfDirectory(handle)

def show_all_brainrots():
    """Affiche toutes les brainrots depuis le catalogue JSON"""
    xbmcplugin.setPluginCategory(handle, "Brainrot Manager")
    xbmcplugin.setContent(handle, "movies")    

    if not os.path.exists(brainrots_data_path):
        xbmcgui.Dialog().ok("Erreur", f"Fichier introuvable : {brainrots_data_path}")
        return

    with open(brainrots_data_path, 'r', encoding='utf-8-sig') as f:
        try:
            brainrots = json.load(f)
        except Exception as e:
            xbmcgui.Dialog().ok("Erreur JSON", f"Impossible de lire le catalogue:\n{e}")
            return

    for b in brainrots:
        name = b.get("Name", "Inconnu")
        rarity = b.get("Rarity", "???")
        cost = b.get("Cost", 0)
        income = b.get("BaseIncomePerSecond", 0)
        spawn_rate = b.get("SpawnRate", "Inconnu")
        secret = b.get("Secret", False)
        controversy = b.get("Controversy", "")
        desc = b.get("Description", "")
        event = b.get("Event", "")
        added = b.get("AddedAt", "")
        acquisition = b.get("Acquisition", {})

        cost_str = format_money(cost)
        income_str = format_money(income)

        # Crée la ligne affichée dans la liste Kodi
        label = f"{name} [{rarity}] - {cost_str} - {income_str}/s"
        list_item = xbmcgui.ListItem(label=name, label2=f"{rarity} - {cost_str} - {income_str}/s")

        # --- InfoTag enrichi ---
        info_tag = list_item.getVideoInfoTag()
        info_tag.setTitle(name)
        info_tag.setGenres([rarity, f"Prix: {cost_str}", f"Revenu: {income_str}/s"])
        info_tag.setPlot(f"{desc} {acquisition.get('Purchase', '')} {acquisition.get('Steal', '')} {acquisition.get('Strategy', '')} {controversy}")
        info_tag.setYear(int(added.split("-")[0]) if added and added[:4].isdigit() else 2025)
        info_tag.setDateAdded(f"{added if added else '2025-01-01'} 00:00:00")

        # --- Image ---
        image_path = os.path.join(brainrots_images_path, b.get("Image", ""))
        if os.path.exists(image_path):
            list_item.setArt({
                'icon': image_path,
                'thumb': image_path,
                'poster': image_path,
                'fanart': image_path
            })
        else:
            list_item.setArt({'icon': 'DefaultFolder.png'})

        # --- Ajouter à la liste Kodi ---
        xbmcplugin.addDirectoryItem(handle=handle, url="", listitem=list_item, isFolder=False)
    xbmcplugin.endOfDirectory(handle)

def show_all_traits():
    """Affiche tous les traits depuis le fichier JSON"""
    xbmcplugin.setPluginCategory(handle, "Brainrot Manager")
    xbmcplugin.setContent(handle, "movies")

    if not os.path.exists(traits_data_path):
        xbmcgui.Dialog().ok("Erreur", f"Fichier introuvable : {traits_data_path}")
        return

    with open(traits_data_path, 'r', encoding='latin-1') as f:
        try:
            traits = json.load(f)
        except Exception as e:
            xbmcgui.Dialog().ok("Erreur JSON", f"Impossible de lire Traits.json :\n{e}")
            return

    for t in traits:
        name = t.get("Name", "Inconnu")
        multiplier = t.get("Multiplier", 1.0)
        image = t.get("Image", "")
        desc = t.get("Description", "")
        
        label = f"{name}"
        list_item = xbmcgui.ListItem(label=label, label2=f"{multiplier}X")

        # --- InfoTagMusic pour les métadonnées ---
        info_tag = list_item.getVideoInfoTag()
        info_tag.setTitle(name)
        info_tag.setGenres(['Trait', f"Multiplicateur: {multiplier}X"])
        info_tag.setYear(2025)
        info_tag.setPlot(desc)
        info_tag.setRating(min(multiplier / 10, 1.0) * 10)  # simple barème 0–10

        # --- Image associée ---
        image_path = os.path.join(traits_images_path, image)
        if os.path.exists(image_path):
            list_item.setArt({
                'icon': image_path,
                'thumb': image_path,
                'poster': image_path,
                'fanart': image_path
            })
        else:
            list_item.setArt({'icon': 'DefaultFolder.png'})

        xbmcplugin.addDirectoryItem(handle=handle, url="", listitem=list_item, isFolder=False)

    xbmcplugin.endOfDirectory(handle)

def show_all_bases():
    """Affiche la liste des bases depuis Bases.json avec menu contextuel"""
    xbmcplugin.setPluginCategory(handle, "Brainrot Manager")
    xbmcplugin.setContent(handle, "movies")

    image_path = os.path.join(addon_path, 'resources', 'images', 'Base_Fanart.png')

    if not os.path.exists(bases_data_path):
        xbmcgui.Dialog().ok("Erreur", f"Fichier introuvable : {bases_data_path}")
        return

    with open(bases_data_path, 'r', encoding='latin-1') as f:
        try:
            bases = json.load(f)
        except Exception as e:
            xbmcgui.Dialog().ok("Erreur JSON", f"Impossible de lire Bases.json :\n{e}")
            return

    # Liste chaque base
    for base in bases:
        base_name = base.get("Name", "Base inconnue")
        brainrots = base.get("Brainrots", [])

        label = f"{base_name} ({len(brainrots)} brainrots)"
        list_item = xbmcgui.ListItem(label=label)

        # --- InfoTagMusic pour un rendu riche ---
        info_tag = list_item.getVideoInfoTag()
        info_tag.setTitle(base_name)
        info_tag.setPlot(f"{len(brainrots)} Brainrots enregistrés dans cette base.")

        # --- Image associée ---
        if os.path.exists(image_path):
            list_item.setArt({
                'icon': image_path,
                'thumb': image_path,
                'poster': image_path,
                'fanart': image_path
            })
        else:
            list_item.setArt({'icon': 'DefaultFolder.png'})

        # --- Menu contextuel ---
        context_items = [
            ("Ajouter une Base", f"RunPlugin({build_url({'action': 'add_base'})})"),
            ("Renommer cette Base", f"RunPlugin({build_url({'action': 'rename_base', 'name': base_name})})"),
            ("Supprimer cette Base", f"RunPlugin({build_url({'action': 'delete_base', 'name': base_name})})")
        ]
        list_item.addContextMenuItems(context_items, replaceItems=True)

        url = build_url({'action': 'show_base_brainrots', 'base': base_name})
        xbmcplugin.addDirectoryItem(handle=handle, url=url, listitem=list_item, isFolder=True)

    xbmcplugin.endOfDirectory(handle)

def show_base_brainrots(base_name):
    """Affiche les brainrots d'une base spécifique"""
    xbmcplugin.setPluginCategory(handle, f"Brainrots de {base_name}")
    xbmcplugin.setContent(handle, "movies")

    # --- Lecture du fichier des bases ---
    if not os.path.exists(bases_data_path):
        xbmcgui.Dialog().ok("Erreur", f"Fichier introuvable : {bases_data_path}")
        return

    with open(bases_data_path, 'r', encoding='latin-1') as f:
        try:
            bases = json.load(f)
        except Exception as e:
            xbmcgui.Dialog().ok("Erreur JSON", f"Impossible de lire Bases.json :\n{e}")
            return

    # Trouve la base par son nom
    base = next((b for b in bases if b.get("Name") == base_name), None)
    if not base:
        xbmcgui.Dialog().ok("Erreur", f"Base '{base_name}' introuvable.")
        return

    brainrots = base.get("Brainrots", [])
    if not brainrots:
        xbmcgui.Dialog().notification("Aucune brainrot", f"La base {base_name} est vide.", xbmcgui.NOTIFICATION_INFO, 2500)
        xbmcplugin.endOfDirectory(handle)
        return

    # --- Liste les brainrots de la base ---
    for b in brainrots:
        name = b.get("Name", "Inconnu")
        rarity = b.get("Rarity", "???")
        cost = b.get("Cost", 0)
        base_income = b.get("BaseIncomePerSecond", 0)
        spawn_rate = b.get("SpawnRate", "Inconnu")
        secret = b.get("Secret", False)
        controversy = b.get("Controversy", "")
        desc = b.get("Description", "")
        event = b.get("Event", "")
        added = b.get("AddedAt", "")
        base = b.get("BaseName", base_name)
        acquisition = b.get("Acquisition", {})
        mutation = b.get("Mutation", {})
        traits = b.get("Traits", [])

        # --- Calcul du multiplicateur total ---
        multipliers = []
        if mutation and "Multiplier" in mutation:
            multipliers.append(mutation["Multiplier"])
        multipliers += [t.get("Multiplier", 1.0) for t in traits if "Multiplier" in t]

        if multipliers:
            N = len(multipliers)
            total_multiplier = sum(multipliers) - (N - 1)
        else:
            total_multiplier = 1.0

        total_income = base_income * total_multiplier

        cost_str = format_money(cost)
        income_str = format_money(total_income)
        mutation_name = mutation.get("Name", "")
        trait_names = [t.get("Name", "") for t in traits if t.get("Name")]
        genres = []
        if mutation_name:
            genres.append(mutation_name)
        if trait_names:
            genres.extend(trait_names)

        label = f"{name} - {rarity} - {income_str}/s"
        list_item = xbmcgui.ListItem(label=label, label2=f"{rarity} - {cost_str} - {income_str}/s")

        # --- InfoTag enrichi ---
        info_tag = list_item.getVideoInfoTag()
        info_tag.setTitle(f"{name} - {rarity} - {income_str}/s")
        info_tag.setGenres(genres)
        info_tag.setPlot(f"{desc}\n\n{acquisition.get('Purchase', '')}\n{acquisition.get('Steal', '')}\n{acquisition.get('Strategy', '')}\n{controversy}")
        info_tag.setYear(int(added.split("-")[0]) if added and added[:4].isdigit() else 2025)
        info_tag.setDateAdded(f"{added if added else '2025-01-01'} 00:00:00")

        # --- Image principale (Brainrot) ---
        image_path = os.path.join(brainrots_images_path, b.get("Image", ""))
        if os.path.exists(image_path):
            list_item.setArt({
                'icon': image_path,
                'thumb': image_path,
                'poster': image_path,
                'fanart': image_path
            })
        else:
            list_item.setArt({'icon': 'DefaultFolder.png'})

        # --- Traits associés (affichés dans "plot") ---
        if traits:
            traits_info = "\n\nTraits associés:\n"
            for t in traits:
                trait_img = os.path.join(traits_images_path, t.get("Image", ""))
                traits_info += f"• {t.get('Name')} (x{t.get('Multiplier')}) - {t.get('Description', '')}\n"
                if os.path.exists(trait_img):
                    list_item.addAvailableArtwork(trait_img, "thumb")

            info_tag.setPlot(info_tag.getPlot() + traits_info)

        # --- Menu contextuel pour chaque Brainrot ---
        context_items = [
            ("Ajouter un Brainrot", f"RunPlugin({build_url({'action': 'add_brainrot', 'base': base_name})})"),
            ("Supprimer ce Brainrot", f"RunPlugin({build_url({'action': 'delete_brainrot', 'base': base_name, 'id': b.get('Id')})})"),
            ("Déplacer ce Brainrot", f"RunPlugin({build_url({'action': 'move_brainrot', 'base': base_name, 'id': b.get('Id')})})")
        ]
        list_item.addContextMenuItems(context_items, replaceItems=True)
        xbmcplugin.addDirectoryItem(handle=handle, url="", listitem=list_item, isFolder=False)

    xbmcplugin.endOfDirectory(handle)

def add_brainrot(base_name):
    """Ajoute un Brainrot existant dans une base, avec sélection visuelle + mutation + traits"""
    dialog = xbmcgui.Dialog()

    # === Étape 1 : Choisir le Brainrot ===
    if not os.path.exists(brainrots_data_path):
        dialog.ok("Erreur", f"Catalogue introuvable : {brainrots_data_path}")
        return

    with open(brainrots_data_path, 'r', encoding='latin-1') as f:
        catalog = json.load(f)

    brainrot_names = [f"{b.get('Name', 'Inconnu')}  [{b.get('Rarity', '?')}]" for b in catalog]

    # Affiche la sélection avec icônes
    list_items = []
    for b in catalog:
        li = xbmcgui.ListItem(label=b.get('Name', 'Inconnu'), label2=b.get('Rarity', ''))
        img = os.path.join(brainrots_images_path, b.get('Image', ''))
        if os.path.exists(img):
            li.setArt({'icon': img, 'thumb': img})
        list_items.append(li)

    ret = dialog.select("Sélectionnez un Brainrot à ajouter", [li.getLabel() for li in list_items])
    if ret == -1:
        return
    selected_brainrot = catalog[ret]

    # === Étape 2 : Choisir la Mutation ===
    if not os.path.exists(mutations_data_path):
        dialog.ok("Erreur", f"Fichier introuvable : {mutations_data_path}")
        return

    with open(mutations_data_path, 'r', encoding='latin-1') as f:
        mutations = json.load(f)

    mutation_names = [f"{m.get('Name')} (x{m.get('Multiplier')})" for m in mutations]
    mutation_labels = []
    for m in mutations:
        li = xbmcgui.ListItem(label=m.get('Name'), label2=f"x{m.get('Multiplier')}")
        mutation_labels.append(li)

    mut_idx = dialog.select("Sélectionnez une Mutation", [li.getLabel() for li in mutation_labels])
    if mut_idx == -1:
        return
    selected_mutation = mutations[mut_idx]

    # === Étape 3 : Choisir les Traits (multi-sélection) ===
    if not os.path.exists(traits_data_path):
        dialog.ok("Erreur", f"Fichier introuvable : {traits_data_path}")
        return

    with open(traits_data_path, 'r', encoding='latin-1') as f:
        traits = json.load(f)

    trait_names = [f"{t.get('Name')} (x{t.get('Multiplier')})" for t in traits]
    trait_labels = []
    for t in traits:
        li = xbmcgui.ListItem(label=t.get('Name'), label2=f"x{t.get('Multiplier')}")
        img = os.path.join(traits_images_path, t.get('Image', ''))
        if os.path.exists(img):
            li.setArt({'icon': img, 'thumb': img})
        trait_labels.append(li)

    sel_traits_idx = dialog.multiselect("Sélectionnez les Traits", [li.getLabel() for li in trait_labels])
    selected_traits = [traits[i] for i in sel_traits_idx] if sel_traits_idx else []

    # === Étape 4 : Ajout dans la Base ===
    with open(bases_data_path, 'r', encoding='latin-1') as f:
        bases = json.load(f)

    base = next((b for b in bases if b.get("Name") == base_name), None)
    if not base:
        dialog.ok("Erreur", f"Base '{base_name}' introuvable.")
        return

    trait_part = "-".join([t.get("Name", "").replace(" ", "").lower() for t in selected_traits])
    base_id = selected_brainrot.get("Id", selected_brainrot.get("Name", "unknown")).replace(" ", "").lower()
    mut_part = selected_mutation.get("Name", "").replace(" ", "").lower()
    unique_id = f"{base_id}-{mut_part}"
    if trait_part:
        unique_id += f"-{trait_part}"

    # === Création du brainrot complet ===
    new_brainrot = selected_brainrot.copy()
    new_brainrot["Id"] = unique_id
    new_brainrot["Mutation"] = selected_mutation
    new_brainrot["BaseName"] = base_name
    new_brainrot["Traits"] = selected_traits

    base["Brainrots"].append(new_brainrot)

    with open(bases_data_path, 'w', encoding='latin-1') as f:
        json.dump(bases, f, indent=4, ensure_ascii=False)

    dialog.notification("Brainrot ajouté", f"{new_brainrot['Name']} dans {base_name}", xbmcgui.NOTIFICATION_INFO, 2500)
    xbmc.executebuiltin("Container.Refresh")

def delete_brainrot(base_name, brainrot_id):
    """Supprime un brainrot d'une base"""
    with open(bases_data_path, 'r', encoding='latin-1') as f:
        bases = json.load(f)

    base = next((b for b in bases if b.get("Name") == base_name), None)
    if not base:
        xbmcgui.Dialog().ok("Erreur", f"Base '{base_name}' introuvable.")
        return

    before = len(base.get("Brainrots", []))
    base["Brainrots"] = [br for br in base.get("Brainrots", []) if br.get("Id") != brainrot_id]
    after = len(base.get("Brainrots", []))

    if before == after:
        xbmcgui.Dialog().notification("Aucun changement", f"ID '{brainrot_id}' introuvable.", xbmcgui.NOTIFICATION_WARNING, 2500)
        return

    # Sauvegarde
    with open(bases_data_path, 'w', encoding='latin-1') as f:
        json.dump(bases, f, indent=4, ensure_ascii=False)

    xbmcgui.Dialog().notification("Brainrot supprimé", f"{name} retiré de {base_name}", xbmcgui.NOTIFICATION_INFO, 2500)
    xbmc.executebuiltin("Container.Refresh")  # 🔄 rafraîchir

def move_brainrot(base_name, brainrot_id):
    """Déplace un brainrot d'une base vers une autre via sélection de base"""
    dialog = xbmcgui.Dialog()

    if not os.path.exists(bases_data_path):
        dialog.ok("Erreur", f"Fichier introuvable : {bases_data_path}")
        return

    with open(bases_data_path, 'r', encoding='latin-1') as f:
        bases = json.load(f)

    # Trouve la base source et le brainrot à déplacer
    source_base = next((b for b in bases if b.get("Name") == base_name), None)
    if not source_base:
        dialog.ok("Erreur", f"Base source '{base_name}' introuvable.")
        return

    brainrot = next((br for br in source_base.get("Brainrots", []) if br.get("Id") == brainrot_id), None)
    if not brainrot:
        dialog.ok("Erreur", f"Brainrot introuvable dans {base_name}")
        return

    # Liste des autres bases disponibles
    other_bases = [b for b in bases if b.get("Name") != base_name]
    if not other_bases:
        dialog.ok("Aucune autre base", "Il n'y a pas d'autre base où déplacer ce Brainrot.")
        return

    base_names = [b.get("Name", "Sans nom") for b in other_bases]
    idx = dialog.select(f"Déplacer {brainrot['Name']} vers quelle base ?", base_names)
    if idx == -1:
        return

    target_base = other_bases[idx]

    # Déplace le brainrot
    source_base["Brainrots"] = [br for br in source_base.get("Brainrots", []) if br.get("Id") != brainrot_id]
    brainrot["BaseName"] = target_base['Name']
    target_base["Brainrots"].append(brainrot)

    # Sauvegarde
    with open(bases_data_path, 'w', encoding='latin-1') as f:
        json.dump(bases, f, indent=4, ensure_ascii=False)

    dialog.notification(
        "🔁 Brainrot déplacé",
        f"{brainrot['Name']} → {target_base['Name']}",
        xbmcgui.NOTIFICATION_INFO, 2500
    )
    xbmc.executebuiltin("Container.Refresh")

def add_base():
    """Ajoute une nouvelle base dans Bases.json"""
    name = xbmcgui.Dialog().input("Nom de la nouvelle base :", type=xbmcgui.INPUT_ALPHANUM)
    if not name:
        return

    # Charger le fichier
    try:
        with open(bases_data_path, 'r', encoding='latin-1') as f:
            bases = json.load(f)
    except:
        bases = []

    new_base = {"Name": name, "Brainrots": []}
    bases.append(new_base)

    with open(bases_data_path, 'w', encoding='latin-1') as f:
        json.dump(bases, f, indent=4, ensure_ascii=False)

    xbmcgui.Dialog().notification("Base ajoutée", f"{name} a été créée.", xbmcgui.NOTIFICATION_INFO, 3000)
    xbmc.executebuiltin("Container.Refresh")

def delete_base(name):
    """Supprime une base par son nom"""
    with open(bases_data_path, 'r', encoding='latin-1') as f:
        bases = json.load(f)

    bases = [b for b in bases if b.get("Name") != name]

    with open(bases_data_path, 'w', encoding='latin-1') as f:
        json.dump(bases, f, indent=4, ensure_ascii=False)

    xbmcgui.Dialog().notification("Base supprimée", f"{name} a été retirée.", xbmcgui.NOTIFICATION_INFO, 3000)
    xbmc.executebuiltin("Container.Refresh")

def rename_base(name):
    """Renomme une base existante"""
    new_name = xbmcgui.Dialog().input("Nouveau nom pour la base :", defaultt=name, type=xbmcgui.INPUT_ALPHANUM)
    if not new_name:
        return

    with open(bases_data_path, 'r', encoding='latin-1') as f:
        bases = json.load(f)

    for base in bases:
        if base.get("Name") == name:
            brainrots = base.get("Brainrots", [])
            for b in brainrots:
                b["BaseName"] = new_name
            base["Name"] = new_name
            break

    with open(bases_data_path, 'w', encoding='latin-1') as f:
        json.dump(bases, f, indent=4, ensure_ascii=False)

    xbmcgui.Dialog().notification("Base renommée", f"{name} → {new_name}", xbmcgui.NOTIFICATION_INFO, 3000)
    xbmc.executebuiltin("Container.Refresh")

def route(paramstring):
    """Router principal"""
    params = dict(urllib.parse.parse_qsl(paramstring))
    action = params.get('action')

    if action is None:
        show_menu()
    elif action == 'mes_bases':
        show_all_bases()
    elif action == 'move_brainrot':
        move_brainrot(params.get('base'), params.get('id'))
    elif action == 'show_base_brainrots':
        show_base_brainrots(params.get('base'))
    elif action == 'add_brainrot':
        add_brainrot(params.get('base'))
    elif action == 'delete_brainrot':
        delete_brainrot(params.get('base'), params.get('id'))
    elif action == 'add_base':
        add_base()
    elif action == 'delete_base':
        delete_base(params.get('name'))
    elif action == 'rename_base':
        rename_base(params.get('name'))
    elif action == 'tous_les_traits':
        show_all_traits()
    elif action == 'toutes_les_brainrots':
        show_all_brainrots()

if __name__ == '__main__':
    route(sys.argv[2][1:])