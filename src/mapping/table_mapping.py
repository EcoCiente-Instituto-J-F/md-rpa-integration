
TABLE_MAPPING = {


"usuario":{

"destination":
"tb_usuarios",

"columns":{

"id_usuario":
"id_usuario",

"nome":
"nome",

"email":
"email",

"senha_hash":
"senha_hash"

}

},



"endereco":{

"destination":
"tb_enderecos",

"columns":{

"id_endereco":
"id_endereco",

"cidade":
"cidade",

"estado":
"estado",

"bairro":
"bairro"

}

}

}



TABLE_ORDER=[

"tipo_usuario",

"endereco",

"usuario",

"cooperativa",

"condominio",

"torre",

"morador",

"material",

"postagem",

"quiz",

"pontuacao"

]