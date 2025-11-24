"""
Módulo de memória para o simulador UFLA-RISC.
Implementa memória RAM com endereçamento de 16 bits e palavras de 32 bits.
"""


class Memoria:
    """
    Classe que representa a memória do processador UFLA-RISC.
    
    Características:
    - 65.536 endereços (16 bits de endereçamento)
    - Cada endereço armazena uma palavra de 32 bits
    - Tamanho total: 256 KB (64K palavras × 4 bytes)
    """
    
    # Constantes
    TAMANHO_MEMORIA = 65536  # 2^16 endereços
    TAMANHO_PALAVRA = 32  # bits por palavra
    ENDERECO_MAXIMO = TAMANHO_MEMORIA - 1
    VALOR_MAXIMO = 0xFFFFFFFF  # Valor máximo de 32 bits
    
    def __init__(self):
        """
        Inicializa a memória com todos os endereços zerados.
        """
        self.memoria = [0] * self.TAMANHO_MEMORIA
    
    def ler(self, endereco: int) -> int:
        """
        Lê uma palavra de 32 bits do endereço especificado.
        
        Args:
            endereco: Endereço de memória (0 a 65535)
            
        Returns:
            Valor de 32 bits armazenado no endereço
            
        Raises:
            ValueError: Se o endereço estiver fora do range válido
            TypeError: Se o endereço não for um inteiro
        """
        if not isinstance(endereco, int):
            raise TypeError(f"Endereço deve ser um inteiro, recebido: {type(endereco).__name__}")
        
        if endereco < 0 or endereco > self.ENDERECO_MAXIMO:
            raise ValueError(
                f"Endereço fora do range válido. "
                f"Esperado: 0-{self.ENDERECO_MAXIMO}, recebido: {endereco}"
            )
        
        return self.memoria[endereco]
    
    def escrever(self, endereco: int, dado: int):
        """
        Escreve uma palavra de 32 bits no endereço especificado.
        
        Args:
            endereco: Endereço de memória (0 a 65535)
            dado: Valor de 32 bits a ser armazenado
            
        Raises:
            ValueError: Se o endereço estiver fora do range válido
            TypeError: Se o endereço ou dados não forem inteiros
        """
        if not isinstance(endereco, int):
            raise TypeError(f"Endereço deve ser um inteiro, recebido: {type(endereco).__name__}")
        
        if not isinstance(dado, int):
            raise TypeError(f"Dados devem ser um inteiro, recebido: {type(dado).__name__}")
        
        if endereco < 0 or endereco > self.ENDERECO_MAXIMO:
            raise ValueError(
                f"Endereço fora do range válido. "
                f"Esperado: 0-{self.ENDERECO_MAXIMO}, recebido: {endereco}"
            )
        
        # Garante que o valor está dentro do range de 32 bits (sem sinal)
        # Usa máscara para manter apenas os 32 bits menos significativos
        self.memoria[endereco] = dado & self.VALOR_MAXIMO
    
    def carregar_programa(self, instrucoes: list, endereco_inicial: int = 0):
        """
        Carrega uma lista de instruções na memória a partir do endereço inicial.
        
        Args:
            instrucoes: Lista de instruções (inteiros de 32 bits)
            endereco_inicial: Endereço inicial para carregar o programa (padrão: 0)
            
        Raises:
            ValueError: Se o programa não couber na memória ou endereço inválido
            TypeError: Se instrucoes não for uma lista ou endereco_inicial não for inteiro
        """
        if not isinstance(instrucoes, list):
            raise TypeError(
                f"Instruções devem ser uma lista, recebido: {type(instrucoes).__name__}"
            )
        
        if not isinstance(endereco_inicial, int):
            raise TypeError(
                f"endereco_inicial deve ser um inteiro, recebido: {type(endereco_inicial).__name__}"
            )
        
        if endereco_inicial < 0 or endereco_inicial > self.ENDERECO_MAXIMO:
            raise ValueError(
                f"Endereço inicial fora do range válido. "
                f"Esperado: 0-{self.ENDERECO_MAXIMO}, recebido: {endereco_inicial}"
            )
        
        endereco_final = endereco_inicial + len(instrucoes) - 1
        
        if endereco_final > self.ENDERECO_MAXIMO:
            raise ValueError(
                f"Programa não cabe na memória. "
                f"Endereço final seria {endereco_final}, máximo permitido: {self.ENDERECO_MAXIMO}"
            )
        
        # Carrega cada instrução na memória
        for i, instrucao in enumerate(instrucoes):
            if not isinstance(instrucao, int):
                raise TypeError(
                    f"Instrução no índice {i} deve ser um inteiro, "
                    f"recebido: {type(instrucao).__name__}"
                )
            self.escrever(endereco_inicial + i, instrucao)
    
    def dump(self, inicio: int, fim: int) -> dict:
        """
        Retorna um dump (cópia) da memória entre os endereços especificados.
        
        Args:
            inicio: Endereço inicial (inclusivo)
            fim: Endereço final (inclusivo)
            
        Returns:
            Dicionário com endereços como chaves e valores como valores
            Formato: {endereco: valor, ...}
            
        Raises:
            ValueError: Se os endereços forem inválidos ou inicio > fim
            TypeError: Se inicio ou fim não forem inteiros
        """
        if not isinstance(inicio, int):
            raise TypeError(f"inicio deve ser um inteiro, recebido: {type(inicio).__name__}")
        
        if not isinstance(fim, int):
            raise TypeError(f"fim deve ser um inteiro, recebido: {type(fim).__name__}")
        
        if inicio < 0 or inicio > self.ENDERECO_MAXIMO:
            raise ValueError(
                f"Endereço inicial fora do range válido. "
                f"Esperado: 0-{self.ENDERECO_MAXIMO}, recebido: {inicio}"
            )
        
        if fim < 0 or fim > self.ENDERECO_MAXIMO:
            raise ValueError(
                f"Endereço final fora do range válido. "
                f"Esperado: 0-{self.ENDERECO_MAXIMO}, recebido: {fim}"
            )
        
        if inicio > fim:
            raise ValueError(
                f"Endereço inicial não pode ser maior que o final. "
                f"inicio: {inicio}, fim: {fim}"
            )
        
        # Cria dicionário com o dump da memória
        return {endereco: self.memoria[endereco] for endereco in range(inicio, fim + 1)}
    
    def limpar(self):
        """
        Limpa toda a memória, zerando todos os endereços.
        """
        self.memoria = [0] * self.TAMANHO_MEMORIA
    
    def __str__(self) -> str:
        """
        Representação em string da memória (útil para debug).
        
        Returns:
            String com informações básicas da memória
        """
        enderecos_nao_zero = sum(1 for valor in self.memoria if valor != 0)
        return (
            f"Memoria(tamanho={self.TAMANHO_MEMORIA} palavras, "
            f"tamanho_palavra={self.TAMANHO_PALAVRA} bits, "
            f"enderecos_nao_zero={enderecos_nao_zero})"
        )
    
    def __repr__(self) -> str:
        """
        Representação técnica da memória.
        
        Returns:
            String com representação técnica
        """
        return self.__str__()