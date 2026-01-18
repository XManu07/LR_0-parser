from typing import List, Set

class GeneratorCodIntermediar:
    """
    Gestionează generarea de cod intermediar și variabile temporare.
    """
    def __init__(self):
        self.contor_temp = 0
        self.cod_intermediar = []
    
    def newtemp(self):
        """
        Generează și returnează o nouă variabilă temporară.
        Returns: string de forma 't1', 't2', etc.
        """
        self.contor_temp += 1
        return f't{self.contor_temp}'
    
    def emit(self, instructiune):
        """
        Emite (adaugă) o instrucțiune de cod intermediar.
        Args:
            instructiune: string cu instrucțiunea (ex: "t1 := a + b")
        """
        self.cod_intermediar.append(instructiune)
    
    def afiseaza_cod_intermediar(self):
        """
        Afișează tot codul intermediar generat.
        """
        print("Cod Intermediar Generat:")
        for i, instructiune in enumerate(self.cod_intermediar, 1):
            print(f"{i}. {instructiune}")
    
    def reseteaza(self):
        """
        Resetează generatorul pentru o nouă parsare.
        """
        self.contor_temp = 0
        self.cod_intermediar = []


class Item:
    """
    Reprezintă un item LR(0) - o regulă gramaticală cu un punct care indică poziția în parsare.
    De exemplu, E → E • + B indică faptul că am recunoscut E și așteptăm + B în continuare.
    """
    def __init__(self, productie, pozitiePunct):
        """
        Inițializează un item LR(0).
        
        Args:
            productie: Un obiect Productie care conține regula gramaticală
            pozitiePunct: Poziția întreagă a punctului (0 până la len(sirInlocuire))
        """
        self.simbolNeterminal = productie.simbolNeterminal
        self.sirInlocuire = productie.sirInlocuire
        self.pozitiePunct = pozitiePunct
        
        # Generează reprezentarea string cu punct
        self.sirCuPunct = self.sirInlocuire[:pozitiePunct] + '.' + self.sirInlocuire[pozitiePunct:]
    
    def esteFinal(self):
        """Verifică dacă punctul este la sfârșit (item de reducere)."""
        return self.pozitiePunct >= len(self.sirInlocuire)
    
    def esteInitial(self):
        """Verifică dacă punctul este la început."""
        return self.pozitiePunct == 0
    
    def simbolDupaPunct(self):
        """
        Returnează simbolul imediat după punct, sau None dacă este la sfârșit.
        Indică ce simbolul pe care parserul se așteaptă să îl vadă în continuare.
        """
        if self.esteFinal():
            return None
        return self.sirInlocuire[self.pozitiePunct]
    
    def avansare(self, productie):
        """
        Creează un nou item cu punctul avansat cu o poziție.
        Folosit când se deplasează un simbol pe stivă.
        """
        if self.esteFinal():
            return None
        return Item(productie, self.pozitiePunct + 1)
    
    def __str__(self):
        """Reprezentarea string a item-ului."""
        return f"{self.simbolNeterminal} -> {self.sirCuPunct}"
    
    def __repr__(self):
        return self.__str__()
    
    def __eq__(self, other):
        """Verifică egalitatea cu alt item."""
        if not isinstance(other, Item):
            return False
        return (self.simbolNeterminal == other.simbolNeterminal and 
                self.sirInlocuire == other.sirInlocuire and 
                self.pozitiePunct == other.pozitiePunct)
    
    def __hash__(self):
        """Face item-urile hashable pentru utilizare în seturi și dicționare."""
        return hash((self.simbolNeterminal, self.sirInlocuire, self.pozitiePunct))

class SetItemi:
    """
    Reprezintă un set de itemi LR(0) - o stare în automatonul LR.
    Fiecare set conține mai mulți itemi (kernel + closure).
    """
    def __init__(self, itemi: Set[Item] = None, id_set: int = None):
        """
        Inițializează un set de itemi.
        
        Args:
            itemi: Setul de itemi (kernel + closure)
            id_set: ID-ul unic al acestui set (stare)
        """
        self.itemi = itemi if itemi is not None else set()
        self.id = id_set
    
    def adaugaItem(self, item: Item):
        """Adaugă un item în set."""
        self.itemi.add(item)
    
    def contineItem(self, item: Item) -> bool:
        """Verifică dacă setul conține deja itemul."""
        return item in self.itemi
    
    def __eq__(self, other):
        """Două seturi sunt egale dacă conțin aceiași itemi."""
        if not isinstance(other, SetItemi):
            return False
        return self.itemi == other.itemi
    
    def __hash__(self):
        """Face setul hashable pentru utilizare în dicționare și seturi."""
        return hash(frozenset(self.itemi))
    
    def __str__(self):
        """Reprezentarea string a setului de itemi."""
        if self.id is not None:
            rezultat = f"Set {self.id}:\n"
        else:
            rezultat = "Set de itemi:\n"
        for item in sorted(self.itemi, key=lambda x: (x.simbolNeterminal, x.sirInlocuire, x.pozitiePunct)):
            rezultat += f"  {item}\n"
        return rezultat
    
    def __repr__(self):
        return f"SetItemi(id={self.id}, {len(self.itemi)} itemi)"

class Gramatica:
    def __init__(self, numeFisier: str):
        self.listaNeterminale = []
        self.listaTerminale = []
        self.simbolStart = ""
        self.listaProductii = []
        self.tabel = None
        self.seturiItemi = []  # Lista de SetItemi (stările automatonului LR)
        self.tranzitii = {}  # Dicționar {(id_set, simbol): id_set_destinație}
        self.tabelAction = {}  # Dicționar {(stare, terminal): acțiune}
        self.tabelGoto = {}  # Dicționar {(stare, neterminal): stare_nouă}
        self.first = {}  # Dicționar {neterminal: set(terminali)}
        self.follow = {}  # Dicționar {neterminal: set(terminali)}
        self.generator = GeneratorCodIntermediar()  # Generator pentru cod intermediar
        self.citesteGramaticaDinFisier(numeFisier)
        self.genereazaTabel("tabel_generat_" + numeFisier)
        
        try:
            self.tabel = TabelGramatica("tabel_generat_" + numeFisier)
        except Exception as e:
            print(f"Eroare la citirea tabelului: {e}")
        
    def genereazaTabel(self, numeFisier: str):
        """
        Generează tabelul de parsare LR.
        1. Augmentează gramatica (S' → S)
        2. Construiește itemii LR(0)
        3. Calculează closure și goto pentru stări
        4. Generează tabelul ACTION și GOTO
        """
        # Pasul 1: Augmentează gramatica
        self.augmenteazaGramatica()
        # Pasul 2: Calculează FIRST și FOLLOW pentru SLR
        self.calculeazaFirst()
        self.calculeazaFollow()
        # Pasul 3: Generează seturile de itemi
        self.genereazaSetItemi()
        self.construiesteTabel()
        self.scrieTabelInFisier(numeFisier)
        
    def construiesteTabel(self):
        """
        Construiește tabelele ACTION și GOTO pentru parserul LR(0).
        """
        self.construiesteTabelAction()
        self.construiesteTabelGoto()
    
    def construiesteTabelAction(self):
        """
        Construiește tabelul ACTION pentru parserul LR(0).
        Tabelul conține acțiuni shift, reduce și accept pentru fiecare combinație (stare, terminal).
        """
        # Iterează prin toate seturile de itemi (stările)
        for setItemi in self.seturiItemi:
            indexSet = setItemi.id
            
            # Prima trecere: adaugă acțiunile shift daca itemul nu este final iar simbolul dupa punct este terminal 
            # si exista tranzitie pentru el din starea curenta
            for item in setItemi.itemi:
                if not item.esteFinal():
                    # Item ne-final: A → α • X β
                    # Verifică dacă există tranziție cu un terminal
                    simbolDupaPunct = item.simbolDupaPunct()
                    if simbolDupaPunct and simbolDupaPunct in self.listaTerminale:
                        # Există tranziție cu terminal -> shift
                        if (indexSet, simbolDupaPunct) in self.tranzitii:
                            indexSetDestinatie = self.tranzitii[(indexSet, simbolDupaPunct)]
                            self.tabelAction[(indexSet, simbolDupaPunct)] = f'd{indexSetDestinatie}'
            
            # A doua trecere: adaugă acțiunile reduce (doar unde nu există shift)
            for item in setItemi.itemi:
                if item.esteFinal():
                    # Item final: A → w •
                    
                    # Găsește numărul regulii (index în listaProductii)
                    numarRegula = None
                    for idx, productie in enumerate(self.listaProductii):
                        if (productie.simbolNeterminal == item.simbolNeterminal and 
                            productie.sirInlocuire == item.sirInlocuire):
                            numarRegula = idx
                            break
                    
                    if numarRegula is not None:
                        if numarRegula == 0:
                            # Regula augmentată S' → S$ •
                            # Adaugă accept pentru simbolul '$'
                            self.tabelAction[(indexSet, '$')] = 'acc'
                        else:
                            # Reducere cu regula m (m > 0) - SLR
                            # Adaugă reduce doar pentru terminalii din FOLLOW(A)
                            neterminal = item.simbolNeterminal
                            followSet = self.follow.get(neterminal, set())
                            for terminal in followSet:
                                if (indexSet, terminal) not in self.tabelAction:
                                    self.tabelAction[(indexSet, terminal)] = f'r{numarRegula}'
    
    def construiesteTabelGoto(self):
        """
        Construiește tabelul GOTO pentru parserul LR(0).
        Tabelul conține tranziții pentru neterminale (indexul setului de itemi din care se ajunge la noul set)
        """
        # Copiază tranzițiile cu neterminale în tabelul GOTO
        for (stare, simbol), stareDestinație in self.tranzitii.items():
            if simbol in self.listaNeterminale:
                self.tabelGoto[(stare, simbol)] = stareDestinație
    
    def scrieTabelInFisier(self, numeFisier: str):
        """
        Scrie tabelele ACTION și GOTO într-un fișier în formatul standard.
        Format: prima linie = coloane (terminale + neterminale), 
                linii următoare = stări cu acțiuni/tranziții.
        Valorile goale sunt marcate cu '0'.
        
        Args:
            numeFisier: Numele fișierului de ieșire
        """
        # Construiește lista de coloane: terminale + neterminale (fără S' augmentat)
        coloane = []
        
        # Adaugă terminale (fără $ la început, îl adăugăm la sfârșit pentru convenție)
        for terminal in self.listaTerminale:
            if terminal != '$':
                coloane.append(terminal)
        coloane.append('$')  # $ la final
        
        # Adaugă neterminale (exclude simbolul de start augmentat S')
        for neterminal in self.listaNeterminale:
            if neterminal != self.simbolStart:  # Exclude S' (simbolul augmentat)
                coloane.append(neterminal)
        
        # Deschide fișierul pentru scriere
        with open(numeFisier, 'w') as f:
            # Scrie header-ul (coloanele) - fiecare coloană are lățime fixă de 5 caractere
            header_parts = [col.ljust(5) for col in coloane]
            f.write(''.join(header_parts).rstrip() + '\n')
            
            # Scrie fiecare stare
            for stare in range(len(self.seturiItemi)):
                linie = []
                
                # Pentru fiecare coloană, găsește valoarea din tabel
                for coloana in coloane:
                    valoare = '0'  # Valoarea implicită pentru celule goale
                    
                    if coloana in self.listaTerminale:
                        # Caută în tabelul ACTION
                        if (stare, coloana) in self.tabelAction:
                            actiune = self.tabelAction[(stare, coloana)]
                            # Formatează acțiunea: 'd5', 'r3', 'acc'
                            valoare = actiune
                    else:
                        # Caută în tabelul GOTO
                        if (stare, coloana) in self.tabelGoto:
                            valoare = str(self.tabelGoto[(stare, coloana)])
                    
                    linie.append(valoare)
                
                # Scrie linia pentru această stare - fiecare valoare are lățime fixă de 5 caractere
                linie_parts = [val.ljust(5) for val in linie]
                f.write(''.join(linie_parts).rstrip() + '\n')
        
    def genereazaSetItemi(self):
        """
        Generează toate seturile de itemi LR(0) accesibile și tranzițiile între ele.
        Construiește automatonul finit pentru parsarea LR.
        """
        # Creează setul inițial cu primul item al regulii augmentate
        # S' → • S$ (unde S este simbolul de start original)
        itemInițial = Item(self.listaProductii[0], 0)
        setInițial = SetItemi({itemInițial}, 0)
        setInițial = self.closure(setInițial)
        
        # Liste de seturi procesate și neprocessate
        self.seturiItemi = [setInițial]
        seturiNeprocessate = [setInițial]
        
        # Dicționar pentru a găsi rapid ID-ul unui set de itemi
        mapareSeturi = {setInițial: 0}
        
        idCurent = 1
        
        # Procesează fiecare set până când nu mai sunt seturi noi
        while seturiNeprocessate:
            setCurent = seturiNeprocessate.pop(0)
            
            # Găsește toate simbolurile care apar după punct în itemii acestui set
            simboluriDupaPunct = set()
            for item in setCurent.itemi:
                simbol = item.simbolDupaPunct()
                if simbol is not None:
                    simboluriDupaPunct.add(simbol)
            
            # Pentru fiecare simbol, calculează goto și adaugă tranziția
            for simbol in simboluriDupaPunct:
                setNou = self.goto(setCurent, simbol)
                
                # Verifică dacă acest set există deja
                if setNou not in mapareSeturi:
                    # Set nou - adaugă-l
                    setNou.id = idCurent
                    mapareSeturi[setNou] = idCurent
                    self.seturiItemi.append(setNou)
                    seturiNeprocessate.append(setNou)
                    idCurent += 1
                
                # Adaugă tranziția
                idDestinație = mapareSeturi[setNou]
                self.tranzitii[(setCurent.id, simbol)] = idDestinație
    
    def calculeazaFirst(self):
        """
        First(A) este multimea de terminali cu care poate incepe un sir derivat din neterminalul A
        """
        # Inițializează FIRST cu mulțimi goale
        for neterminal in self.listaNeterminale:
            self.first[neterminal] = set()
        
        # Repetă până când nu mai sunt schimbări
        schimbat = True
        while schimbat:
            schimbat = False
            
            for productie in self.listaProductii:
                neterminal = productie.simbolNeterminal
                sirDreapta = productie.sirInlocuire
                
                primulSimbol = sirDreapta[0]
                
                if primulSimbol in self.listaTerminale:
                    # Primul simbol este terminal
                    if primulSimbol not in self.first[neterminal]:
                        self.first[neterminal].add(primulSimbol)
                        schimbat = True
                elif primulSimbol in self.listaNeterminale:
                    # Primul simbol este neterminal
                    # Adaugă FIRST(primul simbol) la FIRST(neterminal)
                    for terminal in self.first[primulSimbol]:
                        if terminal not in self.first[neterminal]:
                            self.first[neterminal].add(terminal)
                            schimbat = True
    
    def calculeazaFollow(self):
        """
        Follow(A) este multimea de terminali care pot aprea imediat dupa neterminalul A intr o derivare
        """
        # Inițializează FOLLOW cu mulțimi goale
        for neterminal in self.listaNeterminale:
            self.follow[neterminal] = set()
        
        # Adaugă $ în FOLLOW(S) pentru simbolul de start
        if self.simbolStart in self.listaNeterminale:
            self.follow[self.simbolStart].add('$')
        
        # Repetă până când nu mai sunt schimbări
        schimbat = True
        while schimbat:
            schimbat = False
            
            for productie in self.listaProductii:
                neterminalStanga = productie.simbolNeterminal
                sirDreapta = productie.sirInlocuire
                
                # Parcurge fiecare simbol din partea dreaptă
                for i in range(len(sirDreapta)):
                    simbol = sirDreapta[i]
                    
                    # Interesează doar neterminalele
                    if simbol not in self.listaNeterminale:
                        continue
                    
                    # Verifică ce urmează după acest neterminal
                    if i + 1 < len(sirDreapta):
                        # Mai sunt simboluri după
                        simbolUrmator = sirDreapta[i + 1]
                        
                        if simbolUrmator in self.listaTerminale:
                            # Următorul simbol este terminal
                            if simbolUrmator not in self.follow[simbol]:
                                self.follow[simbol].add(simbolUrmator)
                                schimbat = True
                        elif simbolUrmator in self.listaNeterminale:
                            # Următorul simbol este neterminal
                            # Adaugă FIRST(simbolUrmator) la FOLLOW(simbol)
                            for terminal in self.first[simbolUrmator]:
                                if terminal not in self.follow[simbol]:
                                    self.follow[simbol].add(terminal)
                                    schimbat = True
                            
                            # Dacă simbolul următor poate deriva epsilon, adaugă FOLLOW(neterminalStanga)
                            # Pentru simplitate, presupunem că nu avem producții epsilon
                    else:
                        # Neterminalul este ultimul simbol: A → αB
                        # Adaugă FOLLOW(A) la FOLLOW(B)
                        for terminal in self.follow[neterminalStanga]:
                            if terminal not in self.follow[simbol]:
                                self.follow[simbol].add(terminal)
                                schimbat = True
    
    def closure(self, setItemi: SetItemi) -> SetItemi:
        """
        Closure pleaca de la un set de itemi (kernel)
        Pentru fiecare item din set, daca simbolul dupa punct este un neterminal,
        se adauga in set toti itemii proveniti din productiile acelui neterminal, cu punctul la inceput.
        
        Args:
            setItemi: Setul de itemi inițial (kernel)
            
        Returns:
            Noul set de itemi cu closure complet
        """
        # Creează un nou set cu aceiași itemi
        rezultat = SetItemi(set(setItemi.itemi), setItemi.id)
        
        # Repetă până când nu mai sunt itemi noi de adăugat
        adaugatItemiNoi = True
        while adaugatItemiNoi:
            adaugatItemiNoi = False
            itemiCurenți = list(rezultat.itemi)

            # Pentru fiecare item în setul curent
            for item in itemiCurenți:
                simbolDupaPunct = item.simbolDupaPunct()
                
                # Dacă simbolul după punct este un neterminal
                if simbolDupaPunct and simbolDupaPunct in self.listaNeterminale:
                    # Găsește toate producțiile pentru acest neterminal
                    for productie in self.listaProductii:
                        if productie.simbolNeterminal == simbolDupaPunct:
                            # Creează itemul B → • γ
                            itemNou = Item(productie, 0)
                            
                            # Adaugă itemul dacă nu există deja
                            if not rezultat.contineItem(itemNou):
                                rezultat.adaugaItem(itemNou)
                                adaugatItemiNoi = True
        
        return rezultat
    
    def goto(self, setItemi: SetItemi, simbol: str) -> SetItemi:
        """
        Functia goto returneaza un nou set de itemi (stare) + closure pe acest nou set
        Functia goto trece prin itemi primiti ca parametru
        și avansează punctul pentru toți itemii care au simbolul dupa punct egal cu simbolul dat ca parametru.
        
        Args:
            setItemi: Setul de itemi curent
            simbol: Simbolul (terminal sau neterminal) citit
            
        Returns:
            Noul set de itemi după tranziție
        """
        # Kernel-ul noului set: itemi cu punct avansat după simbol
        itemiNoi = set()
        
        for item in setItemi.itemi:
            # Verifică dacă itemul are simbol după punct egal cu simbolul dat
            if item.simbolDupaPunct() == simbol:
                # Avansează punctul
                # Găsește producția corespunzătoare pentru a crea un nou item
                for productie in self.listaProductii:
                    if (productie.simbolNeterminal == item.simbolNeterminal and 
                        productie.sirInlocuire == item.sirInlocuire):
                        itemNou = Item(productie, item.pozitiePunct + 1)
                        itemiNoi.add(itemNou)
                        break
        
        # Creează setul nou și aplică closure
        setNou = SetItemi(itemiNoi)
        return self.closure(setNou)
    
    def augmenteazaGramatica(self):
        """
        Augmentează gramatica adăugând un nou simbol de start S' și producția S' → S$.
        Aceasta este necesară pentru parsarea LR pentru a identifica clar finalul parsării.
        """
        # Creează noul simbol de start (simbolul vechi + apostrof)
        simbolStartNou = self.simbolStart + "'"
        
        # Verifică dacă gramatica nu este deja augmentată
        if simbolStartNou in self.listaNeterminale:
            return  # Gramatica este deja augmentată
        
        # Adaugă simbolul de sfârșit $ la lista de terminale dacă nu există
        if "$" not in self.listaTerminale:
            self.listaTerminale.append("$")
        
        # Adaugă noul simbol de start la lista de neterminale
        self.listaNeterminale.insert(0, simbolStartNou)
        
        # Creează noua producție S' → S$ (simbolul vechi + $)
        productieNoua = Productie(simbolStartNou, self.simbolStart + "$")
        
        # Inserează noua producție la începutul listei
        self.listaProductii.insert(0, productieNoua)
        
        # Actualizează simbolul de start
        self.simbolStart = simbolStartNou
        
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
    
    def verificaSir(self, sir_intrare: str):
        """
        Parsează un șir de intrare și generează cod intermediar (Three-Address Code).
        Translator Push Down pentru expresii aritmetice.
        
        Args:
            sir_intrare: String cu expresia aritmetică (ex: "a+a*a")
        
        Returns:
            True dacă șirul este acceptat, False altfel
        """
        if not self.tabel:
            return False
        
        # Reset generator
        self.generator.reseteaza()
        
        # Inițializare - 3 stive paralele sincronizate
        stiva_simboluri = ['$']      # Stiva de simboluri (terminale și neterminale)
        stiva_stari = [0]            # Stiva de stări din automatonul LR
        stiva_atribute = []          # Stiva de place values (string-uri: 'a', 't1', 't2', etc.)
        sir_input = sir_intrare + '$'
        pozitie = 0
        pas = 0
        max_pasi = 1000
        
        while True:
            pas += 1
            if pas > max_pasi:
                return False
            
            # Starea curentă
            stare_curenta = stiva_stari[-1]
            
            # Simbolul curent din input
            simbol_curent = sir_input[pozitie] if pozitie < len(sir_input) else '$'
            
            # Obține acțiunea din tabel
            actiune = self.tabel.obtine(stare_curenta, simbol_curent)
            
            # Verifică tipul acțiunii
            if actiune == '0' or actiune == '':
                return False
            
            elif actiune == 'acc':
                return True
            
            elif actiune[0] == 'd':
                # Shift (deplasare) - adaugă în toate cele 3 stive
                try:
                    stare_noua = int(actiune[1:])
                    
                    # Pentru terminale, place value = simbolul însuși
                    place_val = simbol_curent
                    
                    # Sincronizare: adaugă în toate cele 3 stive
                    stiva_simboluri.append(simbol_curent)
                    stiva_stari.append(stare_noua)
                    stiva_atribute.append(place_val)
                    pozitie += 1
                    
                except ValueError:
                    return False
            
            elif actiune[0] == 'r':
                # Reduce (reducere) - scoate din toate cele 3 stive
                try:
                    numar_productie = int(actiune[1:])
                    
                    if numar_productie < 0 or numar_productie >= len(self.listaProductii):
                        return False
                    
                    productie = self.listaProductii[numar_productie]
                    lungime_productie = len(productie.sirInlocuire)
                    
                    # Scoate simbolurile, stările și place values corespunzătoare din toate stivele
                    place_values = []
                    if lungime_productie > 0:
                        for _ in range(lungime_productie):
                            # Sincronizare: scoate din toate cele 3 stive
                            if stiva_simboluri and len(stiva_simboluri) > 1:
                                stiva_simboluri.pop()
                            if stiva_stari and len(stiva_stari) > 1:
                                stiva_stari.pop()
                            if stiva_atribute:
                                place_values.append(stiva_atribute.pop())
                    
                    # Execută acțiunea semantică (returnează place value pentru neterminal)
                    place_nou = productie.executa_actiune_semantica(place_values, self.generator)
                    
                    # Starea după reducere
                    stare_dupa_reduce = stiva_stari[-1]
                    neterminal = productie.simbolNeterminal
                    
                    # Goto
                    stare_salt = self.tabel.obtine(stare_dupa_reduce, neterminal)
                    
                    if stare_salt == '0' or stare_salt == '':
                        return False
                    
                    # Sincronizare: adaugă neterminalul, starea nouă și place value în toate stivele
                    stiva_simboluri.append(neterminal)
                    stiva_stari.append(int(stare_salt))
                    stiva_atribute.append(place_nou)
                    
                except (ValueError, IndexError):
                    return False
            
            else:
                return False
        
class Productie:
    def __init__ (self, simbolNeterminal, sirInlocuire):
        self.simbolNeterminal = simbolNeterminal
        self.sirInlocuire = sirInlocuire

    def afiseazaProductie(self):
        print(self.simbolNeterminal + " -> " + self.sirInlocuire)
    
    def genereaza_actiune_intermediara(self, place_values, generator):
        """
        Execută acțiunea semantică asociată acestei producții.
        
        Args:
            place_values: Lista de place values (string-uri) în ordine inversă de pe stivă
            generator: GeneratorCodIntermediar pentru generare cod
        
        Returns:
            String reprezentând place value pentru neterminalul din stânga producției
        """
        # E → E + T
        if self.simbolNeterminal == 'E' and self.sirInlocuire == 'E+T':
            T_place = place_values[0]
            E1_place = place_values[2]
            E_place = generator.newtemp()
            generator.emit(f"{E_place} := {E1_place} + {T_place}")
            return E_place
        
        # E → T
        elif self.simbolNeterminal == 'E' and self.sirInlocuire == 'T':
            T_place = place_values[0]
            return T_place
        
        # T → T * F
        elif self.simbolNeterminal == 'T' and self.sirInlocuire == 'T*F':
            F_place = place_values[0]
            T1_place = place_values[2]
            T_place = generator.newtemp()
            generator.emit(f"{T_place} := {T1_place} * {F_place}")
            return T_place
        
        # T → F
        elif self.simbolNeterminal == 'T' and self.sirInlocuire == 'F':
            F_place = place_values[0]
            return F_place
        
        # F → (E)
        elif self.simbolNeterminal == 'F' and self.sirInlocuire == '(E)':
            E_place = place_values[1]
            return E_place
        
        # F → a
        elif self.simbolNeterminal == 'F' and self.sirInlocuire == 'a':
            a_value = place_values[0]
            return a_value
        
        # Producție fără acțiune semantică definită (ex: E' -> E$)
        else:
            return None
        
        
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
