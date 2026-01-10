from gramatica import Gramatica

gramatica = Gramatica("gramatica_profu.txt")

# Afișează gramatica + tabel
gramatica.afiseazaGramatica()

siruri_test = [
    "a+a",
    "a*a",
    "a+a*a",
    "(a+a)",
    "abc",
    "a*a+(a*a+a)",
    "a*a*a+(*)"
]

for sir in siruri_test:
    print(f"\nVerificare sir: '{sir}'")
    rezultat = gramatica.verificaSir(sir)
    print(f"Rezultat: {'ACCEPTAT' if rezultat else 'RESPINS'}")

# print("\n\nLanturi generate:")
# gramatica.genereazaLanturi(lungimeMaximaSir)

