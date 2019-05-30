#!/usr/local/bin/python3

import random

def minus_2(a1, a2):
    
    str = '{} - {} = (  )'.format(a1, a2)
    return str

def gen_q():
    
    a1 = random.randrange(20, 90)
    bit_a1 = a1 % 10
    dec_a1 = int(a1 % 100 / 10)
    
    if bit_a1 == 0 or bit_a1 == 9:
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

    for i in range(20):
        print(gen_q())    

if __name__ == '__main__':
    
    render()
    



