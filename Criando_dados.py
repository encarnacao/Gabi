import heapq
import datetime

# import Processamento_de_dados
import random
import copy

"""Implementacao do algoritmo de Dijkstra. Para tal, precisamos de uma matriz kxk com todas as cidades"""

infinity = 9999


def alterar_prioridade(L, w, D):
    for i in range(len(D)):
        if D[i][1] == w:
            D[i] = (L[w], w)
            heapq._siftdown(D, 0, i)  # type: ignore
            return


def dados(filename):
    """Essa funcao fara um pre-processamento dos dados. Ela ira ajeita-los de acordo com o que precisamos, preenchendo as matrizes de numero de voos, horarios de partida e duracao dos voos."""

    file = open(filename, "r")
    n, m, z = file.readline().split()  # le o numero de vertices, arestas e dimensoes
    n = int(n)
    m = int(m)
    z = int(z)
    linhas = file.readlines()
    origens, destinos = (
        [],
        [],
    )  # Todas as origens e destinos possiveis de serem acessados

    duracao, voos, partidas, numero_voo = [], [], [], []
    # infinity = 99999 #Precismos desse valor grande para expressar que um dado caminho nao existe
    destino = 0  # ALTERAR PARA TESTE O INDEX DO DESTINO

    # Inicializando a matriz de duracao dos vooos :
    for k in range(z):
        matriz = []
        for i in range(n):  # Cada linha e referente a um vertice
            linha = []
            for j in range(n):  # Percorrendo as colunas
                if i == j:
                    linha.append(0)
                else:
                    linha.append(datetime.timedelta(hours=99999))
            matriz.append(linha)
        duracao.append(matriz)

    # Inicializando a matriz de voos :
    for k in range(z):  # É importante lembrar que temos uma matriz de k dimensoes
        matriz = []
        for i in range(n):  # Cada linha e referente a um vertice
            linha = []
            for j in range(n):  # Percorrendo as colunas
                if i == j:
                    linha.append(0)
                else:
                    linha.append(infinity)
            matriz.append(linha)
        voos.append(matriz)

    # Inicializando a matriz com a partida dos voos
    for k in range(z):  # É importante lembrar que temos uma matriz de k dimensoes
        matriz = []
        for i in range(n):  # Cada linha e referente a um vertice
            linha = []
            for j in range(n):  # Percorrendo as colunas
                if i == j:
                    linha.append(0)
                else:
                    linha.append(
                        datetime.datetime.strptime("01/01/1923 10:00", "%d/%m/%Y %H:%M")
                    )
            matriz.append(linha)
        partidas.append(matriz)

    # Inicializando a matriz com numeros de voos:
    for k in range(z):  # É importante lembrar que temos uma matriz de k dimensoes
        matriz = []
        for i in range(n):  # Cada linha e referente a um vertice
            linha = []
            for j in range(n):  # Percorrendo as colunas
                if i == j:
                    linha.append(0)
                else:
                    linha.append(1)
            matriz.append(linha)
        numero_voo.append(matriz)

    # ATUALIZANDO PARTIDA, DURACAO E TEMPOS
    for elemento in linhas:
        camada = int(elemento.split()[6])  # Em qual camada vamos alocar o valor
        origem = int(elemento.split()[0])
        if origem not in origens:
            origens.append(origem)  # Criando uma lista com todas as origens possiveis

        destino = int(elemento.split()[1])
        if destino not in destinos:
            destinos.append(
                destino
            )  # Criando uma lista com todos os destinos possiveis

        partida = elemento.split()[2] + " " + elemento.split()[3]
        chegada = elemento.split()[4] + " " + elemento.split()[5]
        date_partida, date_chegada = datetime.datetime.strptime(
            partida, "%d/%m/%Y %H:%M"
        ), datetime.datetime.strptime(
            chegada, "%d/%m/%Y %H:%M"
        )  # Vamos usar para armazenar a duracoa dos voos
        n_voo = elemento.split()[
            7
        ]  # Tem quer ser uma string porque alguns voos possuem letras

        partidas[camada][origem][destino] = date_partida
        voos[camada][origem][
            destino
        ] = 1  # Se entramos aqui e porque existe pelo menos um voo de i para j
        duracao[camada][origem][destino] = (
            date_chegada - date_partida
        )  # A duracao do voo e a diferenca entre a chegada e a partida
        numero_voo[camada][origem][destino] = n_voo

    return partidas, voos, duracao, n, m, z, numero_voo, origens, destinos


def vizinhos(filename, debug=False):
    """This function creates data for the Dijkstra program and the other one"""
    partidas, voos, duracao, n, m, camadas, numero_voo, origens, destinos = dados(
        filename
    )

    n_out = [
        [] for i in range(n)
    ]  # Cada no possui um conjunto de vizinhos possiveis de serem acessados. Aqui estamso criando uma variavel que e um conjunto de n listas, em que cada lista e o conjunto possivel de vizinhos de cada no. Estamos craindo um alista vazia que ainda sera alocada
    # Essa lista de vizinhos deve vir da matriz de voos

    for k in range(camadas):  # Vamos percorrer cada camada
        for i in range(n):  # Percorrendo as origens
            for j in range(n):  # Percorrendo os destinos
                if voos[k][i][j] == 1 and j not in n_out[i]:
                    n_out[i].append(j)

    return n_out, partidas, voos, duracao, n, m, camadas, numero_voo, origens, destinos


def DFS(
    n_out, origem=0, destino=6
):  # Temos que passar essas coisas por fora, pois teremos uma função recursiva
    """Essa funcao e responsavel pelo calculo das rotas possiveis da origem ao destino, sem levar em conta a viabilidade. Isso sera feito em outra funcao"""
    fila = [[origem]]
    resultados = []
    # visitados = []

    while fila:
        lista = fila.pop(0)
        if lista[-1] == destino:
            resultados.append(lista)
        else:
            for vizinho in n_out[lista[-1]]:
                if vizinho in lista:
                    continue
                if len(lista) > 4:
                    continue

                else:
                    fila.append(lista + [vizinho])

    return resultados


def posssibilidades(
    resultados, partidas, duracao, camadas, origem, destino, numero_voo, debug=False
):
    voos_possiveis, numero_voo_possivel = [], []

    for i in range(len(resultados)):
        if debug:
            print(f"Conjunto de voos {i+1}")

        possivel = True
        for j in range(len(resultados[i]) - 2):
            solution_found = False
            for k in range(
                camadas
            ):  # A busca em cada camada de partidas e duracoes de voos
                origem = resultados[i][j + 1]
                destino = resultados[i][j + 2]
                antecessor = resultados[i][j]
                chegada_em_origem = (
                    partidas[k][antecessor][origem] + duracao[k][antecessor][origem]
                )
                partida_de_origem = partidas[k][origem][destino]

                if chegada_em_origem > partida_de_origem and not solution_found:
                    if debug:
                        print(
                            f"Impossível - Voo de {antecessor} para {origem} chega em {chegada_em_origem} e o voo de {origem} para {destino} sai em {partida_de_origem}"
                        )
                    possivel = False
                else:
                    solution_found = True
                    possivel = True
                    if debug:
                        print(
                            f"Voo de {antecessor} para {origem} chega em {chegada_em_origem} e o voo de {origem} para {destino} sai em {partida_de_origem}"
                        )
                    break
            if not possivel:
                break
        if possivel:
            voos_possiveis.append(resultados[i])

        if debug:
            print()

    if voos_possiveis == []:
        print(f"Não há voos posíveis entre {resultados[0][0]} e {resultados[0][-1]}")

    else:
        for i in voos_possiveis:
            voo_por_opcoes = []
            for j in range(len(i) - 1):
                opcoes_por_camada = []
                for k in range(camadas):
                    if numero_voo[k][i[j]][i[j + 1]] != 1:
                        o, d = i[j], i[j + 1]
                        opcoes_por_camada.append(numero_voo[k][o][d])

                voo_por_opcoes.append(opcoes_por_camada)

                if voo_por_opcoes not in numero_voo_possivel:
                    numero_voo_possivel.append(voo_por_opcoes)

    return voos_possiveis, numero_voo_possivel


def checando_voos(linhas, combinacao, voo):
    """Essa funcao ira checar se o voo escolhido na combinacao aleatoria de fato pode ser usado ou se deve ser descartado."""
    datetime_partida = False
    for l in range(len(linhas)):
        if l == 0:
            continue

        else:
            if linhas[l].split()[7] == combinacao[-1]:
                data_chegada = (
                    linhas[l].split()[4] + " " + linhas[l].split()[5]
                )  # Data e hora de chegada do voo na conexao
                datetime_chegada = datetime.datetime.strptime(
                    data_chegada, "%d/%m/%Y %H:%M"
                )

            elif linhas[l].split()[7] == voo:
                data_partida = (
                    linhas[l].split()[2] + " " + linhas[l].split()[3]
                )  # Data e hora de partida do voo que sai da conexao
                datetime_partida = datetime.datetime.strptime(
                    data_partida, "%d/%m/%Y %H:%M"
                )

    if datetime_partida and datetime_partida > datetime_chegada:
        return True

    else:
        return False


def escrevendo_possibilidades(opcoes_voos, voos_possiveis, linhas):
    """Essa funcao vai escrever as possbilidades no formato correto para os outros programas em um arquivo .txt"""
    with open("Dados_criados_comerciais.txt", "a") as f:
        for i in range(len(opcoes_voos)):
            tamanho = 9999
            for combinacoes in voos_possiveis[
                i
            ]:  # Estamos pegando o tamanho do menor conjunto dentre os conjuntos possiveis de se chegar ao destino para fazermos as escalas comerciais

                if len(combinacoes) < tamanho:
                    tamanho = len(combinacoes)

            for j in range(
                tamanho
            ):  # Criando as escalas comerciais para cada opcao de origem/destino # Origem e Destino
                combinacao = []
                copia_voos = copy.deepcopy(voos_possiveis[i])
                origem, destino = "", ""
                contador, validade = 0, False
                descarte = False

                for indice in range(len(voos_possiveis[i])):

                    if contador == 0:
                        voo = random.choice(copia_voos[indice])
                        combinacao.append(
                            voo
                        )  # Criamos o caminho entre a origem e o destino
                        copia_voos[indice].remove(voo)
                        contador += 1

                    else:
                        voo = random.choice(copia_voos[indice])
                        validade = checando_voos(linhas, combinacao, voo)

                        if validade == True:
                            combinacao.append(voo)
                        else:
                            descarte = True
                            break

                        copia_voos[indice].remove(voo)

                    # ELE TEM QUE CHECAR AQUI SE O QUE ESTA NO ARRAY COMBINACAO FAZ SENTIDO OU NAO
                for l in range(len(linhas)):
                    if l == 0:
                        continue

                    if linhas[l].split()[7] == combinacao[0]:  # Procurando a origem
                        origem = (
                            f"{linhas[l].split()[2]} {linhas[l].split()[3]}"  # Partida
                        )

                    if linhas[l].split()[7] == combinacao[-1]:  # Procurando destino
                        destino = (
                            f"{linhas[l].split()[4]} {linhas[l].split()[5]}"  # Chegada
                        )

                    if origem != "" and destino != "":
                        break

                if not descarte:
                    f.write(f"{str(opcoes_voos[i][0])} {str(opcoes_voos[i][-1])} ")
                    f.write(f"{origem} {destino} ")
                    for idx, voo in enumerate(combinacao): # ['a', 'b', 'c'] -> idx = 0, voo = 'a'
                        f.write(f'{voo}{"-" if idx < len(combinacao) - 1 else ""}') # valor_true if condicao else valor_false
                    f.write("\n")


def main():
    """Roda tudo"""

    filename = "Toy_escalas_comerciais_dijkstra_2.txt"

    n_out, partidas, voos, duracao, n, m, z, numero_voo, origens, destinos = vizinhos(
        filename
    )

    file = open(filename, "r")
    linhas = file.readlines()
    tempo_isquemia, data_disponivel = "8", "01/10/2023 06:00"
    lista_espera = ["5", "6", "7", "8", "4"]

    origem = 0
    destino = 8

    with open("Dados_criados_comerciais.txt", "w") as f:
        f.write(tempo_isquemia)
        f.write("\n \n")
        f.write(data_disponivel)
        f.write("\n\n")

        for espera in lista_espera:
            f.write(espera)
            f.write("\n")

        f.write("\n")

    for origem in origens:
        for destino in destinos:
            resultados = DFS(n_out, origem, destino)
            if origem == destino or len(resultados) == 0: continue
            opcoes_voos, voos_possiveis = posssibilidades(resultados, partidas, duracao, z, origem, destino, numero_voo)
            escrevendo_possibilidades(opcoes_voos, voos_possiveis, linhas)

    f.close()
    # print(resultados)
    # print("\n \n \n")
    # print(opcoes_voos, voos_possiveis)


if __name__ == "__main__":
    main()
