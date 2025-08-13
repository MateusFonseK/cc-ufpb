
"""
Atividade 04 - Analisador Léxico para a Linguagem EC1

Este script implementa um analisador léxico completo para a linguagem
Expressões Constantes 1 (EC1), conforme especificado no documento da atividade.
Ele transforma um código-fonte em EC1 em uma lista de tokens.

Uso na linha de comando:
python EC1.py <caminho_para_o_arquivo.ec1>
"""

import sys

# DEFINIÇÃO DA ESTRUTURA DE DADOS DO TOKEN
# Conforme a seção 3.1 do documento, cada token precisa de um tipo,
# um lexema e sua posição. Usamos uma classe simples para organizar esses dados.
class Token:
    def __init__(self, tipo, lexema, posicao):
        self.tipo = tipo
        self.lexema = lexema
        self.posicao = posicao

    # A representação em string segue o formato <tipo, lexema, posicao>
    # solicitado no exemplo da seção 3.2 do documento.
    def __repr__(self):
        return f"<{self.tipo}, '{self.lexema}', {self.posicao}>"

# IMPLEMENTAÇÃO DO ANALISADOR LÉXICO
# Esta é a função principal que realiza a análise. Ela percorre a entrada caractere por caractere para construir a lista de tokens.
def analisador_lexico_ec1(codigo_fonte):
    tokens = []
    posicao_atual = 0
    tamanho_codigo = len(codigo_fonte)

    # O laço percorre toda a string de entrada.
    while posicao_atual < tamanho_codigo:
        caractere_atual = codigo_fonte[posicao_atual]

        # Ignorar espaços em branco (conforme requisito da seção 4).
        # Eles não geram tokens, apenas avançam a posição.
        if caractere_atual.isspace():
            posicao_atual += 1
            continue

        # Reconhecer operadores e pontuação (tokens de um único caractere).
        # A seção 3.1 sugere tipos específicos para cada operador e pontuação.
        if caractere_atual == '(':
            tokens.append(Token('ParenEsq', '(', posicao_atual))
            posicao_atual += 1
        elif caractere_atual == ')':
            tokens.append(Token('ParenDir', ')', posicao_atual))
            posicao_atual += 1
        elif caractere_atual == '+':
            tokens.append(Token('Soma', '+', posicao_atual))
            posicao_atual += 1
        elif caractere_atual == '-':
            tokens.append(Token('Sub', '-', posicao_atual))
            posicao_atual += 1
        elif caractere_atual == '*':
            tokens.append(Token('Mult', '*', posicao_atual))
            posicao_atual += 1
        elif caractere_atual == '/':
            tokens.append(Token('Div', '/', posicao_atual))
            posicao_atual += 1

        # Reconhecer literais inteiros (números).
        # Um número é uma sequência de um ou more dígitos (seção 1).
        # A análise léxica agrupa esses dígitos em um único token 'Numero'.
        elif caractere_atual.isdigit():
            lexema = ''
            posicao_inicial_numero = posicao_atual
            # Continua lendo enquanto encontrar dígitos.
            while posicao_atual < tamanho_codigo and codigo_fonte[posicao_atual].isdigit():
                lexema += codigo_fonte[posicao_atual]
                posicao_atual += 1
            tokens.append(Token('Numero', lexema, posicao_inicial_numero))

        # Tratamento de Erros Léxicos.
        # Se o caractere não for um espaço, operador, parêntese ou dígito,
        # ele é inválido na linguagem EC1.
        else:
            print(f"Erro léxico na posição {posicao_atual}: caractere inesperado '{caractere_atual}'")
            # Interrompe a análise ao encontrar o primeiro erro.
            return []

    return tokens



# ==================
# EXECUÇÃO PRINCIPAL 
# ==================
def processar_arquivo(caminho_arquivo):
    """
    Lê o conteúdo de um arquivo e passa para o analisador léxico.
    """
    try:
        # Abre o arquivo em modo de leitura ('r') com codificação UTF-8
        with open(caminho_arquivo, 'r', encoding='utf-8') as arquivo:
            print(f"--- Analisando o arquivo: {caminho_arquivo} ---")
            codigo_fonte = arquivo.read()
            
            if not codigo_fonte.strip():
                print("Aviso: O arquivo está vazio.")
                return

            print(f"Entrada: '{codigo_fonte.strip()}'")
            
            # Chama o analisador léxico
            resultado_tokens = analisador_lexico_ec1(codigo_fonte)
            
            # Imprime o resultado da análise
            if resultado_tokens is not None:
                print("Saída (Tokens):")
                for token in resultado_tokens:
                    print(f"  {token}")
            else:
                print("Análise falhou devido a um erro léxico.")

    except FileNotFoundError:
        print(f"Erro: O arquivo '{caminho_arquivo}' não foi encontrado.")
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")
    finally:
        print("--- Análise concluída ---\n")


# Ponto de entrada principal do script
if __name__ == "__main__":
    # Verifica se o nome do arquivo foi passado como argumento
    if len(sys.argv) != 2:
        print("Uso: python analisador.py <caminho_para_o_arquivo.ec1>")
        # Encerra o script se o uso for incorreto
        sys.exit(1)

    # O primeiro argumento (índice 1) é o nome do arquivo
    arquivo_para_analisar = sys.argv[1]
    processar_arquivo(arquivo_para_analisar)