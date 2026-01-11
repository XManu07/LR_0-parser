from gramatica import Gramatica

gramatica = Gramatica("gramatica.txt")

gramatica.afiseazaGramatica()

siruri_test = [
    "a+a",          # acceptat
    "a*a",          # acceptat
    "a+a*a",        # acceptat
    "(a+a)",        # acceptat
    "abc",          # respins
    "a*a+(a*a+a)",  # acceptat
    "a*a*a+(*)",    # respins
]

for sir in siruri_test:
    print(f"\nVerificare sir: '{sir}'")
    rezultat = gramatica.verificaSir(sir)
    print(f"Rezultat: {'ACCEPTAT' if rezultat else 'RESPINS'}")

# print("\n\nLanturi generate:")
# gramatica.genereazaLanturi(lungimeMaximaSir)

