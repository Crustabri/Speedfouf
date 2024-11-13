import pygame

import sys
from Skins import SKINS
import time

import firebase_admin

from firebase_admin import credentials, db

import os

from update import check_for_updates, download_update, apply_update



# Fonction pour localiser les ressources incluses dans l'exécutable PyInstaller

def get_personal_leaderboard(pseudo):
    """Récupère les meilleurs scores pour un pseudo donné depuis Firebase."""
    try:
        ref = db.reference('leaderboard')
        data = ref.get()
        if not data:
            return []
        # Filtre les scores pour le pseudo donné
        personal_scores = [
            {"pseudo": entry["pseudo"], "time": float(entry["time"])}
            for entry in data.values()
            if entry["pseudo"] == pseudo
        ]
        # Trie les scores par ordre croissant
        personal_scores = sorted(personal_scores, key=lambda x: x["time"])
        return personal_scores[:5]  # Retourne les 5 meilleurs scores
    except Exception as e:
        print(f"[ERROR] Erreur lors de la récupération du leaderboard personnel : {e}")
        return []

def resource_path(relative_path):

    """ Obtenir le chemin absolu d'une ressource (dev et exe compilée). """

    try:

        base_path = sys._MEIPASS  # PyInstaller crée ce répertoire temporaire

    except AttributeError:

        base_path = os.path.abspath(".")  # Répertoire courant en mode développement

    return os.path.join(base_path, relative_path)



# Configuration Firebase

json_path = resource_path("bbyrapide-firebase-adminsdk-hl7mo-501bb5c8f6.json")

cred = credentials.Certificate(json_path)

firebase_admin.initialize_app(cred, {

    'databaseURL': 'https://bbyrapide-default-rtdb.europe-west1.firebasedatabase.app/'

})



def save_time_online(pseudo, elapsed_time):

    """Enregistre le temps en ligne."""

    try:

        ref = db.reference('leaderboard')

        new_entry = {

            "pseudo": pseudo,

            "time": elapsed_time

        }

        print(f"[DEBUG] Tentative d'enregistrement : {new_entry}")

        ref.push(new_entry)  # Ajoute un nouvel enregistrement

        print("[INFO] Temps sauvegardé en ligne avec succès.")

    except Exception as e:

        print(f"[ERROR] Échec de l'enregistrement en ligne : {e}")





def get_leaderboard_online():

    """Récupère le leaderboard en ligne."""

    ref = db.reference('leaderboard')

    data = ref.get()

    if not data:

        return []

    try:

        # Convertit les temps en float et trie

        sorted_scores = sorted(

            data.values(),

            key=lambda x: float(x['time'])  # Conversion explicite en float

        )

        print(f"[DEBUG] Scores récupérés et triés : {sorted_scores}")

        return sorted_scores[:5]

    except Exception as e:

        print(f"[ERROR] Erreur lors de la récupération du leaderboard : {e}")

        return []





# Initialisation de Pygame

pygame.init()



# Dimensions et couleurs

WIDTH, HEIGHT = 1000, 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GRAY = (200, 200, 200)
SQUARE_SIZE = 400
BRUSH_SIZE = 100
DEFAULT_BACKGROUND_COLOR = (255, 0, 0)  # Rouge par défaut

# Variable globale pour stocker la couleur de fond sélectionnée
background_color = DEFAULT_BACKGROUND_COLOR


# Position du carré blanc au centre

square_x = (WIDTH - SQUARE_SIZE) // 2

square_y = (HEIGHT - SQUARE_SIZE) // 2



# Fichier pour sauvegarder les temps

TIME_RECORD_FILE = "records_with_names.txt"



# Initialisation de l'écran

screen = pygame.display.set_mode((WIDTH, HEIGHT))

pygame.display.set_caption("Remplir le carré blanc")



# Initialisation de la police

pygame.font.init()

font = pygame.font.SysFont('Arial', 24)



def save_time(pseudo, elapsed_time):

    """Enregistre le pseudo et le temps dans un fichier."""

    with open(TIME_RECORD_FILE, "a") as file:

        file.write(f"{pseudo}:{elapsed_time:.2f}\n")  # Format pseudo:temps



def get_leaderboard():

    return get_leaderboard_online()



def is_fully_black(surface):

    """Vérifie si la surface est complètement noire."""

    array = pygame.surfarray.pixels3d(surface)

    return not array.any(axis=(0, 1)).sum()



def input_screen():
    """Écran de saisie du pseudo."""
    input_box = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 - 30, 300, 50)
    play_button = pygame.Rect(WIDTH // 2 - 75, HEIGHT // 2 + 50, 150, 50)
    pseudo = ""
    active = False
    running = True

    while running:
        screen.fill(GRAY)
        pygame.draw.rect(screen, WHITE, input_box)
        pygame.draw.rect(screen, RED, play_button)

        # Texte dans le champ de saisie
        text_surface = font.render(pseudo, True, BLACK)
        screen.blit(text_surface, (input_box.x + 10, input_box.y + 10))

        # Texte du bouton
        play_text = font.render("Jouer", True, WHITE)
        screen.blit(play_text, (play_button.x + 40, play_button.y + 10))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos):
                    active = True
                else:
                    active = False
                if play_button.collidepoint(event.pos) and pseudo:
                    return pseudo  # Retourne le pseudo pour démarrer le jeu
            elif event.type == pygame.KEYDOWN:
                # Ignore "Entrée" et autres touches spéciales
                if event.key == pygame.K_RETURN:
                    if pseudo:  # Valide uniquement si un pseudo existe
                        return pseudo
                elif active:
                    if event.key == pygame.K_BACKSPACE:
                        pseudo = pseudo[:-1]
                    elif len(pseudo) < 10:  # Limite la longueur du pseudo
                        # Ajoute uniquement des caractères imprimables
                        if event.unicode.isprintable():
                            pseudo += event.unicode



def locker_screen():
    """Affiche le casier pour changer la couleur de fond."""
    global background_color
    running = True

    # Position des boutons des couleurs
    button_positions = []
    button_width, button_height = 150, 50
    button_margin = 20

    # Décalage à gauche pour les boutons des couleurs
    colors_x_offset = WIDTH // 4 - button_width // 2  # Position sur le premier quart de l'écran

    # Génère des positions pour chaque couleur
    for i, (name, color) in enumerate(SKINS.items()):
        x = colors_x_offset
        y = 100 + i * (button_height + button_margin)
        button_positions.append((name, color, pygame.Rect(x, y, button_width, button_height)))

    while running:
        screen.fill(GRAY)

        # Titre du casier
        title_text = font.render("Casier : Choisissez une couleur de fond", True, WHITE)
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 20))

        # Affiche les boutons pour chaque couleur
        for name, color, rect in button_positions:
            pygame.draw.rect(screen, color, rect)
            text_surface = font.render(name, True, WHITE if sum(color) < 400 else BLACK)
            screen.blit(text_surface, (rect.x + (button_width - text_surface.get_width()) // 2,
                                       rect.y + (button_height - text_surface.get_height()) // 2))

        # Bouton "Retour"
        back_button = pygame.Rect(WIDTH // 2 - 75, HEIGHT - 100, 150, 50)  # Centré horizontalement
        pygame.draw.rect(screen, BLACK, back_button)
        back_text = font.render("Retour", True, WHITE)
        screen.blit(back_text, (back_button.x + (150 - back_text.get_width()) // 2,
                                back_button.y + (50 - back_text.get_height()) // 2))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()

                # Vérifie si une couleur est sélectionnée
                for name, color, rect in button_positions:
                    if rect.collidepoint(mouse_pos):
                        background_color = color  # Met à jour la couleur de fond
                        print(f"[INFO] Couleur sélectionnée : {name}")
                        running = False

                # Vérifie si le bouton "Retour" est cliqué
                if back_button.collidepoint(mouse_pos):
                    running = False


def main_game(pseudo):
    """Lance le jeu principal."""
    global background_color  # Utilise la couleur de fond sélectionnée
    running = True

    while running:
        # Récupère le leaderboard global et personnel
        leaderboard = get_leaderboard()
        personal_leaderboard = get_personal_leaderboard(pseudo)

        is_drawing = False
        start_time = None
        completed = False
        won = False
        clock = pygame.time.Clock()

        # Surface pour le carré blanc et son remplissage
        filled_surface = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE))
        filled_surface.fill(WHITE)
        print(f"[INFO] Nouvelle partie commencée pour {pseudo}.")

        # Prévisualisation du pinceau
        preview_brush = pygame.Surface((BRUSH_SIZE, BRUSH_SIZE))
        preview_brush.fill(BLACK)
        preview_brush.set_alpha(100)

        last_pos = None  # Garde en mémoire la dernière position de la souris

        # Boutons
        locker_button = pygame.Rect(WIDTH // 2 - 75, square_y + SQUARE_SIZE + 20, 150, 50)  # "Casier"
        back_button = pygame.Rect(10, HEIGHT - 70, 150, 50)  # "Retour"

        while not completed and running:
            # Affiche la couleur de fond sélectionnée
            screen.fill(background_color)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    print("[INFO] Quitter le jeu.")
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if back_button.collidepoint(event.pos):
                        print("[INFO] Retour à l'écran de pseudo.")
                        pygame.quit()  # Ferme la fenêtre actuelle
                        os.execl(sys.executable, sys.executable, *sys.argv)  # Relance le jeu
                    elif locker_button.collidepoint(event.pos):
                        print("[INFO] Accès au casier.")
                        locker_screen()  # Accède à l'écran du casier
                    else:
                        is_drawing = True
                        last_pos = pygame.mouse.get_pos()  # Enregistre la position initiale
                        if start_time is None:
                            start_time = time.time()
                            print(f"[INFO] Clic détecté. Début du chronomètre à {start_time}.")
                elif event.type == pygame.MOUSEBUTTONUP:
                    is_drawing = False
                    last_pos = None  # Réinitialise la position après le relâchement
                    completed = True
                    print("[INFO] Clic relâché. Game Over.")
                elif event.type == pygame.MOUSEMOTION and is_drawing:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    if last_pos:
                        # Remplit les positions intermédiaires pour éviter les trous
                        for i in range(1, 10):  # Divise le déplacement en 10 parties
                            interp_x = last_pos[0] + (mouse_x - last_pos[0]) * i / 10
                            interp_y = last_pos[1] + (mouse_y - last_pos[1]) * i / 10
                            if square_x <= interp_x <= square_x + SQUARE_SIZE and square_y <= interp_y <= square_y + SQUARE_SIZE:
                                brush_x = interp_x - square_x - BRUSH_SIZE // 2
                                brush_y = interp_y - square_y - BRUSH_SIZE // 2
                                pygame.draw.rect(filled_surface, BLACK, (brush_x, brush_y, BRUSH_SIZE, BRUSH_SIZE))
                    last_pos = (mouse_x, mouse_y)  # Met à jour la dernière position

            if is_drawing:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                if square_x <= mouse_x <= square_x + SQUARE_SIZE and square_y <= mouse_y <= square_y + SQUARE_SIZE:
                    brush_x = mouse_x - square_x - BRUSH_SIZE // 2
                    brush_y = mouse_y - square_y - BRUSH_SIZE // 2
                    pygame.draw.rect(filled_surface, BLACK, (brush_x, brush_y, BRUSH_SIZE, BRUSH_SIZE))

            # Affiche le carré blanc rempli
            screen.blit(filled_surface, (square_x, square_y))

            # Prévisualisation du pinceau
            mouse_x, mouse_y = pygame.mouse.get_pos()
            preview_x = mouse_x - BRUSH_SIZE // 2
            preview_y = mouse_y - BRUSH_SIZE // 2
            screen.blit(preview_brush, (preview_x, preview_y))

            # Vérifie si la surface est entièrement noire
            if is_fully_black(filled_surface):
                completed = True
                won = True
                print(f"[INFO] {pseudo} a rempli le carré. Victoire !")

            # Calcul du temps écoulé
            elapsed_time = 0 if start_time is None else time.time() - start_time

            # Affiche le temps écoulé
            elapsed_time_text = f"Temps: {elapsed_time:.2f} s"
            time_surface = font.render(elapsed_time_text, True, WHITE)
            screen.blit(time_surface, (10, 10))

            # Affiche le leaderboard global avec des couleurs
            leaderboard_text = "Leaderboard:"
            leaderboard_surface = font.render(leaderboard_text, True, WHITE)
            screen.blit(leaderboard_surface, (WIDTH - 250, 10))

            # Définir les couleurs des médailles
            medal_colors = [
                (255, 215, 0),  # Or
                (192, 192, 192),  # Argent
                (205, 127, 50)  # Bronze
            ]

            for i, entry in enumerate(leaderboard):
                # Utilise une couleur pour les 3 premiers, sinon blanc
                color = medal_colors[i] if i < 3 else WHITE
                record_text = f"{i + 1}. {entry['pseudo']} - {entry['time']:.2f} s"
                record_surface = font.render(record_text, True, color)
                screen.blit(record_surface, (WIDTH - 250, 40 + i * 30))

            # Affiche le leaderboard personnel
            personal_text = f"PB {pseudo}:"
            personal_surface = font.render(personal_text, True, WHITE)
            screen.blit(personal_surface, (WIDTH - 250, HEIGHT - 175))

            for i, entry in enumerate(personal_leaderboard):
                personal_record_text = f"{i + 1}. {entry['time']:.2f} s"
                personal_record_surface = font.render(personal_record_text, True, WHITE)
                screen.blit(personal_record_surface, (WIDTH - 250, HEIGHT - 150 + i * 30))

            # Affiche le bouton "Casier"
            pygame.draw.rect(screen, BLACK, locker_button)
            locker_text = font.render("Casier", True, WHITE)
            screen.blit(locker_text, (locker_button.x + (150 - locker_text.get_width()) // 2,
                                      locker_button.y + (50 - locker_text.get_height()) // 2))

            # Affiche le bouton "Retour"
            pygame.draw.rect(screen, BLACK, back_button)
            back_text = font.render("Retour", True, WHITE)
            screen.blit(back_text, (back_button.x + (150 - back_text.get_width()) // 2,
                                    back_button.y + (50 - back_text.get_height()) // 2))

            pygame.display.flip()
            clock.tick(60)

        if won:
            elapsed_time = time.time() - start_time
            print(f"[INFO] Envoi du score {pseudo} avec un temps de {elapsed_time:.2f}s à Firebase.")
            save_time_online(pseudo, elapsed_time)
            print(f"[INFO] Score sauvegardé : {pseudo} - {elapsed_time:.2f} secondes.")
        else:
            print("[INFO] Game Over. Temps non sauvegardé.")

        print("[INFO] Partie terminée. Redémarrage dans 1 seconde.")
        time.sleep(0)



if __name__ == "__main__":
    try:
        # Étape 1 : Vérification des mises à jour avant de lancer le jeu
        update_available, latest_version = check_for_updates()

        if update_available:
            print(f"[INFO] Nouvelle mise à jour disponible : version {latest_version}.")
            if download_update():
                apply_update()
                print("[INFO] Mise à jour terminée. Veuillez relancer le jeu.")
                sys.exit(0)  # Quitte le programme après la mise à jour
            else:
                print("[ERROR] Échec de la mise à jour. Lancement de la version actuelle...")

        # Étape 2 : Si aucune mise à jour, continue avec le jeu
        pseudo = input_screen()
        main_game(pseudo)

    except Exception as e:
        print(f"[ERROR] Une erreur est survenue: {e}")
    finally:
        pygame.quit()
        sys.exit()


#TODO Skins, mode de jeu, brush différente