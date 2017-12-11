# -*- coding: utf-8 -*-
"""
Created on Mon Nov 20 14:01:22 2017

@author: Arle
"""
"""CONSTANT"""
#CONST_2pow64 = 2**64
"""
TEST VALUES
"""
key1 = bytearray(b'\x86\x69\xbb\xc5\x0d\xd3\xfc\x1c\x4b\x0a\xa3\xcc\x1f\x0b\x90\x3d\xac\xce\xc9\xa8\xec\xe3\xe5\xec\xcb\x2b\xea\xda\x34\xbb\x8d\x6c')
tweaks = [None]*2
tweaks[0] = bytearray(b'\xf1\x5c\x24\x4f\x22\xd1\xd2\x81')
tweaks[1] = bytearray(b'\x60\x6c\x16\x69\x0a\xca\xf9\xc6')



file = 'C:\\Users\\Arle\\Desktop\\GS15\\test.txt'

from functools import reduce
from collections import deque
from bitstring import BitArray
from itertools import chain

def read_file_as_bits(filename): # On l'implementera peut-etre sous forme de flux, à voir
    
    with open(filename, "rb") as binary_file:
        # Read the whole file at once
        return binary_file.read()
        #print(data)
        """
        # Seek position and read N bytes
        binary_file.seek(0)  # Go to beginning
        couple_bytes = binary_file.read(2)
        print(couple_bytes)
        """
def write_file_from_bytes(f, path):
    # Open a file
    fo = open("C:\\Users\\Arle\\Desktop\\GS15\\"+path, "wb")
    for m in f:fo.write(m)
    # Close opend file
    fo.close()

def bitstring_to_bytes(s):
    return int(s, 2).to_bytes(len(s) // 8, byteorder='big')

def addition_nocarry(a,b): 
    """
    Beware, bytes are read left to right
    """
    result = bytearray()
    carry = 0
    for byte1, byte2 in zip(a,b):
        byte_res = (byte1+byte2+carry)
        #print(byte_res)
        if byte_res > 255:
            carry = 1
            result.append(byte_res%256)
        else:
            carry = 0
            result.append(byte_res)
    return(result)
def substraction_nocarry(a,b): #Beware, it is not commuative
    """
    Beware, bytes are read left to right
    """
    result = bytearray()
    carry = 0
    for byte1, byte2 in zip(a,b):
        byte_res = (byte1-byte2-carry)
        #print(byte_res)
        if byte_res < 0:
            carry = 1
            result.append(byte_res%256)
        else:
            carry = 0
            result.append(byte_res)
    return(result)

def circular_permutation_left(m, R): # Tested and works
    rol_m = BitArray(m)
    rol_m.rol(R)
    return(bytearray(rol_m.bytes))

def circular_permutation_right(m, R): # Tested and works
    ror_m = BitArray(m)
    ror_m.ror(R)
    return(bytearray(ror_m.bytes))

def byte_xor(m1,m2): # Tested and works
    return(bytearray(a ^ b for a,b in zip(m1,m2)))
        
def key_generation(K,tweaks,N,i): 
    """
    N = number of cuts
    K = Key
    tweaks = two tweaks block cypher 
    i = numéro de la tournée
    """
    C = bytes(b'\x1b\xd1\x1b\xda\xa9\xfc\x1a\x22')
    tweaks.append(bytearray(a ^ b for a,b in zip(tweaks[0],tweaks[1])))
    K.append(bytearray(b'\x00\x00\x00\x00\x00\x00\x00\x00'))
    
    for m in range(0,N): K[-1] = bytearray(a ^ b for a,b in zip(K[-1],K[m]))
    
    K[-1] = bytearray(a ^ b for a,b in zip(K[-1],C))
    k = []
    for n in range(0, N-3): k.append(K[(n+i) % (N+1)]) # n = 0 => N-4
        
    k.append((addition_nocarry(K[(N-3+i) % (N+1)] , tweaks[i%3] )))
    k.append((addition_nocarry(K[(N-2+i) % (N+1)] , tweaks[(i+1)%3] )))
    k.append((addition_nocarry(K[(N-1+i) % (N+1)], bytearray([i % 3]+7*[0]) )))
    
    return k

def sub_primitive_mix(m1, m2, R):# Tested and works
    m1_prime = addition_nocarry(m1, m2)
    m2_prime = byte_xor(m1_prime, circular_permutation_left(m2, R))
    return(m1_prime, m2_prime)

def sub_primitive_mixinv(m1_prime, m2_prime, R):# Tested and works, inverts correctly
     m2 = circular_permutation_right(byte_xor(m1_prime, m2_prime), R)
     m1 = substraction_nocarry(m1_prime, m2)
     return(m1, m2)
def perm_primitive_test(M):
    l = len(M)
    M[0], M[l-1] = M[l-1], M[0]
    M[1], M[l-2] = M[l-2], M[1]
    return(M)

def tournee_threefish(M, N):# Tested and works   
    #Subsitution
    for p in range(0,N//2):
        M[2*p], M[2*p + 1] = sub_primitive_mix(M[2*p], M[2*p+1], 4)
    #Permutation
    #M = perm_primitive_test(M)
    return(M)

def tournee_threefish_inv(M, N):# Tested and works   
     #Permutation
    #M = perm_primitive_test(M)
    #Subsitution
    for p in range(0,N//2):
        M[2*p], M[2*p + 1] = sub_primitive_mixinv(M[2*p], M[2*p+1], 4)
   
    return(M)    
    
def cut_as_words(M, l=8):
    """
    M : bytearray to cut, interpreted as hex
    l = length of a word in bytes
    """
    if len(M)%l == 0 :
        N = (len(M)//l)
        cutM = [None] * N
        for m in range(0,N): cutM[m] = M[l*m:l*(m+1)]
    else:
        N = (len(M)//l)
        cutM = [None] * (N+1)
        for m in range(0,N): cutM[m] = M[l*m:l*(m+1)]
        cutM[-1]=M[(N)*l:] + bytearray([0]*(l-len(M[(N)*l:] )))
        
    return(cutM)
    
def CBC_ThreeFish_encrypt(plaintext, block_len, K, tweaks):
    N = block_len//64
    cutPlain = cut_as_words(plaintext)
    cyphertext = [None]*((len(plaintext)*8)//block_len)
    for m in range(0,(len(plaintext)*8)//block_len):
        cutBlock = cutPlain[N*m:N*(m+1)]
        for i in range(0,76):
            if (i%4 == 0) or (i == 75):
                k = key_generation(K, tweaks, N, i)
                for j in range(0, N):
                    cutBlock[j] = byte_xor(cutBlock[j], k[j])
            #print("Block : {} , Tournée : {}, Plaintext : {}, Key : {}".format(m, i, cutBlock, K))
            cutBlock = tournee_threefish(cutBlock, N)
        cyphertext[m] = cutBlock
            
                
        
    
    return(cyphertext)

def CBC_ThreeFish_decrypt(cyphertext, block_len, K, tweaks):
    N = block_len//64
    cutCypher = cut_as_words(cyphertext)
    plaintext = [None]*((len(cyphertext)*8)//block_len)
    keys = [key_generation(K, tweaks, N, i) for i in range(0,76)]
    for m in range(0,(len(cyphertext)*8)//block_len):
        cutBlock = cutCypher[N*m:N*(m+1)]
       
        for l in range(0,76):
            i = 75 - l
            cutBlock = tournee_threefish_inv(cutBlock, N)
            if (i%4 == 0) or (i == 75):
                k = keys[i]
                for j in range(0, N):
                    cutBlock[j] = byte_xor(cutBlock[j], k[j])            
        plaintext[m] = cutBlock
            
                
        
    
    return(plaintext)

key2 = cut_as_words(key1)
plaintext = read_file_as_bits(file)
path_c = "test2.txt"
path_dec = "test3.txt"
c = list(chain.from_iterable(CBC_ThreeFish_encrypt(plaintext, 256, key2, tweaks)))
write_file_from_bytes(c, path_c)
key2 = cut_as_words(key1)
cyphertext = read_file_as_bits('C:\\Users\\Arle\\Desktop\\GS15\\'+path_c)
dec = list(chain.from_iterable(CBC_ThreeFish_decrypt(cyphertext, 256, key2, tweaks)))
write_file_from_bytes(dec, path_dec)