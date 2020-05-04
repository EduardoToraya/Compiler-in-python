import ply.yacc as yacc
import sys
from fa_lex import tokens
from semantic_cube import semantic_cube
from pprint import pprint

class Stack:
     def __init__(self):
         self.items = []

     def isEmpty(self):
         return self.items == []

     def push(self, item):
         self.items.append(item)

     def pop(self):
         return self.items.pop()

     def peek(self):
         return self.items[len(self.items)-1]

     def size(self):
         return len(self.items)

dir_Base_Int = 0;
dir_Base_Float = 2000;
dir_Base_Char = 4000;
dir_Base_Bool = 6000;

dir_Base_Global = 0;
dir_Base_Local = 10000;
dir_Base_Temp = 20000;
dir_Base_Cte = 30000;

dir_counter_Temp_Int = dir_Base_Temp + dir_Base_Int;
dir_counter_Temp_Float = dir_Base_Temp + dir_Base_Float;
dir_counter_Temp_Char = dir_Base_Temp + dir_Base_Char;
dir_counter_Temp_Bool = dir_Base_Temp + dir_Base_Bool;

contadorCuadruplo = 0;
currTemp = 0;
current_type = ''
current_exp = None
current_func = 'global'
dir_func = {
    'global': {
        'vars': {},
        'params':{}
    }
}

# dir typo
Readquadruples = []
quadruples = []

#4 elemtos
currQuad = []

#manejo operadores
popper = Stack();
pilaOp = Stack();
pilaTipos = Stack();
pilaSaltos = Stack();
#pila avail

success = True

## gramatic rules
def p_programa(p):
    '''
    programa : PROGRAMA ID SEMICOLON vars funcion principal
            | PROGRAMA ID SEMICOLON funcion principal
            | PROGRAMA ID SEMICOLON vars principal
            | PROGRAMA ID SEMICOLON principal
    '''
    pprint(dir_func)
    pprint("inicio de cuadruplos")
    pprint(quadruples)
    #print(semantic_cube['float']['+']['int'])


def p_principal(p):
    '''
    principal : PRINCIPAL LPAREN RPAREN bloque
    '''


# variable declaration
def p_vars(p):
  '''
  vars : VAR vars_aux
  '''

  ## seccion de vars para definir varios varios tipos de  id con o sin  brackets
def p_vars_aux(p):
  '''
  vars_aux : tipo_simple vars_aux1 SEMICOLON
  		   | tipo_simple vars_aux1 SEMICOLON vars_aux
  '''

  ##seccion de vars para ciclo de varias id con brackets
def p_vars_aux1(p):
  '''
  vars_aux1 : vars_aux2
  		    | vars_aux2 COMMA vars_aux1
  '''

## seccion de vars para id con brackets
def p_vars_aux2(p):
  '''
    vars_aux2 : ID n_save_var
    		  | ID LSQUARE CTE_I n_save_array RSQUARE
  '''

def p_n_save_array(p):
    '''
        n_save_array :
    '''
    global current_func, current_type, dir_func
    id = p[-3]
    size = p[-1]
    if(id in dir_func[current_func]):
        error(p, 'La variable ya fue instanciada')
    else:
        dir_func[current_func]['vars'][id] ={
            'type' : current_type,
            'size' : size
        }

def p_n_save_var(p):
    '''
        n_save_var :
    '''
    global current_func, current_type, dir_func
    id = p[-1]
    if (id in dir_func[current_func]['vars'] or id in dir_func[current_func]['params']):
        error(p, 'La variable ya fue instanciada')
    else:
        dir_func[current_func]['vars'][id] ={
            'type' : current_type,
        }

def p_tipo_simple(p):
    '''
    tipo_simple : INT n_save_type
                | FLOAT n_save_type
                | CHAR n_save_type
    '''

def p_n_save_type(p):
    '''n_save_type : '''
    global current_type
    current_type = p[-1]


def p_empty(p):
    '''
    empty :
    '''

def p_variable(p):
    '''
    variable : ID LSQUARE mult_exp RSQUARE
             | ID p_n_getVarVal
    '''

def p_n_getVarVal(p):
    '''
    p_n_getVarVal :
    '''
    global current_exp, pilaOp, dir_func, current_func, pilaTipos
    #guarda exp para funciones posteriores
    id = p[-1]
    current_exp = id
    ##segunda parte para cuadruplos
    if(id in dir_func[current_func]['vars']):
        pilaOp.push(id)
        type = dir_func[current_func]['vars'][id]['type']
        pilaTipos.push(type)
    else:
        if(id in dir_func['global']['vars']):
                pilaOp.push(id)
                type = dir_func['global']['vars'][id]['type']
                pilaTipos.push(type)
        else:
            error(p, "La variable no se encuentra en el ambiente")

def p_funcion(p):
  '''
  funcion : FUNCION tipo_simple ID n_register_func LPAREN param RPAREN vars bloque
  		  | FUNCION tipo_simple ID n_register_func LPAREN param RPAREN bloque
  		  | FUNCION VOID n_save_type ID n_register_func LPAREN param RPAREN vars bloque
          | FUNCION VOID n_save_type ID n_register_func LPAREN param RPAREN bloque
          | FUNCION tipo_simple ID n_register_func LPAREN RPAREN vars bloque
          | FUNCION tipo_simple ID n_register_func LPAREN RPAREN bloque
          | FUNCION VOID n_save_type ID n_register_func LPAREN RPAREN vars bloque
          | FUNCION VOID n_save_type ID n_register_func LPAREN RPAREN bloque
  '''

def p_n_register_func(p):
    '''n_register_func : '''
    global dir_func, current_func, current_type
    if (p[-1] in dir_func):
        error(p, 'La función ya existe')
    else:
        current_func = p[-1]
        dir_func[current_func] = {
            'type': current_type,
            'params' : {},
            'vars': {}
        }

def p_param(p):
  '''
  param : tipo_simple param_aux1
  '''

  ##seccion de vars para ciclo de varias id con brackets
def p_param_aux1(p):
  '''
  param_aux1 : ID save_param
  		     | ID save_param COMMA param
  '''

def p_save_param(p):
    '''
    save_param :
    '''
    global current_func, dir_func, current_type
    id = p[-1]
    if(id in dir_func[current_func]['params']):
        error(p, "Parametro ya declarado")
    else:
        dir_func[current_func]['params'][id] ={
            'type': current_type
        }

def p_bloque(p):
  '''
  bloque : LBRACKET mult_estatutos RBRACKET
         | LBRACKET empty RBRACKET
  '''

def p_mult_estatutos(p):
  '''
  mult_estatutos : estatuto
  				 | estatuto mult_estatutos
  '''

def p_estatuto(p):
  '''
  estatuto : asigna SEMICOLON
  		   | llamada
           | lee
           | escribe
           | condicion
           | ciclo_w
           | retorno
           | ciclo_f
  '''

def p_asigna(p):
  '''
  asigna : mult_asigna
  '''


def p_mult_asigna(p):
    '''
    mult_asigna : variable EQUAL n_Operador mult_exp n_asignQuad
                | variable EQUAL n_Operador mult_asigna n_asignQuad
    '''

def p_n_asignQuad(p):
    '''
    n_asignQuad :
    '''
    global popper, pilaOp, pilaTipos, quadruples, currTemp
    if(not popper.isEmpty()):
        aux = popper.peek()
        if(aux == '='):
            opDerecho = pilaOp.pop();
            tipoDerecho = pilaTipos.pop();
            opIzquierdo = pilaOp.pop();
            tipoIzquierdo = pilaTipos.pop();
            operador = popper.pop()
            tipoResultado = semantic_cube[tipoIzquierdo][operador][tipoDerecho]

            if(tipoResultado != None):
                #result avail.next()
                tempQuad = [operador, opDerecho, -1, opIzquierdo]
                pilaOp.push(opIzquierdo)
                pilaTipos.push(tipoResultado)
                quadruples.append(tempQuad)
            else:
                error(p, "Tipo no compatible para la operacion de asignación")



def p_llamada(p):
  '''
  llamada : ID LPAREN mult_exp RPAREN
  '''

def p_lee(p):
  '''
  lee : LEE LPAREN variable RPAREN
  '''

def p_escribe(p):
  '''
  escribe : ESCRIBE LPAREN mult_exp n_escribeExp RPAREN SEMICOLON
  		  | ESCRIBE LPAREN mult_cte_s n_escribeExp RPAREN SEMICOLON
  '''

def p_n_escribeExp(p):
    '''
    n_escribeExp :
    '''
    global dir_func, quadruples, current_exp
    currQuad = ['print', -1, -1, pilaOp.pop()]
    quadruples.append(currQuad)

def p_mult_cte_s(p):
  '''
  mult_cte_s : CTE_S
  		     | CTE_S COMMA mult_cte_s
  '''

def p_mult_exp(p):
  '''
  mult_exp : exp
  		   | exp COMMA mult_exp
  '''

def p_exp(p):
  '''
  exp : t_exp n_orQuad
  	  | t_exp n_orQuad OR n_Operador exp
  '''

def p_n_orQuad(p):
    '''
    n_orQuad :
    '''
    global popper, pilaOp, pilaTipos, quadruples, tempQuad, currTemp
    if(not popper.isEmpty()):
        aux = popper.peek()
        if(aux == '|'):
            opDerecho = pilaOp.pop();
            tipoDerecho = pilaTipos.pop();
            opIzquierdo = pilaOp.pop();
            tipoIzquierdo = pilaTipos.pop();
            operador = popper.pop()
            tipoResultado = semantic_cube[tipoIzquierdo][operador][tipoDerecho]

            if(tipoResultado != None):
                #result avail.next()
                temporal = 't' + str(currTemp)
                tempQuad = [operador, opIzquierdo, opDerecho, temporal]
                currTemp = currTemp + 1;
                pilaOp.push(temporal)
                pilaTipos.push(tipoResultado)
                quadruples.append(tempQuad)
            else:
                error(p, "Tipo no compatible para la operacion de OR")


def p_t_exp(p):
  '''
  t_exp : g_exp n_andQuad
        | g_exp n_andQuad AND n_Operador t_exp
  '''

def p_n_andQuad(p):
    '''
    n_andQuad :
    '''
    global popper, pilaOp, pilaTipos, quadruples, tempQuad, currTemp
    if(not popper.isEmpty()):
        aux = popper.peek()
        if(aux == '&'):
            opDerecho = pilaOp.pop();
            tipoDerecho = pilaTipos.pop();
            opIzquierdo = pilaOp.pop();
            tipoIzquierdo = pilaTipos.pop();
            operador = popper.pop()
            tipoResultado = semantic_cube[tipoIzquierdo][operador][tipoDerecho]

            if(tipoResultado != None):
                #result avail.next()
                temporal = 't' + str(currTemp)
                tempQuad = [operador, opIzquierdo, opDerecho, temporal]
                currTemp = currTemp + 1;
                pilaOp.push(temporal)
                pilaTipos.push(tipoResultado)
                quadruples.append(tempQuad)
            else:
                error(p, "Tipo no compatible para la operacion de AND")



def p_g_exp(p):
  '''
  g_exp : m_exp n_compareQuad
  		| m_exp n_compareQuad LESSTHAN n_Operador g_exp
        | m_exp n_compareQuad LESSEQUAL n_Operador g_exp
        | m_exp n_compareQuad GREATERTHAN n_Operador g_exp
        | m_exp n_compareQuad GREATEREQUAL n_Operador g_exp
        | m_exp n_compareQuad SAME n_Operador g_exp
        | m_exp n_compareQuad NOEQUAL n_Operador g_exp
  '''

def p_n_compareQuad(p):
    '''
    n_compareQuad :
    '''
    global popper, pilaOp, pilaTipos, quadruples, tempQuad, currTemp
    if(not popper.isEmpty()):
        aux = popper.peek()
        if(aux == '<' or aux == '<=' or aux == '>' or aux == '>='
            or aux == '==' or aux == '<>'):
            opDerecho = pilaOp.pop();
            tipoDerecho = pilaTipos.pop();
            opIzquierdo = pilaOp.pop();
            tipoIzquierdo = pilaTipos.pop();
            operador = popper.pop()
            tipoResultado = semantic_cube[tipoIzquierdo][operador][tipoDerecho]

            if(tipoResultado != None):
                #result avail.next()
                temporal = 't' + str(currTemp)
                tempQuad = [operador, opIzquierdo, opDerecho, temporal]
                currTemp = currTemp + 1;
                pilaOp.push(temporal)
                pilaTipos.push(tipoResultado)
                quadruples.append(tempQuad)
            else:
                error(p, "Tipo no compatible para la operacion de comparación")



def p_m_exp(p):
  '''
  m_exp : t n_sumQuad
  	    | t n_sumQuad PLUS n_Operador m_exp
        | t n_sumQuad MINUS n_Operador m_exp
  '''

def p_n_sumQuad(p):
    '''
    n_sumQuad :
    '''
    global popper, pilaOp, pilaTipos, quadruples, tempQuad, currTemp
    if(not popper.isEmpty()):
        aux = popper.peek()
        if(aux == '+' or aux == '-'):
            opDerecho = pilaOp.pop();
            tipoDerecho = pilaTipos.pop();
            opIzquierdo = pilaOp.pop();
            tipoIzquierdo = pilaTipos.pop();
            operador = popper.pop()
            tipoResultado = semantic_cube[tipoIzquierdo][operador][tipoDerecho]

            if(tipoResultado != None):
                #result avail.next()
                temporal = 't' + str(currTemp)
                tempQuad = [operador, opIzquierdo, opDerecho, temporal]
                currTemp = currTemp + 1;
                pilaOp.push(temporal)
                pilaTipos.push(tipoResultado)
                quadruples.append(tempQuad)
            else:
                error(p, "Tipo no compatible para la operacion de suma/resta")



def p_t(p):
  '''
  	t : f n_multQuad
      | f n_multQuad MULT n_Operador t
      | f n_multQuad DIV n_Operador t
  '''

#n_multQuad
def p_n_multQuad(p):
    '''
    n_multQuad :
    '''
    global popper, pilaOp, pilaTipos, quadruples, tempQuad, currTemp
    if(not popper.isEmpty()):
        aux = popper.peek()
        if(aux == '*' or aux == '/'):
            opDerecho = pilaOp.pop();
            tipoDerecho = pilaTipos.pop();
            opIzquierdo = pilaOp.pop();
            tipoIzquierdo = pilaTipos.pop();
            operador = popper.pop()
            tipoResultado = semantic_cube[tipoIzquierdo][operador][tipoDerecho]

            if(tipoResultado != None):
                #result avail.next()
                temporal = 't' + str(currTemp)
                tempQuad = [operador, opIzquierdo, opDerecho, temporal]
                currTemp = currTemp + 1;
                pilaOp.push(temporal)
                pilaTipos.push(tipoResultado)
                quadruples.append(tempQuad)
            else:
                error(p, "Tipo no compatible para la operacion de mult/div")


def p_n_Operador(p):
    '''
    n_Operador :
    '''
    global popper, pilaOp, pilaTipos
    sim = p[-1]
    popper.push(sim)

def p_f(p):
  '''
  f : LPAREN n_FF mult_exp RPAREN n_FF
  	| n_tempTypeI CTE_I n_directPrint
    | n_tempTypeF CTE_F n_directPrint
    | n_tempTypeC CTE_C n_directPrint
    | variable
    | llamada
  '''

  #hacer regla individual para cada tipo de cte usando las reglas de abajo

def p_n_tempTypeI(p):
    '''
    n_tempTypeI :
    '''
    global current_type
    current_type = "int"

def p_n_tempTypeF(p):
    '''
    n_tempTypeF :
    '''
    global current_type
    current_type = "float"

def p_n_tempTypeC(p):
    '''
    n_tempTypeC :
    '''
    global current_type
    current_type = "char"


def p_n_directPrint(p):
    '''
    n_directPrint :
    '''
    global current_exp, pilaOp, pilaTipos
    current_exp = p[-1]
    pilaOp.push(current_exp)
    pilaTipos.push(current_type)

def p_n_FF(p):
    '''
    n_FF :
    '''
    global popper, pilaOp, pilaTipos
    popper.push(p[-1])

def p_condicion(p):
  '''
  condicion : SI LPAREN mult_exp RPAREN n_ifQuad ENTONCES bloque n_endIfQuad
            | SI LPAREN mult_exp RPAREN n_ifQuad ENTONCES bloque SINO p_n_sinoQuad bloque n_endIfQuad
  '''

def p_n_ifQuad(p):
    '''
    n_ifQuad :
    '''
    global popper, pilaOp, pilaTipos, quadruples
    expType = pilaTipos.pop();
    if(expType != 'bool'):
        error(p, 'La expresion condicional no es un booleano')
    else:
        result = pilaOp.pop()
        quad = ['GotoF', result, -1, 'empty']
        quadruples.append(quad)
        pilaSaltos.push(len(quadruples)-1)

def p_n_endIfQuad(p):
    '''
    n_endIfQuad :
    '''
    global pilaSaltos, quadruples
    end = pilaSaltos.pop()
    quadruples[end][3] = len(quadruples)

def p_n_sinoQuad(p):
    '''
    p_n_sinoQuad :
    '''
    global pilaSaltos, quadruples
    falso = pilaSaltos.pop()
    quad = ['Goto', -1, -1, 'empty']
    quadruples.append(quad)
    pilaSaltos.push(len(quadruples)-1)
    quadruples[falso][3] = len(quadruples)

def p_ciclo_w(p):
  '''
  ciclo_w : MIENTRAS n_startCicle LPAREN mult_exp RPAREN n_evalExp HAZ bloque n_endWhile
  '''

def p_n_startCicle(p):
    '''
    n_startCicle :
    '''
    global pilaSaltos
    pilaSaltos.push(len(quadruples))

def p_n_evalExp(p):
    '''
    n_evalExp :
    '''
    global pilaTipos, pilaOp, quadruples
    type = pilaTipos.pop()
    if(type != 'bool'):
        error(p, 'La expresion del mientras no es booleana');
    else:
        result = pilaOp.pop();
        quad = ['GotoF', result, -1, 'empty'];
        quadruples.append(quad)
        pilaSaltos.push(len(quadruples)-1)

def p_n_endWhile(p):
    '''
    n_endWhile :
    '''
    global pilaSaltos, quadruples
    end = pilaSaltos.pop()
    ret = pilaSaltos.pop()
    quad = ['Goto', -1, -1, ret]
    quadruples.append(quad)
    quadruples[end][3] = len(quadruples)




def p_ciclo_f(p):
  '''
  ciclo_f : DESDE n_startCicle asigna HASTA mult_exp n_evalExp_for HACER bloque n_endFor
  '''

#pilatipos pilaOp
def p_n_evalExp_for(p):
    '''
    n_evalExp_for :
    '''
    global pilaTipos, pilaOp, quadruples, semantic_cube, currTemp, pilaSaltos
    typeExp = pilaTipos.pop()
    typeAsig = pilaTipos.pop();
    if(semantic_cube[typeAsig]['<'][typeExp] != 'bool'):
        error(p, 'La expresion del for no es compatible');
    else:
        opExp = pilaOp.pop();
        opAsig = pilaOp.pop();
        temp = 't' + str(currTemp)
        quad = ['<', opAsig, opExp, temp]
        quadruples.append(quad)

        quad = ['GotoF', temp, -1, 'empty'];
        currTemp = currTemp + 1
        quadruples.append(quad)
        pilaSaltos.push(len(quadruples)-1)

def p_n_endFor(p):
    '''
    n_endFor :
    '''
    global pilaSaltos, quadruples
    end = pilaSaltos.pop()
    ret = pilaSaltos.pop()
    quad = ['Goto', -1, -1, ret+1]
    quadruples.append(quad)
    quadruples[end][3] = len(quadruples)


def p_retorno(p):
  '''
  retorno : REGRESA mult_exp SEMICOLON
  '''

##error function for parser
def p_error(p):
    global success
    success = False
    print('SyntaxError', p.value)
    #añadir en que linea
    sys.exit()

    #p.lexer.skip(1)

    # TODO:¨parar la compilación

def error(p, message):
    print("Error: ", message)
    sys.exit()


parser = yacc.yacc()

data = "testFiles/testFile.txt"
f = open(data,'r')
s = f.read()

parser.parse(s)

if success == True:
    print("El archivo se ha aceptado")
    sys.exit()
else:
    print("El archivo tiene errores")
    sys.exit()
