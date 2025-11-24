"""
Módulo de registradores para o simulador UFLA-RISC.
Implementa banco de 32 registradores de uso geral de 32 bits cada.
"""


class Registradores:
    """
    Classe que representa o banco de registradores do processador UFLA-RISC.
    
    Características:
    - 32 registradores de uso geral (R0 a R31)
    - Cada registrador armazena 32 bits
    - R0 sempre retorna 0 (hardwired zero)
    """
    
    # Constantes
    NUM_REGISTRADORES = 32
    TAMANHO_REGISTRADOR = 32  # bits
    REG_MAXIMO = NUM_REGISTRADORES - 1
    VALOR_MAXIMO = 0xFFFFFFFF  # Valor máximo de 32 bits
    
    def __init__(self):
        """
        Inicializa o banco de registradores com todos os valores zerados.
        """
        self.registradores = [0] * self.NUM_REGISTRADORES
    
    def ler(self, num_reg: int) -> int:
        """
        Lê o valor de um registrador.
        
        Args:
            num_reg: Número do registrador (0 a 31)
            
        Returns:
            Valor de 32 bits armazenado no registrador
            
        Raises:
            ValueError: Se o número do registrador estiver fora do range válido
            TypeError: Se o número do registrador não for um inteiro
        """
        if not isinstance(num_reg, int):
            raise TypeError(
                f"Número do registrador deve ser um inteiro, recebido: {type(num_reg).__name__}"
            )
        
        if num_reg < 0 or num_reg > self.REG_MAXIMO:
            raise ValueError(
                f"Número de registrador fora do range válido. "
                f"Esperado: 0-{self.REG_MAXIMO}, recebido: {num_reg}"
            )
        
        # R0 sempre retorna 0
        if num_reg == 0:
            return 0
        
        return self.registradores[num_reg]
    
    def escrever(self, num_reg: int, valor: int):
        """
        Escreve um valor em um registrador.
        
        Args:
            num_reg: Número do registrador (0 a 31)
            valor: Valor de 32 bits a ser armazenado
            
        Raises:
            ValueError: Se o número do registrador estiver fora do range válido
            TypeError: Se o número do registrador ou valor não forem inteiros
            
        Note:
            Escritas em R0 são ignoradas (R0 sempre permanece 0)
        """
        if not isinstance(num_reg, int):
            raise TypeError(
                f"Número do registrador deve ser um inteiro, recebido: {type(num_reg).__name__}"
            )
        
        if not isinstance(valor, int):
            raise TypeError(
                f"Valor deve ser um inteiro, recebido: {type(valor).__name__}"
            )
        
        if num_reg < 0 or num_reg > self.REG_MAXIMO:
            raise ValueError(
                f"Número de registrador fora do range válido. "
                f"Esperado: 0-{self.REG_MAXIMO}, recebido: {num_reg}"
            )
        
        # R0 é hardwired zero - escritas são ignoradas
        if num_reg == 0:
            return
        
        # Garante que o valor está dentro do range de 32 bits (sem sinal)
        # Usa máscara para manter apenas os 32 bits menos significativos
        self.registradores[num_reg] = valor & self.VALOR_MAXIMO
    
    def dump(self) -> dict:
        """
        Retorna o estado atual de todos os registradores.
        
        Returns:
            Dicionário com números dos registradores como chaves e valores como valores
            Formato: {0: valor_R0, 1: valor_R1, ..., 31: valor_R31}
        """
        # R0 sempre retorna 0, independente do que está armazenado
        dump_dict = {i: (0 if i == 0 else self.registradores[i]) 
                     for i in range(self.NUM_REGISTRADORES)}
        return dump_dict
    
    def limpar(self):
        """
        Zera todos os registradores.
        """
        self.registradores = [0] * self.NUM_REGISTRADORES
    
    def __str__(self) -> str:
        """
        Representação em string do banco de registradores (útil para debug).
        
        Returns:
            String com informações básicas dos registradores
        """
        regs_nao_zero = sum(1 for i, valor in enumerate(self.registradores) 
                           if i != 0 and valor != 0)
        return (
            f"Registradores(total={self.NUM_REGISTRADORES}, "
            f"tamanho={self.TAMANHO_REGISTRADOR} bits, "
            f"nao_zero={regs_nao_zero})"
        )
    
    def __repr__(self) -> str:
        """
        Representação técnica do banco de registradores.
        
        Returns:
            String com representação técnica
        """
        return self.__str__()
    
    def __getitem__(self, num_reg: int) -> int:
        """
        Permite acesso aos registradores usando sintaxe de indexação.
        Exemplo: valor = registradores[5]
        
        Args:
            num_reg: Número do registrador (0 a 31)
            
        Returns:
            Valor do registrador
        """
        return self.ler(num_reg)
    
    def __setitem__(self, num_reg: int, valor: int):
        """
        Permite escrita nos registradores usando sintaxe de indexação.
        Exemplo: registradores[5] = 100
        
        Args:
            num_reg: Número do registrador (0 a 31)
            valor: Valor a ser armazenado
        """
        self.escrever(num_reg, valor)