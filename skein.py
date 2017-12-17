# -*- coding: utf-8 -*-
"""
Created on Wed Dec 13 18:09:24 2017

@author: Arle
"""
import threefish as tf
import sys

def UBI(G, M, Ts, blockSize):
    """
    G a starting value of Nb bytes.
    M a message string of arbitrary bit length up to 299 􀀀 8 bits, encoded in a string of bytes.
    Ts a 128-bit integer that is the starting value for the tweak. 
    
    ToBytes(Ts + min(NM; (i + 1)Nb) + ai2126 + bi(B2119 + 2127);
    """
    N = blockSize // 64
    cutM = block_padding(tf.cut_as_words(M), blockSize) # Cut as word of 64 bit and pad it
    
    Nm = len(cutM)
    Nb = N * 8
    
    H = G
    for i in range(0, len(cutM)):
        if i == 0: tweakAddition = (2**126)
        elif i == len(cutM): tweakAddition = ((178**119)+(2**127))
        else: tweakAddition = 0
        
        currentTs = Ts + min(Nm, (i+1)*Nb) + tweakAddition
        currentM = cutM[i]
        H = monoblock_ThreeFish(H, currentTs.to_bytes(16, sys.byteorder), currentM )
        for j in range(0, N): H[j] = tf.byte_xor(H[j], currentM[j])
    
    


def skein(Nb, No, K):
    """ 
    Skein main function, 
    Nb = block state size in bits
    No = output size in bits
    K = key of Nk bits, can be set to 0 if needed
    """
    
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
    for i in range(0,76):
        if (i%4 == 0) or (i == 75):
            k = tf.key_generation(K, T, N, i)
            for j in range(0, N): H[j] = tf.byte_xor(P[j], k[j])
            H = tf.tournee_threefish(P, N)
    return(H)
