import ply.yacc as yacc
import sys

success = True

from fa_lex import tokens

## gramatic rules
def p_programa(p):
    '''
    programa : PROGRAMA ID SEMICOLON vars funcion principal
            | PROGRAMA ID SEMICOLON funcion principal
            | PROGRAMA ID SEMICOLON vars principal
            | PROGRAMA ID SEMICOLON principal
    '''


def p_principal(p):
    '''
    principal : PRINCIPAL LPAREN RPAREN bloque
    '''


# variable declaration
def p_vars(p):
  '''
  vars : VAR vars_aux
  '''
  p[0] = 'popo'

  ## seccion de vars para definir varios varios tipos de  id con o sin  brackets
def p_vars_aux(p):
  '''
  vars_aux : tipo_simple vars_aux1
  		   | tipo_simple vars_aux1 vars_aux
  '''

  ##seccion de vars para ciclo de varias id con brackets
def p_vars_aux1(p):
  '''
  vars_aux1 : vars_aux2 SEMICOLON
  		    | vars_aux2 COMMA vars_aux1
  '''

## seccion de vars para id con brackets
def p_vars_aux2(p):
  '''
    vars_aux2 : ID SEMICOLON
    		  | ID LSQUARE CTE_I RSQUARE SEMICOLON
  '''

def p_tipo_simple(p):
    '''
    tipo_simple : INT
                | FLOAT
                | CHAR
    '''

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
  funcion : FUNCION tipo_simple ID LPAREN param RPAREN vars SEMICOLON bloque
  		  | FUNCION tipo_simple ID LPAREN param RPAREN SEMICOLON bloque
  		  | FUNCION VOID ID LPAREN param RPAREN vars SEMICOLON bloque
          | FUNCION VOID ID LPAREN param RPAREN SEMICOLON bloque
  '''

def p_param(p):
  '''
  param : ID
  		| ID COMMA param
        | empty
  '''


def p_bloque(p):
  '''
  bloque : LBRACKET mult_estatutos RBRACKET
  '''

def p_mult_estatutos(p):
  '''
  mult_estatutos : estatuto
  				 | estatuto mult_estatutos
                 | empty
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
        | EQUAL m_exp
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
      | f DETER t
      | f TRANS t
      | f INVER t
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
    print("Error de sintaxis en '%s'" % p.value[0])
    p.lexer.skip(1)


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
