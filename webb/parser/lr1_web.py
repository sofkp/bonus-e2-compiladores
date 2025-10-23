import sys
import json
import os
from lr1_parser import grammar, first_compute, dfa, action_table_prod, parser, get_dfa_data

def generate_tables(grammar_text):
    """Genera las tablas ACTION y GOTO a partir de la gramática"""
    # Guardar gramática temporalmente con codificación UTF-8
    try:
        with open("temp_grammar.txt", "w", encoding="utf-8") as f:
            f.write(grammar_text)
        
        rules, nonterminals, terminals = grammar("temp_grammar.txt")
        first = first_compute(rules, nonterminals, terminals)
        C, augmented_rules, Sprime = dfa(rules, nonterminals, terminals, first, nonterminals[0])
        action, goto_table, conflicts = action_table_prod(C, augmented_rules, nonterminals, terminals, first, Sprime)
        
        # Obtener datos del DFA
        dfa_data = get_dfa_data()
        
        # Convertir a formatos serializables
        action_serializable = {}
        for state, row in action.items():
            action_serializable[state] = {}
            for symbol, action_val in row.items():
                if action_val[0] == "d":
                    action_serializable[state][symbol] = ["d", action_val[1]]
                elif action_val[0] == "r":
                    left, right = action_val[1]
                    action_serializable[state][symbol] = ["r", [left, list(right)]]
                elif action_val[0] == "acc":
                    action_serializable[state][symbol] = ["acc"]
        
        goto_serializable = {}
        for state, row in goto_table.items():
            goto_serializable[state] = dict(row)
        
        result = {
            "action": action_serializable,
            "goto": goto_serializable,
            "terminals": terminals,
            "nonterminals": nonterminals
        }
        
        # Solo agregar DFA si está disponible
        if dfa_data:
            result["dfa"] = dfa_data
        
        return result
        
    except Exception as e:
        return {"error": str(e)}
    finally:
        # Limpiar archivo temporal
        if os.path.exists("temp_grammar.txt"):
            os.remove("temp_grammar.txt")

def parse_string(grammar_text, input_string):
    """Parsea una cadena usando las tablas LR(1)"""
    try:
        # Guardar gramática temporalmente con codificación UTF-8
        with open("temp_grammar.txt", "w", encoding="utf-8") as f:
            f.write(grammar_text)
        
        rules, nonterminals, terminals = grammar("temp_grammar.txt")
        first = first_compute(rules, nonterminals, terminals)
        C, augmented_rules, Sprime = dfa(rules, nonterminals, terminals, first, nonterminals[0])
        action, goto_table, conflicts = action_table_prod(C, augmented_rules, nonterminals, terminals, first, Sprime)
        
        # Preparar tokens
        tokens = input_string.strip().split()
        if not tokens or tokens[-1] != "$":
            tokens.append("$")
        
        accepted, trace = parser(tokens, action, goto_table)
        
        # Estructurar traza
        trace_data = []
        for stack, input_str, action_str in trace:
            trace_data.append({
                "stack": stack,
                "input": input_str,
                "action": action_str
            })
        
        return {
            "result": "accept" if accepted else "reject",
            "trace": trace_data
        }
    except Exception as e:
        return {"error": str(e)}
    finally:
        # Limpiar archivo temporal
        if os.path.exists("temp_grammar.txt"):
            os.remove("temp_grammar.txt")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(json.dumps({"error": "Uso: python lr1_web.py <tables|parse> <grammar> [input]"}))
        sys.exit(1)
    
    command = sys.argv[1]
    grammar_text = sys.argv[2]
    
    try:
        if command == "tables":
            result = generate_tables(grammar_text)
            print(json.dumps(result))
        elif command == "parse":
            input_string = sys.argv[3] if len(sys.argv) > 3 else ""
            result = parse_string(grammar_text, input_string)
            print(json.dumps(result))
        else:
            print(json.dumps({"error": "Comando no válido"}))
    except Exception as e:
        print(json.dumps({"error": f"Error ejecutando comando: {str(e)}"}))