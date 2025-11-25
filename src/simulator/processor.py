"""
Módulo Processor para o simulador UFLA-RISC.
Integra todos os componentes e implementa os 4 estágios de execução.
"""

from .memoria import Memoria
from .registradores import Registradores
from .alu import ALU
from .flags import Flags
from .decoder import Decoder
from .control_unit import ControlUnit


class Processor:
    """
    Classe que representa o processador UFLA-RISC completo.
    
    Integra todos os componentes:
    - Memória
    - Banco de Registradores
    - ALU (Unidade Lógica Aritmética)
    - Flags de status
    - Decoder (Decodificador de instruções)
    - Control Unit (Unidade de Controle)
    
    Implementa os 4 estágios de execução:
    - IF (Instruction Fetch)
    - ID (Instruction Decode)
    - EX/MEM (Execute and Memory)
    - WB (Write Back)
    """
    
    def __init__(self):
        """
        Inicializa o processador e todos os seus componentes.
        """
        # Componentes do processador
        self.memoria = Memoria()
        self.registradores = Registradores()
        self.alu = ALU()
        self.flags = Flags()
        self.decoder = Decoder()
        self.controle = ControlUnit()
        
        # Registradores especiais
        self.pc = 0          # Program Counter (contador de programa)
        self.ir = 0          # Instruction Register (registrador de instrução)
        self.halted = False  # Flag de parada
        
        # Contadores para estatísticas
        self.ciclos = 0          # Número de ciclos executados
        self.instrucoes = 0      # Número de instruções executadas
    
    def carregar_programa(self, instrucoes: list, endereco_inicial: int = 0):
        """
        Carrega programa na memória.
        
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
        
        # Carrega programa na memória
        self.memoria.carregar_programa(instrucoes, endereco_inicial)
        
        # Ajusta PC para o endereço inicial
        self.pc = endereco_inicial
    
    def resetar(self):
        """
        Reseta o processador ao estado inicial.
        
        Limpa:
        - Memória
        - Registradores
        - Flags
        - PC e IR
        - Contadores
        - Flag de parada
        """
        # Reseta componentes
        self.memoria.limpar()
        self.registradores.limpar()
        self.flags.limpar()
        
        # Reseta registradores especiais
        self.pc = 0
        self.ir = 0
        self.halted = False
        
        # Reseta contadores
        self.ciclos = 0
        self.instrucoes = 0
    
    def _stage_if(self) -> dict:
        """
        Estágio IF (Instruction Fetch) - Busca de Instrução.
        
        Operações realizadas:
        1. Busca instrução da memória no endereço apontado por PC
        2. Armazena instrução no registrador IR (Instruction Register)
        3. Incrementa PC para apontar para próxima instrução
        
        Returns:
            dict com informações do estágio IF:
            {
                'stage': 'IF',
                'pc': int,          # Valor do PC antes do incremento
                'ir': int,          # Instrução buscada
                'instruction': int  # Mesma instrução (para compatibilidade)
            }
            
        Raises:
            ValueError: Se PC estiver fora do range válido da memória
        """
        # Guarda PC atual antes de incrementar
        pc_atual = self.pc
        
        # 1. Busca instrução da memória no endereço PC
        instrucao = self.memoria.ler(self.pc)
        
        # 2. Armazena instrução no registrador IR
        self.ir = instrucao
        
        # 3. Incrementa PC (próxima instrução)
        # O PC pode ser modificado posteriormente por instruções de jump/branch
        self.pc = (self.pc + 1) & 0xFFFF  # Mantém PC em 16 bits
        
        return {
            'stage': 'IF',
            'pc': pc_atual,
            'ir': self.ir,
            'instruction': instrucao
        }
    
    def _stage_id(self) -> dict:
        """
        Estágio ID (Instruction Decode) - Decodificação de Instrução.
        
        Operações realizadas:
        1. Decodifica instrução armazenada em IR
        2. Gera sinais de controle baseados na instrução
        3. Lê operandos do banco de registradores (se necessário)
        
        Returns:
            dict com informações do estágio ID:
            {
                'stage': 'ID',
                'decoded': dict,           # Instrução decodificada
                'control_signals': dict,   # Sinais de controle gerados
                'operand_a': int,          # Valor do primeiro operando (se aplicável)
                'operand_b': int           # Valor do segundo operando (se aplicável)
            }
            
        Note:
            - Para instruções tipo R: operand_a = reg[rb], operand_b = reg[rc]
            - Para instruções tipo I (LW/SW): operand_a = reg[ra]
            - Para instruções tipo B: operand_a = reg[ra], operand_b = reg[rb]
            - Para outras instruções: operandos podem ser None
        """
        # 1. Decodifica instrução do IR
        instrucao_decodificada = self.decoder.decodificar(self.ir)
        
        # 2. Gera sinais de controle
        sinais_controle = self.controle.obter_sinais_controle(instrucao_decodificada)
        
        # 3. Lê operandos do banco de registradores
        operando_a = None
        operando_b = None
        
        tipo_instrucao = instrucao_decodificada['type']
        
        if tipo_instrucao == 'R':
            # Instruções tipo R (ALU): lê rb e rc
            # operand_a = valor de rb, operand_b = valor de rc
            rb = instrucao_decodificada.get('rb')
            rc = instrucao_decodificada.get('rc')
            
            if rb is not None:
                operando_a = self.registradores.ler(rb)
            if rc is not None:
                operando_b = self.registradores.ler(rc)
                
        elif tipo_instrucao == 'I':
            # Instruções tipo I: lê ra
            ra = instrucao_decodificada.get('ra')
            
            # Para LW: ra é destino, mas precisamos ler para calcular endereço se necessário
            # Para SW: ra é fonte (valor a armazenar)
            # Para LOADH/LOADL: ra é destino, pode precisar do valor atual
            if ra is not None:
                operando_a = self.registradores.ler(ra)
                
            # Para LOADH/LOADL, o operando_b será o imediato (tratado no estágio EX)
            
        elif tipo_instrucao == 'B':
            # Instruções tipo B (Branch): lê ra e rb para comparação
            ra = instrucao_decodificada.get('ra')
            rb = instrucao_decodificada.get('rb')
            
            if ra is not None:
                operando_a = self.registradores.ler(ra)
            if rb is not None:
                operando_b = self.registradores.ler(rb)
                
        elif tipo_instrucao == 'JR':
            # Jump Register: lê rc (registrador com endereço de destino)
            rc = instrucao_decodificada.get('rc')
            
            if rc is not None:
                operando_a = self.registradores.ler(rc)
                
        # Para tipo 'J' (Jump) e 'HALT': não precisam ler registradores
        
        return {
            'stage': 'ID',
            'decoded': instrucao_decodificada,
            'control_signals': sinais_controle,
            'operand_a': operando_a,
            'operand_b': operando_b
        }
    
    def _stage_ex_mem(self, decoded: dict, control_signals: dict,
                      operand_a: int, operand_b: int) -> dict:
        """
        Estágio EX/MEM (Execute and Memory) - Execução e Acesso à Memória.
        
        Operações realizadas:
        1. Executa operação na ALU (se instrução ALU)
        2. Calcula endereço efetivo (para LW/SW)
        3. Acessa memória (LW para leitura, SW para escrita)
        4. Resolve branches (JEQ/JNE)
        5. Calcula endereço de jump
        6. Atualiza flags
        
        Args:
            decoded: Instrução decodificada (do estágio ID)
            control_signals: Sinais de controle (do estágio ID)
            operand_a: Primeiro operando (do estágio ID)
            operand_b: Segundo operando (do estágio ID)
            
        Returns:
            dict com informações do estágio EX/MEM:
            {
                'stage': 'EX/MEM',
                'result': int,           # Resultado da ALU ou valor lido da memória
                'mem_address': int,      # Endereço de memória acessado (se aplicável)
                'branch_taken': bool,    # True se branch foi tomado
                'jump_address': int      # Endereço de destino do jump (se aplicável)
            }
        """
        resultado = None
        endereco_memoria = None
        branch_tomado = False
        endereco_jump = None
        
        opcode = decoded['opcode']
        tipo = decoded['type']
        
        # 1. Execução de operações ALU
        if control_signals['alu_op'] is not None:
            # Instrução usa ALU
            alu_op = control_signals['alu_op']
            
            # Determina operandos da ALU
            op_a = operand_a if operand_a is not None else 0
            op_b = operand_b if operand_b is not None else 0
            
            # Executa operação na ALU
            resultado, carry, overflow = self.alu.executar(alu_op, op_a, op_b)
            
            # Atualiza flags
            self.flags.atualizar_flags(resultado, carry, overflow)
        
        # 2. Instruções de Load/Store (LW/SW)
        if control_signals['mem_read'] or control_signals['mem_write']:
            # Calcula endereço efetivo: base (operand_a) + deslocamento (immediate)
            # Para LW: operand_a geralmente é 0 ou base, immediate é o endereço
            # Para SW: similar
            imediato = decoded.get('immediate', 0)
            
            # Endereço efetivo (considerando que immediate já é o endereço direto)
            endereco_memoria = imediato & 0xFFFF  # Mantém em 16 bits
            
            if control_signals['mem_read']:
                # LW: Lê palavra da memória
                resultado = self.memoria.ler(endereco_memoria)
                
            elif control_signals['mem_write']:
                # SW: Escreve palavra na memória
                # O valor a ser escrito está no registrador ra
                ra = decoded.get('ra')
                if ra is not None:
                    valor_escrever = self.registradores.ler(ra)
                    self.memoria.escrever(endereco_memoria, valor_escrever)
        
        # 3. Instruções LOADH e LOADL
        if opcode == 0x0E:  # LOADH
            # Carrega 16 bits nos 2 bytes mais significativos
            imediato = decoded.get('immediate', 0)
            # Mantém os 16 bits menos significativos do valor atual
            valor_atual = operand_a if operand_a is not None else 0
            baixos = valor_atual & 0x0000FFFF
            # Coloca immediate nos bits altos
            resultado = ((imediato & 0xFFFF) << 16) | baixos
            
        elif opcode == 0x0F:  # LOADL
            # Carrega 16 bits nos 2 bytes menos significativos
            imediato = decoded.get('immediate', 0)
            # Mantém os 16 bits mais significativos do valor atual
            valor_atual = operand_a if operand_a is not None else 0
            altos = valor_atual & 0xFFFF0000
            # Coloca immediate nos bits baixos
            resultado = altos | (imediato & 0xFFFF)
        
        # 4. Instruções de Branch (JEQ, JNE)
        if control_signals['branch']:
            # Compara operandos
            op_a = operand_a if operand_a is not None else 0
            op_b = operand_b if operand_b is not None else 0
            
            if opcode == 0x14:  # JEQ (Jump if Equal)
                branch_tomado = (op_a == op_b)
            elif opcode == 0x15:  # JNE (Jump if Not Equal)
                branch_tomado = (op_a != op_b)
            
            if branch_tomado:
                # Atualiza PC: PC = PC + offset
                offset = decoded.get('offset', 0)
                # PC já foi incrementado no estágio IF, então:
                # PC_novo = PC_atual + offset
                self.pc = (self.pc + offset) & 0xFFFF
        
        # 5. Instruções de Jump (JAL, JR, J)
        if control_signals['jump']:
            if opcode == 0x13:  # JR (Jump Register)
                # Jump para endereço no registrador rc
                endereco_jump = operand_a & 0xFFFF if operand_a is not None else 0
                
            elif opcode == 0x12:  # JAL (Jump and Link)
                # Salva PC+1 em R31 (será feito no estágio WB)
                # Obtém endereço de destino
                endereco_jump = decoded.get('address', 0)
                # O resultado será o PC atual (já incrementado) para salvar em R31
                resultado = self.pc
                
            elif opcode == 0x16:  # J (Jump incondicional)
                # Jump para endereço absoluto
                endereco_jump = decoded.get('address', 0)
            
            # Atualiza PC para o endereço de jump
            if endereco_jump is not None:
                self.pc = endereco_jump & 0xFFFF
        
        return {
            'stage': 'EX/MEM',
            'result': resultado,
            'mem_address': endereco_memoria,
            'branch_taken': branch_tomado,
            'jump_address': endereco_jump
        }
    
    def executar(self, max_ciclos: int = 10000, verboso: bool = False) -> dict:
        """
        Executa programa até HALT ou max_ciclos.
        
        Args:
            max_ciclos: Número máximo de ciclos a executar (padrão: 10000)
            verboso: Se True, imprime informações de debug durante execução
            
        Returns:
            dict com estatísticas da execução:
            {
                'ciclos': int,
                'instrucoes': int,
                'halted': bool,
                'pc_final': int,
                'registradores': dict,
                'flags': dict
            }
        """
        # TODO: Implementar em breve
        pass
    
    def passo(self) -> dict:
        """
        Executa uma instrução completa (4 estágios).
        
        Estágios:
        1. IF (Instruction Fetch): Busca instrução na memória
        2. ID (Instruction Decode): Decodifica instrução
        3. EX/MEM (Execute and Memory): Executa operação e acessa memória
        4. WB (Write Back): Escreve resultado
        
        Returns:
            dict com informações do ciclo:
            {
                'pc': int,
                'ir': int,
                'instrucao_decodificada': dict,
                'registradores_modificados': dict,
                'memoria_modificada': dict,
                'flags': dict
            }
        """
        # TODO: Implementar em breve
        pass
    
    def obter_estado(self) -> dict:
        """
        Retorna o estado atual completo do processador.
        
        Returns:
            dict com estado completo:
            {
                'pc': int,
                'ir': int,
                'halted': bool,
                'ciclos': int,
                'instrucoes': int,
                'registradores': dict,
                'flags': dict
            }
        """
        return {
            'pc': self.pc,
            'ir': self.ir,
            'halted': self.halted,
            'ciclos': self.ciclos,
            'instrucoes': self.instrucoes,
            'registradores': self.registradores.dump(),
            'flags': self.flags.dump()
        }
    
    def __str__(self) -> str:
        """
        Representação em string do processador.
        
        Returns:
            String com informações básicas do processador
        """
        return (
            f"Processor(pc={self.pc}, ir=0x{self.ir:08X}, "
            f"ciclos={self.ciclos}, instrucoes={self.instrucoes}, "
            f"halted={self.halted})"
        )
    
    def __repr__(self) -> str:
        """
        Representação técnica do processador.
        
        Returns:
            String com representação técnica
        """
        return self.__str__()