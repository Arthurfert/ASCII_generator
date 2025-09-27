# 🎨 ASCII image convertor

A python-coded image to ASCII convertor

## ✨ Features

- **Image conversion** : Supports JPEG, PNG, BMP, GIF, TIFF
- **4 character styles** : Simple, Standard, Détaillé, Blocs
- **Intelligent resizing** : Proportions preservation
- **Remove background** : Option to remove the background with rembg library
- **Backup**: Export to text files
- **Preview**: Full interface with tkinter
- **Logging**: Detailed tracking of operations
- **Optimizations**: Numpy calculations for better performance

## 📁 Project structure

```
ASCII_generator/
├── README.md                   # This file
├── logger/                     # Logging system
│   ├── __init__.py
│   └── logger.py
└── ascii/
│   ├── main.py                 # Entry point
│   ├── generator.py            # Backend
│   └── generatorGUI.py         # Frontend (GUI)
```

## 🚀 Installation and Use

### 1. Dependencies installation
```bash
pip install pillow
pip install numpy
pip install rembg
```

### 2. Basic use
```bash
python ascii/generator.py
```

## 🎯 Character styles

| Style | Character | Usage case |
|-------|------------|-------------|
| `simple` | ` .:-=+*#%@` | Fast rendering, simple images |
| `standard` | ` .,-:;i=+%O#@` | **Recommended** - Good balance |
| `detailed` | ` .'^\",:;Il!i><~+...` | Maximum detail, complex photos |
| `blocks` | ` ░▒▓█` | Pixel art style, logos |

## 🛠️ Configuration and Customization

### Conversion settings
- **width**: Width in characters (recommended: 40-120)
- **style**: Type of ASCII characters to use
- **save_to_file**: Output file (optional)

### Optimization according to image type
- **Portraits**: `standard` or `detailed` style, width 80-100
- **Logos/Icons**: `simple` or `blocks` style, width 40-60
- **Landscapes**: `detailed` style, width 100-120
- **Simple images**: `simple` style, width 60-80

## 🔧 Development

### Add a new style
```python
# In generator.py, modify ASCII_CHARS
ASCII_CHARS = {
    'my_style': " .-+#@",
    # ... other styles
}
```

## 📄 License

This project is under [MIT License](LICENSE).
