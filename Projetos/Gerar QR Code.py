## 🔧 Instalação
pip install qrcode[pil]

## Passo a passo para gerar o QR Code

import qrcode
from PIL import Image

# Link do QR Code
data = "Colo que o seu link aqui"

# Criar QR Code
qr = qrcode.QRCode(
    version=None,
    error_correction=qrcode.constants.ERROR_CORRECT_H,
    box_size=10,
    border=4,
)

qr.add_data(data)
qr.make(fit=True)

# Criar imagem com cores personalizadas
img = qr.make_image(fill_color="black", back_color="white").convert('RGB')

# Abrir logo
logo = Image.open("logo.png")

# Redimensionar logo
img_w, img_h = img.size
logo_size = img_w // 4
logo = logo.resize((logo_size, logo_size))

# Posicionar no centro
pos = ((img_w - logo_size) // 2, (img_h - logo_size) // 2)

# Colar logo
img.paste(logo, pos)

# Salvar
img.save("qr_custom.png")
