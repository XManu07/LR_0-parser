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
    
    if rezultat:
        print("ACCEPTAT")
        gramatica.generator.afiseaza_cod_intermediar()
    else:
        print("RESPINS")
    
    print()

# print("\n\nLanturi generate:")
# gramatica.genereazaLanturi(lungimeMaximaSir)

