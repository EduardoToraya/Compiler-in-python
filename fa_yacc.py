import ply.yacc as yacc
import sys
from fa_lex import tokens
from semantic_cube import semantic_cube

current_type = ''
current_func = 'global'
dir_func = {
    'global': {
        'vars': {},
        'params':{}
    }
}
# dir typo

quadruples = []
#4 elemtos
currQuad = []

popper = []


success = True

## gramatic rules
def p_programa(p):
    '''
    programa : PROGRAMA ID SEMICOLON vars funcion principal
            | PROGRAMA ID SEMICOLON funcion principal
            | PROGRAMA ID SEMICOLON vars principal
            | PROGRAMA ID SEMICOLON principal
    '''
    print(dir_func)


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
    variable : ID LSQUARE exp RSQUARE
             | ID
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
            'vars': {}
        }

def p_param(p):
  '''
  param : tipo_simple param_aux1
        | tipo_simple param_aux1 param
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
        error('p', "Parametro ya declarado")
    else:
        id  = p[-1]
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
  estatuto : asigna
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
  asigna : variable EQUAL exp SEMICOLON
  '''

def p_llamada(p):
  '''
  llamada : ID LPAREN mult_exp RPAREN
  '''

def p_mult_exp(p):
  '''
  mult_exp : exp
  		   | exp COMMA mult_exp
           | empty
  '''

def p_lee(p):
  '''
  lee : LEE LPAREN variable RPAREN
  '''

def p_escribe(p):
  '''
  escribe : ESCRIBE LPAREN mult_exp RPAREN SEMICOLON
  		  | LPAREN mult_cte_s RPAREN SEMICOLON
  '''

def p_mult_cte_s(p):
  '''
  mult_cte_s : CTE_S
  		     | CTE_S COMMA mult_cte_s
             | empty
  '''

############################### TORAYA

def p_exp(p):
  '''
  exp : t_exp OR exp
  	  | t_exp
  '''

def p_t_exp(p):
  '''
  t_exp : g_exp AND t_exp
  	    | g_exp
  '''

def p_g_exp(p):
  '''
  g_exp : m_exp
  		| LESSTHAN m_exp
        | LESSEQUAL m_exp
        | GREATERTHAN m_exp
        | GREATEREQUAL m_exp
        | SAME m_exp
        | NOEQUAL m_exp
  '''

def p_m_exp(p):
  '''
  m_exp : t
  	    | t PLUS m_exp
        | t MINUS m_exp
  '''

def p_t(p):
  '''
  	t : f
      | f MULT t
      | f DIV t
  '''

def p_f(p):
  '''
  f : LPAREN exp RPAREN
  	| CTE_I
    | CTE_F
    | CTE_C
    | variable
    | llamada
  '''

def p_condicion(p):
  '''
  condicion : SI LPAREN exp RPAREN ENTONCES bloque SINO bloque SEMICOLON
  		    | SI LPAREN exp RPAREN ENTONCES bloque SEMICOLON
  '''

def p_ciclo_w(p):
  '''
  ciclo_w : MIENTRAS LPAREN exp RPAREN HAZ bloque
  '''


def p_ciclo_f(p):
  '''
  ciclo_f : DESDE asigna HASTA CTE_I HACER bloque
  '''

def p_var_cte(p):
	'''
  var_cte : exp
  	      | CTE_I
          | CTE_F
  '''

def p_retorno(p):
  '''
  retorno : REGRESA exp SEMICOLON
  '''


############################### FIN TORAYA


##error function for parser
def p_error(p):
    global success
    success = False
    p.lexer.skip(1)
    raise SyntaxError
    # TODO:¨parar la compilación

def error(p, message):
    print("Error: ", message)
    p_error(p)


parser = yacc.yacc()

data = "testFile.txt"
f = open(data,'r')
s = f.read()

parser.parse(s)

if success == True:
    print("El archivo se ha aceptado")
    sys.exit()
else:
    print("El archivo tiene errores")
    sys.exit()
