"""
Módulo de flags para o simulador UFLA-RISC.
Implementa os flags de status do processador: neg, zero, carry e overflow.
"""


class Flags:
    """
    Classe que representa os flags de status do processador UFLA-RISC.
    
    Flags disponíveis:
    - neg: Resultado negativo (bit 31 = 1)
    - zero: Resultado zero
    - carry: Carry out da operação
    - overflow: Overflow aritmético
    """
    
    # Constantes
    FLAGS_VALIDOS = {'neg', 'zero', 'carry', 'overflow'}
    BIT_SINAL = 31  # Bit mais significativo (sinal em complemento de 2)
    MASCARA_BIT_SINAL = 0x80000000  # Máscara para bit 31
    
    def __init__(self):
        """
        Inicializa todos os flags como False.
        """
        self.neg = False
        self.zero = False
        self.carry = False
        self.overflow = False
    
    def definir_flag(self, nome_flag: str, valor: bool):
        """
        Define o valor de um flag específico.
        
        Args:
            nome_flag: Nome do flag ('neg', 'zero', 'carry', 'overflow')
            valor: Valor booleano a ser atribuído ao flag
            
        Raises:
            ValueError: Se o nome do flag for inválido
            TypeError: Se o valor não for booleano
        """
        if not isinstance(valor, bool):
            raise TypeError(
                f"Valor do flag deve ser booleano, recebido: {type(valor).__name__}"
            )
        
        nome_flag = nome_flag.lower()
        
        if nome_flag not in self.FLAGS_VALIDOS:
            raise ValueError(
                f"Nome de flag inválido: '{nome_flag}'. "
                f"Flags válidos: {', '.join(sorted(self.FLAGS_VALIDOS))}"
            )
        
        setattr(self, nome_flag, valor)
    
    def obter_flag(self, nome_flag: str) -> bool:
        """
        Retorna o valor de um flag específico.
        
        Args:
            nome_flag: Nome do flag ('neg', 'zero', 'carry', 'overflow')
            
        Returns:
            Valor booleano do flag
            
        Raises:
            ValueError: Se o nome do flag for inválido
        """
        nome_flag = nome_flag.lower()
        
        if nome_flag not in self.FLAGS_VALIDOS:
            raise ValueError(
                f"Nome de flag inválido: '{nome_flag}'. "
                f"Flags válidos: {', '.join(sorted(self.FLAGS_VALIDOS))}"
            )
        
        return getattr(self, nome_flag)
    
    def atualizar_flags(self, resultado: int, carry: bool = False, overflow: bool = False):
        """
        Atualiza os flags baseado no resultado de uma operação.
        
        Args:
            resultado: Valor resultante da operação (32 bits)
            carry: Indica se houve carry out (padrão: False)
            overflow: Indica se houve overflow aritmético (padrão: False)
            
        Raises:
            TypeError: Se os parâmetros não forem dos tipos corretos
            
        Note:
            - zero: True se resultado == 0
            - neg: True se bit 31 (sinal) == 1
            - carry: Definido pelo parâmetro carry
            - overflow: Definido pelo parâmetro overflow
        """
        if not isinstance(resultado, int):
            raise TypeError(
                f"Resultado deve ser um inteiro, recebido: {type(resultado).__name__}"
            )
        
        if not isinstance(carry, bool):
            raise TypeError(
                f"Carry deve ser booleano, recebido: {type(carry).__name__}"
            )
        
        if not isinstance(overflow, bool):
            raise TypeError(
                f"Overflow deve ser booleano, recebido: {type(overflow).__name__}"
            )
        
        # Garante que trabalhamos com 32 bits
        resultado_32bits = resultado & 0xFFFFFFFF
        
        # Flag ZERO: True se resultado é 0
        self.zero = (resultado_32bits == 0)
        
        # Flag NEG: True se bit mais significativo (bit 31) é 1
        # Indica número negativo em complemento de 2
        self.neg = bool(resultado_32bits & self.MASCARA_BIT_SINAL)
        
        # Flags CARRY e OVERFLOW são definidos pelos parâmetros
        self.carry = carry
        self.overflow = overflow
    
    def limpar(self):
        """
        Zera todos os flags (define todos como False).
        """
        self.neg = False
        self.zero = False
        self.carry = False
        self.overflow = False
    
    def dump(self) -> dict:
        """
        Retorna o estado atual de todos os flags.
        
        Returns:
            Dicionário com nomes dos flags como chaves e valores booleanos
            Formato: {'neg': bool, 'zero': bool, 'carry': bool, 'overflow': bool}
        """
        return {
            'neg': self.neg,
            'zero': self.zero,
            'carry': self.carry,
            'overflow': self.overflow
        }
    
    def __str__(self) -> str:
        """
        Representação em string dos flags (útil para debug e visualização).
        
        Returns:
            String formatada com estado dos flags
        """
        return (
            f"Flags(N={int(self.neg)}, Z={int(self.zero)}, "
            f"C={int(self.carry)}, V={int(self.overflow)})"
        )
    
    def __repr__(self) -> str:
        """
        Representação técnica dos flags.
        
        Returns:
            String com representação técnica
        """
        return self.__str__()
    
    def __getitem__(self, nome_flag: str) -> bool:
        """
        Permite acesso aos flags usando sintaxe de indexação.
        Exemplo: valor = flags['zero']
        
        Args:
            nome_flag: Nome do flag
            
        Returns:
            Valor do flag
        """
        return self.obter_flag(nome_flag)
    
    def __setitem__(self, nome_flag: str, valor: bool):
        """
        Permite definição de flags usando sintaxe de indexação.
        Exemplo: flags['zero'] = True
        
        Args:
            nome_flag: Nome do flag
            valor: Valor booleano
        """
        self.definir_flag(nome_flag, valor)