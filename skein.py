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
        H = monoblock_ThreeFish(H, bytearray(currentTs.to_bytes(16, 'big')), cutBlock[:], blockSize )
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
    elif Nb == 32 and No == 128:
        C = 0
        
    T_cfg = 4*(2**120)
    T_msg = 48*(2**120)
    
    K_prime = bytearray(Nb//8)
    cutM = skein_cut_as_words(M)
    G0 = UBI(tf.cut_as_words(K_prime), C, T_cfg.to_bytes(16, 'big'), Nb)
    G1 = UBI(G0[:], cutM, T_msg.to_bytes(16, 'big'), Nb)
    H = skein_output(G1, Nb, 2)
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
            cutM.append(b'\x00\x00\x00\x00\x00\x00\x00\x00')
    return cutM

def monoblock_ThreeFish(K, T, P, blockSize):
    """
    K Block cipher key; a string of 32, 64, or 128 bytes (256, 512, or 1024 bits).
    T Tweak, a string of 16 bytes (128 bits).
    P Plaintext, a string of bytes of length equal to the key.
    """
    N = blockSize//64
    tweaks =[T[0:7], T[8:]]
    for i in range(0,76):
        if (i%4 == 0) or (i == 75):
            k = tf.key_generation(K, tweaks, N, i)
            for j in range(0, N): P[j] = tf.byte_xor(P[j], k[j])
            H = tf.tournee_threefish(P, N)
    return(H)


hashTest = simple_skein(256, 256, b'sadnightforthehosrsetofail')
