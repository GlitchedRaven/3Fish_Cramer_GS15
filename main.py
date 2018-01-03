# -*- coding: utf-8 -*-
"""
Created on Wed Jan  3 14:57:33 2018

@author: Arle
"""

from itertools import chain
import os
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
            mdp=input("Entrez une clé :")
            plain_path=input("Choisissez le fichier à chiffrer :")
            path_c = os.path.join(cwd, 'encrypted.txt')
            blockSize=int(input("Choisissez la taille des blocs (256,512,1024) :"))
            
            hashedMdp = skein.simple_skein(1024, 1024, bytearray(m.encode()))
            key = tf.cut_as_words(bytearray(hashedMdp[0:blockSize]))
            tweaks = [bytearray(hashedMdp[64:72]), bytearray(hashedMdp[72:80])]
            plaintext = tf.read_file_as_bits(os.path.join(cwd, plain_path))
            
            
            
            
            c = list(chain.from_iterable(tf.CBC_ThreeFish_encrypt(plaintext, blockSize, key, tweaks)))
            tf.write_file_from_bytes(c, path_c)
            
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
            print(h)
            fo = open(path_h, "w")
            fo.write(h)
            fo.close
        elif selection == '4':
            import threefish as tf
            import skein
            mdp=input("Entrez la clé :")
            cypher_path=input("Choisissez le fichier à déchiffrer :")
            path_d = os.path.join(cwd, 'decrypted.txt')
            blockSize=int(input("Entrez la taille des blocs (256,512,1024) :"))
            
            hashedMdp = skein.simple_skein(1024, 1024, bytearray(m.encode()))
            key = tf.cut_as_words(bytearray(hashedMdp[0:blockSize]))
            tweaks = [bytearray(hashedMdp[64:72]), bytearray(hashedMdp[72:80])]
            plaintext = tf.read_file_as_bits(os.path.join(cwd, cypher_path))
            
            
            
            
            d = list(chain.from_iterable(tf.CBC_ThreeFish_decrypt(plaintext, blockSize, key, tweaks)))
            tf.write_file_from_bytes(d, path_d)
        elif selection == '5':
            break
        elif selection == '6':
            import threefish as tf
            import skein
            hash_path=input("Choisissez le fichier contenant le hash :")
            file_path=input("Choisissez le fichier avec lequel vosu souhaitez comparer ce hash :")
            Nb=int(input("Choisissez la taille des blocs (256,512,1024) :"))
            No=int(input("Choisissez la taille du hash (256,512,1024) :"))
            plaintext = tf.read_file_as_bits(os.path.join(cwd, file_path))
            hashfile =  tf.read_file_as_bits(os.path.join(cwd, hash_path))
            
            h = skein.simple_skein(Nb, No, plaintext)
        elif selection == '7': 
            break
        else: 
            print("Unknown Option Selected!")

if __name__ == '__main__':
    choix_chiffrement()