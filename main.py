from gramatica import Gramatica, Productie
from gramatica import lungimeMaximaSir

gramaticaText = open("gramatica.txt", "r")
linii = gramaticaText.readlines()

listaNeterminale = linii[0].strip().split(" ")
listaTerminale = linii[1].strip().split(" ")
simbolStart = linii[2].strip()

gramatica = Gramatica(listaNeterminale, listaTerminale, simbolStart, [])

for i in range(3, len(linii)):
    linie = linii[i].split("->")
    productie = Productie(linie[0].strip(), linie[1].strip())
    gramatica.adaugaProductie(productie)

gramatica.afiseazaGramatica()

gramatica.genereazaLanturi(lungimeMaximaSir)

gramaticaText.close()

