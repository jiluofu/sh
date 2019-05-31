#!/usr/local/bin/python3

import random

def minus_2(a1, a2):
    
    str = '{} - (   ) = {}'.format(a1, a2)
    return str

def get_a1():

    a1 = random.randrange(20, 90)
    bit_a1 = a1 % 10
    dec_a1 = int(a1 % 100 / 10)
    return {
        'a1' : a1, 
        'bit_a1': bit_a1,
        'dec_a1': dec_a1
    }

def gen_q():
    
    dict_a1 = get_a1()
    while dict_a1['bit_a1'] == 9:
        dict_a1 = get_a1()

    a1 = dict_a1['a1']
    bit_a1 = dict_a1['bit_a1']
    dec_a1 = dict_a1['dec_a1']
    
    if bit_a1 == 0:
        bit_a2 = random.randrange(bit_a1, 10)
    else:
        bit_a2 = random.randrange(bit_a1 + 1, 10)

    if dec_a1 == 0:
        dec_a2 = random.randrange(0, dec_a1)
    else:
        dec_a2 = random.randrange(0, dec_a1 - 1)
    a2 = dec_a2 * 10 + bit_a2

    return minus_2(a1, a2)

def render():
    lines = []
    for i in range(132):
        lines.append(gen_q())
    random.shuffle(lines)  
    
    return lines  

if __name__ == '__main__':
    
    lines = render()
    print('\n\n'.join(lines))
    



