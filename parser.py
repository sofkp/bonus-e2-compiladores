class lr1:
    def __init__(self,grammar):
        self.grammar = grammar #gramatica scaneada 
        self.first = {} #diccionario para los FIRST
        self.states = [] #estados del LR(1)
        self.action_table = {} # [state][terminal-no terminal] = acción/regla
        self.got_to = {} #[state][no terminal] = estado destino


def gramatica(filename):
    regla = [] #reglas
    nterminal = [] #no terminales

    with open(filename) as f:
        for l in f:
            #reconocer las lineas y separar por ->
            l = l.strip()
            if not l or l.startswith("#"):
                continue
            if "->" not in l:
                continue
            left, right = l.split("->",1)
            left = left.strip()
            nterminal.append(left)

            #separar reglas
            alt = [] #lista de alternativas de una misma variable
            for a in right.split("|"):
                alt.append(a.strip()) #strip elimina espacios al inicio y al final

            for a in alt:
                if a in("","''","ε") : symb = [] #si es simbolo es vacio, lista vacia
                else : 
                    symb = [] 
                    for s in a.split() : #agregar los symbols
                        if s : symb.append(s) #evitar espacios vacios 
                regla.append((left,symb))

    nterminal = list(dict.fromkeys(nterminal))

    terminal = set() #set de terminales
    for left,right in regla:
        for s in right:
            if s not in nterminal:
                terminal.add(s)

    terminal.add("$") #añadir el $ final a los terminales
    return regla, nterminal, sorted(list(terminal))

#calcular FIRST 
def first(regla, nterminal, terminal):
    first = set()   
    for nt in nterminal: first.add(nt)
    c = True #bool para indicar si cambio o no
    while c:
        c = False
        for left, right in regla:
            if len(right) == 0:
                if "''" not in first[right]:
                    first[right].add("''")
                    c = True
                continue
            epsilon = True
            

