# -*- coding: utf-8 -*-
"""
Created on Wed Dec 13 18:09:24 2017

@author: Arle
"""
import threefish as tf
from math import ceil
from itertools import chain

def skein_cut_as_words(M, l=8):
    """
    M : bytearray to cut, interpreted as hex
    l = length of a word in bytes
    
    Use specific padding for UBI tweaking
    """
    if len(M)%l == 0 :
        N = (len(M)//l)
        cutM = [None] * N
        for m in range(0,N): cutM[m] = M[l*m:l*(m+1)]
    else:
        N = (len(M)//l)
        cutM = [None] * (N+1)
        for m in range(0,N): cutM[m] = M[l*m:l*(m+1)]
        cutM[-1]=M[(N)*l:] + bytearray(b'\x80') + bytearray([0]*(l-len(M[(N)*l:] )-1))
        
    return(cutM)
def UBI(G, M, Ts, blockSize):
    """
    G a starting value of Nb bytes.
    M a message string of arbitrary bit length up to 299 􀀀 8 bits, encoded in a string of bytes.
    Ts a 128-bit integer that is the starting value for the tweak. 
    
    ToBytes(Ts + min(NM; (i + 1)Nb) + ai2126 + bi(B2119 + 2127);
    """
    N = blockSize // 64
    cutM = block_padding(M, blockSize) # Cut as word of 64 bit and pad it
    blockNumber = ((len(cutM)*64)//blockSize)
    
    Nm = len(cutM)
    Nb = N * 8
    
    H = G
    for i in range(0,blockNumber):
        cutBlock = cutM[N*i:N*(i+1)]
        if i == 0: tweakAddition = (2**126)
        elif i == len(cutM): tweakAddition = ((178**119)+(2**127))
        else: tweakAddition = 0
        
        currentTs = int.from_bytes(Ts, 'big') + min(Nm, (i+1)*Nb) + tweakAddition
        H = monoblock_ThreeFish(H[:], bytearray(currentTs.to_bytes(16, 'big')), cutBlock[:], blockSize )
        for j in range(0, N): H[j] = tf.byte_xor(H[j], cutBlock[j])
        
    return(H)
    
    

def skein_output(G,Nb, iterations):
    T_out = 63*(2**120)
    O = []
    for i in range(0, iterations):
        O.append(UBI(G[:], [bytearray(i.to_bytes(8, 'big'))], T_out.to_bytes(16, 'big'),Nb))
    return list(chain.from_iterable(O))
    
def simple_skein(Nb, No, M):
    """ 
    Skein main function, 
    Nb = block state size in bytes. Must be 32, 64, or 128.
    No = output size in bits
    M = The message to be hashed, a string of up to 299 􀀀 8 bits (296 􀀀 1 bytes)
    K = key of Nk bits, can be set to 0 if needed
    """
    if Nb == 256 and No == 256: 
        C = [0xFC9DA860D048B449.to_bytes(8, 'big'), 0x2FCA66479FA7D833.to_bytes(8, 'big'), 0xB33BC3896656840F.to_bytes(8, 'big'), 0x6A54E920FDE8DA69.to_bytes(8, 'big')]
    elif Nb == 512 and No == 512:
         C = [0x4903ADFF749C51CE.to_bytes(8, 'big'), 0x0D95DE399746DF03.to_bytes(8, 'big'), 0x8FD1934127C79BCE.to_bytes(8, 'big'), 0x9A255629FF352CB1.to_bytes(8, 'big'), 0x5DB62599DF6CA7B0.to_bytes(8, 'big'), 0xEABE394CA9D5C3F4.to_bytes(8, 'big'), 0x991112C71A75B523.to_bytes(8, 'big'), 0xAE18A40B660FCC33.to_bytes(8, 'big')]
    elif Nb == 512 and No == 256:
        C = [0xCCD044A12FDB3E13.to_bytes(8, 'big'), 0xE83590301A79A9EB.to_bytes(8, 'big'), 0x55AEA0614F816E6F.to_bytes(8, 'big'), 0x2A2767A4AE9B94DB.to_bytes(8, 'big'), 0xEC06025E74DD7683.to_bytes(8, 'big'), 0xE7A436CDC4746251.to_bytes(8, 'big'), 0xC36FBAF9393AD185.to_bytes(8, 'big'), 0x3EEDBA1833EDFC13.to_bytes(8, 'big')]
    elif Nb == 1024  and No == 1024:
        C = [0xD593DA0741E72355.to_bytes(8, 'big'), 0x15B5E511AC73E00C.to_bytes(8, 'big'), 0x5180E5AEBAF2C4F0.to_bytes(8, 'big'), 0x03BD41D3FCBCAFAF.to_bytes(8, 'big'),0x1CAEC6FD1983A898.to_bytes(8, 'big'), 0x6E510B8BCDD0589F.to_bytes(8, 'big'), 0x77E2BDFDC6394ADA.to_bytes(8, 'big'), 0xC11E1DB524DCB0A3.to_bytes(8, 'big'),0xD6D14AF9C6329AB5.to_bytes(8, 'big'), 0x6A9B0BFC6EB67E0D.to_bytes(8, 'big'), 0x9243C60DCCFF1332.to_bytes(8, 'big'), 0x1A1F1DDE743F02D4.to_bytes(8, 'big'),0x0996753C10ED0BB8.to_bytes(8, 'big'), 0x6572DD22F2B4969A.to_bytes(8, 'big'), 0x61FD3062D00A579A.to_bytes(8, 'big'), 0x1DE0536E8682E539.to_bytes(8, 'big')]
    T_cfg = 4*(2**120)
    T_msg = 48*(2**120)
    
    K_prime = bytearray(Nb//8)
    cutM = skein_cut_as_words(M)
    G0 = UBI(tf.cut_as_words(K_prime), C, T_cfg.to_bytes(16, 'big'), Nb)
    G1 = UBI(G0[:], cutM, T_msg.to_bytes(16, 'big'), Nb)
    H = skein_output(G1, Nb, 1)
    H = b''.join(H)
    return(H[0:ceil(No/8)])
def block_padding(cutM, blockSize):
    """
    M is a list of 64 bits words
    blocksize, blocksize for padding
    """
    N = blockSize // 64
    if (len(cutM) % N) != 0:
        for i in range(1,(N * ((len(cutM) // N ) + 1) - len(cutM))+1):
            cutM.append(bytearray(b'\x00\x00\x00\x00\x00\x00\x00\x00'))
    return cutM

def monoblock_ThreeFish(K, T, P, blockSize):
    """
    K Block cipher key; a string of 32, 64, or 128 bytes (256, 512, or 1024 bits).
    T Tweak, a string of 16 bytes (128 bits).
    P Plaintext, a string of bytes of length equal to the key.
    """
    N = blockSize//64
    tweaks =[T[0:8], T[8:]]
    keys = [tf.key_generation(K[:], tweaks[:], N, i) for i in range(0,76)]
    for i in range(0,76):
        if (i%4 == 0) or (i == 75):
            #k = tf.key_generation(K[:], tweaks, N, i)
            k = keys[i]
            for j in range(0, N): P[j] = tf.byte_xor(P[j], k[j])
        H = tf.tournee_threefish(P, N)
    return(H)


#hashTest = simple_skein(256, 256, b'sadnightforthehosrsetofailmustgointothe123456789sadnightforthehosrsetofailmustgointothe12345678sadnightforthehosrsetofailmustgointothe123456789')

#g0 = [bytearray(b'\ng\x19\xc2[\xfa\xb3'), bytearray(b'Z\xb2\x81\xa8\xad\xaf\x8b'), bytearray(b'\xf9a\x9e\x18\xa56#'), bytearray(b'\xf24\xa3\xe5q\xbc\xf4')]
#T_out = 63*(2**120)
#b = [b'\x00\x00\x00\x00\x00\x00\x00\x00', b'\x00\x00\x00\x00\x00\x00\x00\x00', b'\x00\x00\x00\x00\x00\x00\x00\x00', b'\x00\x00\x00\x00\x00\x00\x00\x00']