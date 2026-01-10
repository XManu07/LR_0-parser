from typing import List, Set, Dict, Tuple, FrozenSet
import os

class Item:
    """Reprezintă un item LR(0): A → α • β"""
    def __init__(self, productieIdx: int, pozitieDot: int):
        self.productieIdx = productieIdx  # Indexul producției în lista de producții
        self.pozitieDot = pozitieDot      # Poziția punctului (0 = înainte de tot)
    
    def __eq__(self, other):
        return (self.productieIdx == other.productieIdx and 
                self.pozitieDot == other.pozitieDot)
    
    def __hash__(self):
        return hash((self.productieIdx, self.pozitieDot))
    
    def __repr__(self):
        return f"Item(prod={self.productieIdx}, dot={self.pozitieDot})"

class Gramatica:
    def __init__(self, numeFisier: str, numeFisierTabel: str = None):
        self.listaNeterminale = []
        self.listaTerminale = []
        self.simbolStart = ""
        self.listaProductii = []
        self.tabel = None
        
        # Citește gramatica din fișier
        self.citesteGramaticaDinFisier(numeFisier)
        
        # Determină numele fișierului de tabel
        if numeFisierTabel is None:
            # Generează nume automat: gramatica.txt -> tabel_gramatica.txt
            base = os.path.splitext(os.path.basename(numeFisier))[0]
            numeFisierTabel = f"tabel_{base}.txt"
        
        self.numeFisierTabel = numeFisierTabel
        
        # Generează tabelul, salvează în fișier, apoi încarcă din fișier
        generator = GeneratorTabel(self)
        generator.genereazaTabel()
        generator.salveazaTabelInFisier(self.numeFisierTabel)
        self.tabel = TabelGramatica(self.numeFisierTabel)
        
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
            
        self.tabel.afiseazaTabel()

    def genereazaLanturi(self, lungimeMaximaSir):
        listaSiruri = [self.simbolStart]
        while len(listaSiruri) > 0:
            sirCurent = listaSiruri.pop(0)
            if len(sirCurent) > lungimeMaximaSir:
                continue
            # verificam daca sirul curent este format doar din terminale, print daca da
            if self.esteSirTerminal(sirCurent):
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
    
    def esteSirTerminal(self, sir: str) -> bool:
        """Verifică dacă un șir conține doar terminale"""
        return all(caracter in self.listaTerminale for caracter in sir)
    
    def proceseazaShift(self, stiva: list, actiune: str, sirInput: str, pozitie: int) -> tuple:
        """Procesează operația shift. Returnează (success, pozitieNoua)"""
        try:
            stareNoua = int(actiune[1:])
            stiva.append(sirInput[pozitie])
            stiva.append(stareNoua)
            return True, pozitie + 1
        except (ValueError, IndexError):
            return False, pozitie
    
    def proceseazaReduce(self, stiva: list, actiune: str) -> bool:
        """Procesează operația reduce. Returnează success"""
        try:
            numarProductie = int(actiune[1:])
            indexProductie = numarProductie - 1
            
            if indexProductie < 0 or indexProductie >= len(self.listaProductii):
                return False
            
            productie = self.listaProductii[indexProductie]
            lungimeDreapta = len(productie.sirInlocuire)
            
            # Scoate 2 * lungimeDreapta elemente din stivă
            if lungimeDreapta > 0:
                for _ in range(2 * lungimeDreapta):
                    if len(stiva) > 1:
                        stiva.pop()
            
            stareDupaReduce = stiva[-1]
            neterminal = productie.simbolNeterminal
            stareSalt = self.tabel.obtine(stareDupaReduce, neterminal)
            
            if stareSalt == '0' or stareSalt == '':
                return False
            
            stiva.append(neterminal)
            stiva.append(int(stareSalt))
            return True
        except (ValueError, IndexError):
            return False
    
    def verificaSir(self, sir: str):
        if not self.tabel:
            return False
        
        # Inițializare
        stiva = [0]  # Stiva începe cu starea 0
        sirInput = sir + '$'  # Adaugă marcatorul de final
        pozitie = 0  # Poziția curentă în șir
        
        pas = 0
        
        while True:
            pas += 1
            
            # Starea curentă = vârful stivei
            stareCurenta = stiva[-1]
            
            # Simbolul curent din input
            if pozitie < len(sirInput):
                simbolCurent = sirInput[pozitie]
            else:
                simbolCurent = '$'
            
            # Obține acțiunea din tabel
            actiune = self.tabel.obtine(stareCurenta, simbolCurent)
            
            # Verifică tipul acțiunii
            if actiune == '0' or actiune == '':
                # Eroare - acțiune invalidă
                return False
            
            elif actiune == 'acc':
                # Acceptare - șirul este valid
                return True
            
            elif actiune[0] == 'd':
                # Shift (deplasare)
                success, pozitie = self.proceseazaShift(stiva, actiune, sirInput, pozitie)
                if not success:
                    return False
            
            elif actiune[0] == 'r':
                # Reduce (reducere)
                if not self.proceseazaReduce(stiva, actiune):
                    return False
            
            else:
                # Acțiune necunoscută
                return False
            
            # Protecție împotriva buclelor infinite
            if pas > 1000:
                return False


class GeneratorTabel:
    """
    Generator de tabel SLR (Simple LR Parser)
    Construieste tabelul de parsing pentru o gramatica data
    """
    def __init__(self, gramatica: 'Gramatica'):
        self.gramatica = gramatica
        
        # Augmentam gramatica: adaugam S' -> S pentru a avea un punct de start clar
        self.simbolStartAugmentat = self.gramatica.simbolStart + "'"
        productieAugmentata = Productie(self.simbolStartAugmentat, self.gramatica.simbolStart)
        self.productii = [productieAugmentata] + self.gramatica.listaProductii
        
        # FIRST[simbol] = terminalele care pot aparea primele in derivarea acelui simbol
        self.first: Dict[str, Set[str]] = {}
        
        # FOLLOW[neterminal] = terminalele care pot aparea imediat dupa neterminal
        self.follow: Dict[str, Set[str]] = {}
        
        # Lista tuturor starilor automatului LR(0)
        self.stari: List[FrozenSet[Item]] = []
        
        # Memoreaza tranzitiile: (stareIdx, simbol) -> stareDestinatie
        self.tranzitii: Dict[Tuple[int, str], int] = {}
        
        # Tabelul ACTION: (stareIdx, terminal) -> actiune (shift/reduce/accept)
        self.tabelAction: Dict[Tuple[int, str], str] = {}
        
        # Tabelul GOTO: (stareIdx, neterminal) -> stareDestinatie
        self.tabelGoto: Dict[Tuple[int, str], int] = {}
        
    def genereazaTabel(self):
        """
        Pasii pentru generarea tabelului SLR:
        1. Calculeaza seturile FIRST pentru toate simbolurile
        2. Calculeaza seturile FOLLOW pentru neterminale
        3. Construieste starile automatului LR(0)
        4. Populeaza tabelele ACTION si GOTO
        """
        self.calculeazaFirst()
        self.calculeazaFollow()
        self.construiesteStari()
        self.construiesteTabele()
        return self.tabelAction, self.tabelGoto
    
    def calculeazaFirst(self):
        """
        Calculeaza seturile FIRST pentru toate simbolurile.
        FIRST[simbol] = mulțimea terminalelor care pot aparea primele
        in orice derivare pornind de la acel simbol.
        
        Exemplu: FIRST(E) = {a, (} pentru gramatica de expresii
        """
        # Pas 1: Initializare - pentru terminale, FIRST = {terminalul insusi}
        for terminal in self.gramatica.listaTerminale + ['$']:
            self.first[terminal] = {terminal}
    
        # Pas 2: Pentru neterminale, initializam cu multimea vida
        for neterminal in self.gramatica.listaNeterminale + [self.simbolStartAugmentat]:
            self.first[neterminal] = set()
    
        # Pas 3: Iteram pana cand nu mai avem modificari (algoritm de punct fix)
        seModifica = True
        while seModifica:
            seModifica = False
            
            # Pentru fiecare productie A -> alfa
            for productie in self.productii:
                neterminalStang = productie.simbolNeterminal
                parteDreapta = productie.sirInlocuire
                
                if not parteDreapta:  # Productie vida
                    continue
                    
                # Luam primul simbol din partea dreapta
                primulSimbol = parteDreapta[0]
                
                # FIRST(A) primeste FIRST(primulSimbol)
                dimensiuneInainte = len(self.first[neterminalStang])
                self.first[neterminalStang].update(self.first.get(primulSimbol, set()))
                
                # Daca s-a modificat, continuam iteratiile
                if len(self.first[neterminalStang]) > dimensiuneInainte:
                    seModifica = True
    
    def calculeazaFollow(self):
        """
        Calculeaza seturile FOLLOW pentru neterminale.
        FOLLOW[neterminal] = mulțimea terminalelor care pot aparea
        imediat dupa acel neterminal in orice derivare.
        
        Exemplu: FOLLOW(E) = {$, ), +} pentru gramatica de expresii
        """
        # Pas 1: Initializare - toate neterminalele incep cu FOLLOW vid
        for neterminal in self.gramatica.listaNeterminale + [self.simbolStartAugmentat]:
            self.follow[neterminal] = set()
        
        # Pas 2: $ apartine FOLLOW(simbolul de start)
        self.follow[self.simbolStartAugmentat].add('$')
        
        # Pas 3: Iteram pana nu mai avem modificari (algoritm de punct fix)
        seModifica = True
        while seModifica:
            seModifica = False
            
            # Pentru fiecare productie A -> alfa
            for productie in self.productii:
                neterminalStang = productie.simbolNeterminal
                parteDreapta = productie.sirInlocuire
                
                # Examinam fiecare simbol din partea dreapta
                for pozitie, simbol in enumerate(parteDreapta):
                    # Ne intereseaza doar neterminalele
                    if simbol not in self.gramatica.listaNeterminale:
                        continue
                    
                    # Restul sirului dupa acest neterminal
                    restulSirului = parteDreapta[pozitie + 1:]
                    
                    if restulSirului:
                        # Caz 1: A -> alfa B beta
                        # FOLLOW(B) primeste FIRST(beta)
                        # Pentru gramatici fara epsilon: FIRST(beta) = FIRST(primul simbol din beta)
                        primulSimbol = restulSirului[0]
                        firstBeta = self.first.get(primulSimbol, set())
                        
                        dimensiuneInainte = len(self.follow[simbol])
                        self.follow[simbol].update(firstBeta)
                        
                        if len(self.follow[simbol]) > dimensiuneInainte:
                            seModifica = True
                    else:
                        # Caz 2: A -> alfa B (B este ultimul simbol)
                        # FOLLOW(B) primeste FOLLOW(A)
                        dimensiuneInainte = len(self.follow[simbol])
                        self.follow[simbol].update(self.follow[neterminalStang])
                        
                        if len(self.follow[simbol]) > dimensiuneInainte:
                            seModifica = True
    
    def closure(self, itemsInitiale: Set[Item]) -> FrozenSet[Item]:
        """
        Calculeaza closure (inchiderea) pentru un set de items.
        
        Regula: Daca avem [A -> alfa • B beta] si B este neterminal,
        adaugam toate items-urile [B -> • gamma] pentru fiecare productie B -> gamma
        
        Returneaza setul complet de items pentru o stare.
        """
        itemsCurente = set(itemsInitiale)
        
        # Iteram pana nu mai gasim items noi de adaugat
        seAdauga = True
        while seAdauga:
            seAdauga = False
            itemsDeAdaugat = set()
            
            # Examinam fiecare item din setul curent
            for item in itemsCurente:
                productie = self.productii[item.productieIdx]
                sirInlocuire = productie.sirInlocuire
                
                # Daca punctul e la sfarsit, nu mai avem ce adauga
                if item.pozitieDot >= len(sirInlocuire):
                    continue
                
                # Simbolul dupa punct
                simbolDupaPunct = sirInlocuire[item.pozitieDot]
                
                # Daca simbolul dupa punct este neterminal
                if simbolDupaPunct in self.gramatica.listaNeterminale or simbolDupaPunct == self.simbolStartAugmentat:
                    # Adaugam toate productiile pentru acest neterminal
                    # cu punctul la inceput: [B -> • gamma]
                    for idx, prod in enumerate(self.productii):
                        if prod.simbolNeterminal == simbolDupaPunct:
                            itemNou = Item(idx, 0)
                            if itemNou not in itemsCurente:
                                itemsDeAdaugat.add(itemNou)
                                seAdauga = True
            
            # Actualizam setul de items
            itemsCurente.update(itemsDeAdaugat)
        
        # Returnam un frozenset (imuabil) pentru a putea fi folosit ca cheie in dictionare
        return frozenset(itemsCurente)
    
    def goto(self, stare: FrozenSet[Item], simbolCitit: str) -> FrozenSet[Item]:
        """
        Calculeaza GOTO(stare, simbol) - starea rezultata dupa citirea unui simbol.
        
        Pentru fiecare item [A -> alfa • simbol beta], cream [A -> alfa simbol • beta]
        (mutam punctul peste simbol) si aplicam closure pe rezultat.
        """
        itemsDupaCitire = set()
        
        # Examinam fiecare item din starea curenta
        for item in stare:
            productie = self.productii[item.productieIdx]
            parteDreapta = productie.sirInlocuire
            
            # Daca punctul nu e la sfarsit
            if item.pozitieDot < len(parteDreapta):
                simbolDupaPunct = parteDreapta[item.pozitieDot]
                
                # Daca simbolul dupa punct este cel pe care il citim
                if simbolDupaPunct == simbolCitit:
                    # Cream item nou cu punctul mutat cu o pozitie
                    itemNou = Item(item.productieIdx, item.pozitieDot + 1)
                    itemsDupaCitire.add(itemNou)
        
        # Daca nu am gasit items, returnam multime vida
        if not itemsDupaCitire:
            return frozenset()
        
        # Aplicam closure pe items-urile gasite
        return self.closure(itemsDupaCitire)
    
    def construiesteStari(self):
        """
        Construieste toate starile automatului LR(0).
        
        Algoritmul:
        1. Incepe cu starea 0: closure([S' -> • S])
        2. Pentru fiecare stare si fiecare simbol posibil, calculeaza goto
        3. Daca goto da o stare noua, o adauga in lista
        4. Repeta pana nu mai sunt stari noi
        """
        # Starea initiala: closure cu item-ul [S' -> • S]
        itemInitial = Item(0, 0)  # Productia augmentata, punct la inceput
        stareInitiala = self.closure({itemInitial})
        
        # Lista de stari si coada de stari de vizitat
        self.stari = [stareInitiala]
        stariDeVizitat = [0]  # Indexul starii initiale
        
        # Cat timp mai avem stari nevizitate
        while stariDeVizitat:
            idxStareCurenta = stariDeVizitat.pop(0)
            stareCurenta = self.stari[idxStareCurenta]
            
            # Gasim toate simbolurile care apar dupa punct in aceasta stare
            simboluriPosibile = self.obtineSimboluri(stareCurenta)
            
            # Pentru fiecare simbol, calculam starea urmatoare
            for simbol in simboluriPosibile:
                stareNoua = self.goto(stareCurenta, simbol)
                
                # Daca starea noua e vida, nu facem nimic
                if not stareNoua:
                    continue
                
                # Cautam daca starea noua exista deja
                if stareNoua in self.stari:
                    # Stare existenta - folosim indexul ei
                    idxStareDestinatie = self.stari.index(stareNoua)
                else:
                    # Stare noua - o adaugam
                    idxStareDestinatie = len(self.stari)
                    self.stari.append(stareNoua)
                    stariDeVizitat.append(idxStareDestinatie)
                
                # Memoram tranzitia: (stare_sursa, simbol) -> stare_destinatie
                self.tranzitii[(idxStareCurenta, simbol)] = idxStareDestinatie
    
    def obtineSimboluri(self, stare: FrozenSet[Item]) -> list:
        """
        Functie helper: extrage toate simbolurile care apar dupa punct
        in items-urile din stare, ordonate (neterminale, apoi terminale).
        """
        neterminale = set()
        terminale = set()
        
        # Colectam simbolurile dupa punct
        for item in stare:
            productie = self.productii[item.productieIdx]
            parteDreapta = productie.sirInlocuire
            
            # Daca punctul nu e la sfarsit
            if item.pozitieDot < len(parteDreapta):
                simbolDupaPunct = parteDreapta[item.pozitieDot]
                
                # Clasificam simbolul ca neterminal sau terminal
                if simbolDupaPunct in self.gramatica.listaNeterminale or simbolDupaPunct == self.gramatica.simbolStart:
                    neterminale.add(simbolDupaPunct)
                else:
                    terminale.add(simbolDupaPunct)
        
        # Returnam lista ordonata: neterminale alfabetic, apoi terminale alfabetic
        return sorted(neterminale) + sorted(terminale)
    
    def construiesteTabele(self):
        """
        Construieste tabelele ACTION si GOTO pentru parser.
        
        Tabelul ACTION (pentru terminale):
        - d<n>: shift si mergi in starea n
        - r<n>: reduce folosind productia n
        - acc: accepta sirul
        
        Tabelul GOTO (pentru neterminale):
        - <n>: dupa reduce, mergi in starea n
        """
        # Pentru fiecare stare din automat
        for idxStare, stare in enumerate(self.stari):
            
            # Examinam fiecare item din stare
            for item in stare:
                productie = self.productii[item.productieIdx]
                sirInlocuire = productie.sirInlocuire
                
                # CAZ 1: Punctul e inainte de un terminal -> SHIFT
                # [A -> alfa • a beta] unde 'a' este terminal
                if item.pozitieDot < len(sirInlocuire):
                    simbolDupaPunct = sirInlocuire[item.pozitieDot]
                    
                    if simbolDupaPunct in self.gramatica.listaTerminale:
                        # Gasim starea destinatie din tranzitii
                        idxStareDestinatie = self.tranzitii.get((idxStare, simbolDupaPunct))
                        if idxStareDestinatie is not None:
                            # ACTION[stare, terminal] = "shift si mergi in stareDestinatie"
                            self.tabelAction[(idxStare, simbolDupaPunct)] = f'd{idxStareDestinatie}'
                
                # CAZ 2: Punctul e la sfarsit -> REDUCE sau ACCEPT
                # [A -> alfa •]
                elif item.pozitieDot == len(sirInlocuire):
                    neterminalStang = productie.simbolNeterminal
                    
                    # Caz special: productia augmentata [S' -> S •] -> ACCEPT
                    if item.productieIdx == 0:
                        self.tabelAction[(idxStare, '$')] = 'acc'
                    else:
                        # REDUCE: pentru fiecare terminal din FOLLOW(A)
                        # ACTION[stare, terminal] = "reduce folosind aceasta productie"
                        for terminal in self.follow.get(neterminalStang, set()):
                            self.tabelAction[(idxStare, terminal)] = f'r{item.productieIdx}'
            
            # Completam tabelul GOTO pentru neterminale
            for neterminal in self.gramatica.listaNeterminale:
                idxStareDestinatie = self.tranzitii.get((idxStare, neterminal))
                if idxStareDestinatie is not None:
                    # GOTO[stare, neterminal] = stareDestinatie
                    self.tabelGoto[(idxStare, neterminal)] = idxStareDestinatie
    
    def salveazaTabelInFisier(self, numeFisier: str):
        """
        Salveaza tabelul de parsing in fisier.
        
        Format:
        - Prima linie: header cu toate simbolurile (terminale, $, neterminale)
        - Urmatoarele linii: cate o linie pentru fiecare stare cu actiunile si goto-urile
        """
        # Construim lista de simboluri pentru header
        listaSimboluri = self.gramatica.listaTerminale + ['$'] + self.gramatica.listaNeterminale
        
        with open(numeFisier, 'w') as fisier:
            # Scriem headerul (simbolurile aliniate pe 5 caractere)
            partiHeader = [f"{simbol:5}" for simbol in listaSimboluri]
            fisier.write(''.join(partiHeader).rstrip() + '\n')
            
            # Scriem cate o linie pentru fiecare stare
            for idxStare in range(len(self.stari)):
                linie = []
                
                # Partea ACTION: actiuni pentru terminale + $
                for terminal in self.gramatica.listaTerminale + ['$']:
                    actiune = self.tabelAction.get((idxStare, terminal), '0')
                    linie.append(f"{actiune:5}")
                
                # Partea GOTO: tranzitii pentru neterminale
                for neterminal in self.gramatica.listaNeterminale:
                    stareGoto = self.tabelGoto.get((idxStare, neterminal), None)
                    valoare = str(stareGoto) if stareGoto is not None else '0'
                    linie.append(f"{valoare:5}")
                
                # Scriem linia in fisier
                fisier.write(''.join(linie).rstrip() + '\n')
    

class Productie:
    def __init__ (self, simbolNeterminal, sirInlocuire):
        self.simbolNeterminal = simbolNeterminal
        self.sirInlocuire = sirInlocuire

    def afiseazaProductie(self):
        print(self.simbolNeterminal + " -> " + self.sirInlocuire)


class TabelGramatica:
    """Tabel de gramatică încărcat din fișier"""
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
            numarLinieTabel = 0
            for numarLinie in range(1, len(linii)):
                valori = linii[numarLinie].strip().split()
                if valori and len(valori) == len(self.selectoriColoana):  # Verifică că linia e validă
                    # Creează dicționar pentru această linie
                    self.tabel[numarLinieTabel] = {}
                    for i, selector in enumerate(self.selectoriColoana):
                        self.tabel[numarLinieTabel][selector] = valori[i]
                    numarLinieTabel += 1
    
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
