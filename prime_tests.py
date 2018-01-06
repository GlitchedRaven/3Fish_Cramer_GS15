
import os
import random
from math import gcd
from math import log
from math import floor

def load_first_primes(path='fisrt_primes'):
    # loads the first prime integers from a file, to avoid generating them each time from a sieve
    path = os.path.join(os.getcwd(), path)
    first_prime_file = open(path)
    first_primes = [int(s) for s in first_prime_file.read().split() if s.isdigit()]
    return first_primes

def Erathostenes(B):
    # Implementation of the Erathostenes sieve
    # It will list all prime integers up to a threshold B
    # Can be heavy on ressource since all integers must be compared to the list of composite integers up to it
    composed = []
    p=2
    # we list all composed integers by generating them from each prime being multiplied until the threshold is reached
    while (p * p <= B):
        if p not in composed:
            for c in range(p*2, B+1, p):
                composed.append(c)
        p += 1

    # Then every remaining integer not in that composed list must be a prime integer
    # We create that first prime list and return it
    prime_sieve = []
    for n in range(2,B):
        if n not in composed:
            prime_sieve.append(n)
    return prime_sieve

def test_first_primes(n, B):
    # A test to verify if an integer n is divideable by a list of first prime integers
    first_primes = load_first_primes()
    for prime_index in list(range(B)):
        prime = first_primes[prime_index]

        if prime < n:
            if n % prime == 0:
                return False
    return True

def factorise(n, p=2):
    # for an integer n, this fuction will find d and s such as n-1 = d * 2^s
    d = n-1
    s = 0
    q = p
    while d%q == 0:
        s+=1
        if p == 2:
            d>>=1
        else:
            q *= p
    return s, d //(q//p)

def Miller_Rabin_test(n, k):
    #Test de primalite sur n avec proba 1/4 ^ k de faux positif
    # n is the integer to be tested and k is the number of random candidates
    # that will be potential Rabin Miller witnesses
    if not n >= 2:
        return False
    if n == 2:
        return True

    s, d = factorise(n)

    def is_composite(a, s, d, n):
        # Miller Rabin primality test for a potential winess a
        # For an integer a, we verify that no power of a is a divider of n
        # From Fermat: if a^(n-1) != -1 then a^d != -1 and n is not prime
        # We have to cycle trough every a^(d*2*k) and asses the compositiveness of n
        x = pow(a, d, n)

        if x == 1 or x == n-1:
            return False
        else:
            for r in list(range(0,s-1)):
                x = pow(x, 2, n)
                if x == n - 1:
                    return False
                elif x == 1:
                    return True
            return True


    for round in list(range(k)):
        # for each round up to k, we randomly pick a and proceed to check if it is a Miller Rabin witness of n
        a = random.randint(2, n-1)
        if is_composite(a, s, d, n):
            return False
    return True

def Jacobi_symol(a, n):
    # Computation of the Jacobi symbol (a/n)
    if n <= 0 or n%2 ==0:
        return 0
    if a == 0 or a == 1:
        return a
    j = 1
    if a < 0:
        a = -a
        if n % 4 == 3:
            j = -j
    while (a!=0):
        while (a%2 ==0):
            a>>=1
            if n % 8 == 3 or n % 8 == 5:
                j=-j
        a,n = n,a
        if a % 4 ==3 and n % 4 == 3:
            j=-j
        a = a % n
    if n == 1:
        return j
    else:
        return 0


def Solovay_Strassen(n, k):

    def Lagrange_symbol(a, n):
        return pow(a,(n-1)/2, n)
    m = n - 1
    for round in list(range(k)):
        a = random.randint(2, m)
        j = Jacobi_symol(a, n)
        l = Lagrange_symbol(a, n)

        if l !=1 and l != 0:
            l = -1

        if j == 0 or j!= l:
            return False
    return True

def Lucas_test(n):
    def Selfridge_params(n):
        d = 5
        s = 1
        ds = d * s
        while True:
            if gcd(ds, n) > 1:
                return ds, 0, 0
            if Jacobi_symol(ds, n) == -1:
                return ds, 1, (1 - ds) / 4
            d += 2
            s *= -1
            ds = d * s
    def lucas_sequence(n, u1, v1, u2, v2, d, q, m):
        k = q
        while m > 0:
            u2 = u2*v2% n
            v2 = v2*v2-2*q
            q = (q*q)%n
            if m%2 ==0:
                t1, t2 = u2 * v1, u1 * v2
                t3, t4 = v2 * v1, u2 * u1 * d
                u1, v1 = t1 + t2, t3 + t4
                if u1 != 1:
                    u1 = u1 + n
                if v1 != 1:
                    v1 = v1 + n
                u1, v1 = (u1 / 2) % n, (v1 / 2) % n
                k = (q * k) % n
            m = m >> 1
        return u1, v1, k

    d, p, q = Selfridge_params(n)
    if p == 0:
        return n == d

    s, t = factorise(n)

    u, v, k = lucas_sequence(n, 1, p, 1, p, d, q, t>>1)

    if u ==0 or v ==0:
        return False
    for i in list(range(1,s)):
        v = (v*v - 2*k)%n
        k = (k*k)%n
        if v==0:
            return False
    return True

def is_square(n):
    # A test to quickly verify if an integer n is not another integer's square
    # It can usefully eleminate some non prime numbers that could be resistent to Miller Rabin
    def bitlength(x):
        return int(log(n, 2)) + 1

    x = int(n)
    if x == 0:
        return False
    a, b = divmod(bitlength(x), 2)
    s = 2**(a+b)
    while True:
        y = (s+x //s) >>1
        if y>= s:
            if s*s==n:
                return s
            else:
                return False
        s = y

def Baillie_PSW(n, k, B):
    if n== 1:
        return False
    if n <2 or is_square(n):
        return False

    #check des premiers primes ou autre crible
    for i in list(range(3, B+1, 2)):
        if n % i == 0:
            if n == i:
                return True
            else:
                return False


    if not Miller_Rabin_test(n, k):
        return False
    if not Lucas_test(n):
        return False
    return True

def Pollard(n, B, k):
    m = n - 1
    for round in list(range(k)):
        a = random.randint(2, m)
        first_primes = load_first_primes()
        for prime_index in list(range(B)):
            prime = first_primes[prime_index]
            e = floor(log(B,2)/log(prime,2))
            exposant = pow(prime, e)
            a = pow(a, exposant, n)
        g = gcd(a - 1, n)

        if g != 1 and g != n:
            return False
    else:
        return True




