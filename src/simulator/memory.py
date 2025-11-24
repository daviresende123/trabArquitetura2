"""
Módulo de memória para o simulador UFLA-RISC.
Implementa memória RAM com endereçamento de 16 bits e palavras de 32 bits.
"""


class Memory:
    """
    Classe que representa a memória do processador UFLA-RISC.
    
    Características:
    - 65.536 endereços (16 bits de endereçamento)
    - Cada endereço armazena uma palavra de 32 bits
    - Tamanho total: 256 KB (64K palavras × 4 bytes)
    """
    
    # Constantes
    MEMORY_SIZE = 65536  # 2^16 endereços
    WORD_SIZE = 32  # bits por palavra
    MAX_ADDRESS = MEMORY_SIZE - 1
    MAX_VALUE = 0xFFFFFFFF  # Valor máximo de 32 bits
    
    def __init__(self):
        """
        Inicializa a memória com todos os endereços zerados.
        """
        self.memory = [0] * self.MEMORY_SIZE
    
    def read(self, address: int) -> int:
        """
        Lê uma palavra de 32 bits do endereço especificado.
        
        Args:
            address: Endereço de memória (0 a 65535)
            
        Returns:
            Valor de 32 bits armazenado no endereço
            
        Raises:
            ValueError: Se o endereço estiver fora do range válido
            TypeError: Se o endereço não for um inteiro
        """
        if not isinstance(address, int):
            raise TypeError(f"Endereço deve ser um inteiro, recebido: {type(address).__name__}")
        
        if address < 0 or address > self.MAX_ADDRESS:
            raise ValueError(
                f"Endereço fora do range válido. "
                f"Esperado: 0-{self.MAX_ADDRESS}, recebido: {address}"
            )
        
        return self.memory[address]
    
    def write(self, address: int, data: int):
        """
        Escreve uma palavra de 32 bits no endereço especificado.
        
        Args:
            address: Endereço de memória (0 a 65535)
            data: Valor de 32 bits a ser armazenado
            
        Raises:
            ValueError: Se o endereço estiver fora do range válido
            TypeError: Se o endereço ou dados não forem inteiros
        """
        if not isinstance(address, int):
            raise TypeError(f"Endereço deve ser um inteiro, recebido: {type(address).__name__}")
        
        if not isinstance(data, int):
            raise TypeError(f"Dados devem ser um inteiro, recebido: {type(data).__name__}")
        
        if address < 0 or address > self.MAX_ADDRESS:
            raise ValueError(
                f"Endereço fora do range válido. "
                f"Esperado: 0-{self.MAX_ADDRESS}, recebido: {address}"
            )
        
        # Garante que o valor está dentro do range de 32 bits (sem sinal)
        # Usa máscara para manter apenas os 32 bits menos significativos
        self.memory[address] = data & self.MAX_VALUE
    
    def load_program(self, instructions: list, start_address: int = 0):
        """
        Carrega uma lista de instruções na memória a partir do endereço inicial.
        
        Args:
            instructions: Lista de instruções (inteiros de 32 bits)
            start_address: Endereço inicial para carregar o programa (padrão: 0)
            
        Raises:
            ValueError: Se o programa não couber na memória ou endereço inválido
            TypeError: Se instructions não for uma lista ou start_address não for inteiro
        """
        if not isinstance(instructions, list):
            raise TypeError(
                f"Instructions deve ser uma lista, recebido: {type(instructions).__name__}"
            )
        
        if not isinstance(start_address, int):
            raise TypeError(
                f"start_address deve ser um inteiro, recebido: {type(start_address).__name__}"
            )
        
        if start_address < 0 or start_address > self.MAX_ADDRESS:
            raise ValueError(
                f"Endereço inicial fora do range válido. "
                f"Esperado: 0-{self.MAX_ADDRESS}, recebido: {start_address}"
            )
        
        end_address = start_address + len(instructions) - 1
        
        if end_address > self.MAX_ADDRESS:
            raise ValueError(
                f"Programa não cabe na memória. "
                f"Endereço final seria {end_address}, máximo permitido: {self.MAX_ADDRESS}"
            )
        
        # Carrega cada instrução na memória
        for i, instruction in enumerate(instructions):
            if not isinstance(instruction, int):
                raise TypeError(
                    f"Instrução no índice {i} deve ser um inteiro, "
                    f"recebido: {type(instruction).__name__}"
                )
            self.write(start_address + i, instruction)
    
    def dump(self, start: int, end: int) -> dict:
        """
        Retorna um dump (cópia) da memória entre os endereços especificados.
        
        Args:
            start: Endereço inicial (inclusivo)
            end: Endereço final (inclusivo)
            
        Returns:
            Dicionário com endereços como chaves e valores como valores
            Formato: {address: value, ...}
            
        Raises:
            ValueError: Se os endereços forem inválidos ou start > end
            TypeError: Se start ou end não forem inteiros
        """
        if not isinstance(start, int):
            raise TypeError(f"start deve ser um inteiro, recebido: {type(start).__name__}")
        
        if not isinstance(end, int):
            raise TypeError(f"end deve ser um inteiro, recebido: {type(end).__name__}")
        
        if start < 0 or start > self.MAX_ADDRESS:
            raise ValueError(
                f"Endereço inicial fora do range válido. "
                f"Esperado: 0-{self.MAX_ADDRESS}, recebido: {start}"
            )
        
        if end < 0 or end > self.MAX_ADDRESS:
            raise ValueError(
                f"Endereço final fora do range válido. "
                f"Esperado: 0-{self.MAX_ADDRESS}, recebido: {end}"
            )
        
        if start > end:
            raise ValueError(
                f"Endereço inicial não pode ser maior que o final. "
                f"start: {start}, end: {end}"
            )
        
        # Cria dicionário com o dump da memória
        return {address: self.memory[address] for address in range(start, end + 1)}
    
    def clear(self):
        """
        Limpa toda a memória, zerando todos os endereços.
        """
        self.memory = [0] * self.MEMORY_SIZE
    
    def __str__(self) -> str:
        """
        Representação em string da memória (útil para debug).
        
        Returns:
            String com informações básicas da memória
        """
        non_zero_count = sum(1 for value in self.memory if value != 0)
        return (
            f"Memory(size={self.MEMORY_SIZE} words, "
            f"word_size={self.WORD_SIZE} bits, "
            f"non_zero_addresses={non_zero_count})"
        )
    
    def __repr__(self) -> str:
        """
        Representação técnica da memória.
        
        Returns:
            String com representação técnica
        """
        return self.__str__()