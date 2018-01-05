
import random
import json
from math import gcd
from math import log
from math import floor
import binascii
import hashlib

class LFSR:
    def __init__(self, memory_size, xor_points_list=[]):
        self._memory = [0 for i in list(range(memory_size))]
        self._xor_map = xor_points_list
        self._output = []

    def display_memory(self):
        print(self._memory)

    def display_output(self):
        print(self._output)

    def start(self, iv=[1]):
        if len(iv) < len(self._memory):
            iv.extend([0 for i in list(range(len(self._memory)-len(iv)))])
            self._memory = iv

        else:
            self._memory = iv[0:len(self._memory)-1]

    def rand_gen(self, rand_lenght, offset=0):
        number_rounds = rand_lenght + offset

        key_gen = []
        for round in list(range(number_rounds+1)):
            xor_res = 0
            #(self._memory)
            for term in self._xor_map:

                xor_res += self._memory[term-1]
                xor_res = xor_res%2
            self._output.append(xor_res)
            self._memory.append(xor_res)
            self._memory = self._memory[1:]

            if round > offset:
                key_gen.append(xor_res)

        return key_gen


    def clear(self):
        self._memory = [0 for i in list(range(len(self._memory)-1))]
        self._output = []

def load_first_primes():
    first_prime_file = open('first_primes')
    first_primes = [int(s) for s in first_prime_file.read().split() if s.isdigit()]
    return first_primes

def Erathostenes(B):
    composed = []
    p=2
    while (p * p <= B):
        if p not in composed:
            for c in range(p*2, B+1, p):
                composed.append(c)
        p += 1

    prime_sieve = []
    for n in range(2,B):
        if n not in composed:
            prime_sieve.append(n)
    return prime_sieve

def test_first_primes(n, B):
    first_primes = load_first_primes()
    for prime_index in list(range(B)):
        prime = first_primes[prime_index]

        if prime < n:
            if n % prime == 0:
                return False
    return True

def factorise(n, p=2):
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
    if not n >= 2:
        return False
    if n == 2:
        return True

    s, d = factorise(n)

    def is_composite(a, s, d, n):
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
        a = random.randint(2, n-1)
        if is_composite(a, s, d, n):
            return False
    return True

def Jacobi_symol(a, n):
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
            u2 = (u2*v2)% n
            v2 = (v2*v2-2*q)
            q= (q*q)%n
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


if __name__ == '__main__':

    def pick_candidate(length):
        range_start = (2**(length-1))
        range_end = (2**length)-1
        candidate = random.randint(range_start, range_end)

        return candidate

    def pick_prime(length=64):
        prime= 0
        while prime == 0:
            candidate = pick_candidate(length)
            if Baillie_PSW(candidate, 2, 800):
                prime = candidate
        return prime

    def is_smooth(p, k=2, B=800):
        if p % 2 != 0:
            q = (p-1)//2
            if Baillie_PSW(q, k, B):
                return False
            else:
                return True
        else:
            return True

    def find_generator(p):
        q = (p-1)//2
        h = 0
        while h == 0:
            candidate = random.randint(2, p-1)
            if pow(candidate, (p-1)//q, p) !=1:
                h = candidate
        return h


    def generate_keys(length=8):
        length*=8
        p = pick_prime(length)
        alpha1 = find_generator(p)
        alpha2 = find_generator(p)
        while alpha1 == alpha2:
            alpha2 = find_generator(p)
        x1 = random.randint(2, p-1)
        x2 = random.randint(2, p-1)
        y1 = random.randint(2, p-1)
        y2 = random.randint(2, p-1)
        w = random.randint(2, p-1)
        X = (pow(alpha1, x1, p)*pow(alpha2, x2, p))%p
        Y = (pow(alpha1, y1, p)*pow(alpha2, y2, p))%p
        W = pow(alpha1, w, p)

        key_data = {'public key':
                               {'p': p,
                                'alpha1': alpha1,
                                'alpha2': alpha2,
                                'X':X,
                                'Y':Y,
                                'W':W,
                                },
                           'private key':
                               {'x1': x1,
                                'x2': x2,
                                'y1': y1,
                                'y2': y2,
                                'w': w
                                }
                           }

        with open('keys.json', 'w') as keydatafile:
            json.dump(key_data, keydatafile,indent=4, sort_keys=True)

        return key_data

    def byte_len(x):
        s = bin(x)
        s = s.lstrip('-0b')
        return (len(s)//8)+1

    def encode_block(block,p, b, B1, B2, W, block_num):

        block = int.from_bytes(block, byteorder='big')

        c = int((pow(W, b, p)*block)%p)
        cyfered_block = bytearray(c.to_bytes(((c.bit_length()+7)//8), byteorder='big'))

        return cyfered_block

    def pack_block_verif(cyfered_block, B1, B2, b, p, X, Y):
        chain_to_hash = bytearray()
        chain_to_hash.extend(B1.to_bytes(((B1.bit_length()+7)//8), byteorder='big'))
        chain_to_hash.extend(B2.to_bytes(((B2.bit_length()+7)//8), byteorder='big'))
        chain_to_hash.extend(cyfered_block)
        beta_hash = hashlib.sha3_256(chain_to_hash).digest()

        beta = int.from_bytes(beta_hash, byteorder='big')
        verif = (pow(X, b, p) * pow(Y, (b*beta), p))%p
        verif_bytes = bytearray(verif.to_bytes(((verif.bit_length()+7)//8), byteorder='big'))
        packed_dict =  {'B1':B1, 'B2': B2, 'cyfer': bytes(cyfered_block), 'verif': bytes(verif_bytes)}
        return packed_dict


    def encode_message(m, public_key, block_size):
        p = public_key['p']
        alpha1 = public_key['alpha1']
        alpha2 = public_key['alpha2']
        X = public_key['X']
        Y = public_key['Y']
        W = public_key['W']


        m_bytes = bytearray(m.encode('utf-8'))

        m_blocks = []
        for block_number in list(range(len(m_bytes)//block_size)):
            m_block = bytearray()
            for i in list(range(block_size)):
                m_block.append(m_bytes[block_number*block_size+i])
            m_blocks.append(m_block)

        m_block = m_bytes[(len(m_bytes)//block_size)*block_size:]
        while len(m_block) < block_size:
            m_block.append(0)
        m_blocks.append(m_block)

        cyfered_text = bytearray()

        cyfered_packed_list = []
        block_num = 0
        with open('cyfer.json', 'r+') as cyferdatafile:
            data = cyferdatafile.read()
            if len(data)>0:
                current_dict = json.loads(data)
            else:
                current_dict = {}

            for block_num in list(range(len(m_blocks))):
                b = random.randint(2, p-1)
                B1 = pow(alpha1, b, p)
                B2 = pow(alpha2, b, p)
                cyfered_block = encode_block(m_blocks[block_num],p, b, B1, B2, W, block_num)
                cyfered_text.extend(cyfered_block)

                cyfered_packed = pack_block_verif(cyfered_block, B1, B2, b, p, X, Y)
                cyfered_packed_list. append(cyfered_packed)
                str_cyfered_pack = {'B1' : cyfered_packed['B1'],
                                 'B2' : cyfered_packed['B2'],
                                 'cyfer' : str(cyfered_packed['cyfer']),
                                 'verif' : str(cyfered_packed['verif'])}

                if current_dict != {}:
                    if 'Cyfered Block' not in list(current_dict.keys()):
                        current_dict['Cyfered Block'] = [str_cyfered_pack]
                    else:
                        if block_num >= len(current_dict['Cyfered Block']):
                            update = list(current_dict['Cyfered Block'])
                            update.append(str_cyfered_pack)
                            current_dict['Cyfered Block'] = update

                        else:
                            current_dict['Cyfered Block'][block_num] = str_cyfered_pack
                else:
                    current_dict = {'Cyfered Block':[str_cyfered_pack]}

            current_dict['Cyfered Block'] = current_dict['Cyfered Block'][:block_num+1]

            cyferdatafile.seek(0)
            json.dump(current_dict,
                      cyferdatafile,indent=4, sort_keys=True)
            cyferdatafile.truncate()



        return cyfered_packed_list


    def decode_bloc(block, p, B1, w, block_num):

        block = int.from_bytes(block, byteorder='big')
        m = (pow(B1, p-1-w, p) * block)% p

        uncyfered_block = bytearray(m.to_bytes(((m.bit_length()+7)//8), byteorder='big'))


        return uncyfered_block

    def check_verif(B1,B2,c,x1,x2,y1,y2,p,verif):

        chain_to_hash = bytearray()
        chain_to_hash.extend(B1.to_bytes(((B1.bit_length()+7)//8), byteorder='big'))
        chain_to_hash.extend(B2.to_bytes(((B2.bit_length()+7)//8), byteorder='big'))
        chain_to_hash.extend(c)
        beta_hash = hashlib.sha3_256(chain_to_hash).digest()

        beta = int.from_bytes(beta_hash, byteorder='big')
        to_check = (pow(B1, x1, p) * pow(B2, x2, p) * pow((pow(B1, y1, p) * pow(B2, y2, p)), beta, p))%p
        to_check_bytes = bytearray(to_check.to_bytes(((to_check.bit_length()+7)//8), byteorder='big'))

        if to_check_bytes == verif:
            return True
        else:
            # raise ValueError('Hash not matching during verification check')
            return False




    def decode_message(cyfer_packed, private_key, public_key, block_size):

        p = public_key['p']
        w = private_key['w']
        x1 = private_key['x1']
        x2 = private_key['x2']
        y1 = private_key['y1']
        y2 = private_key['y2']


        uncyfered_text = bytearray()


        block_num = 0
        with open('cyfer.json', 'r+') as cyferdatafile:
            data = cyferdatafile.read()
            if len(data)>0:
                current_dict = json.loads(data)
            else:
                current_dict = {}
            for block_num in list(range(len(cyfer_packed))):
                B1 = cyfer_packed[block_num]['B1']
                B2 = cyfer_packed[block_num]['B2']
                c = cyfer_packed[block_num]['cyfer']
                verif = cyfer_packed[block_num]['verif']
                uncyfered_block = decode_bloc(c, p, B1, w, block_num)

                check = check_verif(B1,B2,c,x1,x2,y1,y2,p,verif)
                if check :
                    str_uncyfered_pack = {'decoded' : str(bytes(uncyfered_block)),
                                        'verif' : str(check)}
                    uncyfered_text.extend(uncyfered_block)
                else:
                    str_uncyfered_pack = {'verif' : str(check)}
                if current_dict != {}:
                    if 'Uncyfered Block' not in list(current_dict.keys()):
                        current_dict['Uncyfered Block'] = [str_uncyfered_pack]
                    else:
                        if block_num >= len(current_dict['Uncyfered Block']):
                            update = list(current_dict['Uncyfered Block'])
                            update.append(str_uncyfered_pack)
                            current_dict['Uncyfered Block'] = update
                        else:
                            current_dict['Uncyfered Block'][block_num] = str_uncyfered_pack
                else:
                    current_dict = {'Uncyfered Block':[str_uncyfered_pack]}

            current_dict['Uncyfered Block'] = current_dict['Uncyfered Block'][:block_num+1]

            cyferdatafile.seek(0)
            json.dump(current_dict,
                      cyferdatafile,indent=4, sort_keys=True)
            cyferdatafile.truncate()

        with open('cyfer.json', 'r+') as cyferdatafile:
            data = cyferdatafile.read()
            if len(data) > 0:
                current_dict = json.loads(data)
                current_dict['Uncyfered Text'] = str(uncyfered_text.decode('utf-8'))
            else:
                current_dict = {'Uncyfered Text': str(uncyfered_text.decode('utf-8'))}

            cyferdatafile.seek(0)
            json.dump(current_dict,
                      cyferdatafile,indent=4, sort_keys=True)
            cyferdatafile.truncate()

        return uncyfered_text

    def test(message=None, block_len=8):
        if message is None:
            message = 'Hello World!! This is a default test string to be cyfered to check if everything works as expected!'
        clear_text = bytearray(str(message).encode('utf-8'))
        byte_text = bytearray(binascii.hexlify(bytes(clear_text)))
        with open('cyfer.json', 'r+') as cyferdatafile:
            data = cyferdatafile.read()
            if len(data) > 0:
                current_dict = json.loads(data)
                current_dict['Clear Text'] = str(clear_text)
                current_dict['byte_text'] = str(byte_text)
            else:
                current_dict = {'Clear Text': str(clear_text)}
                current_dict['byte_text'] = str(byte_text)
            cyferdatafile.seek(0)
            json.dump(current_dict,
                      cyferdatafile,indent=4, sort_keys=True)
            cyferdatafile.truncate()

        generate_keys(block_len)

        with open('keys.json') as keydatafile:
            keys = json.loads(keydatafile.read())
            public_key = keys['public key']
            cyfer_packed = encode_message(message, public_key, block_len)
            private_key = keys['private key']
            decyfer = decode_message(cyfer_packed, private_key, public_key, block_len)



    test('STAR WARS VIII est nul a chier c est honteux bordel! Ils ont tue la saga, fuck mickey', 32)


