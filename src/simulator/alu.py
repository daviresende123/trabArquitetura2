"""
Módulo ALU (Unidade Lógica Aritmética) para o simulador UFLA-RISC.
Implementa as 12 operações aritméticas e lógicas do processador.
"""


class ALU:
    """
    Classe que representa a Unidade Lógica Aritmética do processador UFLA-RISC.
    
    Operações suportadas:
    - Aritméticas: ADD, SUB
    - Lógicas: XOR, OR, NOT, AND
    - Shifts: SAL, SAR, SLL, SLR
    - Especiais: ZERO, COPY
    """
    
    # Constantes - Opcodes
    ADD = 0x01   # Soma
    SUB = 0x02   # Subtração
    ZERO = 0x03  # Zera (retorna 0)
    XOR = 0x04   # XOR lógico
    OR = 0x05    # OR lógico
    NOT = 0x06   # NOT lógico (inversão)
    AND = 0x07   # AND lógico
    SAL = 0x08   # Shift aritmético esquerda
    SAR = 0x09   # Shift aritmético direita
    SLL = 0x0A   # Shift lógico esquerda
    SLR = 0x0B   # Shift lógico direita
    COPY = 0x0C  # Copia operando A
    
    # Constantes auxiliares
    MASK_32_BITS = 0xFFFFFFFF  # Máscara para 32 bits
    BIT_SINAL = 0x80000000      # Bit 31 (sinal em complemento de 2)
    MAX_SHIFT = 31              # Máximo de posições para shift
    
    def __init__(self):
        """
        Inicializa a ALU.
        """
        # Mapeamento de opcodes para métodos
        self.operacoes = {
            self.ADD: self._add,
            self.SUB: self._sub,
            self.ZERO: self._zero,
            self.XOR: self._xor,
            self.OR: self._or,
            self.NOT: self._not,
            self.AND: self._and,
            self.SAL: self._sal,
            self.SAR: self._sar,
            self.SLL: self._sll,
            self.SLR: self._slr,
            self.COPY: self._copy
        }
    
    def executar(self, opcode: int, operando_a: int, operando_b: int) -> tuple:
        """
        Executa operação ALU.
        
        Args:
            opcode: código da operação (0x01-0x0C)
            operando_a: primeiro operando (32 bits)
            operando_b: segundo operando (32 bits)
            
        Returns:
            tuple: (resultado, carry, overflow)
            - resultado: valor de 32 bits resultante
            - carry: True se houve carry out
            - overflow: True se houve overflow aritmético
            
        Raises:
            ValueError: Se o opcode for inválido
            TypeError: Se os operandos não forem inteiros
        """
        if not isinstance(opcode, int):
            raise TypeError(
                f"Opcode deve ser um inteiro, recebido: {type(opcode).__name__}"
            )
        
        if not isinstance(operando_a, int):
            raise TypeError(
                f"Operando A deve ser um inteiro, recebido: {type(operando_a).__name__}"
            )
        
        if not isinstance(operando_b, int):
            raise TypeError(
                f"Operando B deve ser um inteiro, recebido: {type(operando_b).__name__}"
            )
        
        if opcode not in self.operacoes:
            raise ValueError(
                f"Opcode inválido: 0x{opcode:02X}. "
                f"Opcodes válidos: 0x01-0x0C"
            )
        
        # Garante que operandos estão em 32 bits
        operando_a = operando_a & self.MASK_32_BITS
        operando_b = operando_b & self.MASK_32_BITS
        
        # Executa a operação correspondente
        return self.operacoes[opcode](operando_a, operando_b)
    
    def _add(self, a: int, b: int) -> tuple:
        """
        Soma com detecção de carry e overflow.
        
        Returns:
            tuple: (resultado, carry, overflow)
        """
        resultado = a + b
        
        # Carry: resultado ultrapassou 32 bits
        carry = resultado > self.MASK_32_BITS
        
        # Overflow: soma de dois números com mesmo sinal resulta em sinal diferente
        # Só pode ocorrer overflow se ambos operandos têm o mesmo sinal
        sinal_a = a & self.BIT_SINAL
        sinal_b = b & self.BIT_SINAL
        sinal_resultado = resultado & self.BIT_SINAL
        
        # Overflow ocorre quando:
        # - A e B são positivos (bit 31 = 0) e resultado é negativo (bit 31 = 1)
        # - A e B são negativos (bit 31 = 1) e resultado é positivo (bit 31 = 0)
        overflow = (sinal_a == sinal_b) and (sinal_a != sinal_resultado)
        
        # Mantém apenas 32 bits
        resultado = resultado & self.MASK_32_BITS
        
        return (resultado, carry, overflow)
    
    def _sub(self, a: int, b: int) -> tuple:
        """
        Subtração com detecção de carry (borrow) e overflow.
        
        Returns:
            tuple: (resultado, carry, overflow)
        """
        # Subtração é equivalente a A + (-B)
        # Em complemento de 2: -B = NOT(B) + 1
        resultado = a - b
        
        # Carry (borrow): resultado ficou negativo (necessitou empréstimo)
        carry = resultado < 0
        
        # Overflow: subtração de números com sinais diferentes resulta em sinal inesperado
        sinal_a = a & self.BIT_SINAL
        sinal_b = b & self.BIT_SINAL
        sinal_resultado = resultado & self.BIT_SINAL
        
        # Overflow ocorre quando:
        # - A é positivo, B é negativo e resultado é negativo
        # - A é negativo, B é positivo e resultado é positivo
        overflow = (sinal_a != sinal_b) and (sinal_a != sinal_resultado)
        
        # Mantém apenas 32 bits (converte negativo para representação sem sinal)
        resultado = resultado & self.MASK_32_BITS
        
        return (resultado, carry, overflow)
    
    def _zero(self, a: int, b: int) -> tuple:
        """
        Retorna zero.
        
        Returns:
            tuple: (0, False, False)
        """
        return (0, False, False)
    
    def _xor(self, a: int, b: int) -> tuple:
        """
        XOR bit a bit.
        
        Returns:
            tuple: (resultado, False, False)
        """
        resultado = (a ^ b) & self.MASK_32_BITS
        return (resultado, False, False)
    
    def _or(self, a: int, b: int) -> tuple:
        """
        OR bit a bit.
        
        Returns:
            tuple: (resultado, False, False)
        """
        resultado = (a | b) & self.MASK_32_BITS
        return (resultado, False, False)
    
    def _not(self, a: int, b: int) -> tuple:
        """
        NOT bit a bit (inversão do operando A).
        Operando B é ignorado.
        
        Returns:
            tuple: (resultado, False, False)
        """
        resultado = (~a) & self.MASK_32_BITS
        return (resultado, False, False)
    
    def _and(self, a: int, b: int) -> tuple:
        """
        AND bit a bit.
        
        Returns:
            tuple: (resultado, False, False)
        """
        resultado = (a & b) & self.MASK_32_BITS
        return (resultado, False, False)
    
    def _sal(self, a: int, b: int) -> tuple:
        """
        Shift Aritmético à Esquerda (mantém sinal).
        Desloca A para esquerda B posições, preenchendo com zeros à direita.
        
        Args:
            a: valor a ser deslocado
            b: número de posições (usa apenas 5 bits menos significativos)
        
        Returns:
            tuple: (resultado, False, False)
        """
        # Usa apenas os 5 bits menos significativos de B (0-31 posições)
        shift_amount = b & 0x1F
        
        if shift_amount == 0:
            return (a, False, False)
        
        resultado = (a << shift_amount) & self.MASK_32_BITS
        return (resultado, False, False)
    
    def _sar(self, a: int, b: int) -> tuple:
        """
        Shift Aritmético à Direita (mantém sinal).
        Desloca A para direita B posições, preenchendo com o bit de sinal à esquerda.
        
        Args:
            a: valor a ser deslocado
            b: número de posições (usa apenas 5 bits menos significativos)
        
        Returns:
            tuple: (resultado, False, False)
        """
        # Usa apenas os 5 bits menos significativos de B (0-31 posições)
        shift_amount = b & 0x1F
        
        if shift_amount == 0:
            return (a, False, False)
        
        # Verifica se é negativo (bit 31 = 1)
        eh_negativo = (a & self.BIT_SINAL) != 0
        
        # Desloca à direita
        resultado = a >> shift_amount
        
        # Se era negativo, preenche bits à esquerda com 1s
        if eh_negativo:
            # Cria máscara de bits 1 à esquerda
            mascara = (self.MASK_32_BITS << (32 - shift_amount)) & self.MASK_32_BITS
            resultado = resultado | mascara
        
        resultado = resultado & self.MASK_32_BITS
        return (resultado, False, False)
    
    def _sll(self, a: int, b: int) -> tuple:
        """
        Shift Lógico à Esquerda.
        Desloca A para esquerda B posições, preenchendo com zeros à direita.
        
        Args:
            a: valor a ser deslocado
            b: número de posições (usa apenas 5 bits menos significativos)
        
        Returns:
            tuple: (resultado, False, False)
        """
        # Usa apenas os 5 bits menos significativos de B (0-31 posições)
        shift_amount = b & 0x1F
        
        if shift_amount == 0:
            return (a, False, False)
        
        resultado = (a << shift_amount) & self.MASK_32_BITS
        return (resultado, False, False)
    
    def _slr(self, a: int, b: int) -> tuple:
        """
        Shift Lógico à Direita.
        Desloca A para direita B posições, preenchendo com zeros à esquerda.
        
        Args:
            a: valor a ser deslocado
            b: número de posições (usa apenas 5 bits menos significativos)
        
        Returns:
            tuple: (resultado, False, False)
        """
        # Usa apenas os 5 bits menos significativos de B (0-31 posições)
        shift_amount = b & 0x1F
        
        if shift_amount == 0:
            return (a, False, False)
        
        # Shift lógico: sempre preenche com zeros à esquerda
        resultado = (a >> shift_amount) & self.MASK_32_BITS
        return (resultado, False, False)
    
    def _copy(self, a: int, b: int) -> tuple:
        """
        Copia operando A para resultado.
        Operando B é ignorado.
        
        Returns:
            tuple: (operando_a, False, False)
        """
        return (a, False, False)
    
    def __str__(self) -> str:
        """
        Representação em string da ALU.
        
        Returns:
            String com informações da ALU
        """
        return f"ALU(operacoes={len(self.operacoes)})"
    
    def __repr__(self) -> str:
        """
        Representação técnica da ALU.
        
        Returns:
            String com representação técnica
        """
        return self.__str__()