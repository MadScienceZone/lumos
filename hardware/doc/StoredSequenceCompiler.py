#
# vi:set ts=4 sw=4 expandtab sm nu:
#
import sys
import ply.lex as lex
import ply.yacc as yacc

class SequenceError (Exception): pass

tokens = ('COMMENT', 'INTEGER', 'IDENTIFIER', 'NEWLINE')
literals = '+-*'

t_ignore_COMMENT = r'//.*'

def t_INTEGER(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_IDENTIFIER(t):
    r'[a-zA-Z]\w*'
    t.value = t.value.lower()
    t.type='IDENTIFIER'
    return t

def t_NEWLINE(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    raise SequenceError("Unrecognized symbol ('{0}') on line {1}".format(t.value[0],t.lexer.lineno))

def p_sequence_statement(p):
    "sequence : statement"
    p[0] = 
    print "SEQUENCE:", p[1]

def p_sequence_list(p):
    "sequence : sequence statement"
    print "SEQUENCE:", p[1], p[2]

def p_simple_command(p):
    ''' statement : expression '''
    print "STATEMENT:", p[1]

def p_expression_term(p):
    "expression : term"
    print "EXPR:", p[1]

def p_expression_binary(p):
    ''' expression : expression '+' term
                   | expression '-' term
                   | expression '*' term '''
    print "EXPRESSION:", p[1], p[2], p[3]

def p_term(p):
    ''' term : IDENTIFIER
             | INTEGER '''
    print "TERM:", p[1]


def p_error(p):
    raise SequenceError("Syntax error")

if __name__ == "__main__":
    #lex.runmain()
    #yylex = lex.lex()
    #yylex.input(sys.stdin.read())
    #print "INPUT TOKENS:"
    #for tok in yylex:
    #    print tok
    yylex = lex.lex()
    yyparse = yacc.yacc()
    print "RESULT:", yyparse.parse(sys.stdin.read())
