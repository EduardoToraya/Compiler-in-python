import ply.yacc as yacc
import sys
from fa_lex import tokens
from semantic_cube import semantic_cube
from pprint import pprint
from stack import Stack

# Se definen los rangos de direcciones por tipo de dato.
DIR_BASE_INT = 0
DIR_BASE_FLOAT = 2500
DIR_BASE_CHAR = 5000
DIR_BASE_BOOL = 7500

# Se define el largo por seccion y los rangos de direcciones base.
DIR_LENGTH = 2500

DIR_BASE_GLOBAL = 0
DIR_BASE_LOCAL = 10000
DIR_BASE_CTE = 20000
DIR_BASE_POINTER = 30000

# Contador de parametros y se guarda la función en la que esta la variable llamada.
address_func_var_global = None
parameter_counter = 0
retornoFuncion = None

curr_Call = None

#Clase operando para el push a la pila de operandos con id y con address
class Operando:
    def __init__(self):
        self.id = None
        self.address = None

#contadores para manejo de temporales de cuadruplos legibles.
currTemp = 1;
currTempArr = 1;
#variable para tipo de expresion global
current_type = ''
current_exp = None
#inicializa  la funcion actual como global
current_func = 'global'

#se inicializa el directorio de funciones con las direcciones base de
#integros de variables globales, de constantes y de apuntadores a arreglos.
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
        }
    },
    'array_pointers' : {
        'next_pointer' : DIR_BASE_POINTER
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

## Funcion que inicializa el programa e imprime los cruadruplos y el directorio de funciones.
def p_programa(p):
    '''
    programa : PROGRAMA p_n_mainJump ID SEMICOLON vars mult_funcion principal
            | PROGRAMA p_n_mainJump ID SEMICOLON mult_funcion principal
            | PROGRAMA p_n_mainJump ID SEMICOLON vars principal
            | PROGRAMA p_n_mainJump ID SEMICOLON principal
    '''
    del dir_func['global']['vars']
    pprint(dir_func)
    print("inicio de cuadruplos nombres", '\t\t', 'inicio de cuadruplos de direcciones')
    for i, cuadruplo in enumerate(read_quadruples):
        print(i, cuadruplo, " ",'\t\t', i ,dir_quadruples[i])

#genera cuadruplo para el salto a la funcion principal para comenzar ejecución.
def p_n_mainJump(p):
    '''
    p_n_mainJump :
    '''
    global dir_quadruples, read_quadruples
    temp_quad = ['Goto', -1, -1, None]
    dir_quadruples.append(temp_quad)
    read_quadruples.append(temp_quad)

#Grupo de funciones para registrar el cuadruplo donde empieza principal.
def p_principal(p):
    '''
    principal : PRINCIPAL n_register_glob LPAREN RPAREN bloque
    '''

def p_n_register_glob(p):
    '''
    n_register_glob :
    '''
    global current_func, read_quadruples, dir_quadruples
    current_func = 'global'
    read_quadruples[0][3] = len(read_quadruples)
    dir_quadruples[0][3] = len(dir_quadruples)


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

#Codigo para agregar arreglos, igual a variable pero con tamaño.
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
            'address' : get_next_arr_address(p, int(size)),
            'size' : int(size)
        }

#Guarda cariable con su tipo y direccion en el directorio de funciones.
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

#Funcion de manejo de memoria para conseguir la siguiente direccion de un arreglo
#Toma en cuenta el tamaño del arreglo para dar la siguiente direccion.
def get_next_arr_address(p, size):
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

    if dir_func[current_func]['next_' + current_type] + size - base - baseType < DIR_LENGTH:
        aux = dir_func[current_func]['next_' + current_type]
        dir_func[current_func]['next_' + current_type] += size
        return aux
    else:
        error(p, "Numero de variables en su limite")

#Funcion de manejo de memoria para conseguir la siguiente direccion de una variable
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

#Funcion de manejo de memoria para conseguir la siguiente direccion de un apuntador
def get_next_pointer_address(p):
    global dir_func, DIR_BASE_POINTER
    if dir_func['array_pointers']['next_pointer'] - DIR_BASE_POINTER < DIR_LENGTH*4:
        aux = dir_func['array_pointers']['next_pointer']
        dir_func['array_pointers']['next_pointer']  += 1
        #dir_func['array_pointers']['pointer'][aux] = {
        #    'points_to' : None
        #}
        return aux
    else:
        error(p, "Numero de variables de arreglos en su limite")

#Funcion de manejo de memoria para conseguir la siguiente direccion de un arreglo
def get_next_cte_address(p, id):
    global dir_func, current_type
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

#Funciones auxiliares para guardar el tipo de la expresion.
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

#Funcion para llamada a la variable, se apega a la gramática con subfunciones.
def p_variable(p):
    '''
    variable : ID n_getVarVal LSQUARE n_start_FF n_hasDim mult_exp RSQUARE n_end_FF n_arr_quad
             | ID n_getVarVal
    '''

#Maneja las stacks de tipo y operando así como la generación de cruadruplos
#Funcion específica de arreglos y de generación de verificación.
def p_n_arr_quad(p):
    '''
    n_arr_quad :
    '''
    global read_quadruples, dir_quadruples, pilaTipos, currTemp, current_type, current_func, currTempArr
    temp_exp = pilaOp.pop()
    temp_array = pilaOp.pop()
    temp_exp_type = pilaTipos.pop()
    if(temp_exp_type != 'int'):
        error(p, 'El indice del arreglo debe ser un íntegro')
    id = temp_array.id
    if(id in dir_func[current_func]['vars']):
        aux = current_func
    else:
        aux = 'global'

    current_type = 'int'
    temp_arr_limit = dir_func[aux]['vars'][temp_array.id]['size']
    temp_cte = get_next_cte_address(p, str(temp_arr_limit))

    temp_quad = ['VERIFY', temp_exp.id, -1, temp_arr_limit]
    read_quadruples.append(temp_quad)
    temp_quad = ['VERIFY', temp_exp.address, -1, temp_cte]
    dir_quadruples.append(temp_quad)

    temp_cte = get_next_cte_address(p, str(temp_array.address))
    dir_array = get_next_pointer_address(p)

    temp_quad = ['+', temp_exp.id, temp_array.id, dir_array]
    read_quadruples.append(temp_quad)
    temp_quad = ['+', temp_exp.address, temp_cte, dir_array]
    dir_quadruples.append(temp_quad)

    temporalArr = 't' + str(currTempArr)
    currTempArr += 1;
    toPush = Operando()
    toPush.id = temporalArr
    toPush.address = dir_array
    pilaOp.push(toPush)

#Revisa si una variable que se identifica como arreglo requiere dimensiones
def p_n_hasDim(p):
    '''
    n_hasDim :
    '''
    global dir_func, current_func, pilaOp, pilaTipos
    temp_op = pilaOp.peek()
    #know which function it is in
    if(temp_op.id in dir_func[current_func]['vars']):
        aux = current_func
    else:
        aux = 'global'

    #print(len(dir_func[aux]['vars'][temp_op.id]))
    if(len(dir_func[aux]['vars'][temp_op.id]) < 3):
        error(p, 'La variable que se está tratando de accesar requiere dimensión')

#Obtiene el valor de una variable, se usa para no dimensionadas y dimensionadas
#Obtienee su tipo y si id.
def p_n_getVarVal(p):
    '''
    n_getVarVal :
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

#Conjunto de funciones para tener Funciones
#De tipo void o con retorno de char int o float.
#Con parametros y sin parametros.
def p_mult_funcion(p):
    '''
    mult_funcion : funcion
                 | funcion mult_funcion
    '''

def p_funcion(p):
  '''
  funcion : FUNCION tipo_simple ID n_register_func LPAREN param RPAREN vars bloque n_endof_func
  		  | FUNCION tipo_simple ID n_register_func LPAREN param RPAREN bloque n_endof_func
  		  | FUNCION VOID n_save_type ID n_register_func LPAREN param RPAREN vars bloque n_endof_func
          | FUNCION VOID n_save_type ID n_register_func LPAREN param RPAREN bloque n_endof_func
          | FUNCION tipo_simple ID n_register_func LPAREN RPAREN vars bloque n_endof_func
          | FUNCION tipo_simple ID n_register_func LPAREN RPAREN bloque n_endof_func
          | FUNCION VOID n_save_type ID n_register_func LPAREN RPAREN vars bloque n_endof_func
          | FUNCION VOID n_save_type ID n_register_func LPAREN RPAREN bloque n_endof_func
  '''
  global dir_func
  del dir_func[current_func]['vars']

#Inicializa la funcion con su pertinente información
#Numero de variables tipo, en qué cuadruplo comienza, y su manejador de mememoria.
def p_n_register_func(p):
    '''n_register_func : '''
    global dir_func, current_func, current_type
    if (p[-1] in dir_func):
        error(p, 'La función ya existe')
    else:
        current_func = p[-1]
        dir_func[current_func] = {
            'type': current_type,
            'params' : [],
            'vars': {},
            'num_vars_int' : None,
            'num_vars_float' : None,
            'num_vars_char' : None,
            'num_vars_bool' : None,
            'starts' : len(dir_quadruples),
            'next_int': DIR_BASE_LOCAL + DIR_BASE_INT,
            'next_float': DIR_BASE_LOCAL + DIR_BASE_FLOAT,
            'next_char': DIR_BASE_LOCAL + DIR_BASE_CHAR,
            'next_bool': DIR_BASE_LOCAL + DIR_BASE_BOOL
        }
        #guardando una variable global con el nombre de la funcion si no es VOID
        if(current_type != 'void'):
            current_func = 'global'
            if p[-1] in dir_func['global']['vars']:
                error(p, "Una funcion y una variable global no pueden tener el mismo nombre")

            else:
                dir_func['global']['vars'][p[-1]] ={
                    'type' : current_type,
                    'address': get_next_var_address(p)
                }
                current_func = p[-1]


#Funcion para llamada a funciones con parámetro
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

#Funcion que revisa si un parámetro de los que
#se tienen en la declaración de la función ya existe.
def p_save_param(p):
    '''
    save_param :
    '''
    global current_func, dir_func, current_type
    id = p[-1]
    if(id in dir_func[current_func]['vars']):
        error(p, "Parametro ya declarado")
    else:
        dir_func[current_func]['params'].append(current_type)
        dir_func[current_func]['vars'][id] ={
            'type' : current_type,
            'address': get_next_var_address(p)
        }

#Punto neurálgico para el final de la función donde se reinicial las variables
#Y se genera cuadruplo de terminación de la función.
def p_n_endof_func(p):
    '''
    n_endof_func :
    '''
    global dir_func, current_func, read_quadruples, dir_quadruples, currTemp
    dir_func[current_func]['num_vars_int'] = dir_func[current_func]['next_int'] - DIR_BASE_INT - DIR_BASE_LOCAL
    dir_func[current_func]['num_vars_float'] = dir_func[current_func]['next_float'] - DIR_BASE_FLOAT - DIR_BASE_LOCAL
    dir_func[current_func]['num_vars_char'] = dir_func[current_func]['next_char'] - DIR_BASE_CHAR - DIR_BASE_LOCAL
    dir_func[current_func]['num_vars_bool'] = dir_func[current_func]['next_bool'] - DIR_BASE_BOOL - DIR_BASE_LOCAL
    temp_quad = ['ENDFUNC', -1, -1, -1]
    read_quadruples.append(temp_quad);
    dir_quadruples.append(temp_quad);
    currTemp = 1


#Funciones para la gramática de estatutos.
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
  		   | llamada SEMICOLON
           | lee
           | escribe
           | condicion
           | ciclo_w
           | retorno
           | ciclo_f
  '''

#Conjunto de funciones para la acción de asignación.
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


#Función para tener el exponente de un parámetro.
def p_param_exp(p):
    '''
    param_exp : mult_exp n_parameter_action
              | mult_exp n_parameter_action COMMA param_exp
    '''

#Funcion para generar cuadruplos de parámetros.
def p_n_parameter_action(p):
    '''
    n_parameter_action :
    '''
    global pilaOp, pilaTipos, dir_func, curr_Call, read_quadruples, dir_quadruples, parameter_counter
    argument = pilaOp.pop()
    argumentType = pilaTipos.pop()
    if dir_func[curr_Call]['params'][parameter_counter] == argumentType:
        parameter = 'par' + str(parameter_counter+1)
        temp_quad = ['PARAM', argument.id, -1, parameter]
        read_quadruples.append(temp_quad)

        #obteniendo la direccion del parametro
        Address_param = getParamAddress(parameter_counter, argumentType)

        temp_quad = ['PARAM', argument.address, -1, Address_param]
        dir_quadruples.append(temp_quad)
        parameter_counter += 1
    else:
        error(p, "El parametro "+ str(parameter_counter+1) + " de la funcion es incorrecto");

#Manejo de memoria de los parámetros.
def getParamAddress(counter, type):
    global current_func
    tempBase = 0
    if type == 'int':
        tempBase = 0;
    elif type == 'float':
        tempBase = 2500;
    else:
        tempBase = 5000;
    return counter + tempBase + DIR_BASE_LOCAL


#Conjunto de funciones para  llamada a funciones.
def p_llamada(p):
  '''
  llamada : ID n_verify_func LPAREN n_start_FF n_start_pcounter param_exp RPAREN n_end_FF n_last_param_action
          | ID n_verify_func LPAREN n_start_FF n_start_pcounter RPAREN n_end_FF n_last_param_action
  '''

#Ultimo punto neurálgico que revisa consistencia entre numero de parámetros y parámetros declarados.
#Empuja a la pila de operandos el resultado de la llamada  como cualquier otra expresion.
def p_n_last_param_action(p):
    '''
    n_last_param_action :
    '''
    global dir_func, read_quadruples, dir_quadruples, pilaOp, currTemp, current_type, parameter_counter, address_func_var_global
    if(parameter_counter < len(dir_func[curr_Call]['params'])):
        error(p, 'Se declararon menos parámetros de los requeridos por la función')
    else:
        temp_quad = ['GOSUB', curr_Call, -1, dir_func[curr_Call]['starts']]
        read_quadruples.append(temp_quad)
        #add call address
        dir_quadruples.append(temp_quad)

        if(dir_func[curr_Call]['type'] != 'void'):
            address_func_var_global = dir_func['global']['vars'][curr_Call]['address']
            dir_quadruples.pop()
            temp_quad = ['GOSUB', address_func_var_global, -1, dir_func[curr_Call]['starts']]
            dir_quadruples.append(temp_quad)
            temp_op = Operando()
            pilaTipos.push(dir_func['global']['vars'][curr_Call]['type'])
            temporal = 't' + str(currTemp)
            currTemp +=1;
            temp_op.id = temporal
            current_type = dir_func[curr_Call]['type']
            temp_op.address = get_next_var_address(p)
            temp_quad = ['=', curr_Call, -1, temp_op.id]
            read_quadruples.append(temp_quad)
            temp_quad = ['=', address_func_var_global, -1, temp_op.address]

            dir_quadruples.append(temp_quad)
            pilaOp.push(temp_op)

#Funcion para contar el número de parámetros.
def p_n_start_pcounter(p):
    '''
    n_start_pcounter :
    '''
    global dir_func, parameter_counter, read_quadruples, dir_quadruples, curr_Call, address_func_var_global
    parameter_counter = 0
    temp_quad = ['ERA', curr_Call, -1, -1];
    read_quadruples.append(temp_quad)
    #if(dir_func[curr_Call]['type'] != 'void'):
    #    address_func_var_global = dir_func['global']['vars'][curr_Call]['address']
        #temp_quad = ['ERA', address_func_var_global, -1, -1];
    dir_quadruples.append(temp_quad)

#Verifica que la función exista.
def p_n_verify_func(p):
    '''
    n_verify_func :
    '''
    global dir_func, curr_Call
    if(p[-1] not in dir_func):
        error(p, 'La función que se está llamando no existe')
    else:
        curr_Call = p[-1]

#Genera cuadruplo de lectura para el usuario.
def p_lee(p):
  '''
  lee : LEE LPAREN variable RPAREN SEMICOLON
  '''
  global dir_func, dir_quadruples, read_quadruples, pilaOp
  elemento = pilaOp.pop()

  temp_quad = ['read', -1, -1, elemento.id]
  read_quadruples.append(temp_quad)
  temp_quad = ['read', -1, -1, elemento.address]
  dir_quadruples.append(temp_quad)

#Conjunto de funciones para generación del cuadruplo escribe.
def p_escribe(p):
  '''
  escribe : ESCRIBE LPAREN mult_exp n_escribeExp RPAREN SEMICOLON
  		  | ESCRIBE LPAREN mult_cte_s n_escribeExp RPAREN SEMICOLON
  '''

def p_n_escribeExp(p):
    '''
    n_escribeExp :
    '''
    global dir_func, read_quadruples, current_exp, pilaOp, dir_quadruples
    operando = pilaOp.pop();
    currQuad = ['print', -1, -1, operando.id]
    read_quadruples.append(currQuad)
    currQuad = ['print', -1, -1, operando.address]
    dir_quadruples.append(currQuad)

#Conjunto de expresiones para expresiones mult div exp llamadas etc.
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
#Genera cuadruplo y maneja pilas para operaciones de OR
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
#Genera cuadruplo y maneja pilas para operaciones de AND
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

#Genera cuadruplo y maneja pilas para operaciones de comparativos
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
#Genera cuadruplo y maneja pilas para operaciones de suma y resta
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

#Genera cuadruplo y maneja pilas para operaciones de multiplicacion y division
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

#Nivel mas bajo de expresion con constantes, variables, llamadas a funciones y paréntesis,
def p_f(p):
  '''
  f : LPAREN n_start_FF mult_exp RPAREN n_end_FF
    | n_tempTypeI MINUS CTE_I n_directPrint_neg
    | n_tempTypeF MINUS CTE_F n_directPrint_neg
    | n_tempTypeI CTE_I n_directPrint
    | n_tempTypeF CTE_F n_directPrint
    | n_tempTypeC CTE_C n_directPrint
    | variable
    | llamada
  '''
#Funcion auxiliar para tipo de variable leida en cada caso.
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

#Funcion auxiliar  para manejo de constantes negativas y evitar error.
def p_n_directPrint_neg(p):
    '''
    n_directPrint_neg :
    '''
    global current_exp, pilaOp, pilaTipos, current_type
    current_exp = p[-1]
    operador = Operando();
    operador.id = '-' + current_exp;
    operador.address = get_next_cte_address(p, operador.id);
    pilaOp.push(operador)
    pilaTipos.push(current_type)

#Auxliar  para constantes a expresiones y que se puedan usar en operaciones.
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

#Inicio y termino del fondo falso usado en operaciones y arreglos.
def p_n_start_FF(p):
    '''
    n_start_FF :
    '''
    global popper, pilaOp, pilaTipos
    popper.push(p[-1])

def p_n_end_FF(p):
    '''
    n_end_FF :
    '''
    global popper, pilaOp, pilaTipos
    aux = popper.peek();
    if aux == '(' or aux == '[':
        popper.pop();
    else:
        error(p, "Error de paréntesis inconsistentes")

#Conjunto de funciones para manejo de If y ELSE
def p_condicion(p):
  '''
  condicion : SI LPAREN mult_exp RPAREN n_ifQuad ENTONCES bloque n_endIfQuad
            | SI LPAREN mult_exp RPAREN n_ifQuad ENTONCES bloque SINO p_n_sinoQuad bloque n_endIfQuad
  '''

#Genera cuadruplo de gotoFalse
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

#Vacia pila de saltos y rellena espacios dejados vacios para manejo de saltos.
def p_n_endIfQuad(p):
    '''
    n_endIfQuad :
    '''
    global pilaSaltos, read_quadruples, dir_quadruples
    end = pilaSaltos.pop()
    read_quadruples[end][3] = len(read_quadruples)
    dir_quadruples[end][3] = len(dir_quadruples)

#Cuadruplo que maneja el else de la condicion.
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

#conjunto de funciones que manejan el ciclo while.
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

#Maneja especificamente el generar el cuadruplo gotoFalse.
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

#Termina el while, genera cuadruplo Goto y rellena cuadruplos de manejo de saltos.
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

#Genera operacion del ciclo for. similar a la operacion anterior.
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

#Termina el cilo for.
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

#Conjunto de funciones que manejan el return de una función.
def p_retorno(p):
  '''
  retorno : REGRESA LPAREN mult_exp n_regresaExp RPAREN SEMICOLON
  '''

#Revisa que se este regresando el mismo tipo que la definición de la función y regresa memoria.
def p_n_regresaExp(p):
    '''
    n_regresaExp :
    '''
    global dir_func, read_quadruples, current_exp, current_type, current_func, dir_quadruples, pilaTipos
    operando = pilaOp.pop();
    if(pilaTipos.pop() == dir_func[current_func]['type']):
      temp_quad = ['RETURN', -1, -1, operando.id]
      read_quadruples.append(temp_quad)
      temp_quad = ['RETURN', -1, -1, operando.address]
      dir_quadruples.append(temp_quad)
    else:
      error(p, "La función está regresando un tipo distinto al de la función")


##error function for parser
def p_error(p):
    global success
    success = False
    print('SyntaxError', p.value)
    print("at line ", p.lineno)
    #añadir en que linea
    sys.exit()

    #p.lexer.skip(1)

    # TODO:¨parar la compilación

def error(p, message):
    print("Error: ", message)
    sys.exit()


parser = yacc.yacc()

# nombre archivo, nombre programa
if len(sys.argv) != 2:
    print('Please send a file.')
    raise SyntaxError('Compiler needs 1 file.')

program_name = sys.argv[1]
# Compile program.
with open(program_name, 'r') as file:
    try:
        parser.parse(file.read())
        export = {
            'tabla_func': dir_func,
            'dir_quadruples': dir_quadruples
        }
        with open(program_name + '.obj', 'w') as file1:
            file1.write(str(export))
    except:
        pass

if success == True:
    print("El archivo se ha aceptado")
    sys.exit()
else:
    print("El archivo tiene errores")
    sys.exit()
