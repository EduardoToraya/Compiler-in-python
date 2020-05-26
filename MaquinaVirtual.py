from stack import Stack
from memoria import Memoria
import sys
import six

dir_func = {}
dir_quadruples = {}
llamadas = Stack()
memorias = Stack()
memoria_global = Memoria()
this_func = Stack()
param_stack = Stack()

#memory ranges
#global 0 - 9999
top_limit_global = 10000
#local 10000- 19999
top_limit_local = 20000
#constants 20000- 29999
top_limit_cte = 30000
#pointers 30000- 39999.
top_limit_pointer = 40000



def set_value(address, value):
    if address < top_limit_global:
        memoria_global.set_value(address, value)
    elif address < top_limit_local:
        memorias.peek().set_value(address, value)
    elif address < top_limit_cte:
        memoria_global.set_value(address, value)
    else:
        #in case of a pointer
        content_pointer = memoria_global.get_value(address)
        memoria_global.set_value(content_pointer, value)

def get_value(address):
    if address < top_limit_global:
        return memoria_global.get_value(address)
    elif address < top_limit_local:
        return memorias.peek().get_value(address)
    elif address < top_limit_cte:
        return memoria_global.get_value(address)
    else:
        #in case of a pointer
        content_pointer = memoria_global.get_value(address)
        return memoria_global.get_value(content_pointer)


def save_ctes():
    global memoria_global
    for i in dir_func['constants']['cte']:
        memoria_global.set_value(dir_func['constants']['cte'][i]['address'], i)

def getParam(address):
    if address%10000 < 2500:
        return int(get_value(address))
    elif address%10000 < 5000:
        return float(get_value(address))
    elif address%10000 < 7500:
        return get_value(address)
    else:
        return bool(get_value(address))

def calculate(p1, op, p2):
    if(op == '+'):
        return p1 + p2
    elif(op == '-'):
        return p1 - p2
    elif(op == '*'):
        return p1 * p2
    elif(op == '/'):
        return p1 / p2
    elif(op == '<'):
        return p1 < p2
    elif(op == '<='):
        return p1 <= p2
    elif(op == '>'):
        return p1 > p2
    elif(op == '>='):
        return p1 >= p2
    elif(op == '=='):
        return p1 == p2
    elif(op == '<>'):
        return p1 != p2
    elif(op == '&'):
        return p1 and p2
    elif(op == '|'):
        return p1 or p2


def run():
    global memoria_global, param_stack, memorias, llamadas, pila_returns, this_func
    #añadiendo ctes y apuntadores a memoria.
    save_ctes();
    tracker = 0
    while tracker < len(dir_quadruples):
        #print(tracker)
        curr_quad = dir_quadruples[tracker]
        instr = curr_quad[0]
        el2 = curr_quad[1]
        el3 = curr_quad[2]
        el4 = curr_quad[3]

        if instr == 'Goto':
            tracker = el4

        elif instr == 'print':
            print(get_value(el4))
            tracker += 1

        elif instr == 'read':
            # agregar el leer variable
            tracker+=1

        elif instr == '+' or instr == '-' or instr == '*' or instr == '/' or instr == '<' or instr == '<=' or instr == '>' or instr == '>=' or instr == '==' or instr == '<>' or instr == '&' or instr == '|':
            p1 = getParam(el2)
            p2 = getParam(el3)
            value = calculate(p1, instr, p2)
            set_value(el4, value)
            tracker += 1

        elif instr == '=':
            toAsign = get_value(el2)
            set_value(el4, toAsign)
            tracker += 1

        elif instr == 'ENDFUNC':
            #liberar memoria actual
            #recuperar dir ret
            #regresar a la mem anterior
            if(not memorias.isEmpty()):
                memorias.pop()
            tracker = llamadas.pop()

        elif instr == 'GotoF':
            evaluar = getParam(el2)
            if(evaluar == False):
                tracker = el4
            else:
                tracker += 1

        elif instr == 'ERA':
            #Allocates memory
            #aux = Memoria()
            #memorias.push(aux)
            tracker += 1

        elif instr == 'PARAM':
            #aux = Memoria()
            #aux = memorias.pop()
            val = get_value(el2)
            #memorias.push(aux)
            #set_value(el4, val)
            param_stack.push(val)
            param_stack.push(el4)
            tracker += 1

        elif instr == 'GOSUB':
            aux = Memoria()
            memorias.push(aux)
            #if(not param_stack.isEmpty()):
            this_func.push(el2)
            while(not param_stack.isEmpty()):
                set_value(param_stack.pop(), param_stack.pop())
            llamadas.push(tracker+1)
            tracker = el4

        elif instr == 'RETURN':
            aux_val = get_value(el4)
            memorias.pop()
            tracker = llamadas.pop()
            if isinstance(this_func.peek(), str):
                this_func.pop()
            set_value(this_func.pop(), aux_val)

        else:
            #lets hope this does not get called
            print('error en cuadruplos')
            sys.exit()

if len(sys.argv) != 2:
    print('Please send a file.')
    raise SyntaxError('vm.')

program_name = sys.argv[1]
# Compile program.
with open(program_name, 'r') as file:
    #global dir_func, dir_quadruples
    input = eval(file.read())
    dir_func = input['tabla_func']
    dir_quadruples = input['dir_quadruples']
    run()
