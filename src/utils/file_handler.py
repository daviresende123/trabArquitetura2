"""
Módulo de manipulação de arquivos para o simulador UFLA-RISC.
Lê e escreve arquivos de programa em formato binário e assembly.
"""

import os
from typing import List, Tuple


class FileHandler:
    """
    Classe para manipulação de arquivos do simulador UFLA-RISC.
    
    Suporta:
    - Leitura de arquivos binários (.bin)
    - Escrita de arquivos binários
    - Leitura de arquivos assembly (.asm)
    - Escrita de logs de execução
    """
    
    @staticmethod
    def ler_arquivo_binario(caminho_arquivo: str) -> Tuple[List[int], int]:
        """
        Lê arquivo binário do UFLA-RISC.
        
        Formato do arquivo:
        - Linhas com instruções em binário (32 bits)
        - Diretiva 'address <endereço_binário>' define posição inicial
        - Linhas vazias são ignoradas
        - Comentários iniciados com '#' são ignorados
        
        Args:
            caminho_arquivo: Caminho do arquivo a ser lido
            
        Returns:
            tuple: (lista de instruções como int, endereço inicial)
            
        Raises:
            FileNotFoundError: Se o arquivo não for encontrado
            ValueError: Se o formato do arquivo for inválido
            
        Exemplo de arquivo:
            address 0
            00000001000010000100000110000000
            # Este é um comentário
            00000010001000001010001100000000
            11111111111111111111111111111111  # HALT
        """
        if not isinstance(caminho_arquivo, str):
            raise TypeError(
                f"caminho_arquivo deve ser string, recebido: {type(caminho_arquivo).__name__}"
            )
        
        if not os.path.exists(caminho_arquivo):
            raise FileNotFoundError(f"Arquivo não encontrado: {caminho_arquivo}")
        
        instrucoes = []
        endereco_inicial = 0
        numero_linha = 0
        
        try:
            with open(caminho_arquivo, 'r', encoding='utf-8') as arquivo:
                for linha in arquivo:
                    numero_linha += 1
                    
                    # Remove espaços em branco no início e fim
                    linha = linha.strip()
                    
                    # Ignora linhas vazias
                    if not linha:
                        continue
                    
                    # Remove comentários
                    if '#' in linha:
                        linha = linha.split('#')[0].strip()
                    
                    # Ignora se linha ficou vazia após remover comentário
                    if not linha:
                        continue
                    
                    # Verifica se é diretiva 'address'
                    if linha.lower().startswith('address'):
                        partes = linha.split()
                        if len(partes) != 2:
                            raise ValueError(
                                f"Linha {numero_linha}: Formato inválido de diretiva 'address'. "
                                f"Esperado: 'address <endereço>'"
                            )
                        
                        try:
                            # Tenta converter endereço (pode ser binário ou decimal)
                            endereco_str = partes[1].replace('_', '').replace(' ', '')
                            
                            # Detecta se é binário ou decimal
                            if all(c in '01' for c in endereco_str):
                                # String binária
                                endereco_inicial = int(endereco_str, 2)
                            else:
                                # Decimal
                                endereco_inicial = int(endereco_str)
                            
                            # Valida range
                            if endereco_inicial < 0 or endereco_inicial > 65535:
                                raise ValueError(
                                    f"Linha {numero_linha}: Endereço fora do range (0-65535): "
                                    f"{endereco_inicial}"
                                )
                                
                        except ValueError as e:
                            raise ValueError(
                                f"Linha {numero_linha}: Endereço inválido em diretiva 'address': "
                                f"'{partes[1]}'"
                            ) from e
                        
                        continue
                    
                    # Processa como instrução binária
                    # Remove espaços e underscores para facilitar leitura
                    linha_limpa = linha.replace(' ', '').replace('_', '')
                    
                    # Valida se é string binária válida
                    if not all(c in '01' for c in linha_limpa):
                        raise ValueError(
                            f"Linha {numero_linha}: Instrução contém caracteres inválidos. "
                            f"Esperado apenas 0s e 1s: '{linha}'"
                        )
                    
                    # Valida tamanho (deve ser exatamente 32 bits)
                    if len(linha_limpa) != 32:
                        raise ValueError(
                            f"Linha {numero_linha}: Instrução deve ter exatamente 32 bits. "
                            f"Encontrado: {len(linha_limpa)} bits"
                        )
                    
                    # Converte para inteiro
                    try:
                        instrucao = int(linha_limpa, 2)
                        instrucoes.append(instrucao)
                    except ValueError as e:
                        raise ValueError(
                            f"Linha {numero_linha}: Erro ao converter instrução binária: "
                            f"'{linha}'"
                        ) from e
        
        except UnicodeDecodeError as e:
            raise ValueError(
                f"Erro ao decodificar arquivo. Verifique a codificação (deve ser UTF-8)"
            ) from e
        
        return (instrucoes, endereco_inicial)
    
    @staticmethod
    def escrever_arquivo_binario(caminho_arquivo: str, instrucoes: List[int],
                                  endereco_inicial: int = 0):
        """
        Escreve arquivo binário do UFLA-RISC.
        
        Args:
            caminho_arquivo: Caminho do arquivo a ser criado
            instrucoes: Lista de instruções (inteiros de 32 bits)
            endereco_inicial: Endereço inicial do programa (padrão: 0)
            
        Raises:
            TypeError: Se os tipos dos argumentos forem inválidos
            ValueError: Se os valores forem inválidos
            IOError: Se houver erro ao escrever o arquivo
        """
        if not isinstance(caminho_arquivo, str):
            raise TypeError(
                f"caminho_arquivo deve ser string, recebido: {type(caminho_arquivo).__name__}"
            )
        
        if not isinstance(instrucoes, list):
            raise TypeError(
                f"instrucoes deve ser lista, recebido: {type(instrucoes).__name__}"
            )
        
        if not isinstance(endereco_inicial, int):
            raise TypeError(
                f"endereco_inicial deve ser inteiro, recebido: {type(endereco_inicial).__name__}"
            )
        
        if endereco_inicial < 0 or endereco_inicial > 65535:
            raise ValueError(
                f"endereco_inicial deve estar entre 0 e 65535, recebido: {endereco_inicial}"
            )
        
        try:
            with open(caminho_arquivo, 'w', encoding='utf-8') as arquivo:
                # Escreve diretiva de endereço
                arquivo.write(f"address {endereco_inicial}\n")
                arquivo.write("\n")
                
                # Escreve cada instrução
                for i, instrucao in enumerate(instrucoes):
                    if not isinstance(instrucao, int):
                        raise TypeError(
                            f"Instrução {i} deve ser inteiro, "
                            f"recebido: {type(instrucao).__name__}"
                        )
                    
                    # Garante 32 bits
                    instrucao = instrucao & 0xFFFFFFFF
                    
                    # Converte para string binária de 32 bits
                    bin_str = format(instrucao, '032b')
                    
                    # Escreve com formatação (grupos de 8 bits)
                    formatada = ' '.join([bin_str[j:j+8] for j in range(0, 32, 8)])
                    arquivo.write(f"{formatada}\n")
        
        except IOError as e:
            raise IOError(f"Erro ao escrever arquivo: {caminho_arquivo}") from e
    
    @staticmethod
    def ler_arquivo_assembly(caminho_arquivo: str) -> List[str]:
        """
        Lê arquivo assembly (.asm) do UFLA-RISC.
        
        Remove comentários e linhas vazias, retornando apenas
        linhas de código assembly válidas.
        
        Args:
            caminho_arquivo: Caminho do arquivo assembly
            
        Returns:
            Lista de linhas de código assembly (sem comentários e linhas vazias)
            
        Raises:
            FileNotFoundError: Se o arquivo não for encontrado
            
        Exemplo:
            # Arquivo entrada.asm:
            # Programa de exemplo
            LOADL R1, 10    # Carrega 10 em R1
            
            ADD R2, R1, R1  # R2 = R1 + R1
            HALT
            
            # Retorna: ['LOADL R1, 10', 'ADD R2, R1, R1', 'HALT']
        """
        if not isinstance(caminho_arquivo, str):
            raise TypeError(
                f"caminho_arquivo deve ser string, recebido: {type(caminho_arquivo).__name__}"
            )
        
        if not os.path.exists(caminho_arquivo):
            raise FileNotFoundError(f"Arquivo não encontrado: {caminho_arquivo}")
        
        linhas_codigo = []
        
        try:
            with open(caminho_arquivo, 'r', encoding='utf-8') as arquivo:
                for linha in arquivo:
                    # Remove espaços em branco no início e fim
                    linha = linha.strip()
                    
                    # Ignora linhas vazias
                    if not linha:
                        continue
                    
                    # Remove comentários
                    if '#' in linha:
                        linha = linha.split('#')[0].strip()
                    
                    # Ignora se linha ficou vazia após remover comentário
                    if not linha:
                        continue
                    
                    linhas_codigo.append(linha)
        
        except UnicodeDecodeError as e:
            raise ValueError(
                f"Erro ao decodificar arquivo. Verifique a codificação (deve ser UTF-8)"
            ) from e
        
        return linhas_codigo
    
    @staticmethod
    def escrever_log_saida(caminho_arquivo: str, log_execucao: List[dict]):
        """
        Escreve log de execução em arquivo texto legível.
        
        Formato do log:
        - Informações de cada ciclo de execução
        - Estado dos registradores modificados
        - Estado da memória modificada
        - Estado dos flags
        
        Args:
            caminho_arquivo: Caminho do arquivo de log a ser criado
            log_execucao: Lista de dicionários com informações de cada ciclo
            
        Raises:
            TypeError: Se os tipos dos argumentos forem inválidos
            IOError: Se houver erro ao escrever o arquivo
        """
        if not isinstance(caminho_arquivo, str):
            raise TypeError(
                f"caminho_arquivo deve ser string, recebido: {type(caminho_arquivo).__name__}"
            )
        
        if not isinstance(log_execucao, list):
            raise TypeError(
                f"log_execucao deve ser lista, recebido: {type(log_execucao).__name__}"
            )
        
        try:
            with open(caminho_arquivo, 'w', encoding='utf-8') as arquivo:
                arquivo.write("=" * 80 + "\n")
                arquivo.write("LOG DE EXECUÇÃO - SIMULADOR UFLA-RISC\n")
                arquivo.write("=" * 80 + "\n\n")
                
                for ciclo in log_execucao:
                    arquivo.write("=" * 80 + "\n")
                    arquivo.write(
                        f"CICLO {ciclo['cycle_count']} | "
                        f"INSTRUÇÃO {ciclo['instruction_count']}\n"
                    )
                    arquivo.write("=" * 80 + "\n\n")
                    
                    # Informações básicas
                    arquivo.write(f"PC: {ciclo['pc']} (0x{ciclo['pc']:04X})\n")
                    arquivo.write(f"IR: 0x{ciclo['ir']:08X}\n")
                    arquivo.write(f"Instrução binária: {format(ciclo['ir'], '032b')}\n\n")
                    
                    # Instrução decodificada
                    decoded = ciclo['decoded']
                    arquivo.write(f"Tipo: {decoded['type']}\n")
                    
                    if decoded['type'] != 'HALT':
                        arquivo.write(f"Opcode: 0x{decoded['opcode']:02X}\n")
                        
                        if 'ra' in decoded:
                            arquivo.write(f"  ra: R{decoded['ra']}\n")
                        if 'rb' in decoded:
                            arquivo.write(f"  rb: R{decoded['rb']}\n")
                        if 'rc' in decoded:
                            arquivo.write(f"  rc: R{decoded['rc']}\n")
                        if 'immediate' in decoded:
                            arquivo.write(
                                f"  immediate: {decoded['immediate']} "
                                f"(0x{decoded['immediate']:04X})\n"
                            )
                        if 'address' in decoded:
                            arquivo.write(
                                f"  address: {decoded['address']} "
                                f"(0x{decoded['address']:04X})\n"
                            )
                        if 'offset' in decoded:
                            arquivo.write(f"  offset: {decoded['offset']}\n")
                    
                    arquivo.write("\n")
                    
                    # Estágios de execução
                    arquivo.write("--- Estágios de Execução ---\n")
                    
                    stages = ciclo.get('stages', {})
                    
                    # IF
                    if 'IF' in stages:
                        if_info = stages['IF']
                        arquivo.write(f"IF:  PC={if_info['pc']}, IR=0x{if_info['ir']:08X}\n")
                    
                    # ID
                    if 'ID' in stages:
                        id_info = stages['ID']
                        arquivo.write(f"ID:  Decodificado, sinais de controle gerados\n")
                    
                    # EX/MEM
                    if 'EX/MEM' in stages:
                        ex_info = stages['EX/MEM']
                        arquivo.write(f"EX:  ")
                        if ex_info.get('result') is not None:
                            arquivo.write(f"Resultado=0x{ex_info['result']:08X}")
                        if ex_info.get('mem_address') is not None:
                            arquivo.write(f", Mem[{ex_info['mem_address']}]")
                        if ex_info.get('branch_taken'):
                            arquivo.write(f", Branch tomado")
                        if ex_info.get('jump_address') is not None:
                            arquivo.write(f", Jump para {ex_info['jump_address']}")
                        arquivo.write("\n")
                    
                    # WB
                    if 'WB' in stages:
                        wb_info = stages['WB']
                        arquivo.write(f"WB:  ")
                        if wb_info.get('register') is not None:
                            arquivo.write(
                                f"R{wb_info['register']} = "
                                f"0x{wb_info['value']:08X}"
                            )
                        else:
                            arquivo.write("Sem escrita")
                        arquivo.write("\n")
                    
                    arquivo.write("\n")
                    
                    # Registradores modificados
                    if ciclo.get('registers_modified'):
                        arquivo.write("--- Registradores Modificados ---\n")
                        for reg, valor in ciclo['registers_modified'].items():
                            arquivo.write(
                                f"  R{reg:2d} = {valor:10d} (0x{valor:08X})\n"
                            )
                        arquivo.write("\n")
                    
                    # Memória modificada
                    if ciclo.get('memory_modified'):
                        arquivo.write("--- Memória Modificada ---\n")
                        for endereco, valor in ciclo['memory_modified'].items():
                            arquivo.write(
                                f"  MEM[{endereco:5d}] = {valor:10d} (0x{valor:08X})\n"
                            )
                        arquivo.write("\n")
                    
                    # Flags
                    flags = ciclo.get('flags', {})
                    arquivo.write(
                        f"--- Flags ---\n"
                        f"N={int(flags.get('neg', False))} "
                        f"Z={int(flags.get('zero', False))} "
                        f"C={int(flags.get('carry', False))} "
                        f"V={int(flags.get('overflow', False))}\n"
                    )
                    arquivo.write("\n")
                    
                    # Status
                    if ciclo.get('halted'):
                        arquivo.write("*** HALT ***\n")
                        arquivo.write("\n")
                
                arquivo.write("=" * 80 + "\n")
                arquivo.write("FIM DO LOG DE EXECUÇÃO\n")
                arquivo.write("=" * 80 + "\n")
        
        except IOError as e:
            raise IOError(f"Erro ao escrever arquivo de log: {caminho_arquivo}") from e