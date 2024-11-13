import os
import requests
import zipfile
import sys
import shutil

# Configuration
VERSION = "1.0.1"  # Version locale initiale
VERSION_URL = "https://raw.githubusercontent.com/Crustabri/Speedfouf/main/version.txt"  # URL du fichier version.txt distant
UPDATE_DIR = "update"  # Dossier temporaire pour les mises à jour

def check_for_updates():
    """
    Vérifie si une mise à jour est disponible en comparant la version locale avec celle sur GitHub.
    """
    try:
        print("[INFO] Vérification des mises à jour...")
        response = requests.get(VERSION_URL)
        response.raise_for_status()
        latest_version = response.text.strip()  # Version sur GitHub

        if latest_version != VERSION:
            print(f"[INFO] Nouvelle version disponible : {latest_version}")
            return True, latest_version
        else:
            print("[INFO] Aucune mise à jour disponible.")
            return False, VERSION
    except Exception as e:
        print(f"[ERROR] Impossible de vérifier les mises à jour : {e}")
        return False, VERSION

def download_update(latest_version):
    """
    Télécharge la mise à jour depuis GitHub en générant l'URL basée sur la version récupérée.
    """
    try:
        # Génère l'URL de téléchargement pour la version récupérée
        game_url = f"https://github.com/Crustabri/Speedfouf/releases/download/{latest_version}/mygame.zip"
        print(f"[INFO] Téléchargement de la nouvelle version depuis : {game_url}")

        response = requests.get(game_url, stream=True)
        response.raise_for_status()

        # Crée un dossier temporaire pour la mise à jour
        zip_path = os.path.join(UPDATE_DIR, "update.zip")
        os.makedirs(UPDATE_DIR, exist_ok=True)

        # Télécharge le fichier zip
        with open(zip_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)

        print("[INFO] Téléchargement terminé. Extraction de la mise à jour...")

        # Extraction des fichiers
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(UPDATE_DIR)

        return True
    except Exception as e:
        print(f"[ERROR] Impossible de télécharger la mise à jour : {e}")
        return False

def apply_update(latest_version):
    """
    Applique la mise à jour téléchargée et met à jour la version locale.
    """
    global VERSION  # Permet de modifier la variable globale VERSION

    try:
        print("[INFO] Application de la mise à jour...")

        # Parcourt les fichiers extraits et les copie dans le répertoire principal
        for root, dirs, files in os.walk(UPDATE_DIR):
            for file in files:
                src_path = os.path.join(root, file)
                dst_path = os.path.join(os.getcwd(), file)
                print(f"[INFO] Remplacement : {src_path} -> {dst_path}")
                shutil.move(src_path, dst_path)

        # Met à jour la version locale
        VERSION = latest_version
        print(f"[INFO] Version locale mise à jour : {VERSION}")
        print("[INFO] Mise à jour appliquée avec succès.")
    except Exception as e:
        print(f"[ERROR] Impossible d'appliquer la mise à jour : {e}")

def restart_application():
    """
    Redémarre l'application après la mise à jour.
    """
    try:
        print("[INFO] Redémarrage de l'application...")
        os.execl(sys.executable, sys.executable, *sys.argv)
    except Exception as e:
        print(f"[ERROR] Impossible de redémarrer l'application : {e}")
        sys.exit(1)

def main():
    """
    Point d'entrée principal pour vérifier et appliquer les mises à jour avant de lancer le jeu.
    """
    # Vérifie les mises à jour
    update_available, latest_version = check_for_updates()

    if update_available:
        print(f"[INFO] Mise à jour disponible vers la version {latest_version}.")
        if download_update(latest_version):
            apply_update(latest_version)
            print("[INFO] Mise à jour terminée. Redémarrage...")
            restart_application()
        else:
            print("[ERROR] La mise à jour a échoué. Lancement de la version actuelle.")
    else:
        print(f"[INFO] Lancement de la version actuelle : {VERSION}")

if __name__ == "__main__":
    main()
