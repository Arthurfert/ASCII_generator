"""Point d'entrée principal du générateur ASCII."""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from logger.logger import logger
from tkinter import messagebox
from generatorGUI import ASCIIGeneratorGUI

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