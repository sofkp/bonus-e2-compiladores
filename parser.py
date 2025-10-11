class lr1:
    def __init__(self,grammar):
        self.grammar = grammar #gramatica scaneada 
        self.first = {} #diccionario para los FIRST
        self.states = [] #estados del LR(1)
        self.action_table = {} # [state][terminal-no terminal] = acción/regla
        self.got_to = {} #[state][no terminal] = estado destino

class item:
    def __init__(self, left, right, dot, lookahead):
        self.left = left
        self.right = tuple(right)
        self.dot = dot
        self.la = lookahead #token terminal A -> .a, $
    
    def __eq__(self, other):
        return (self.left, self.right, self.dot, self.la) == (other.left, other.right, other.dot, other.la)
    
    def __hash__(self):
        return hash((self.left, self.right, self.dot, self.la))
    
    def __repr__(self):
        right = list(self.right)
        right.insert(self.dot,".")
        right_s = " ".join(right) if right else "."
        return f"[{self.left} -> {right_s}, {self.la}]" 


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
def first_compute(regla, nterminal, terminal):
    first = {nt: set() for nt in nterminal}   #inicializar sets vacios para los no terminarles
    for t in terminal: first.setdefault(t,set()).add(t) #inicializar sets vacios para los terminales
    c = True #flag para repetir hasta que no haya cambios 
    while c:
        c = False
        for left, right in regla:
            if len(right) == 0: # regla 1: si la produccion tiene epsilon, se agrega a los first
                if "''" not in first[right]:
                    first[right].add("''")
                    c = True
                continue
            allEpsilon = True #se supone que todas las producciones tienen epsiol
            for s in right:
                if s in nterminal:  #regla 2: symbol es no terminal, se agrega el first de este
                    before = len(first[left])
                    agregar = [] #los terminales de la variable 
                    for i in first[s]:
                        if i != "''" : agregar.append(i) #agregar todos menos epsilon
                    first[left].update(agregar) #agregar los terminales
                    if len(first[left]) != before:
                        c = True
                    
                    if "''" in first[s]: #si first de la variable contiene epsilon, se evalua el siguiente simbolo
                        continue 
                    else:
                        allEpsilon = False
                        break
                    
                else:
                    # regla 1: agregar todos los terminarles
                    if s not in first[left]:
                        first[left].add(s)
                        c = True
                    allEpsilon = False
                    break
            if allEpsilon: #si todos los simbolos producen epsilon, se agrega epsilon al first de la variable
                if "''" not in first[left]:
                    first[left.add("''")]
                    c = True

    return first                

def first_prod(prod, first, nterminal): #para calulcar los first en produccion expandida
    res = set()
    if not prod:
        res.add("''")
        return res
    
    for s in prod:
        if s in nterminal:
            agregar = [] #los terminales de la variable 
            for i in first[s]:
                if i != "''" : agregar.append(i) #agregar todos menos epsilon
            res.update(agregar)
        else:
            res.add(s)
            return res
    res.add("''")
    return res
