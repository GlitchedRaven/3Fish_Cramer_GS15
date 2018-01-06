# -*- coding: utf-8 -*-
"""
Created on Wed Jan  3 14:57:33 2018

@author: Arle
"""

from itertools import chain
import json
import os
import ast
import random
cwd = os.getcwd()

def choix_chiffrement():   
    menu = {}
    menu['1']="Chiffrement symétrique ThreeFish (3 ><(((> )" 
    menu['2']="Chiffrement de Cramer-Shoup"
    menu['3']="Hashage d’un message"
    menu['4']="Déchiffrement symétrique ThreeFish (3 ><(((> )"
    menu['5']="Déchiffrement de Cramer-Shoup"
    menu['6']="Vérification d’un Hash"
    menu['7']="Quitter"
    while True: 
        options=menu.keys()
        #options.sort()
        for entry in options: 
            print(entry, menu[entry])

        selection=input("Please Select:") 
        if selection =='1': 
            import threefish as tf
            import skein
            
            mode=input("CBC (1) or EBC (2) ? : ") 
            mdp=input("Entrez une clé :")
            plain_path=input("Choisissez le fichier à chiffrer :")

            path_c = os.path.join(cwd, 'encrypted.json')
            blockSize=int(input("Choisissez la taille des blocs (256,512,1024) :"))
            
            param= {'Mode': '', 'blockSize': str(blockSize), 'IV': '', 'cyphertext' : ''}
            
            hashedMdp = skein.simple_skein(1024, 1024, bytearray(mdp.encode()))
            key = tf.cut_as_words(bytearray(hashedMdp[0:blockSize]))
            tweaks = [bytearray(hashedMdp[64:72]), bytearray(hashedMdp[72:80])]
            plaintext = tf.read_file_as_bits(os.path.join(cwd, plain_path))
            
            if (mode == '1'):
                param['Mode'] = '1'
                IV = skein.simple_skein(blockSize, blockSize, random.randint(0, 2**2048).to_bytes(256, 'big'))
                param['IV'] = str(bytes(IV))
                c = list(chain.from_iterable(tf.CBC_ThreeFish_encrypt(plaintext, blockSize, key, tweaks, IV)))
                cyphertext =''
                for block in c : cyphertext += str(bytes(block))
                param['cyphertext'] = cyphertext
            if (mode == '2'):
                param['Mode'] = '2'
                c = list(chain.from_iterable(tf.ECB_ThreeFish_encrypt(plaintext, blockSize, key, tweaks)))
                cyphertext =''
                for block in c : cyphertext += str(bytes(block))
                param['cyphertext'] = cyphertext
            
            #tf.write_file_from_bytes(c, path_c)
            with open(path_c, "w") as f:
                json.dump(param, f ,indent=4, sort_keys=True)
            
            
        elif selection == '2': 
            print("delete")
        elif selection == '3':
            import threefish as tf
            import skein
            file_path=input("Choisissez le fichier à hasher :")
            path_h = os.path.join(cwd, 'hash.txt')
            Nb=int(input("Choisissez la taille des blocs (256,512,1024) :"))
            No=int(input("Choisissez la taille du hash (256,512,1024) :"))
            plaintext = tf.read_file_as_bits(os.path.join(cwd, file_path))
            
            h = skein.simple_skein(Nb, No, plaintext)
            
            param= {'Nb': str(Nb), 'No': str(No), 'hash' : str(bytes(h))}
            with open(path_h, "w") as f:
                json.dump(param, f ,indent=4, sort_keys=True)


        elif selection == '4':
            import threefish as tf
            import skein
            mdp=input("Entrez la clé :")
            cypher_path=input("Choisissez le fichier à déchiffrer :")
            path_d = os.path.join(cwd, 'decrypted.txt')
            
            with open(cypher_path, "r") as f:  param = json.loads(f.read())
            blockSize = int(param['blockSize'])
            cyphertext = ast.literal_eval(param['cyphertext'])
            mode = param['Mode']
            
            
            hashedMdp = skein.simple_skein(1024, 1024, bytearray(mdp.encode()))
            key = tf.cut_as_words(bytearray(hashedMdp[0:blockSize]))
            tweaks = [bytearray(hashedMdp[64:72]), bytearray(hashedMdp[72:80])]
           
            
            
             
            if (mode == '1'):
                IV = ast.literal_eval(param['IV'])
                d = list(chain.from_iterable(tf.CBC_ThreeFish_decrypt( cyphertext, blockSize, key, tweaks, IV)))           
            if (mode == '2'):
                d = list(chain.from_iterable(tf.ECB_ThreeFish_decrypt( cyphertext, blockSize, key, tweaks)))
            
            
            
            tf.write_file_from_bytes(d, path_d)
        elif selection == '5':
            break
        elif selection == '6':
            import threefish as tf
            import skein
            hash_path=input("Choisissez le fichier contenant le hash :")
            file_path=input("Choisissez le fichier avec lequel vous souhaitez comparer ce hash :")
        
            plaintext = tf.read_file_as_bits(os.path.join(cwd, file_path))
            
            with open(hash_path, "r") as f:  param = json.loads(f.read())
            Nb = int(param['Nb'])
            No = int(param['No'])
            hashfile = ast.literal_eval(param['hash'])
            
            h = skein.simple_skein(Nb, No, plaintext)
            
            if h == hashfile:
                print("The hash and the file match")
            else:
                print("The hash and the file DON'T match")
            
        elif selection == '7': 
            break
        else: 
            print("Unknown Option Selected!")

if __name__ == '__main__':
    #plaintext = tf.read_file_as_bits('test.txt')
    choix_chiffrement()