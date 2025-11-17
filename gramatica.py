from typing import List

class Gramatica:
    def __init__(self, numeFisier: str, numeFisierTabel: str = None):
        self.listaNeterminale = []
        self.listaTerminale = []
        self.simbolStart = ""
        self.listaProductii = []
        self.tabel = None
        self.citesteGramaticaDinFisier(numeFisier)
        
        # Citește tabelul dacă e furnizat
        if numeFisierTabel:
            self.tabel = TabelGramatica(numeFisierTabel)
        
    def citesteGramaticaDinFisier(self, numeFisier: str):
        with open(numeFisier, 'r') as f:
            linii = f.readlines()
            self.listaNeterminale = linii[0].strip().split(" ")
            self.listaTerminale = linii[1].strip().split(" ")
            self.simbolStart = linii[2].strip()
            self.listaProductii = []
            for i in range(3, len(linii)):
                linie = linii[i].split("->")
                productie = Productie(linie[0].strip(), linie[1].strip())
                self.adaugaProductie(productie)

    def adaugaProductie(self, productie):
            self.listaProductii.append(productie)

    def afiseazaGramatica(self):
        print("Gramatica a fost creata\n")
        print("Neterminale: ")
        for _ in range (0, len(self.listaNeterminale)):
            print(" " + self.listaNeterminale[_], end="")
        print("\nTerminale: ")
        for _ in range (0, len(self.listaTerminale)):
            print(" " + self.listaTerminale[_], end="")
        print("\nSimbol start: " + self.simbolStart)
        print("Productii: ")
        for i in range (0, len(self.listaProductii)):
            self.listaProductii[i].afiseazaProductie()

    def genereazaLanturi(self, lungimeMaximaSir):
        listaSiruri = [self.simbolStart]
        while len(listaSiruri) > 0:
            sirCurent = listaSiruri.pop(0)
            if len(sirCurent) > lungimeMaximaSir:
                continue
            # verificam daca sirul curent este format doar din terminale, print daca da
            if all(caracter in self.listaTerminale for caracter in sirCurent):
                print(sirCurent)
            else:
                # generam noi siruri prin inlocuirea neterminalelor
                for i in range(len(sirCurent)):
                    # cautam primul neterminal in sirul curent
                    if sirCurent[i] in self.listaNeterminale:
                        # inlocuim neterminalul cu fiecare posibilitate de productie
                        for productie in self.listaProductii:
                            # daca simbolul neterminal corespunde, inlocuim si generam un nou sir in lista de lanturi
                            if productie.simbolNeterminal == sirCurent[i]:
                                noulSir = sirCurent[:i] + productie.sirInlocuire + sirCurent[i+1:]
                                listaSiruri.append(noulSir)
                        break
    
    def verificaSir(self, sir: str):
        if not self.tabel:
            return False
        
        # Inițializare
        stiva = [0]  # Stiva începe cu starea 0
        sir_input = sir + '$'  # Adaugă marcatorul de final
        pozitie = 0  # Poziția curentă în șir
        
        pas = 0
        
        while True:
            pas += 1
            
            # Starea curentă = vârful stivei
            stare_curenta = stiva[-1]
            
            # Simbolul curent din input
            if pozitie < len(sir_input):
                simbol_curent = sir_input[pozitie]
            else:
                simbol_curent = '$'
            
            # Obține acțiunea din tabel
            actiune = self.tabel.obtine(stare_curenta, simbol_curent)
            
            # Verifică tipul acțiunii
            if actiune == '0' or actiune == '':
                # Eroare - acțiune invalidă
                return False
            
            elif actiune == 'acc':
                # Acceptare - șirul este valid
                return True
            
            elif actiune[0] == 'd':
                # Shift (deplasare) - d<stare>
                try:
                    stare_noua = int(actiune[1:])
                    stiva.append(simbol_curent)  # Adaugă simbolul
                    stiva.append(stare_noua)      # Adaugă starea nouă
                    pozitie += 1                  # Avansează în input
                except ValueError:
                    return False
            
            elif actiune[0] == 'r':
                # Reduce (reducere) - r<numar_productie>
                try:
                    numar_productie = int(actiune[1:])
                    
                    # Tabelul indexează producțiile de la 1, dar lista noastră de la 0
                    index_productie = numar_productie - 1
                    
                    # Găsește producția corespunzătoare, daca productia nu exista sirul nu apartine limbajului
                    if index_productie < 0 or index_productie >= len(self.listaProductii):
                        return False
                    
                    productie = self.listaProductii[index_productie]
                    
                    # Numărul de simboluri din partea dreaptă a producției
                    # Toate simbolurile sunt single-character
                    lungime_dreapta = len(productie.sirInlocuire)
                    
                    # Scoate 2 * lungime_dreapta elemente din stivă (stare + simbol pentru fiecare)
                    # Dacă producția este de lungime 0, nu scoatem nimic
                    if lungime_dreapta > 0:
                        for _ in range(2 * lungime_dreapta):
                            if len(stiva) > 1:  # Nu scoatem starea inițială 0
                                stiva.pop()
                    
                    # Starea de pe vârful stivei după reducere
                    stare_dupa_reduce = stiva[-1]
                    
                    # Neterminalul din partea stângă a producției
                    neterminal = productie.simbolNeterminal
                    
                    # Obține starea de salt din tabel
                    stare_salt = self.tabel.obtine(stare_dupa_reduce, neterminal)
                    
                    if stare_salt == '0' or stare_salt == '':
                        return False
                    
                    # Adaugă neterminalul și starea de salt pe stivă
                    stiva.append(neterminal)
                    stiva.append(int(stare_salt))
                    
                except (ValueError, IndexError):
                    return False
            
            else:
                # Acțiune necunoscută
                return False
            
            # Protecție împotriva buclelor infinite
            if pas > 1000:
                return False
        
class Productie:
    def __init__ (self, simbolNeterminal, sirInlocuire):
        self.simbolNeterminal = simbolNeterminal
        self.sirInlocuire = sirInlocuire

    def afiseazaProductie(self):
        print(self.simbolNeterminal + " -> " + self.sirInlocuire)
        
        
class TabelGramatica:
    def __init__(self, numeFisier: str):
        self.tabel = {}
        self.selectoriColoana = []
        self.citesteTabelDinFisier(numeFisier)
        
    def citesteTabelDinFisier(self, numeFisier: str):
        with open(numeFisier, 'r') as f:
            linii = f.readlines()
            
            # Prima linie - selectori pentru coloane
            self.selectoriColoana = linii[0].strip().split()
            
            # Restul liniilor - date (linia 1, 2, 3, ...)
            for numarLinie in range(1, len(linii)):
                valori = linii[numarLinie].strip().split()
                if valori and len(valori) == len(self.selectoriColoana):  # Verifică că linia e validă
                    # Creează dicționar pentru această linie (indexul liniei = numarLinie - 1)
                    self.tabel[numarLinie - 1] = {}
                    for i, selector in enumerate(self.selectoriColoana):
                        self.tabel[numarLinie - 1][selector] = valori[i]
    
    def obtine(self, selectorLinie: int, selectorColoana: str):
        return self.tabel.get(selectorLinie, {}).get(selectorColoana, '0')
    
    def afiseazaTabel(self):
        # Header
        print("     ", end="")
        for selector in self.selectoriColoana:
            print(f"{selector:5}", end="")
        print()
        
        # Date
        for linie in sorted(self.tabel.keys()):
            print(f"{linie:4} ", end="")
            for selector in self.selectoriColoana:
                valoare = self.obtine(linie, selector)
                print(f"{valoare:5}", end="")
            print()

lungimeMaximaSir = 10
