import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from logger.logger import logger
from PIL import Image
import numpy as np

# Import conditionnel pour rembg
try:
    from rembg import remove
    REMBG_AVAILABLE = True
    logger.info("rembg disponible - Support de suppression d'arrière-plan activé")
except ImportError:
    REMBG_AVAILABLE = False
    logger.warning("rembg non disponible - Suppression d'arrière-plan désactivée")

class ASCIIGenerator:
    """
    Générateur d'images ASCII à partir d'images classiques.
    Supporte différents niveaux de détail et styles de caractères.
    """
    
    # Différentes palettes de caractères ASCII (du plus sombre au plus clair)
    ASCII_CHARS = {
        'simple': " .:-=+*#%@",
        'detailed': " .'`^\",:;Il!i><~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$",
        'blocks': " ░▒▓█",
        'standard': " .,-:;i=+%O#@"
    }
    
    def __init__(self, ascii_chars='standard'):
        """
        Initialise le générateur ASCII.
        
        Args:
            ascii_chars (str): Type de caractères à utiliser ('simple', 'detailed', 'blocks', 'standard')
        """
        self.chars = self.ASCII_CHARS.get(ascii_chars, self.ASCII_CHARS['standard'])
        
        # Cache pour optimiser le traitement d'images
        self._image_cache = {}
        self._last_image_path = None
        self._original_image = None
        self._no_bg_image = None
        
        logger.info(f"Générateur ASCII initialisé avec la palette '{ascii_chars}'")
    
    def load_image(self, image_path):
        """
        Charge une image depuis un fichier avec mise en cache.
        
        Args:
            image_path (str): Chemin vers l'image
            
        Returns:
            PIL.Image: Image chargée ou None si erreur
        """
        try:
            if not os.path.exists(image_path):
                logger.error(f"Le fichier {image_path} n'existe pas")
                return None
            
            # Vérifier si c'est une nouvelle image
            if image_path != self._last_image_path:
                logger.info(f"Chargement d'une nouvelle image: {image_path}")
                
                # Nettoyer le cache pour la nouvelle image
                self._clear_cache()
                
                # Charger la nouvelle image
                image = Image.open(image_path)
                self._original_image = image.copy()
                self._last_image_path = image_path
                
                logger.info(f"Image chargée: {image_path} - Taille: {image.size}")
            else:
                logger.debug("Utilisation de l'image en cache")
                image = self._original_image.copy()
                
            return image
            
        except Exception as e:
            logger.error(f"Erreur lors du chargement de l'image: {e}")
            return None
    
    def _clear_cache(self):
        """Nettoie le cache des images traitées."""
        self._image_cache.clear()
        self._original_image = None
        self._no_bg_image = None
        logger.debug("Cache des images nettoyé")
    
    def remove_background(self, image):
        """
        Supprime l'arrière-plan de l'image avec mise en cache.
        
        Args:
            image (PIL.Image): Image source
            
        Returns:
            PIL.Image: Image sans arrière-plan ou image originale si erreur
        """
        if not REMBG_AVAILABLE:
            logger.warning("rembg non disponible - Suppression d'arrière-plan ignorée")
            return image
        
        # Vérifier si on a déjà traité cette image
        if self._no_bg_image is not None:
            logger.debug("Utilisation de l'image sans arrière-plan en cache")
            return self._no_bg_image.copy()
        
        try:
            logger.info("Suppression de l'arrière-plan en cours...")
            
            # Convertir en bytes pour rembg
            import io
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()
            
            # Supprimer l'arrière-plan
            output = remove(img_byte_arr)
            
            # Reconvertir en PIL Image
            result_image = Image.open(io.BytesIO(output))
            
            # Créer un fond noir pour remplacer la transparence
            if result_image.mode == 'RGBA':
                # Créer une image noire de la même taille
                background = Image.new('RGB', result_image.size, (0, 0, 0))
                # Composer l'image avec le fond noir
                background.paste(result_image, mask=result_image.split()[-1])  # Utiliser le canal alpha comme masque
                result_image = background
            
            # Mettre en cache le résultat
            self._no_bg_image = result_image.copy()
            logger.info("Arrière-plan supprimé avec succès et mis en cache")
            
            return result_image
            
        except Exception as e:
            logger.error(f"Erreur lors de la suppression d'arrière-plan: {e}")
            logger.info("Utilisation de l'image originale")
            return image
    
    def resize_image(self, image, width=100):
        """
        Redimensionne l'image en conservant les proportions.
        
        Args:
            image (PIL.Image): Image à redimensionner
            width (int): Largeur désirée en caractères
            
        Returns:
            PIL.Image: Image redimensionnée
        """
        # Calcul de la hauteur proportionnelle (caractères ASCII sont plus hauts que larges)
        aspect_ratio = image.height / image.width
        height = int(aspect_ratio * width * 0.55)  # 0.55 pour compenser la forme des caractères
        
        resized_image = image.resize((width, height))
        logger.debug(f"Image redimensionnée: {width}x{height}")
        return resized_image
    
    def convert_to_grayscale(self, image):
        """
        Convertit l'image en niveaux de gris.
        
        Args:
            image (PIL.Image): Image couleur
            
        Returns:
            PIL.Image: Image en niveaux de gris
        """
        grayscale = image.convert('L')
        logger.debug("Image convertie en niveaux de gris")
        return grayscale
    
    def pixels_to_ascii(self, image):
        """
        Convertit les pixels en caractères ASCII.
        
        Args:
            image (PIL.Image): Image en niveaux de gris
            
        Returns:
            list: Liste de chaînes ASCII (une par ligne)
        """
        # Conversion en array numpy pour traitement plus rapide
        pixels = np.array(image)
        
        # Normalisation des valeurs de pixels vers l'indice des caractères
        pixel_range = 256.0
        char_range = len(self.chars)
        
        # Calcul sécurisé pour éviter l'overflow
        ascii_pixels = (pixels.astype(float) * (char_range - 1) / (pixel_range - 1)).astype(int)
        
        # S'assurer que les indices sont dans la bonne plage
        ascii_pixels = np.clip(ascii_pixels, 0, char_range - 1)
        
        # Conversion en caractères ASCII
        ascii_lines = []
        for row in ascii_pixels:
            ascii_line = ''.join([self.chars[pixel] for pixel in row])
            ascii_lines.append(ascii_line)
        
        logger.debug(f"Conversion terminée: {len(ascii_lines)} lignes générées")
        return ascii_lines
    
    def generate_ascii(self, image_path, width=100, save_to_file=None, remove_bg=False, progress_callback=None):
        """
        Génère l'art ASCII à partir d'une image avec optimisations de cache.
        
        Args:
            image_path (str): Chemin vers l'image source
            width (int): Largeur en caractères
            save_to_file (str): Chemin pour sauvegarder (optionnel)
            remove_bg (bool): Supprimer l'arrière-plan avant conversion
            progress_callback (callable): Fonction appelée pour indiquer la progression
            
        Returns:
            str: Art ASCII ou None si erreur
        """
        def update_progress(step, details=""):
            if progress_callback:
                progress_callback(step, details)
        
        logger.info(f"Début de la génération ASCII pour: {image_path}")
        if remove_bg:
            logger.info("Option de suppression d'arrière-plan activée")
        
        update_progress("Chargement de l'image", "Lecture du fichier depuis le disque...")
        
        # Chargement de l'image (avec cache)
        image = self.load_image(image_path)
        if image is None:
            update_progress("❌ Erreur", "Impossible de charger l'image")
            return None
        
        # Suppression de l'arrière-plan si demandée (avec cache)
        if remove_bg:
            if self._no_bg_image is not None:
                update_progress("Arrière-plan", "Utilisation de l'image sans fond en cache...")
            else:
                update_progress("Suppression arrière-plan", "Traitement IA en cours (peut prendre quelques secondes)...")
            image = self.remove_background(image)
        
        update_progress("Redimensionnement", f"Ajustement à {width} caractères de largeur...")
        # Redimensionnement
        image = self.resize_image(image, width)
        
        update_progress("Conversion niveaux de gris", "Transformation de l'image en monochrome...")
        # Conversion en niveaux de gris
        image = self.convert_to_grayscale(image)
        
        update_progress("Génération ASCII", "Conversion des pixels en caractères...")
        # Conversion en ASCII
        ascii_lines = self.pixels_to_ascii(image)
        ascii_art = '\n'.join(ascii_lines)
        
        # Sauvegarde si demandée
        if save_to_file:
            update_progress("Sauvegarde", f"Écriture dans {save_to_file}...")
            try:
                with open(save_to_file, 'w', encoding='utf-8') as f:
                    f.write(ascii_art)
                logger.info(f"Art ASCII sauvegardé dans: {save_to_file}")
            except Exception as e:
                logger.error(f"Erreur lors de la sauvegarde: {e}")
                update_progress("❌ Erreur sauvegarde", str(e))
        
        update_progress("✅ Terminé", f"Art ASCII généré avec succès ({len(ascii_lines)} lignes)")
        logger.info("Génération ASCII terminée avec succès")
        return ascii_art