from collections import defaultdict
import pprint

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


def grammar(filename):
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
    for t in terminal: #inicializar sets vacios para los terminales
        first.setdefault(t,set()).add(t) 
    c = True #flag para repetir hasta que no haya cambios 
    while c:
        c = False
        for left, right in regla:
            if len(right) == 0: # regla 1: si la produccion tiene epsilon, se agrega a los first
                if "''" not in first[left]:
                    first[left].add("''")
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
                    if len(first[left]) > before:
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
                    first[left].add("''")
                    c = True

    return first                

def first_prod(prod, first, nterminal): #para calulcar los first en produccion expandida
    res = set()
    if not prod:
        res.add("''")
        return res
    
    for s in prod:
        if s in nterminal:
            res.update(x for x in first[s] if x != "''")
            if "''" in first[s]:
                continue
            else:
                return res
        else:
            res.add(s)
            return res
    res.add("''")
    return res



def closure(items, regla, nterminal, first): #anade producciones según reglas LR1
    c = set(items)
    f = True # otro flag por si se agrego algo o no
    while f:
        f = False
        ilist = list(c) #lista de items
        for it in ilist: #por cada item en el closure
            if it.dot < len(it.right): #A -> x · X b, a
                x = it.right[it.dot] 
                if x in nterminal: #si . antes de un no terminal, para cada prod de b se repiten con el first como look ahead
                    b = list(it.right[it.dot+1:])
                    bb = b + [it.la]
                    lookaheads = first_prod(bb, first, nterminal)

                    for(left, right) in regla: #por cada produccion de X, copiar con nuevo looahead 
                        if left == x:
                            for a in lookaheads:
                                new_item = item(x, right, 0, a)
                                if new_item not in c:
                                    c.add(new_item)
                                    f = True
    return c                        

def goto(items, x, regla, nterminal,first): #movimiento de estados de A -> α · X β, a => A -> α X · β, a
    moved = set()
    for it in items:
        if it.dot < len(it.right) and it.right[it.dot] == x:
            moved.add(item(it.left,it.right,it.dot+1,it.la))
    return closure(moved,regla,nterminal,first)

def generate_dfa_diagram_data(C, augmented_rules, nonterminals, terminals):
    """Genera datos para el diagrama DFA LR(1)"""
    diagram_data = {
        "states": {},
        "transitions": []
    }
    
    # Procesar cada estado
    for i, state_items in enumerate(C):
        state_id = str(i)
        diagram_data["states"][state_id] = {
            "id": state_id,
            "items": []
        }
        
        # Convertir items a formato legible - USAR ATRIBUTOS DEL OBJETO item
        for it in state_items:
            left = it.left
            right = list(it.right)
            dot_pos = it.dot
            lookahead = it.la
            
            # Crear representación del item
            item_str = f"{left} → "
            for j, symbol in enumerate(right):
                if j == dot_pos:
                    item_str += "• "
                item_str += f"{symbol} "
            if dot_pos == len(right):
                item_str += "•"
            
            item_str += f", {lookahead}"
            diagram_data["states"][state_id]["items"].append(item_str)
    
    # Procesar transiciones (versión mejorada)
    for i, state_items in enumerate(C):
        state_id = str(i)
        
        # Para cada item en el estado
        for it in state_items:
            left = it.left
            right = list(it.right)
            dot_pos = it.dot
            lookahead = it.la
            
            if dot_pos < len(right):
                next_symbol = right[dot_pos]
                
                # Buscar el estado que contiene el item con el punto avanzado
                for j, target_state_items in enumerate(C):
                    # Verificar si este estado contiene el item con punto avanzado
                    target_item_found = False
                    for target_item in target_state_items:
                        target_left = target_item.left
                        target_right = list(target_item.right)
                        target_dot = target_item.dot
                        target_lookahead = target_item.la
                        
                        if (target_left == left and 
                            target_right == right and 
                            target_dot == dot_pos + 1 and
                            target_lookahead == lookahead):
                            
                            # Verificar si ya existe esta transición
                            transition_exists = any(
                                t["from"] == state_id and 
                                t["to"] == str(j) and 
                                t["label"] == next_symbol 
                                for t in diagram_data["transitions"]
                            )
                            
                            if not transition_exists:
                                diagram_data["transitions"].append({
                                    "from": state_id,
                                    "to": str(j),
                                    "label": next_symbol
                                })
                            target_item_found = True
                            break
                    
                    if target_item_found:
                        break
    
    return diagram_data

dfa_diagram_data = None

def dfa(regla, nterminal, terminal, first, symb): #colección canónica de estados
    sprima = symb + "'" #S' -> simbolo de entrada
    regla_au = [(sprima, [symb])] + regla #reglas aumentadas 
    s_i = item(sprima, [symb], 0, "$") #start item
    c = [] #closure
    c0 = closure({s_i}, regla_au, nterminal + [sprima], first)
    c.append(c0)
    changed = True
    while changed:
        changed = False
        for i in list(c):
            for x in nterminal + terminal:
                j = goto(i,x,regla_au,nterminal + [sprima], first)
                if not j:
                    continue
                if all(frozenset(j) != frozenset(existing) for existing in c):
                    c.append(j)
                    changed = True

    global dfa_diagram_data
    dfa_diagram_data = generate_dfa_diagram_data(c, regla_au, nterminal, terminal)
    
    return c, regla_au, sprima 


def action_table_prod(c, regla_au, nterminal, terminal, first, sprima):
    action = defaultdict(dict) #action[estado][[terminal-no terminal] = reducción o desplazamiento
    goto_table = defaultdict(dict) #goto[estado][noterminal] = estado
    state_of = {frozenset(st):idx for idx, st in enumerate(c)}
    for idx, i in enumerate(c):
        for a in terminal: #desplazamientos a estados
            j = goto(i, a, regla_au, nterminal + [sprima], first)
            if j:
                j = state_of.get(frozenset(j))
                if j is not None:
                    action[idx][a] = ("d", j) #desplaza del estado idx a j en a
    
        for b in nterminal: #gotos de no terminales
            j = goto(i, b, regla_au, nterminal + [sprima], first)
            if j:
                j = state_of.get(frozenset(j))
                if j is not None:
                    goto_table[idx][b] = j

        for it in i:
            if it.dot == len(it.right):
                if it.left == sprima and it.la == "$":
                    action[idx]["$"] = ("acc", ) #cuando llega a S'-> start, acepta

                else:
                    action[idx].setdefault(it.la, ("r",(it.left,it.right))) #reduccion de prod

    conflicts = [] #conflictos en estados de la tabla
    for st, row in action.items():
        for t, act in row.items():
            temp = [] #para ver si hay conflictos en cada uno
            i = c[st]
            for it in i:
                if it.dot <len(it.right) and it.right[it.dot] == t:
                    temp.append(("d", ))
                if it.dot == len(it.right) and it.la == t:
                    temp.append(("r", (it.left, it.right)))
                if it.left == sprima and it.dot == len(it.right) and t == "$":
                    temp.append(("acc",))
            if len(temp) > 1:
                conflicts.append((st,t,temp))
        
    return action, goto_table, conflicts



def parser(token, action, goto_table):
    state_stack = [0] #estado
    ip = 0
    trace = [] #traza
    symb_stack = []
    while True:
        state = state_stack[-1]
        look = token[ip] if ip < len(token) else "$"
        a = action.get(state, {}).get(look)
        if symb_stack:
            pairs = [f" {state_stack[i]} {sym}" for i, sym in enumerate(symb_stack)]
            pila_str = "".join(pairs)
        else:
            pila_str = " 0 "  

        entrada_str = " ".join(token[ip:])
        act_str = format_action(a)

        trace.append((pila_str, entrada_str, act_str))
        if a is None:
            return False, trace
        if a[0] == "d":
            symb_stack.append(look)
            state_stack.append(a[1])
            ip += 1
            continue
        elif a[0] == "r":
            left, right = a[1]
            pop_n = len(right)

            for _ in range(pop_n): 
                if symb_stack:
                    symb_stack.pop()
                if len(state_stack) > 0:
                    state_stack.pop()
            top = state_stack[-1]
            g = goto_table.get(top, {}).get(left)
            if g is None:
                return False, trace
            state_stack.append(g)
            symb_stack.append(left)
        elif a[0] == "acc":
            return True, trace
        

def print_states(c):
    for i, st in enumerate(c):
        print(f"estado {i}:")
        for it in sorted(st, key=lambda x:(x.left,x.right,x.dot,x.la)):
            print(" ", it)
        print()

def print_table(action, goto_table, terminals, nonterminals):
    print("\n=== ACTION ===")
    header = ["ST"] + terminals
    print(" | ".join(f"{h:10}" for h in header))
    print("-" * (13 * len(header)))
    states = sorted(set(list(action.keys()) + list(goto_table.keys())))
    for st in states:
        row = []
        for t in terminals:
            cell = action.get(st, {}).get(t, "")
            if cell == "":
                cell_str = ""
            elif cell[0] == "d":
                cell_str = f"s{cell[1]}"
            elif cell[0] == "r":
                A, rhs = cell[1]
                rhs_str = " ".join(rhs) if rhs else "ε"
                cell_str = f"r({A}->{rhs_str})"
            elif cell[0] == "acc":
                cell_str = "acc"
            else:
                cell_str = str(cell)
            row.append(f"{cell_str:10}")
        print(f"{st:2} | " + " | ".join(row))

    print("\n=== GOTO ===")
    header = ["ST"] + nonterminals
    print(" | ".join(f"{h:10}" for h in header))
    print("-" * (13 * len(header)))
    states_g = sorted(goto_table.keys())
    for st in states_g:
        row = []
        for A in nonterminals:
            cell = goto_table[st].get(A, "")
            cell_str = str(cell) if cell != "" else ""
            row.append(f"{cell_str:10}")
        print(f"{st:2} | " + " | ".join(row))

def format_action(act):
    if act is None:
        return ""
    if act[0] == "d":
        return f"d {act[1]}"
    elif act[0] == "r":
        A, rhs = act[1]
        rhs_str = " ".join(rhs) if rhs else "ε"
        return f"r ( {A} -> {rhs_str} )"
    elif act[0] == "acc":
        return "acc"
    return str(act)


import json

def run_parser_from_text(grammar_text, input_text):
    # Guardar temporalmente la gramática como archivo
    with open("input2.txt", "w", encoding="utf-8") as f:
        f.write(grammar_text.strip() + "\n")

    rules, nonterminals, terminals = grammar("input2.txt")
    first = first_compute(rules, nonterminals, terminals)
    C, augmented_rules, Sprime = dfa(rules, nonterminals, terminals, first, nonterminals[0])
    action, goto_table, conflicts = action_table_prod(C, augmented_rules, nonterminals, terminals, first, Sprime)

    # preparar tokens
    tokens = input_text.strip().split()
    if not tokens or tokens[-1] != "$":
        tokens.append("$")

    accepted, trace = parser(tokens, action, goto_table)

    # estructurar salida limpia para el frontend
    trace_data = []
    for pila, entrada, accion in trace:
        trace_data.append({
            "stack": pila,
            "input": entrada,
            "action": accion
        })

    result = {
        "result": "accept" if accepted else "reject",
        "trace": trace_data,
        "conflicts": conflicts
    }

    print(json.dumps(result))  # para enviar de vuelta a Node

def get_dfa_data():
    """Obtiene los datos del diagrama DFA"""
    global dfa_diagram_data
    return dfa_diagram_data if 'dfa_diagram_data' in globals() else None

def main():
    grammar_file = "input2.txt" 
    rules, nonterminals, terminals = grammar(grammar_file)
    print("reglas leídas:")
    for r in rules:
        print("  ", r)
    print("\nno terminales:", nonterminals)
    print("terminales:", terminals)

    # tabla first
    first = first_compute(rules, nonterminals, terminals)
    print("\nFIRST:")
    print("-" * 30)
    for sym, fset in first.items():
        print(f"{sym:5}: {', '.join(sorted(fset))}")
    print("-" * 30)


    # DFA
    C, augmented_rules, Sprime = dfa(rules, nonterminals, terminals, first, nonterminals[0])
    print("\nDFA: ")
    print_states(C)

    # tablasss
    action, goto_table, conflicts = action_table_prod(C, augmented_rules, nonterminals, terminals, first, Sprime)
    print("\nconflictos encontrados (lista):", conflicts)

    print_table(action, goto_table, terminals, nonterminals)

    while True:
        choice = input("\n¿parsear cadena? (s/n): ").strip().lower()
        if choice != "s": break

        inp = input("cadena a parsear: ").strip().split()
        tokens = inp + ["$"] if inp[-1] != "$" else inp

        accepted, trace = parser(tokens, action, goto_table)
        print("\ncadena:", " ".join(tokens))
        print("¿aceptada?:", "chi" if accepted else "ño")

        print("\n--- Trace ---")
        print(f"{'pila (símbolos/estados)':40} {'entrada':35} {'acción'}")
        print("-" * 100)
        for pila_str, entrada_str, act_str in trace:
            print(f"{pila_str:40} {entrada_str:35} {act_str}")




if __name__ == "__main__":
    main()