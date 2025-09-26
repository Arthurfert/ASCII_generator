from logger.logger import logger
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading

from generator import ASCIIGenerator

# Vérifier si rembg est disponible (même logique que generator.py)
try:
    from rembg import remove
    REMBG_AVAILABLE = True
    logger.info("rembg disponible dans l'interface - Support de suppression d'arrière-plan activé")
except ImportError:
    REMBG_AVAILABLE = False
    logger.warning("rembg non disponible dans l'interface - Suppression d'arrière-plan désactivée")

class ASCIIGeneratorGUI:
    """Interface graphique pour le générateur ASCII."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Générateur d'Images ASCII")
        self.root.geometry("800x650")
        
        # Variables
        self.image_path = tk.StringVar()
        self.style = tk.StringVar(value="standard")
        self.width = tk.IntVar(value=80)
        self.remove_background = tk.BooleanVar(value=False)
        
        # Log du statut de rembg au démarrage
        if REMBG_AVAILABLE:
            logger.info("Interface: Suppression d'arrière-plan disponible")
        else:
            logger.warning("Interface: Suppression d'arrière-plan non disponible")
        
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
        title_label = ttk.Label(main_frame, text="Générateur d'Images ASCII", 
                                font=("Courier", 16, "bold"))
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
        
        # Options de traitement
        options_frame = ttk.LabelFrame(main_frame, text="Options de traitement", padding="5")
        options_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        # Checkbox pour suppression d'arrière-plan
        self.bg_checkbox = ttk.Checkbutton(
            options_frame, 
            text="Supprimer l'arrière-plan", 
            variable=self.remove_background,
            command=self.on_background_option_change
        )
        self.bg_checkbox.grid(row=0, column=0, sticky=tk.W)
        
        # Label d'information sur rembg - condition corrigée
        if REMBG_AVAILABLE:
            self.bg_info = ttk.Label(options_frame, text="✅ Disponible - Améliore le focus sur le sujet", 
                                    foreground="green", font=("Arial", 8))
        else:
            self.bg_info = ttk.Label(options_frame, text="❌ Installer avec 'pip install rembg' pour activer", 
                                    foreground="red", font=("Arial", 8))
            # Désactiver la checkbox si rembg n'est pas disponible
            self.bg_checkbox.config(state="disabled")
        
        self.bg_info.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        
        # Largeur
        ttk.Label(main_frame, text="Largeur:").grid(row=4, column=0, sticky=tk.W, pady=5)
        
        width_frame = ttk.Frame(main_frame)
        width_frame.grid(row=4, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Sous-frame pour le slider et le label
        slider_frame = ttk.Frame(width_frame)
        slider_frame.grid(row=0, column=0, sticky=tk.W)
        
        width_scale = ttk.Scale(slider_frame, from_=20, to=300, 
                               variable=self.width, orient=tk.HORIZONTAL, length=200)
        width_scale.grid(row=0, column=0, padx=(0, 10))
        
        self.width_label = ttk.Label(slider_frame, text="80 caractères")
        self.width_label.grid(row=0, column=1)
        
        # Boutons de taille prédéfinie
        preset_frame = ttk.LabelFrame(width_frame, text="Tailles prédéfinies", padding="5")
        preset_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Définition des tailles prédéfinies
        preset_sizes = [
            ("Très petit", 40),
            ("Petit", 60), 
            ("Moyen", 80),
            ("Grand", 120),
            ("Très grand", 200),
            ("Énorme", 300)
        ]
        
        # Créer les boutons de taille
        for i, (label, size) in enumerate(preset_sizes):
            btn = ttk.Button(preset_frame, text=f"{label}",
                            command=lambda s=size: self.set_width_preset(s),
                            width=10)
            btn.grid(row=0, column=i, padx=2, pady=2)
            
            # Ajouter une infobulle
            self.create_tooltip(btn, f"Définir la largeur à {size} caractères\nRecommandé pour: {self.get_size_recommendation(size)}")
        
        self.width.trace('w', self.update_width_label)
        
        # Boutons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=3, pady=20)
        
        self.generate_btn = ttk.Button(button_frame, text="🚀 Générer ASCII", 
                                        command=self.generate_ascii, style="Accent.TButton")
        self.generate_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="❌ Quitter", 
                    command=self.root.quit).pack(side=tk.LEFT)
        
        # Zone de résultat
        result_frame = ttk.LabelFrame(main_frame, text="Résultat ASCII", padding="5")
        result_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(20, 0))
        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(6, weight=1)
        
        # Zone de texte avec scrollbars
        text_frame = ttk.Frame(result_frame)
        text_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)
        
        self.result_text = tk.Text(text_frame, wrap=tk.NONE, font=("Courier", 9),
                                    bg="black", fg="white", insertbackground="white")
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.result_text.yview)
        h_scrollbar = ttk.Scrollbar(text_frame, orient=tk.HORIZONTAL, command=self.result_text.xview)
        
        self.result_text.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grille pour le texte et scrollbars
        self.result_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Message d'accueil dans la zone de résultat
        self.show_welcome_message()
        
        # Boutons pour le résultat
        result_buttons = ttk.Frame(result_frame)
        result_buttons.grid(row=1, column=0, pady=(10, 0))
        
        self.save_btn = ttk.Button(result_buttons, text="💾 Sauvegarder", 
                                    command=self.save_result, state="disabled")
        self.save_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.copy_btn = ttk.Button(result_buttons, text="📋 Copier", 
                                    command=self.copy_result, state="disabled")
        self.copy_btn.pack(side=tk.LEFT)

    def on_background_option_change(self):
        """Appelé quand l'option de suppression d'arrière-plan change."""
        if self.remove_background.get() and not REMBG_AVAILABLE:
            messagebox.showwarning(
                "Fonctionnalité non disponible",
                "Pour utiliser la suppression d'arrière-plan, installez rembg :\n\n"
                "pip install rembg\n\n"
                "Cette bibliothèque utilise l'IA pour détecter et supprimer "
                "automatiquement l'arrière-plan de vos images."
            )
            self.remove_background.set(False)
        elif self.remove_background.get():
            logger.info("Suppression d'arrière-plan activée par l'utilisateur")
        else:
            logger.info("Suppression d'arrière-plan désactivée par l'utilisateur")

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
        
    def set_width_preset(self, size):
        """Définit une taille prédéfinie."""
        self.width.set(size)
        logger.info(f"Taille prédéfinie sélectionnée: {size} caractères")
        
        # Effet visuel temporaire
        current_text = self.width_label.cget("text")
        self.width_label.config(text=f"✓ {size} caractères", foreground="green")
        self.root.after(1000, lambda: self.width_label.config(text=current_text, foreground="black"))
    
    def get_size_recommendation(self, size):
        """Retourne une recommandation d'usage pour chaque taille."""
        recommendations = {
            40: "Aperçu rapide, icônes",
            60: "Petits détails, miniatures", 
            80: "Usage général, équilibré",
            120: "Beaux détails, impression",
            200: "Haute qualité, affiches",
            300: "Très haute résolution"
        }
        return recommendations.get(size, "Usage personnalisé")
    
    def create_tooltip(self, widget, text):
        """Crée une infobulle pour un widget avec support du thème."""
        def on_enter(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            
            bg_color = "#FFFFDD"
            fg_color = "#000000"
            
            label = tk.Label(tooltip, text=text, justify=tk.LEFT,
                            background=bg_color, foreground=fg_color,
                            relief=tk.SOLID, borderwidth=1,
                            font=("Courier", 9))
            label.pack()
            
            widget.tooltip = tooltip
        
        def on_leave(event):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
                del widget.tooltip
        
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)

    def update_width_label(self, *args):
        """Met à jour le label de largeur avec indicateur de qualité."""
        size = self.width.get()
        
        # Indicateur de qualité selon la taille
        if size < 50:
            quality = "⚡ Rapide"
        elif size < 80:
            quality = "🚀 Optimal"  
        elif size < 150:
            quality = "⭐ Détaillé"
        elif size < 250:
            quality = "💎 Haute qualité"
        else:
            quality = "🔥 Ultra HD"
        
        self.width_label.config(text=f"{size} caractères - {quality}")
        
    def generate_ascii(self):
        """Lance la génération ASCII dans un thread séparé."""
        if not self.image_path.get():
            messagebox.showerror("Erreur", "Veuillez sélectionner une image")
            return
        
        # Réactiver l'édition de la zone de texte
        if hasattr(self, '_enable_editing'):
            self._enable_editing()
            
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
                width=self.width.get(),
                remove_bg=self.remove_background.get()
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
            
            # Statistiques avec style selon le thème
            lines = len(ascii_art.split('\n'))
            chars = len(ascii_art)
            style_name = self.style.get()
            width = self.width.get()
            bg_removed = "Oui" if self.remove_background.get() else "Non"
            
            stats = f"\n\n📊 Statistiques:\n"
            stats += f"   • Lignes: {lines}\n"
            stats += f"   • Caractères: {chars:,}\n"
            stats += f"   • Style: {style_name}\n"
            stats += f"   • Largeur: {width}\n"
            stats += f"   • Arrière-plan supprimé: {bg_removed}\n"
            
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
    
    def show_welcome_message(self):
        """Affiche le message d'accueil dans la zone de résultat."""
        welcome_text = f"""
╔════════════════════════════════════════════════════════════════════╗
║                         BIENVENUE !                               ║
╚════════════════════════════════════════════════════════════════════╝

 Ce logiciel convertit vos images en art ASCII créatif et personnalisable.

 COMMENT COMMENCER :
   1.  Cliquez sur "Parcourir..." pour sélectionner votre image
   2.  Choisissez un style de rendu dans le menu déroulant
   3.  Activez la suppression d'arrière-plan si désiré (recommandé pour portraits)
   4.  Ajustez la largeur avec le curseur ou les boutons prédéfinis
   5.  Cliquez sur "🚀 Générer ASCII" pour créer votre art

 STYLES DISPONIBLES :
   • Simple     → Rapide, idéal pour les tests
   • Standard   → Équilibre parfait qualité/vitesse
   • Detailed   → Maximum de détails et de nuances
   • Blocks     → Style pixel art moderne

 TAILLES RECOMMANDÉES :
   • 40-60      → Aperçus rapides, icônes
   • 80-100     → Usage général, partage
   • 120-200    → Haute qualité, impression
   • 200+       → Très haute résolution

 FONCTIONNALITÉS :
   ✅ Sauvegarde au format TXT
   ✅ Copie directe vers le presse-papiers
   ✅ Prévisualisation en temps réel
   ✅ Statistiques détaillées
   ✅ Suppression intelligente d'arrière-plan

 Formats supportés : JPEG, PNG, BMP, GIF, TIFF

═══════════════════════════════════════════════════════════════════════
        """
        
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(1.0, welcome_text.strip())
        
        # Désactiver l'édition du texte d'accueil
        self.result_text.config(state="disabled")
        
        # Réactiver l'édition lors de la prochaine génération
        def enable_editing():
            self.result_text.config(state="normal")
        
        # Stocker la fonction pour pouvoir la réutiliser
        self._enable_editing = enable_editing

    def run(self):
        """Lance l'interface graphique."""
        self.root.mainloop()