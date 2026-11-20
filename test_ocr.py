
import pytesseract

pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

languages = pytesseract.get_languages(config="")

print("Tesseract fonctionne !")
print("Langues disponibles :", languages)

required = {"eng", "fra", "ara"}
missing = required - set(languages)

if missing:
    print("Langues manquantes :", missing)
else:
    print("Toutes les langues nécessaires sont installées.")
