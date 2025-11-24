"""
Módulo Decoder para o simulador UFLA-RISC.
Decodifica instruções de 32 bits em seus componentes.
"""


class Decoder:
    """
    Classe que decodifica instruções do processador UFLA-RISC.
    
    Suporta 5 formatos de instrução:
    - Tipo R: Operações ALU com 3 registradores
    - Tipo I: Operações com imediato (constantes, load/store)
    - Tipo J: Jump incondicional
    - Tipo JR: Jump para registrador
    - Tipo B: Branch condicional
    """
    
    # Constantes - Opcodes
    # Tipo R (ALU)
    ADD = 0x01
    SUB = 0x02
    ZERO = 0x03
    XOR = 0x04
    OR = 0x05
    NOT = 0x06
    AND = 0x07
    SAL = 0x08
    SAR = 0x09
    SLL = 0x0A
    SLR = 0x0B
    COPY = 0x0C
    
    # Tipo I (Imediato)
    LOADH = 0x0E
    LOADL = 0x0F
    LW = 0x10
    SW = 0x11
    
    # Tipo J (Jump)
    JAL = 0x12
    J = 0x16
    
    # Tipo JR (Jump Register)
    JR = 0x13
    
    # Tipo B (Branch)
    JEQ = 0x14
    JNE = 0x15
    
    # Halt
    HALT = 0xFFFFFFFF
    
    # Máscaras para extração de campos
    MASK_OPCODE = 0xFF000000      # [31-24] - 8 bits
    MASK_RA = 0x00F80000          # [23-19] - 5 bits
    MASK_RB = 0x0007C000          # [18-14] - 5 bits
    MASK_RC = 0x00003E00          # [13-9] - 5 bits
    MASK_RC_JR = 0x00F80000       # [23-19] - 5 bits para JR
    MASK_IMMEDIATE = 0x0007FFF8   # [18-3] - 16 bits
    MASK_ADDRESS = 0x00FFFF00     # [23-8] - 16 bits
    MASK_OFFSET = 0x00003FFF      # [13-0] - 14 bits
    
    # Deslocamentos (shifts) para posicionar campos
    SHIFT_OPCODE = 24
    SHIFT_RA = 19
    SHIFT_RB = 14
    SHIFT_RC = 9
    SHIFT_RC_JR = 19
    SHIFT_IMMEDIATE = 3
    SHIFT_ADDRESS = 8
    SHIFT_OFFSET = 0
    
    def __init__(self):
        """
        Inicializa o decodificador.
        """
        # Mapeamento de opcodes para tipos de instrução
        self.tipo_instrucao = {
            # Tipo R (ALU)
            self.ADD: 'R',
            self.SUB: 'R',
            self.ZERO: 'R',
            self.XOR: 'R',
            self.OR: 'R',
            self.NOT: 'R',
            self.AND: 'R',
            self.SAL: 'R',
            self.SAR: 'R',
            self.SLL: 'R',
            self.SLR: 'R',
            self.COPY: 'R',
            
            # Tipo I (Imediato)
            self.LOADH: 'I',
            self.LOADL: 'I',
            self.LW: 'I',
            self.SW: 'I',
            
            # Tipo J (Jump)
            self.JAL: 'J',
            self.J: 'J',
            
            # Tipo JR (Jump Register)
            self.JR: 'JR',
            
            # Tipo B (Branch)
            self.JEQ: 'B',
            self.JNE: 'B',
        }
    
    def decodificar(self, instrucao: int) -> dict:
        """
        Decodifica instrução de 32 bits.
        
        Args:
            instrucao: Instrução de 32 bits a ser decodificada
            
        Returns:
            dict com campos decodificados:
            {
                'opcode': int,
                'type': str,  # 'R', 'I', 'J', 'JR', 'B', 'HALT'
                'ra': int (se aplicável),
                'rb': int (se aplicável),
                'rc': int (se aplicável),
                'immediate': int (se aplicável),
                'address': int (se aplicável),
                'offset': int (se aplicável)
            }
            
        Raises:
            TypeError: Se a instrução não for um inteiro
            ValueError: Se o opcode for inválido
        """
        if not isinstance(instrucao, int):
            raise TypeError(
                f"Instrução deve ser um inteiro, recebido: {type(instrucao).__name__}"
            )
        
        # Garante 32 bits
        instrucao = instrucao & 0xFFFFFFFF
        
        # Verifica se é HALT (instrução especial)
        if instrucao == self.HALT:
            return {
                'opcode': self.HALT,
                'type': 'HALT'
            }
        
        # Extrai opcode (8 bits mais significativos)
        opcode = (instrucao & self.MASK_OPCODE) >> self.SHIFT_OPCODE
        
        # Determina tipo da instrução
        if opcode not in self.tipo_instrucao:
            raise ValueError(
                f"Opcode inválido: 0x{opcode:02X}. "
                f"Instrução: 0x{instrucao:08X}"
            )
        
        tipo = self.tipo_instrucao[opcode]
        
        # Decodifica baseado no tipo
        if tipo == 'R':
            return self._decodificar_tipo_r(instrucao, opcode)
        elif tipo == 'I':
            return self._decodificar_tipo_i(instrucao, opcode)
        elif tipo == 'J':
            return self._decodificar_tipo_j(instrucao, opcode)
        elif tipo == 'JR':
            return self._decodificar_tipo_jr(instrucao, opcode)
        elif tipo == 'B':
            return self._decodificar_tipo_b(instrucao, opcode)
    
    def _decodificar_tipo_r(self, instrucao: int, opcode: int) -> dict:
        """
        Decodifica instrução Tipo R (ALU com 3 registradores).
        
        Formato:
        [31-24] opcode
        [23-19] ra (destino)
        [18-14] rb (operando 1)
        [13-9] rc (operando 2)
        [8-0] não usado
        
        Args:
            instrucao: Instrução de 32 bits
            opcode: Opcode já extraído
            
        Returns:
            dict com campos decodificados
        """
        ra = (instrucao & self.MASK_RA) >> self.SHIFT_RA
        rb = (instrucao & self.MASK_RB) >> self.SHIFT_RB
        rc = (instrucao & self.MASK_RC) >> self.SHIFT_RC
        
        return {
            'opcode': opcode,
            'type': 'R',
            'ra': ra,
            'rb': rb,
            'rc': rc
        }
    
    def _decodificar_tipo_i(self, instrucao: int, opcode: int) -> dict:
        """
        Decodifica instrução Tipo I (Imediato).
        
        Formato:
        [31-24] opcode
        [23-19] ra (destino/fonte)
        [18-3] imediato (16 bits)
        [2-0] não usado
        
        Args:
            instrucao: Instrução de 32 bits
            opcode: Opcode já extraído
            
        Returns:
            dict com campos decodificados
        """
        ra = (instrucao & self.MASK_RA) >> self.SHIFT_RA
        imediato = (instrucao & self.MASK_IMMEDIATE) >> self.SHIFT_IMMEDIATE
        
        return {
            'opcode': opcode,
            'type': 'I',
            'ra': ra,
            'immediate': imediato
        }
    
    def _decodificar_tipo_j(self, instrucao: int, opcode: int) -> dict:
        """
        Decodifica instrução Tipo J (Jump incondicional).
        
        Formato:
        [31-24] opcode
        [23-8] endereço (16 bits)
        [7-0] não usado
        
        Args:
            instrucao: Instrução de 32 bits
            opcode: Opcode já extraído
            
        Returns:
            dict com campos decodificados
        """
        endereco = (instrucao & self.MASK_ADDRESS) >> self.SHIFT_ADDRESS
        
        return {
            'opcode': opcode,
            'type': 'J',
            'address': endereco
        }
    
    def _decodificar_tipo_jr(self, instrucao: int, opcode: int) -> dict:
        """
        Decodifica instrução Tipo JR (Jump Register).
        
        Formato:
        [31-24] opcode
        [23-19] rc (registrador com endereço)
        [18-0] não usado
        
        Args:
            instrucao: Instrução de 32 bits
            opcode: Opcode já extraído
            
        Returns:
            dict com campos decodificados
        """
        rc = (instrucao & self.MASK_RC_JR) >> self.SHIFT_RC_JR
        
        return {
            'opcode': opcode,
            'type': 'JR',
            'rc': rc
        }
    
    def _decodificar_tipo_b(self, instrucao: int, opcode: int) -> dict:
        """
        Decodifica instrução Tipo B (Branch condicional).
        
        Formato:
        [31-24] opcode
        [23-19] ra (primeiro registrador)
        [18-14] rb (segundo registrador)
        [13-0] offset (14 bits em complemento de 2)
        
        Args:
            instrucao: Instrução de 32 bits
            opcode: Opcode já extraído
            
        Returns:
            dict com campos decodificados
        """
        ra = (instrucao & self.MASK_RA) >> self.SHIFT_RA
        rb = (instrucao & self.MASK_RB) >> self.SHIFT_RB
        offset = (instrucao & self.MASK_OFFSET) >> self.SHIFT_OFFSET
        
        # Converte offset de complemento de 2 (14 bits com sinal)
        # Se bit 13 (bit de sinal) está setado, é negativo
        if offset & 0x2000:  # bit 13 = 1 (negativo)
            # Estende sinal: preenche bits superiores com 1s
            offset = offset | 0xFFFFC000  # Mantém os 14 bits e estende com 1s
            # Converte para int com sinal do Python
            offset = offset - 0x100000000 if offset > 0x7FFFFFFF else offset
        
        return {
            'opcode': opcode,
            'type': 'B',
            'ra': ra,
            'rb': rb,
            'offset': offset
        }
    
    def __str__(self) -> str:
        """
        Representação em string do decodificador.
        
        Returns:
            String com informações do decodificador
        """
        return f"Decoder(instrucoes_suportadas={len(self.tipo_instrucao)})"
    
    def __repr__(self) -> str:
        """
        Representação técnica do decodificador.
        
        Returns:
            String com representação técnica
        """
        return self.__str__()