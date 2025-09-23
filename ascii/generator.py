import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from logger.logger import logger
from PIL import Image
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading

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


class ASCIIGeneratorGUI:
    """Interface graphique pour le générateur ASCII."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🎨 Générateur d'Images ASCII")
        self.root.geometry("800x600")
        
        # Variables
        self.image_path = tk.StringVar()
        self.style = tk.StringVar(value="standard")
        self.width = tk.IntVar(value=80)
        
        self.setup_ui()
        
    def setup_ui(self):
        """Configure l'interface utilisateur."""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configuration responsive
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Titre
        title_label = ttk.Label(main_frame, text="🎨 Générateur d'Images ASCII", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Sélection d'image
        ttk.Label(main_frame, text="Image:").grid(row=1, column=0, sticky=tk.W, pady=5)
        
        image_frame = ttk.Frame(main_frame)
        image_frame.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        image_frame.columnconfigure(0, weight=1)
        
        self.image_entry = ttk.Entry(image_frame, textvariable=self.image_path, state="readonly")
        self.image_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        ttk.Button(image_frame, text="Parcourir...", 
                  command=self.browse_image).grid(row=0, column=1)
        
        # Style
        ttk.Label(main_frame, text="Style:").grid(row=2, column=0, sticky=tk.W, pady=5)
        
        style_combo = ttk.Combobox(main_frame, textvariable=self.style, 
                                  values=list(ASCIIGenerator.ASCII_CHARS.keys()),
                                  state="readonly", width=15)
        style_combo.grid(row=2, column=1, sticky=tk.W, pady=5)
        
        # Description du style
        self.style_desc = ttk.Label(main_frame, text="Bon équilibre qualité/vitesse", 
                                   foreground="gray")
        self.style_desc.grid(row=2, column=2, sticky=tk.W, padx=(10, 0), pady=5)
        style_combo.bind('<<ComboboxSelected>>', self.update_style_description)
        
        # Largeur
        ttk.Label(main_frame, text="Largeur:").grid(row=3, column=0, sticky=tk.W, pady=5)
        
        width_frame = ttk.Frame(main_frame)
        width_frame.grid(row=3, column=1, columnspan=2, sticky=tk.W, pady=5)
        
        width_scale = ttk.Scale(width_frame, from_=20, to=150, 
                               variable=self.width, orient=tk.HORIZONTAL, length=200)
        width_scale.grid(row=0, column=0, padx=(0, 10))
        
        self.width_label = ttk.Label(width_frame, text="80 caractères")
        self.width_label.grid(row=0, column=1)
        
        self.width.trace('w', self.update_width_label)
        
        # Boutons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=3, pady=20)
        
        self.generate_btn = ttk.Button(button_frame, text="🚀 Générer ASCII", 
                                      command=self.generate_ascii, style="Accent.TButton")
        self.generate_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="❌ Quitter", 
                  command=self.root.quit).pack(side=tk.LEFT)
        
        # Zone de résultat
        result_frame = ttk.LabelFrame(main_frame, text="Résultat ASCII", padding="5")
        result_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(20, 0))
        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(5, weight=1)
        
        # Zone de texte avec scrollbars
        text_frame = ttk.Frame(result_frame)
        text_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)
        
        self.result_text = tk.Text(text_frame, wrap=tk.NONE, font=("Courier", 8),
                                  bg="black", fg="white", insertbackground="white")
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.result_text.yview)
        h_scrollbar = ttk.Scrollbar(text_frame, orient=tk.HORIZONTAL, command=self.result_text.xview)
        
        self.result_text.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grille pour le texte et scrollbars
        self.result_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Boutons pour le résultat
        result_buttons = ttk.Frame(result_frame)
        result_buttons.grid(row=1, column=0, pady=(10, 0))
        
        self.save_btn = ttk.Button(result_buttons, text="💾 Sauvegarder", 
                                  command=self.save_result, state="disabled")
        self.save_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.copy_btn = ttk.Button(result_buttons, text="📋 Copier", 
                                  command=self.copy_result, state="disabled")
        self.copy_btn.pack(side=tk.LEFT)
        
    def browse_image(self):
        """Ouvre le dialogue de sélection d'image."""
        filename = filedialog.askopenfilename(
            title="Sélectionner une image",
            filetypes=[
                ("Images", "*.jpg *.jpeg *.png *.bmp *.gif *.tiff"),
                ("JPEG", "*.jpg *.jpeg"),
                ("PNG", "*.png"),
                ("Tous les fichiers", "*.*")
            ]
        )
        if filename:
            self.image_path.set(filename)
            
    def update_style_description(self, event=None):
        """Met à jour la description du style sélectionné."""
        descriptions = {
            'simple': "Rapide, moins de détails",
            'standard': "Bon équilibre qualité/vitesse",
            'detailed': "Maximum de détails, plus lent",
            'blocks': "Style pixel art"
        }
        desc = descriptions.get(self.style.get(), "")
        self.style_desc.config(text=desc)
        
    def update_width_label(self, *args):
        """Met à jour le label de largeur."""
        self.width_label.config(text=f"{self.width.get()} caractères")
        
    def generate_ascii(self):
        """Lance la génération ASCII dans un thread séparé."""
        if not self.image_path.get():
            messagebox.showerror("Erreur", "Veuillez sélectionner une image")
            return
            
        # Désactiver le bouton pendant la génération
        self.generate_btn.config(state="disabled", text="⏳ Génération...")
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(1.0, "Génération en cours...\n")
        
        # Lancer dans un thread pour éviter de bloquer l'interface
        thread = threading.Thread(target=self._generate_ascii_thread)
        thread.daemon = True
        thread.start()
        
    def _generate_ascii_thread(self):
        """Thread de génération ASCII."""
        try:
            generator = ASCIIGenerator(self.style.get())
            ascii_art = generator.generate_ascii(
                self.image_path.get(), 
                width=self.width.get()
            )
            
            # Mettre à jour l'interface dans le thread principal
            self.root.after(0, self._update_result, ascii_art)
            
        except Exception as e:
            error_msg = f"Erreur lors de la génération: {str(e)}"
            logger.error(error_msg)
            self.root.after(0, self._show_error, error_msg)
            
    def _update_result(self, ascii_art):
        """Met à jour le résultat dans l'interface (thread principal)."""
        self.generate_btn.config(state="normal", text="🚀 Générer ASCII")
        
        if ascii_art:
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(1.0, ascii_art)
            self.save_btn.config(state="normal")
            self.copy_btn.config(state="normal")
            
            # Statistiques
            lines = len(ascii_art.split('\n'))
            chars = len(ascii_art)
            stats = f"\n\n📊 Statistiques: {lines} lignes, {chars} caractères"
            self.result_text.insert(tk.END, stats)
        else:
            self._show_error("Échec de la génération ASCII")
            
    def _show_error(self, error_msg):
        """Affiche une erreur."""
        self.generate_btn.config(state="normal", text="🚀 Générer ASCII")
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(1.0, f"❌ {error_msg}")
        messagebox.showerror("Erreur", error_msg)
        
    def save_result(self):
        """Sauvegarde le résultat ASCII."""
        content = self.result_text.get(1.0, tk.END)
        if not content.strip():
            return
            
        filename = filedialog.asksaveasfilename(
            title="Sauvegarder l'art ASCII",
            defaultextension=".txt",
            filetypes=[("Fichiers texte", "*.txt"), ("Tous les fichiers", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                messagebox.showinfo("Succès", f"Art ASCII sauvegardé dans:\n{filename}")
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de la sauvegarde:\n{str(e)}")
                
    def copy_result(self):
        """Copie le résultat dans le presse-papiers."""
        content = self.result_text.get(1.0, tk.END)
        if content.strip():
            self.root.clipboard_clear()
            self.root.clipboard_append(content)
            messagebox.showinfo("Succès", "Art ASCII copié dans le presse-papiers!")
            
    def run(self):
        """Lance l'interface graphique."""
        self.root.mainloop()


def main():
    """Fonction principale avec interface graphique."""
    logger.info("=== GÉNÉRATEUR D'IMAGES ASCII - INTERFACE GRAPHIQUE ===")
    
    try:
        app = ASCIIGeneratorGUI()
        app.run()
    except Exception as e:
        logger.error(f"Erreur lors du lancement de l'interface: {e}")
        messagebox.showerror("Erreur", f"Impossible de lancer l'interface:\n{str(e)}")


if __name__ == "__main__":
    main()