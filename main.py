from gramatica import Gramatica
from gramatica import lungimeMaximaSir

# Creează gramatica din fișier cu tabel
gramatica = Gramatica("gramatica_profu.txt")

# Afișează gramatica
gramatica.afiseazaGramatica()

# Afișează tabelul
if gramatica.tabel:
    print("\nTabel:")
    gramatica.tabel.afiseazaTabel()

# Șiruri de test
siruri_test = [
    "a+a",
    "a*a",
    "a+a*a",
    "(a+a)",
]

for sir in siruri_test:
    print(f"\nVerificare șir: '{sir}'")
    rezultat = gramatica.verificaSir(sir)
    print(f"Rezultat: {'ACCEPTAT' if rezultat else 'RESPINS'}")

# print("\n\nLanturi generate:")
# gramatica.genereazaLanturi(lungimeMaximaSir)

