
"""
Atividade 05 - Analisador Sintático e Interpretador para a Linguagem EC1

Este script implementa um analisador léxico e sintático completo.
Ele lê um arquivo-fonte, gera uma Árvore de Sintaxe Abstrata (AST),
imprime uma REPRESENTAÇÃO VISUAL da árvore e, por fim, interpreta-a
para calcular o resultado da expressão.

Uso na linha de comando:
python EC1.py <caminho_para_o_arquivo.ec1>
"""

import sys


# ANALISADOR LÉXICO
class Token:
    def __init__(self, tipo, lexema, posicao):
        self.tipo = tipo
        self.lexema = lexema
        self.posicao = posicao
    def __repr__(self):
        return f"<{self.tipo}, '{self.lexema}', {self.posicao}>"

def analisador_lexico_ec1(codigo_fonte):
    tokens = []
    posicao_atual = 0
    tamanho_codigo = len(codigo_fonte)
    while posicao_atual < tamanho_codigo:
        caractere_atual = codigo_fonte[posicao_atual]
        if caractere_atual.isspace():
            posicao_atual += 1
            continue
        mapa_tokens = {'(': 'ParenEsq', ')': 'ParenDir', '+': 'Soma', '-': 'Sub', '*': 'Mult', '/': 'Div'}
        if caractere_atual in mapa_tokens:
            tokens.append(Token(mapa_tokens[caractere_atual], caractere_atual, posicao_atual))
            posicao_atual += 1
        elif caractere_atual.isdigit():
            lexema = ''
            pos_inicial = posicao_atual
            while posicao_atual < tamanho_codigo and codigo_fonte[posicao_atual].isdigit():
                lexema += codigo_fonte[posicao_atual]
                posicao_atual += 1
            tokens.append(Token('Numero', lexema, pos_inicial))
        else:
            return None, f"Erro léxico na posição {posicao_atual}: caractere inesperado '{caractere_atual}'"
    tokens.append(Token('EOF', '', posicao_atual))
    return tokens, None


class Exp:
    pass

class Const(Exp):
    def __init__(self, token):
        self.token = token
        self.valor = int(token.lexema)
    def interpretar(self):
        return self.valor
    def __repr__(self):
        return f"Const({self.valor})"

class OpBin(Exp):
    def __init__(self, op_esq, operador, op_dir):
        self.op_esq = op_esq
        self.operador = operador
        self.op_dir = op_dir
    def interpretar(self):
        val_esq = self.op_esq.interpretar()
        val_dir = self.op_dir.interpretar()
        op = self.operador.lexema
        if op == '+': return val_esq + val_dir
        elif op == '-': return val_esq - val_dir
        elif op == '*': return val_esq * val_dir
        elif op == '/':
            if val_dir == 0: raise ValueError("Erro de execução: Divisão por zero.")
            return int(val_esq / val_dir)
    def __repr__(self):
        return f"OpBin(esq={repr(self.op_esq)}, op='{self.operador.lexema}', dir={repr(self.op_dir)})"

# ANALISADOR SINTÁTICO 
class AnalisadorSintatico:
    def __init__(self, tokens):
        self.tokens = tokens; self.posicao = 0; self.token_atual = self.tokens[self.posicao]
    def _avancar(self):
        self.posicao += 1
        if self.posicao < len(self.tokens): self.token_atual = self.tokens[self.posicao]
    def _consumir(self, tipo_esperado):
        if self.token_atual.tipo == tipo_esperado: self._avancar()
        else: raise SyntaxError(f"Erro de sintaxe na posição {self.token_atual.posicao}: Esperado '{tipo_esperado}', mas encontrou '{self.token_atual.tipo}'.")
    def analisar(self):
        arvore = self._analisa_expressao()
        if self.token_atual.tipo != 'EOF': raise SyntaxError(f"Erro de sintaxe na posição {self.token_atual.posicao}: Caractere inesperado '{self.token_atual.lexema}' após o fim da expressão.")
        return arvore
    def _analisa_expressao(self):
        token = self.token_atual
        if token.tipo == 'Numero': self._avancar(); return Const(token)
        elif token.tipo == 'ParenEsq':
            self._consumir('ParenEsq')
            op_esq = self._analisa_expressao()
            operador = self.token_atual
            if operador.tipo not in ['Soma', 'Sub', 'Mult', 'Div']: raise SyntaxError(f"Erro de sintaxe na posição {operador.posicao}: Operador inválido '{operador.lexema}'.")
            self._avancar()
            op_dir = self._analisa_expressao()
            self._consumir('ParenDir')
            return OpBin(op_esq, operador, op_dir)
        else: raise SyntaxError(f"Erro de sintaxe na posição {token.posicao}: Expressão inválida. Esperado número ou '(', mas encontrou '{token.tipo}'.")


# IMPRESSÃO VISUAL DA ÁRVORE
def _imprimir_ast_recursivo(no, prefixo, eh_ultimo):
    """Função auxiliar recursiva para imprimir a árvore."""
    # Imprime o prefixo atual para o nó.
    print(prefixo, end="")

    # Usa caracteres especiais para desenhar os "galhos" da árvore.
    # '└──' para o último filho, '├──' para os demais.
    print("└── " if eh_ultimo else "├── ", end="")

    # Imprime a informação do nó atual.
    if isinstance(no, OpBin):
        print(f"Operador: {no.operador.lexema}")
        # Prepara o prefixo para os nós filhos.
        novo_prefixo = prefixo + ("    " if eh_ultimo else "│   ")
        # Chama recursivamente para os filhos.
        _imprimir_ast_recursivo(no.op_esq, novo_prefixo, False)
        _imprimir_ast_recursivo(no.op_dir, novo_prefixo, True)
    elif isinstance(no, Const):
        print(f"Constante: {no.valor}")

def imprimir_ast(raiz):
    """Função principal para iniciar a impressão da árvore a partir da raiz."""
    print("Visualização da Árvore Sintática (AST):")
    if raiz is not None:
        _imprimir_ast_recursivo(raiz, "", True)



# ==================
# EXECUÇÃO PRINCIPAL 
# ==================
def main():
    if len(sys.argv) != 2:
        print("Uso: python EC1.py <caminho_para_o_arquivo.ec1>")
        sys.exit(1)

    caminho_arquivo = sys.argv[1]
    print(f"--- Processando o arquivo: {caminho_arquivo} ---")

    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as arquivo:
            codigo_fonte = arquivo.read()
            if not codigo_fonte.strip():
                print("Aviso: O arquivo está vazio.")
                return
            
            # Fases 1 e 2: Análise Léxica e Sintática
            tokens, erro_lexico = analisador_lexico_ec1(codigo_fonte)
            if erro_lexico:
                print(erro_lexico)
                return
            
            parser = AnalisadorSintatico(tokens)
            ast_raiz = parser.analisar()
            print("Análise sintática concluída com sucesso.")

            # Fase 3: Impressão Visual da Árvore
            imprimir_ast(ast_raiz)

            # Fase 4: Interpretação
            resultado = ast_raiz.interpretar()
            print(f"\nResultado da interpretação: {resultado}")

    except FileNotFoundError:
        print(f"Erro: O arquivo '{caminho_arquivo}' não foi encontrado.")
    except (SyntaxError, ValueError) as e:
        print(e)
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")
    finally:
        print("--- Fim do processamento ---\n")

if __name__ == "__main__":
    main()