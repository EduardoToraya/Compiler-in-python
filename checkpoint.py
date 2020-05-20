import ply.yacc as yacc
import sys
from fa_lex import tokens
from semantic_cube import semantic_cube
from pprint import pprint
from stack import Stack

DIR_BASE_INT = 0
DIR_BASE_FLOAT = 2500
DIR_BASE_CHAR = 5000
DIR_BASE_BOOL = 7500



DIR_LENGTH = 2500

DIR_BASE_GLOBAL = 0
DIR_BASE_LOCAL = 10000
DIR_BASE_CTE = 20000

# dir_counter_Temp_Int = dir_Base_Temp + dir_Base_Int;
# dir_counter_Temp_Float = dir_Base_Temp + dir_Base_Float;
# dir_counter_Temp_Char = dir_Base_Temp + dir_Base_Char;
# dir_counter_Temp_Bool = dir_Base_Temp + dir_Base_Bool;

class Operando:
    def __init__(self):
        self.id = None
        self.address = None

contadorCuadruplo = 0;
currTemp = 0;
current_type = ''
current_exp = None
current_func = 'global'
dir_func = {
    'global': {
        'vars': {},
        'params': {},
        'next_int': DIR_BASE_GLOBAL + DIR_BASE_INT,
        'next_float': DIR_BASE_GLOBAL + DIR_BASE_FLOAT,
        'next_char': DIR_BASE_GLOBAL + DIR_BASE_CHAR,
        'next_bool': DIR_BASE_GLOBAL + DIR_BASE_BOOL
    },
    'constants': {
        'next_int': DIR_BASE_CTE + DIR_BASE_INT,
        'next_float': DIR_BASE_CTE + DIR_BASE_FLOAT,
        'next_char': DIR_BASE_CTE + DIR_BASE_CHAR,
        'next_bool': DIR_BASE_CTE + DIR_BASE_BOOL,
        'cte': {
            #'a': 1000 Formato compilación
            #1000: 'a' Formato maquina virtual
        }
    }
}

# dir typo
read_quadruples = []
dir_quadruples = []

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
    programa : PROGRAMA ID SEMICOLON vars mult_funcion principal
            | PROGRAMA ID SEMICOLON mult_funcion principal
            | PROGRAMA ID SEMICOLON vars principal
            | PROGRAMA ID SEMICOLON principal
    '''
    pprint(dir_func)
    print("inicio de cuadruplos nombres", '\t\t', 'inicio de cuadruplos de direcciones')
    for i, cuadruplo in enumerate(read_quadruples):
        print(i, cuadruplo, " ",'\t\t', i ,dir_quadruples[i])

def p_principal(p):
    '''
    principal : PRINCIPAL n_register_glob LPAREN RPAREN bloque
    '''

def p_n_register_glob(p):
    '''
    n_register_glob :
    '''
    global current_func
    current_func = 'global'

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
            'address': get_next_var_address(p)
        }

def get_next_var_address(p):
    global dir_func
    if current_func == 'global':
        base = DIR_BASE_GLOBAL
    else:
        base = DIR_BASE_LOCAL

    if(current_type == 'int'):
        baseType = 0;
    elif(current_type == 'float'):
        baseType = 2500;
    elif(current_type == 'char'):
        baseType = 5000;
    else:
        baseType = 7500;

    if dir_func[current_func]['next_' + current_type] - base - baseType < DIR_LENGTH:
        aux = dir_func[current_func]['next_' + current_type]
        dir_func[current_func]['next_' + current_type] += 1
        return aux
    else:
        error(p, "Numero de variables en su limite")


def get_next_cte_address(p, id):
    global dir_func
    if (id in dir_func['constants']['cte']):
        return dir_func['constants']['cte'][id]['address'];
    else:
        if(current_type == 'int'):
            baseType = 0;
        elif(current_type == 'float'):
            baseType = 2500;
        elif(current_type == 'char'):
            baseType = 5000;
        else:
            baseType = 7500;
        base = DIR_BASE_CTE;
        if(dir_func['constants']['next_'+current_type] - base - baseType < DIR_LENGTH):
            aux = dir_func['constants']['next_'+current_type];
            dir_func['constants']['next_'+current_type] += 1;
            dir_func['constants']['cte'][id] = {
                'address' : aux
            }
            return aux;
        else:
            error(p, "Numero de constantes " + current_type + " en su límite")



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
    temp_op = Operando()
    ##segunda parte para cuadruplos
    temp_op.id = id
    if(id in dir_func[current_func]['vars']):
        temp_op.address = dir_func[current_func]['vars'][id]['address']
        pilaOp.push(temp_op)
        type = dir_func[current_func]['vars'][id]['type']
        pilaTipos.push(type)
    else:
        if(id in dir_func['global']['vars']):
            temp_op.address = dir_func['global']['vars'][id]['address']
            pilaOp.push(temp_op)
            type = dir_func['global']['vars'][id]['type']
            pilaTipos.push(type)
        else:
            error(p, "La variable no se encuentra en el ambiente")

def p_mult_funcion(p):
    '''
    mult_funcion : funcion
                 | funcion mult_funcion
    '''

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
            'vars': {},
            'next_int': DIR_BASE_LOCAL + DIR_BASE_INT,
            'next_float': DIR_BASE_LOCAL + DIR_BASE_FLOAT,
            'next_char': DIR_BASE_LOCAL + DIR_BASE_CHAR,
            'next_bool': DIR_BASE_LOCAL + DIR_BASE_BOOL
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
    global popper, pilaOp, pilaTipos, read_quadruples, currTemp, dir_quadruples
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
                tempQuad = [operador, opDerecho.id, -1, opIzquierdo.id]
                pilaOp.push(opIzquierdo)
                pilaTipos.push(tipoResultado)
                read_quadruples.append(tempQuad)
                tempQuad = [operador, opDerecho.address, -1, opIzquierdo.address]
                dir_quadruples.append(tempQuad)

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
    global dir_func, read_quadruples, current_exp
    operando = pilaOp.pop();
    currQuad = ['print', -1, -1, operando.id]
    read_quadruples.append(currQuad)
    currQuad = ['print', -1, -1, operando.address]
    dir_quadruples.append(currQuad)



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
    global popper, pilaOp, pilaTipos, read_quadruples, currTemp, dir_quadruples, current_type
    if(not popper.isEmpty()):
        aux = popper.peek()
        if(aux == '|'):
            opDerecho = pilaOp.pop();
            tipoDerecho = pilaTipos.pop();
            opIzquierdo = pilaOp.pop();
            tipoIzquierdo = pilaTipos.pop();
            operador = popper.pop()
            tipoResultado = semantic_cube[tipoIzquierdo][operador][tipoDerecho]
            current_type = tipoResultado
            if(tipoResultado != None):
                #result avail.next()
                temporal = 't' + str(currTemp)
                temp_op = Operando();
                temp_op.id = temporal;

                temp_op.address = get_next_var_address(p);

                tempQuad = [operador, opIzquierdo.id, opDerecho.id, temp_op.id]
                currTemp = currTemp + 1;

                pilaOp.push(temp_op)
                pilaTipos.push(tipoResultado)
                read_quadruples.append(tempQuad)
                tempQuad = [operador, opIzquierdo.address, opDerecho.address, temp_op.address]
                dir_quadruples.append(tempQuad)

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
    global popper, pilaOp, pilaTipos, read_quadruples, currTemp, dir_quadruples, current_type
    if(not popper.isEmpty()):
        aux = popper.peek()
        if(aux == '&'):
            opDerecho = pilaOp.pop();
            tipoDerecho = pilaTipos.pop();
            opIzquierdo = pilaOp.pop();
            tipoIzquierdo = pilaTipos.pop();
            operador = popper.pop()
            tipoResultado = semantic_cube[tipoIzquierdo][operador][tipoDerecho]
            current_type = tipoResultado
            if(tipoResultado != None):
                #result avail.next()
                temporal = 't' + str(currTemp)
                temp_op = Operando();
                temp_op.id = temporal;
                temp_op.address = get_next_var_address(p)

                tempQuad = [operador, opIzquierdo.id, opDerecho.id, temp_op.id]
                currTemp = currTemp + 1;

                pilaOp.push(temp_op)
                pilaTipos.push(tipoResultado)
                read_quadruples.append(tempQuad)
                tempQuad = [operador, opIzquierdo.address, opDerecho.address, temp_op.address]
                dir_quadruples.append(tempQuad);
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
    global popper, pilaOp, pilaTipos, read_quadruples, currTemp, dir_quadruples, current_type
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
            current_type = tipoResultado
            if(tipoResultado != None):
                #result avail.next()
                temporal = 't' + str(currTemp)
                temp_op = Operando();
                temp_op.id = temporal;
                temp_op.address = get_next_var_address(p);

                tempQuad = [operador, opIzquierdo.id, opDerecho.id, temp_op.id]
                currTemp = currTemp + 1;
                pilaOp.push(temp_op)
                pilaTipos.push(tipoResultado)
                read_quadruples.append(tempQuad)
                tempQuad = [operador, opIzquierdo.address, opDerecho.address, temp_op.address];
                dir_quadruples.append(tempQuad)
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
    global popper, pilaOp, pilaTipos, read_quadruples, currTemp, dir_quadruples, current_type
    if(not popper.isEmpty()):
        aux = popper.peek()
        if(aux == '+' or aux == '-'):
            opDerecho = pilaOp.pop();
            tipoDerecho = pilaTipos.pop();
            opIzquierdo = pilaOp.pop();
            tipoIzquierdo = pilaTipos.pop();
            operador = popper.pop()
            tipoResultado = semantic_cube[tipoIzquierdo][operador][tipoDerecho]
            current_type = tipoResultado
            if(tipoResultado != None):
                #result avail.next()
                temporal = 't' + str(currTemp)
                temp_op = Operando();
                temp_op.id = temporal;
                temp_op.address = get_next_var_address(p);

                tempQuad = [operador, opIzquierdo.id, opDerecho.id, temp_op.id]
                currTemp = currTemp + 1;
                pilaOp.push(temp_op)
                pilaTipos.push(tipoResultado)
                read_quadruples.append(tempQuad)
                tempQuad = [operador, opIzquierdo.address, opDerecho.address, temp_op.address]
                dir_quadruples.append(tempQuad)
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
    global popper, pilaOp, pilaTipos, read_quadruples, currTemp, dir_quadruples, current_type
    if(not popper.isEmpty()):
        aux = popper.peek()
        if(aux == '*' or aux == '/'):
            opDerecho = pilaOp.pop();
            tipoDerecho = pilaTipos.pop();
            opIzquierdo = pilaOp.pop();
            tipoIzquierdo = pilaTipos.pop();
            operador = popper.pop()
            tipoResultado = semantic_cube[tipoIzquierdo][operador][tipoDerecho]
            current_type = tipoResultado;

            if(tipoResultado != None):
                #result avail.next()
                temporal = 't' + str(currTemp)
                temp_op = Operando();
                temp_op.id=temporal;
                temp_op.address = get_next_var_address(p);

                tempQuad = [operador, opIzquierdo.id, opDerecho.id, temp_op.id]
                currTemp = currTemp + 1;
                pilaOp.push(temp_op)
                pilaTipos.push(tipoResultado)
                read_quadruples.append(tempQuad)
                tempQuad = [operador, opIzquierdo.address, opDerecho.address, temp_op.address]
                dir_quadruples.append(tempQuad);
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
    operador = Operando();
    operador.id = current_exp;
    operador.address = get_next_cte_address(p, operador.id);
    pilaOp.push(operador)
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
    global popper, pilaOp, pilaTipos, read_quadruples, dir_quadruples
    expType = pilaTipos.pop();
    if(expType != 'bool'):
        error(p, 'La expresion condicional no es un booleano')
    else:
        result = pilaOp.pop()
        quad = ['GotoF', result.id, -1, 'empty']
        read_quadruples.append(quad)
        quad = ['GotoF', result.address, -1, 'empty']
        dir_quadruples.append(quad)
        pilaSaltos.push(len(read_quadruples)-1)

def p_n_endIfQuad(p):
    '''
    n_endIfQuad :
    '''
    global pilaSaltos, read_quadruples, dir_quadruples
    end = pilaSaltos.pop()
    read_quadruples[end][3] = len(read_quadruples)
    dir_quadruples[end][3] = len(dir_quadruples)

def p_n_sinoQuad(p):
    '''
    p_n_sinoQuad :
    '''
    global pilaSaltos, read_quadruples, dir_quadruples
    falso = pilaSaltos.pop()
    quad = ['Goto', -1, -1, 'empty']
    read_quadruples.append(quad)
    dir_quadruples.append(quad)
    pilaSaltos.push(len(read_quadruples)-1)
    read_quadruples[falso][3] = len(read_quadruples)
    dir_quadruples[falso][3] = len(dir_quadruples)

def p_ciclo_w(p):
  '''
  ciclo_w : MIENTRAS n_startCicle LPAREN mult_exp RPAREN n_evalExp HAZ bloque n_endWhile
  '''

def p_n_startCicle(p):
    '''
    n_startCicle :
    '''
    global pilaSaltos
    pilaSaltos.push(len(read_quadruples))

def p_n_evalExp(p):
    '''
    n_evalExp :
    '''
    global pilaTipos, pilaOp, read_quadruples, dir_quadruples
    type = pilaTipos.pop()
    if(type != 'bool'):
        error(p, 'La expresion del mientras no es booleana');
    else:
        result = pilaOp.pop();
        quad = ['GotoF', result.id, -1, 'empty'];
        read_quadruples.append(quad)
        quad = ['GotoF', result.address, -1, 'empty'];
        dir_quadruples.append(quad)
        pilaSaltos.push(len(read_quadruples)-1)

def p_n_endWhile(p):
    '''
    n_endWhile :
    '''
    global pilaSaltos, read_quadruples, dir_quadruples
    end = pilaSaltos.pop()
    ret = pilaSaltos.pop()
    quad = ['Goto', -1, -1, ret]
    read_quadruples.append(quad)
    read_quadruples[end][3] = len(read_quadruples)

    dir_quadruples.append(quad)
    dir_quadruples[end][3] = len(dir_quadruples)




def p_ciclo_f(p):
  '''
  ciclo_f : DESDE asigna n_startCicle HASTA mult_exp n_evalExp_for HACER bloque n_endFor
  '''

#pilatipos pilaOp
def p_n_evalExp_for(p):
    '''
    n_evalExp_for :
    '''
    global pilaTipos, pilaOp, read_quadruples, semantic_cube, currTemp, pilaSaltos, dir_quadruples, current_type
    typeExp = pilaTipos.pop()
    typeAsig = pilaTipos.pop();
    if(semantic_cube[typeAsig]['<'][typeExp] != 'bool'):
        error(p, 'La expresion del for no es compatible');
    else:
        current_type = 'bool'
        opExp = pilaOp.pop();
        opAsig = pilaOp.pop();
        temp = 't' + str(currTemp)
        temp_op = Operando();
        temp_op.id = temp;
        temp_op.address = get_next_var_address(p);

        quad = ['<', opAsig.id, opExp.id, temp_op.id]
        read_quadruples.append(quad)
        quad = ['<', opAsig.address, opExp.address, temp_op.address]
        dir_quadruples.append(quad);

        quad = ['GotoF', temp_op.id, -1, 'empty'];
        currTemp = currTemp + 1
        read_quadruples.append(quad)
        quad = ['GotoF', temp_op.address, -1, 'empty'];
        dir_quadruples.append(quad)
        pilaSaltos.push(len(read_quadruples)-1)

def p_n_endFor(p):
    '''
    n_endFor :
    '''
    global pilaSaltos, read_quadruples
    end = pilaSaltos.pop()
    ret = pilaSaltos.pop()
    quad = ['Goto', -1, -1, ret]
    read_quadruples.append(quad)
    read_quadruples[end][3] = len(read_quadruples)
    dir_quadruples.append(quad)
    dir_quadruples[end][3] = len(dir_quadruples)


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

data = "testFiles/pelos.txt"
f = open(data,'r')
s = f.read()

parser.parse(s)

if success == True:
    print("El archivo se ha aceptado")
    sys.exit()
else:
    print("El archivo tiene errores")
    sys.exit()
