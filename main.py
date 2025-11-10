from gramatica import Gramatica
from gramatica import lungimeMaximaSir

# Creează gramatica din fișier cu tabel
gramatica = Gramatica("gramatica.txt", "tabel_gramatica.txt")

# Afișează gramatica
gramatica.afiseazaGramatica()

# Afișează tabelul
if gramatica.tabel:
    print("\nTabel de analiza:")
    gramatica.tabel.afiseazaTabel()

# Testează verificarea de șiruri
print("\n" + "="*70)
print("VERIFICARE SIRURI CU ALGORITMUL LR")
print("="*70)

# Șiruri de test
siruri_test = [
    "a+a",
    "a*a",
    "a+a*a",
    "(a+a)",
    "a+a+a",
    "abc",  # Invalid
    "(a",   # Invalid
]

for sir in siruri_test:
    print(f"\n{'='*70}")
    print(f"Verificare șir: '{sir}'")
    print(f"{'='*70}")
    rezultat = gramatica.verificaSir(sir, afiseazaPasi=True)
    print(f"\nRezultat: {'✓ ACCEPTAT' if rezultat else '✗ RESPINS'}")

# # Generează lanțuri (opțional - comentat pentru a nu încărca output-ul)
# print("\n\nLanturi generate:")
# gramatica.genereazaLanturi(lungimeMaximaSir)

