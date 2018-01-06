# -*- coding: utf-8 -*-
"""
Created on Tue Dec 12 10:29:07 2017

@author: Arle, NervousK
"""

import os
import random
import json
import binascii
import hashlib
import ast
import prime_tests as pt

def pick_candidate(length):
    range_start = (2**(length-1))
    range_end = (2**length)-1
    candidate = random.randint(range_start, range_end)

    return candidate



def is_smooth(p, k=2, B=800):
    if p % 2 != 0:
        q = (p-1)//2
        if pt.Baillie_PSW(q, k, B):
            return False
        else:
            return True
    else:
        return True

def pick_prime(length=64):
    prime= 0
    while prime == 0:
        candidate = pick_candidate(length)
        if pt.Baillie_PSW(candidate, 2, 800):
            if is_smooth(candidate):
                prime = candidate
    return prime

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

    with open(os.path.join(os.getcwd(), 'keys.json'), 'w') as keydatafile:
        keydatafile.seek(0)
        json.dump(key_data, keydatafile,indent=4, sort_keys=True)
        keydatafile.truncate()

    return key_data

def byte_len(x):
    s = bin(x)
    s = s.lstrip('-0b')
    return (len(s)//8)+1

def encode_block(block,p, b, B1, B2, W):

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
    packed_dict =  {'B1':B1, 'B2': B2, 'cyfer': str(bytes(cyfered_block)), 'verif': str(bytes(verif_bytes))}
    return packed_dict


def encode_message(m, public_key, block_size):
    p = public_key['p']
    alpha1 = public_key['alpha1']
    alpha2 = public_key['alpha2']
    X = public_key['X']
    Y = public_key['Y']
    W = public_key['W']


    # m_bytes = bytearray(m.encode('utf-8'))
    m_bytes = bytearray(m)

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
    with open(os.path.join(os.getcwd(), 'cyfer.json'), 'r+') as cyferdatafile:
        data = cyferdatafile.read()
        if len(data)>0:
            current_dict = json.loads(data)
        else:
            current_dict = {}

        for block_num in list(range(len(m_blocks))):
            b = random.randint(2, p-1)
            B1 = pow(alpha1, b, p)
            B2 = pow(alpha2, b, p)
            cyfered_block = encode_block(m_blocks[block_num],p, b, B1, B2, W)
            cyfered_text.extend(cyfered_block)

            cyfered_packed = pack_block_verif(cyfered_block, B1, B2, b, p, X, Y)
            cyfered_packed_list.append(cyfered_packed)
            str_cyfered_pack = {'B1' : cyfered_packed['B1'],
                                'B2' : cyfered_packed['B2'],
                                'cyfer' : cyfered_packed['cyfer'],
                                'verif' : cyfered_packed['verif']}

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


def decode_bloc(block, p, B1, w):

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
    with open(os.path.join(os.getcwd(), 'cyfer.json'), 'r+') as cyferdatafile:
        data = cyferdatafile.read()
        if len(data)>0:
            current_dict = json.loads(data)
        else:
            current_dict = {}
        for block_num in list(range(len(cyfer_packed))):
            B1 = cyfer_packed[block_num]['B1']
            B2 = cyfer_packed[block_num]['B2']
            c = bytearray(ast.literal_eval(cyfer_packed[block_num]['cyfer']))
            verif = bytearray(ast.literal_eval(cyfer_packed[block_num]['verif']))
            uncyfered_block = decode_bloc(c, p, B1, w)

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

    with open(os.path.join(os.getcwd(), 'cyfer.json'), 'r+') as cyferdatafile:
        data = cyferdatafile.read()
        if len(data) > 0:
            current_dict = json.loads(data)
            current_dict['Uncyfered Text'] = str(bytes(uncyfered_text))
        else:
            current_dict = {'Uncyfered Text': str(bytes(uncyfered_text))}

        cyferdatafile.seek(0)
        json.dump(current_dict,
                  cyferdatafile,indent=4, sort_keys=True)
        cyferdatafile.truncate()

    return uncyfered_text

def Cramer_Shoup_encode(path, block_len=8):
    with open(os.path.join(os.getcwd(),path), 'rb') as bin_file:
        message = bin_file.read()
    if message is None:
        message = 'Hello World!! This is a default test string to be cyfered to check if everything works as expected!'
    clear_text = bytearray(message)
    byte_text = bytearray(binascii.hexlify(bytes(clear_text)))
    with open(os.path.join(os.getcwd(), 'cyfer.json'), 'r+') as cyferdatafile:
        data = cyferdatafile.read()
        if len(data) > 0:
            current_dict = json.loads(data)
            current_dict['Block length'] = str(block_len)
            current_dict['Clear Text'] = str(bytes(clear_text))
            current_dict['byte_text'] = str(bytes(byte_text))
        else:
            current_dict = {'Block length': str(block_len),
                            'Clear Text': str(bytes(clear_text)),
                            'byte_text': str(bytes(byte_text))}
        cyferdatafile.seek(0)
        json.dump(current_dict,
                  cyferdatafile,indent=4, sort_keys=True)
        cyferdatafile.truncate()

    generate_keys(block_len)

    with open(os.path.join(os.getcwd(), 'keys.json')) as keydatafile:
        keys = json.loads(keydatafile.read())
        public_key = keys['public key']
        cyfer_packed = encode_message(message, public_key, block_len)
        return cyfer_packed


def Cramer_Shoup_decode(path='asym_decrypted'):
    public_key = None
    private_key = None
    block_len = None
    cyfer_packed = None
    with open(os.path.join(os.getcwd(), 'keys.json')) as keydatafile:
        keys = json.loads(keydatafile.read())
        public_key = keys['public key']
        private_key = keys['private key']
    with open(os.path.join(os.getcwd(), 'cyfer.json'), 'r+') as cyferdatafile:
        data = cyferdatafile.read()
        if len(data) > 0:
            cyfer_data = json.loads(data)
            block_len = cyfer_data['Block length']
            cyfer_packed = cyfer_data['Cyfered Block']

    if public_key is not None and private_key is not None and cyfer_packed is not None and block_len is not None:

        decyfer = decode_message(cyfer_packed, private_key, public_key, block_len)

        with open(os.path.join(os.getcwd(),path), 'wb') as output_file:
            output_file.write(bytes(decyfer))

        return decyfer

if __name__ == '__main__':


    Cramer_Shoup_encode('test.txt', 512)
    Cramer_Shoup_decode('asym_decrypted.txt')