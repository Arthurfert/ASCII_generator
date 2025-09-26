import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from logger.logger import logger
from PIL import Image
import numpy as np

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
        logger.info(f"Générateur ASCII initialisé avec la palette '{ascii_chars}'")
    
    def load_image(self, image_path):
        """
        Charge une image depuis un fichier.
        
        Args:
            image_path (str): Chemin vers l'image
            
        Returns:
            PIL.Image: Image chargée ou None si erreur
        """
        try:
            if not os.path.exists(image_path):
                logger.error(f"Le fichier {image_path} n'existe pas")
                return None
                
            image = Image.open(image_path)
            logger.info(f"Image chargée: {image_path} - Taille: {image.size}")
            return image
            
        except Exception as e:
            logger.error(f"Erreur lors du chargement de l'image: {e}")
            return None
    
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
    
    def generate_ascii(self, image_path, width=100, save_to_file=None):
        """
        Génère l'art ASCII à partir d'une image.
        
        Args:
            image_path (str): Chemin vers l'image source
            width (int): Largeur en caractères
            save_to_file (str): Chemin pour sauvegarder (optionnel)
            
        Returns:
            str: Art ASCII ou None si erreur
        """
        logger.info(f"Début de la génération ASCII pour: {image_path}")
        
        # Chargement de l'image
        image = self.load_image(image_path)
        if image is None:
            return None
        
        # Redimensionnement
        image = self.resize_image(image, width)
        
        # Conversion en niveaux de gris
        image = self.convert_to_grayscale(image)
        
        # Conversion en ASCII
        ascii_lines = self.pixels_to_ascii(image)
        ascii_art = '\n'.join(ascii_lines)
        
        # Sauvegarde si demandée
        if save_to_file:
            try:
                with open(save_to_file, 'w', encoding='utf-8') as f:
                    f.write(ascii_art)
                logger.info(f"Art ASCII sauvegardé dans: {save_to_file}")
            except Exception as e:
                logger.error(f"Erreur lors de la sauvegarde: {e}")
        
        logger.info("Génération ASCII terminée avec succès")
        return ascii_art