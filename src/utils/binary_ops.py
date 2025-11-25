"""
Módulo de operações binárias auxiliares para o simulador UFLA-RISC.
Fornece funções para manipulação de bits e conversões.
"""


def estender_sinal(valor: int, bits: int) -> int:
    """
    Estende sinal de um valor de N bits para 32 bits.
    
    Se o bit mais significativo (bit de sinal) for 1, preenche os bits
    superiores com 1s. Caso contrário, preenche com 0s.
    
    Args:
        valor: Valor a estender
        bits: Número de bits do valor original (1-32)
        
    Returns:
        Valor com sinal estendido para 32 bits
        
    Raises:
        ValueError: Se bits estiver fora do range 1-32
        TypeError: Se valor ou bits não forem inteiros
        
    Exemplos:
        >>> estender_sinal(0b11111111111111, 14)  # -1 em 14 bits
        4294967295  # -1 em 32 bits (0xFFFFFFFF)
        
        >>> estender_sinal(0b01111111111111, 14)  # +8191 em 14 bits
        8191  # +8191 em 32 bits
        
        >>> estender_sinal(0b10000000, 8)  # -128 em 8 bits
        4294967168  # -128 em 32 bits (0xFFFFFF80)
    """
    if not isinstance(valor, int):
        raise TypeError(f"valor deve ser um inteiro, recebido: {type(valor).__name__}")
    
    if not isinstance(bits, int):
        raise TypeError(f"bits deve ser um inteiro, recebido: {type(bits).__name__}")
    
    if bits < 1 or bits > 32:
        raise ValueError(f"bits deve estar entre 1 e 32, recebido: {bits}")
    
    # Cria máscara para os N bits
    mascara = (1 << bits) - 1
    valor = valor & mascara
    
    # Verifica se o bit de sinal está setado
    bit_sinal = 1 << (bits - 1)
    
    if valor & bit_sinal:
        # Bit de sinal é 1: número negativo
        # Preenche bits superiores com 1s
        extensao = ((1 << 32) - 1) ^ mascara  # Cria máscara de 1s nos bits superiores
        return valor | extensao
    else:
        # Bit de sinal é 0: número positivo
        # Bits superiores já são 0
        return valor


def para_unsigned_32(valor: int) -> int:
    """
    Converte valor para unsigned 32 bits (0 a 2^32-1).
    
    Garante que o valor esteja no range de 32 bits sem sinal,
    aplicando máscara de 32 bits.
    
    Args:
        valor: Valor inteiro (pode ser negativo)
        
    Returns:
        Valor como unsigned 32 bits (0 a 4294967295)
        
    Raises:
        TypeError: Se valor não for inteiro
        
    Exemplos:
        >>> para_unsigned_32(-1)
        4294967295  # 0xFFFFFFFF
        
        >>> para_unsigned_32(256)
        256
        
        >>> para_unsigned_32(0x1FFFFFFFF)  # Overflow de 32 bits
        4294967295  # Apenas 32 bits menos significativos
    """
    if not isinstance(valor, int):
        raise TypeError(f"valor deve ser um inteiro, recebido: {type(valor).__name__}")
    
    return valor & 0xFFFFFFFF


def para_signed_32(valor: int) -> int:
    """
    Converte valor unsigned 32 bits para signed (-2^31 a 2^31-1).
    
    Interpreta um valor de 32 bits como número com sinal em
    complemento de 2.
    
    Args:
        valor: Valor unsigned 32 bits (0 a 2^32-1)
        
    Returns:
        Valor interpretado como signed (-2147483648 a 2147483647)
        
    Raises:
        TypeError: Se valor não for inteiro
        
    Exemplos:
        >>> para_signed_32(0xFFFFFFFF)
        -1
        
        >>> para_signed_32(0x80000000)
        -2147483648
        
        >>> para_signed_32(0x7FFFFFFF)
        2147483647
    """
    if not isinstance(valor, int):
        raise TypeError(f"valor deve ser um inteiro, recebido: {type(valor).__name__}")
    
    # Garante 32 bits
    valor = valor & 0xFFFFFFFF
    
    # Verifica se bit de sinal (bit 31) está setado
    if valor & 0x80000000:
        # Número negativo: subtrai 2^32 para obter valor negativo
        return valor - 0x100000000
    else:
        # Número positivo
        return valor


def extrair_bits(valor: int, inicio: int, fim: int) -> int:
    """
    Extrai bits de uma posição [inicio:fim] (inclusive).
    
    Args:
        valor: Valor de 32 bits
        inicio: Bit inicial (MSB, 0-31)
        fim: Bit final (LSB, 0-31)
        
    Returns:
        Bits extraídos como inteiro (deslocados para LSB)
        
    Raises:
        ValueError: Se inicio ou fim estiverem fora do range ou inicio < fim
        TypeError: Se argumentos não forem inteiros
        
    Exemplos:
        >>> extrair_bits(0xABCD1234, 31, 24)
        171  # 0xAB
        
        >>> extrair_bits(0xABCD1234, 15, 8)
        18  # 0x12
        
        >>> extrair_bits(0b11110000, 7, 4)
        15  # 0b1111
    """
    if not isinstance(valor, int):
        raise TypeError(f"valor deve ser um inteiro, recebido: {type(valor).__name__}")
    
    if not isinstance(inicio, int):
        raise TypeError(f"inicio deve ser um inteiro, recebido: {type(inicio).__name__}")
    
    if not isinstance(fim, int):
        raise TypeError(f"fim deve ser um inteiro, recebido: {type(fim).__name__}")
    
    if inicio < 0 or inicio > 31:
        raise ValueError(f"inicio deve estar entre 0 e 31, recebido: {inicio}")
    
    if fim < 0 or fim > 31:
        raise ValueError(f"fim deve estar entre 0 e 31, recebido: {fim}")
    
    if inicio < fim:
        raise ValueError(
            f"inicio deve ser >= fim (MSB >= LSB), recebido: inicio={inicio}, fim={fim}"
        )
    
    # Número de bits a extrair
    num_bits = inicio - fim + 1
    
    # Cria máscara
    mascara = (1 << num_bits) - 1
    
    # Desloca e aplica máscara
    return (valor >> fim) & mascara


def definir_bits(valor: int, novos_bits: int, inicio: int, fim: int) -> int:
    """
    Define bits em uma posição [inicio:fim] (inclusive).
    
    Args:
        valor: Valor original de 32 bits
        novos_bits: Novos bits a serem inseridos
        inicio: Bit inicial (MSB, 0-31)
        fim: Bit final (LSB, 0-31)
        
    Returns:
        Valor com bits modificados
        
    Raises:
        ValueError: Se inicio ou fim estiverem fora do range ou inicio < fim
        TypeError: Se argumentos não forem inteiros
        
    Exemplos:
        >>> definir_bits(0x00000000, 0xFF, 31, 24)
        4278190080  # 0xFF000000
        
        >>> definir_bits(0xFFFFFFFF, 0x00, 15, 8)
        4294902015  # 0xFFFF00FF
    """
    if not isinstance(valor, int):
        raise TypeError(f"valor deve ser um inteiro, recebido: {type(valor).__name__}")
    
    if not isinstance(novos_bits, int):
        raise TypeError(f"novos_bits deve ser um inteiro, recebido: {type(novos_bits).__name__}")
    
    if not isinstance(inicio, int):
        raise TypeError(f"inicio deve ser um inteiro, recebido: {type(inicio).__name__}")
    
    if not isinstance(fim, int):
        raise TypeError(f"fim deve ser um inteiro, recebido: {type(fim).__name__}")
    
    if inicio < 0 or inicio > 31:
        raise ValueError(f"inicio deve estar entre 0 e 31, recebido: {inicio}")
    
    if fim < 0 or fim > 31:
        raise ValueError(f"fim deve estar entre 0 e 31, recebido: {fim}")
    
    if inicio < fim:
        raise ValueError(
            f"inicio deve ser >= fim (MSB >= LSB), recebido: inicio={inicio}, fim={fim}"
        )
    
    # Número de bits a modificar
    num_bits = inicio - fim + 1
    
    # Cria máscara para limpar bits antigos
    mascara = (1 << num_bits) - 1
    mascara_limpar = ~(mascara << fim)
    
    # Limpa bits antigos
    valor = valor & mascara_limpar
    
    # Insere novos bits
    novos_bits = (novos_bits & mascara) << fim
    
    return (valor | novos_bits) & 0xFFFFFFFF


def binario_para_hex(valor: int) -> str:
    """
    Converte inteiro para string hexadecimal.
    
    Args:
        valor: Valor inteiro
        
    Returns:
        String no formato '0xABCD1234' (8 dígitos hex)
        
    Raises:
        TypeError: Se valor não for inteiro
        
    Exemplos:
        >>> binario_para_hex(305419896)
        '0x12345678'
        
        >>> binario_para_hex(0)
        '0x00000000'
    """
    if not isinstance(valor, int):
        raise TypeError(f"valor deve ser um inteiro, recebido: {type(valor).__name__}")
    
    # Garante 32 bits
    valor = valor & 0xFFFFFFFF
    
    return f"0x{valor:08X}"


def hex_para_binario(hex_str: str) -> int:
    """
    Converte string hexadecimal para inteiro.
    
    Args:
        hex_str: String hexadecimal (com ou sem prefixo '0x')
        
    Returns:
        Valor inteiro
        
    Raises:
        ValueError: Se a string não for hexadecimal válida
        TypeError: Se hex_str não for string
        
    Exemplos:
        >>> hex_para_binario('0x12345678')
        305419896
        
        >>> hex_para_binario('ABCD1234')
        2882343476
    """
    if not isinstance(hex_str, str):
        raise TypeError(f"hex_str deve ser uma string, recebido: {type(hex_str).__name__}")
    
    # Remove espaços
    hex_str = hex_str.strip()
    
    # Remove prefixo se presente
    if hex_str.startswith('0x') or hex_str.startswith('0X'):
        hex_str = hex_str[2:]
    
    try:
        valor = int(hex_str, 16)
        return valor & 0xFFFFFFFF
    except ValueError as e:
        raise ValueError(f"String hexadecimal inválida: '{hex_str}'") from e


def string_binaria_para_int(bin_str: str) -> int:
    """
    Converte string binária para inteiro.
    
    Remove espaços e underscores para facilitar leitura.
    
    Args:
        bin_str: String binária (ex: '0000 0001' ou '0b00000001')
        
    Returns:
        Valor inteiro
        
    Raises:
        ValueError: Se a string não for binária válida
        TypeError: Se bin_str não for string
        
    Exemplos:
        >>> string_binaria_para_int('00000001 00000000')
        256
        
        >>> string_binaria_para_int('0b11111111')
        255
        
        >>> string_binaria_para_int('1111_0000_1010_0101')
        61605
    """
    if not isinstance(bin_str, str):
        raise TypeError(f"bin_str deve ser uma string, recebido: {type(bin_str).__name__}")
    
    # Remove espaços e underscores
    bin_str = bin_str.replace(' ', '').replace('_', '').strip()
    
    # Remove prefixo se presente
    if bin_str.startswith('0b') or bin_str.startswith('0B'):
        bin_str = bin_str[2:]
    
    try:
        valor = int(bin_str, 2)
        return valor
    except ValueError as e:
        raise ValueError(f"String binária inválida: '{bin_str}'") from e


def int_para_string_binaria(valor: int, bits: int = 32) -> str:
    """
    Converte inteiro para string binária de N bits.
    
    Args:
        valor: Valor inteiro
        bits: Número de bits na representação (padrão: 32)
        
    Returns:
        String binária (ex: '00000001000000000000000000000000')
        
    Raises:
        ValueError: Se bits < 1 ou se valor não couber em N bits
        TypeError: Se argumentos não forem inteiros
        
    Exemplos:
        >>> int_para_string_binaria(256, 32)
        '00000000000000000000000100000000'
        
        >>> int_para_string_binaria(15, 8)
        '00001111'
        
        >>> int_para_string_binaria(255, 8)
        '11111111'
    """
    if not isinstance(valor, int):
        raise TypeError(f"valor deve ser um inteiro, recebido: {type(valor).__name__}")
    
    if not isinstance(bits, int):
        raise TypeError(f"bits deve ser um inteiro, recebido: {type(bits).__name__}")
    
    if bits < 1:
        raise ValueError(f"bits deve ser >= 1, recebido: {bits}")
    
    # Garante que valor está no range de N bits
    mascara = (1 << bits) - 1
    valor = valor & mascara
    
    # Converte para binário com padding
    return format(valor, f'0{bits}b')


def int_para_string_binaria_formatada(valor: int, bits: int = 32, grupo: int = 8) -> str:
    """
    Converte inteiro para string binária formatada com espaços.
    
    Args:
        valor: Valor inteiro
        bits: Número de bits na representação (padrão: 32)
        grupo: Tamanho do grupo para separação (padrão: 8)
        
    Returns:
        String binária formatada (ex: '00000001 00000000 00000000 00000000')
        
    Raises:
        ValueError: Se bits < 1 ou grupo < 1
        TypeError: Se argumentos não forem inteiros
        
    Exemplos:
        >>> int_para_string_binaria_formatada(256, 32, 8)
        '00000000 00000000 00000001 00000000'
        
        >>> int_para_string_binaria_formatada(0xABCD, 16, 4)
        '1010 1011 1100 1101'
    """
    if not isinstance(grupo, int):
        raise TypeError(f"grupo deve ser um inteiro, recebido: {type(grupo).__name__}")
    
    if grupo < 1:
        raise ValueError(f"grupo deve ser >= 1, recebido: {grupo}")
    
    # Obtém string binária sem formatação
    bin_str = int_para_string_binaria(valor, bits)
    
    # Adiciona espaços a cada N bits
    grupos = []
    for i in range(0, len(bin_str), grupo):
        grupos.append(bin_str[i:i+grupo])
    
    return ' '.join(grupos)