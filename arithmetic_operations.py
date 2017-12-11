# -*- coding: utf-8 -*-
"""
Created on Tue Sep 26 08:38:12 2017

@author: Arle
"""
from math import * 
import numpy as np


def ex_euclidian(a,b): 
    """
    The algorithm could be cleaner with divmod, but it keeps clear teh details of the algorithm 
    pgcd = s*a + t*b bezout
    L'algorithe retourne [d, s, t] avec d = PGCD(a,b) = s*a +t*b
    """
    if (a < b):
        temp = a
        a=b
        b=temp
        #print("a < b, breaking...")
        #return([0,0,0])
    
    c,d = a,b
    q = divmod(c, d)[0]
    r = c - q*d
    x = [1,0]
    y = [0,1]
    n = 1
    x[1], x[0] = q*x[1] + x[0], x[1]
    y[1],y[0] = q*y[1] + y[0], y[1]
    
    while r > 0:
        n = n+ 1
        c, d = d, r
        #print(c,d)
        
        
        q = divmod(c, d)[0]
        r = c - q*d
        
        #print(q,x,y)
        if r > 0:
            x[1], x[0] = q*x[1] + x[0], x[1]
            y[1],y[0] = q*y[1] + y[0], y[1]
            
            
    s = ((-1)**n)*x[1]
    t = ((-1)**(n+1))*y[1]
    result = [d, s, t]
    return(result)



def fast_exp(a, e, n):
    resultat = 1
    for i in range (1, ceil(log(e, 2))):
        if e % 2 == 1:
            resultat = resultat * a
        e = floor(e/2)    
        a = (a**2) % n
    return (resultat % n )

def mod_inverse(a, m):
    """
    Par Bezout, on a PGCD(a,m) = 1 = a*x+k*m admet des solutions si a et m sont premiers entre eux. 
        C'est à dire a*x = 1 [m] où x est l'inverse de a. Il suffit donc
        d'appliquer euclide étendu pour trouver l'inverse. 
    """
    
    euc = ex_euclidian(a,m)
    if euc[0] == 1:
        if a > m:
            inv = euc[1]
        else:
            inv = euc[2]
        if inv < 0:
            return(inv+m)
        else:
            return(inv)
    else:
        print("a and m are not relatively prime ; there is no inverse.")
        return(None)
    
    

def primes(lim):
    """
    Nombre : p=2i+1 | 3*p=6i+3=2*(3i+1)+1 | 5*p=10i+5=2*(5i+2)+1
    Indice :    i   |    3i+1 = i+p       |     5i+2 = i+2p
    """
    # Initialisation
    prime=[False, False]+[True]*(lim-1) # indices de 0 à lim
 
    # On lance le crible
    for p in range(2, int(lim**0.5)+1):
        if prime[p]: # p est premier
            prime[2*p::p]=[False]*(lim//p - 1)
        # mais les multiples suivants de p seront composés
 
    # Le crible est fini, on génère
    i=0
    primelist=[]
    for p in range(2, lim+1):
        if not prime[p]: 
            primelist[i] = p
            i = i+1
    return(primelist)

def mod_solver(ak, mk):
    """
    a an m are vector such that 
        x = a0 [m0] ; x = a1 [m1] ; etc...
    The solution exists in Z(M), M being the product of the mk
    """
    M = np.prod(mk)
    Mk = [M/m for m in mk]
    yk = [mod_inverse(Mk[k], mk[k]) for k in range(0,len(mk))]
    
    x = 0
    for k in range(0, len(mk)):
        x = x + ak[k]*yk[k]*Mk[k]
    
    return(x % M)

def decompo(c):
    p = primes(c**0.5)
 
    
    
        
        
        
    
    
    