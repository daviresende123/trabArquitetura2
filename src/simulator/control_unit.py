"""
Módulo Control Unit para o simulador UFLA-RISC.
Gera sinais de controle para execução de instruções.
"""


class ControlUnit:
    """
    Classe que representa a Unidade de Controle do processador UFLA-RISC.
    
    Responsável por gerar sinais de controle baseados na instrução decodificada,
    determinando o comportamento de cada componente do processador.
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
    
    def __init__(self):
        """
        Inicializa a Unidade de Controle.
        """
        # Conjunto de opcodes ALU
        self.opcodes_alu = {
            self.ADD, self.SUB, self.ZERO, self.XOR,
            self.OR, self.NOT, self.AND, self.SAL,
            self.SAR, self.SLL, self.SLR, self.COPY
        }
        
        # Conjunto de opcodes de branch
        self.opcodes_branch = {self.JEQ, self.JNE}
        
        # Conjunto de opcodes de jump
        self.opcodes_jump = {self.JAL, self.J, self.JR}
    
    def obter_sinais_controle(self, instrucao_decodificada: dict) -> dict:
        """
        Gera sinais de controle baseado na instrução decodificada.
        
        Args:
            instrucao_decodificada: Dicionário retornado pelo Decoder com campos:
                - opcode: código da operação
                - type: tipo da instrução ('R', 'I', 'J', 'JR', 'B', 'HALT')
                - outros campos dependendo do tipo
                
        Returns:
            dict com sinais de controle:
            {
                'alu_op': int ou None,     # Operação da ALU (ou None se não usar ALU)
                'reg_write': bool,         # True se escreve em registrador
                'mem_read': bool,          # True se lê da memória
                'mem_write': bool,         # True se escreve na memória
                'mem_to_reg': bool,        # True se dados da memória vão para registrador
                'branch': bool,            # True se é instrução de branch
                'jump': bool,              # True se é jump incondicional
                'alu_src': str,            # 'reg' ou 'imm' (fonte do segundo operando da ALU)
                'pc_src': str,             # 'inc', 'jump', 'branch' (fonte do próximo PC)
                'halt': bool               # True se é instrução HALT
            }
            
        Raises:
            TypeError: Se instrucao_decodificada não for um dicionário
            ValueError: Se opcode for inválido ou campos obrigatórios faltarem
        """
        if not isinstance(instrucao_decodificada, dict):
            raise TypeError(
                f"instrucao_decodificada deve ser um dicionário, "
                f"recebido: {type(instrucao_decodificada).__name__}"
            )
        
        if 'opcode' not in instrucao_decodificada:
            raise ValueError("instrucao_decodificada deve conter campo 'opcode'")
        
        if 'type' not in instrucao_decodificada:
            raise ValueError("instrucao_decodificada deve conter campo 'type'")
        
        opcode = instrucao_decodificada['opcode']
        tipo = instrucao_decodificada['type']
        
        # Sinais padrão (todos desativados)
        sinais = {
            'alu_op': None,
            'reg_write': False,
            'mem_read': False,
            'mem_write': False,
            'mem_to_reg': False,
            'branch': False,
            'jump': False,
            'alu_src': 'reg',
            'pc_src': 'inc',
            'halt': False
        }
        
        # Gera sinais baseado no opcode
        if tipo == 'HALT':
            sinais['halt'] = True
            sinais['pc_src'] = 'halt'
            
        elif opcode in self.opcodes_alu:
            # Instruções ALU (ADD, SUB, XOR, OR, NOT, AND, SAL, SAR, SLL, SLR, COPY, ZERO)
            sinais['alu_op'] = opcode
            sinais['reg_write'] = True
            sinais['alu_src'] = 'reg'
            sinais['pc_src'] = 'inc'
            
        elif opcode == self.LOADH:
            # LOADH: Carrega 16 bits nos 2 bytes mais significativos
            sinais['reg_write'] = True
            sinais['alu_src'] = 'imm'
            sinais['pc_src'] = 'inc'
            
        elif opcode == self.LOADL:
            # LOADL: Carrega 16 bits nos 2 bytes menos significativos
            sinais['reg_write'] = True
            sinais['alu_src'] = 'imm'
            sinais['pc_src'] = 'inc'
            
        elif opcode == self.LW:
            # LW: Load Word da memória
            sinais['mem_read'] = True
            sinais['reg_write'] = True
            sinais['mem_to_reg'] = True
            sinais['alu_src'] = 'imm'
            sinais['pc_src'] = 'inc'
            
        elif opcode == self.SW:
            # SW: Store Word na memória
            sinais['mem_write'] = True
            sinais['alu_src'] = 'imm'
            sinais['pc_src'] = 'inc'
            
        elif opcode == self.JAL:
            # JAL: Jump and Link (salva PC+1 em R31 e pula para endereço)
            sinais['jump'] = True
            sinais['reg_write'] = True  # Salva PC+1 em R31
            sinais['pc_src'] = 'jump'
            
        elif opcode == self.JR:
            # JR: Jump Register (pula para endereço em registrador)
            sinais['jump'] = True
            sinais['pc_src'] = 'jump'
            
        elif opcode == self.JEQ:
            # JEQ: Jump se igual
            sinais['branch'] = True
            sinais['alu_src'] = 'reg'
            sinais['pc_src'] = 'branch'
            
        elif opcode == self.JNE:
            # JNE: Jump se diferente
            sinais['branch'] = True
            sinais['alu_src'] = 'reg'
            sinais['pc_src'] = 'branch'
            
        elif opcode == self.J:
            # J: Jump incondicional
            sinais['jump'] = True
            sinais['pc_src'] = 'jump'
            
        else:
            raise ValueError(
                f"Opcode não reconhecido: 0x{opcode:02X} "
                f"(tipo: {tipo})"
            )
        
        return sinais
    
    def eh_instrucao_alu(self, opcode: int) -> bool:
        """
        Verifica se o opcode corresponde a uma instrução ALU.
        
        Args:
            opcode: Código da operação
            
        Returns:
            True se for instrução ALU, False caso contrário
        """
        return opcode in self.opcodes_alu
    
    def eh_instrucao_branch(self, opcode: int) -> bool:
        """
        Verifica se o opcode corresponde a uma instrução de branch.
        
        Args:
            opcode: Código da operação
            
        Returns:
            True se for instrução de branch, False caso contrário
        """
        return opcode in self.opcodes_branch
    
    def eh_instrucao_jump(self, opcode: int) -> bool:
        """
        Verifica se o opcode corresponde a uma instrução de jump.
        
        Args:
            opcode: Código da operação
            
        Returns:
            True se for instrução de jump, False caso contrário
        """
        return opcode in self.opcodes_jump
    
    def eh_instrucao_memoria(self, opcode: int) -> bool:
        """
        Verifica se o opcode corresponde a uma instrução de acesso à memória.
        
        Args:
            opcode: Código da operação
            
        Returns:
            True se for instrução de memória (LW ou SW), False caso contrário
        """
        return opcode in {self.LW, self.SW}
    
    def __str__(self) -> str:
        """
        Representação em string da Unidade de Controle.
        
        Returns:
            String com informações da UC
        """
        return (
            f"ControlUnit(alu_ops={len(self.opcodes_alu)}, "
            f"branch_ops={len(self.opcodes_branch)}, "
            f"jump_ops={len(self.opcodes_jump)})"
        )
    
    def __repr__(self) -> str:
        """
        Representação técnica da Unidade de Controle.
        
        Returns:
            String com representação técnica
        """
        return self.__str__()