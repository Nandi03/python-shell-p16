grammar Shell;

// parser
line            : command | EOF ;

command         : pipe | command ';' command | call;

pipe            : call '|' call
                | pipe '|' call ;



call            : ( SPACE | LINE_BREAKS)? ( redirection ( SPACE | LINE_BREAKS) )* argument ( ( SPACE | LINE_BREAKS) atom )* ( SPACE | LINE_BREAKS)? ;

atom            : redirection | argument ;

argument        : ( quoted | unquoted )+ ;

redirection     : '<' SPACE? argument
                | '>'?'>' SPACE? argument
                ;




unquoted        :  BASIC_TEXT ;

quoted          : single_quoted
                | double_quoted
                | backquoted
                ;

single_quoted   : '\'' ( BASIC_TEXT | ';' | '|' | '<' | '>' | '"' | '`' | SPACE)* '\''  ;

backquoted      : BASIC_TEXT* '`' ( BASIC_TEXT | ';' | '|' | '<' | '>' | '"' | '\'' | SPACE  )* '`' BASIC_TEXT* ;

double_quoted   : BASIC_TEXT* '"' ( backquoted | BASIC_TEXT | ';' | '|' | '<' | '>' | '\'' | SPACE) * '"' BASIC_TEXT*;


// lexer

SPACE           : [ \t]+ ;

BASIC_TEXT      : ~[ \r\n\t"'`;|<>]+ ;
LINE_BREAKS     :  [\r\n]+ ;