# 🎨 Générateur d'Images ASCII

Un générateur Python complet pour convertir vos images en art ASCII avec différents styles et niveaux de détail.

## ✨ Fonctionnalités

- 🖼️ **Conversion d'images** : Support JPEG, PNG, BMP, GIF, TIFF
- 🎭 **4 styles de caractères** : Simple, Standard, Détaillé, Blocs
- 📏 **Redimensionnement intelligent** : Préservation des proportions
- 💾 **Sauvegarde** : Export en fichiers texte
- 🔍 **Aperçu** : Interface complète avec tkinter
- 📊 **Logging** : Suivi détaillé des opérations
- 🚀 **Optimisations** : Calculs numpy pour de meilleures performances

## 📁 Structure du Projet

```
ASCII_generator/
├── README.md                   # Ce fichier
├── logger/                     # Système de logging
│   ├── __init__.py
│   └── logger.py
└── project_name/               # Code principal
```

## 🚀 Installation et Utilisation

### 1. Installation des dépendances
```bash
pip install pillow
pip install numpy
```

### 2. Utilisation basique
```bash
python ascii/generator.py
```

## 🎯 Styles de Caractères

| Style | Caractères | Cas d'usage |
|-------|------------|-------------|
| `simple` | ` .:-=+*#%@` | Rendu rapide, images simples |
| `standard` | ` .,-:;i=+%O#@` | **Recommandé** - Bon équilibre |
| `detailed` | ` .'^\",:;Il!i><~+...` | Maximum de détails, photos complexes |
| `blocks` | ` ░▒▓█` | Style pixel art, logos |

## 🛠️ Configuration et Personnalisation

### Paramètres de conversion
- **width** : Largeur en caractères (recommandé: 40-120)
- **style** : Type de caractères ASCII à utiliser
- **save_to_file** : Fichier de sortie (optionnel)

### Optimisation selon le type d'image
- **Portraits** : style `standard` ou `detailed`, width 80-100
- **Logos/Icônes** : style `simple` ou `blocks`, width 40-60  
- **Paysages** : style `detailed`, width 100-120
- **Images simples** : style `simple`, width 60-80

## 🔧 Développement

### Ajouter un nouveau style
```python
# Dans generator.py, modifier ASCII_CHARS
ASCII_CHARS = {
    'mon_style': " .-+#@",
    # ... autres styles
}
```

## 📄 Licence

Ce projet est libre d'utilisation ! Amusez-vous bien ! 🎉
