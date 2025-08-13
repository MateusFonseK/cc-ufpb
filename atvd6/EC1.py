
"""
Atividade 06 - Compilador Completo para a Linguagem EC1

Este script implementa um compilador completo para a linguagem
Expressões Constantes 1 (EC1). Ele realiza as seguintes etapas:
1. Análise Léxica: Transforma o código-fonte em tokens.
2. Análise Sintática: Constrói uma Árvore de Sintaxe Abstrata (AST).
3. Geração de Código: Percorre a AST para gerar código assembly x86-64.
4. Saída: Salva o código assembly completo em um arquivo .s.

Uso na linha de comando:
python compilador.py <caminho_para_o_arquivo.ec1>
"""

import sys
import os


# ANALISADOR LÉXICO 
class Token:
    def __init__(self, tipo, lexema, posicao):
        self.tipo = tipo; self.lexema = lexema; self.posicao = posicao
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
            lexema = ''; pos_inicial = posicao_atual
            while posicao_atual < tamanho_codigo and codigo_fonte[posicao_atual].isdigit():
                lexema += codigo_fonte[posicao_atual]
                posicao_atual += 1
            tokens.append(Token('Numero', lexema, pos_inicial))
        else:
            return None, f"Erro léxico na posição {posicao_atual}: caractere inesperado '{caractere_atual}'"
    tokens.append(Token('EOF', '', posicao_atual))
    return tokens, None


# AST E ANÁLISE SINTÁTICA 
class Exp:
    """Classe base para nós da AST."""
    pass

class Const(Exp):
    """Nó para constantes numéricas."""
    def __init__(self, token):
        self.valor = int(token.lexema)

    def compilar(self):
        """Compila uma constante: move o valor para o registrador RAX. [cite: 31]"""
        return [f"  mov ${self.valor}, %rax"]

class OpBin(Exp):
    """Nó para operações binárias."""
    def __init__(self, op_esq, operador, op_dir):
        self.op_esq = op_esq
        self.operador = operador
        self.op_dir = op_dir

    def compilar(self):
        """Compila uma operação binária usando o esquema da pilha. [cite: 101, 128]"""
        
        # 1. Gera código para o operando ESQUERDO. 
        codigo_esq = self.op_esq.compilar()
        
        # 2. Salva o resultado do operando direito (em RAX) na pilha. 
        salvar_dir = ["  push %rax"]
        
        # 3. Gera código para o operando DIREITO. 
        codigo_dir = self.op_dir.compilar()
        
        # 4. Recupera o resultado direito da pilha para RBX. 
        recuperar_dir = ["  pop %rbx"]
        
        # 5. Executa a operação aritmética. 
        op = self.operador.lexema
        if op == '+':
            operacao = ["  add %rbx, %rax"]
        elif op == '-':
            # Ordem correta: RAX = RAX - RBX
            operacao = ["  sub %rbx, %rax"]
        elif op == '*':
            # Ordem correta: RAX = RAX * RBX
            operacao = ["  imul %rbx, %rax"]
        elif op == '/':
            # Para divisão, o dividendo está em RAX. O divisor foi para RBX.
            # `idiv rbx` divide RDX:RAX por rbx.
            # `cqo` estende o sinal de RAX para RDX.
            operacao = ["  cqo", "  idiv %rbx"]
        
        # Concatena todas as partes na ordem correta
        return codigo_esq + salvar_dir + codigo_dir + recuperar_dir + operacao

# Analisador Sintático (sem alterações na lógica, apenas no nome da classe para clareza)
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens; self.posicao = 0; self.token_atual = self.tokens[self.posicao]
    def _avancar(self):
        self.posicao += 1
        if self.posicao < len(self.tokens): self.token_atual = self.tokens[self.posicao]
    def _consumir(self, tipo_esperado):
        if self.token_atual.tipo == tipo_esperado: self._avancar()
        else: raise SyntaxError(f"Erro de sintaxe na posição {self.token_atual.posicao}: Esperado '{tipo_esperado}', mas encontrou '{self.token_atual.tipo}'.")
    def parse(self):
        arvore = self._parse_expressao()
        if self.token_atual.tipo != 'EOF': raise SyntaxError(f"Erro de sintaxe na posição {self.token_atual.posicao}: Caractere inesperado '{self.token_atual.lexema}' após o fim da expressão.")
        return arvore
    def _parse_expressao(self):
        token = self.token_atual
        if token.tipo == 'Numero': self._avancar(); return Const(token)
        elif token.tipo == 'ParenEsq':
            self._consumir('ParenEsq')
            op_esq = self._parse_expressao()
            operador = self.token_atual
            if operador.tipo not in ['Soma', 'Sub', 'Mult', 'Div']: raise SyntaxError(f"Erro de sintaxe na posição {operador.posicao}: Operador inválido '{operador.lexema}'.")
            self._avancar()
            op_dir = self._parse_expressao()
            self._consumir('ParenDir')
            return OpBin(op_esq, operador, op_dir)
        else: raise SyntaxError(f"Erro de sintaxe na posição {token.posicao}: Expressão inválida. Esperado número ou '(', mas encontrou '{token.tipo}'.")



# MONTAGEM DO ARQUIVO ASSEMBLY 
def gerar_arquivo_assembly(codigo_expressao, nome_arquivo_saida):
    """Insere o código da expressão no modelo e salva em um arquivo."""
    
    # Junta a lista de instruções em uma única string com quebras de linha.
    codigo_final_expressao = "\n".join(codigo_expressao)
    
    # Modelo completo para o arquivo assembly. 
    template_assembly = f"""
.section .text
.globl _start

_start:
{codigo_final_expressao}

  # Chama as sub-rotinas do runtime para imprimir e sair. 
  call imprime_num
  call sair

# Inclui o arquivo com as sub-rotinas.
.include "runtime.s"
"""
    
    try:
        with open(nome_arquivo_saida, 'w', encoding='utf-8') as f:
            f.write(template_assembly)
        print(f"Assembly gerado com sucesso em '{nome_arquivo_saida}'.")
    except IOError as e:
        print(f"Erro ao escrever no arquivo de saída: {e}")



# ==================
# EXECUÇÃO PRINCIPAL 
# ==================
def main():
    if len(sys.argv) != 2:
        print("Uso: python compilador.py <caminho_para_o_arquivo.ec1>")
        sys.exit(1)

    caminho_arquivo_entrada = sys.argv[1]
    
    # Define o nome do arquivo de saída (ex: teste.ec1 -> teste.s)
    base_name = os.path.splitext(os.path.basename(caminho_arquivo_entrada))[0]
    caminho_arquivo_saida = f"{base_name}.s"

    print(f"--- Compilando o arquivo: {caminho_arquivo_entrada} ---")

    try:
        with open(caminho_arquivo_entrada, 'r', encoding='utf-8') as arquivo:
            codigo_fonte = arquivo.read()
            if not codigo_fonte.strip():
                print("Aviso: O arquivo de entrada está vazio.")
                return
        
        # 1. Análise Léxica
        tokens, erro_lexico = analisador_lexico_ec1(codigo_fonte)
        if erro_lexico:
            print(erro_lexico)
            return

        # 2. Análise Sintática (Parsing)
        parser = Parser(tokens)
        ast_raiz = parser.parse()
        print("Análise léxica e sintática concluídas com sucesso.")

        # 3. Geração de Código
        codigo_expressao = ast_raiz.compilar()
        print("Geração de código assembly concluída.")

        # 4. Escrita do Arquivo Final
        gerar_arquivo_assembly(codigo_expressao, caminho_arquivo_saida)

    except FileNotFoundError:
        print(f"Erro: O arquivo de entrada '{caminho_arquivo_entrada}' não foi encontrado.")
    except SyntaxError as e:
        print(e)
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")
    finally:
        print("--- Fim da compilação ---\n")

if __name__ == "__main__":
    main()