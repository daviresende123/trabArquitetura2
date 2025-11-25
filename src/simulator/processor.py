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