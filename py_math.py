#!/usr/local/bin/python3

import sys
import random

runType = 'minus'
if len(sys.argv) > 1:
    runType = sys.argv[1]

def minus_2(a1, a2):
    
    str = '{} - (   ) = {}'.format(a1, a2)
    return str

def money_minus(a1, a2):

    price_a1 = get_price(a1, random.randrange(30, 60))
    price_a2 = get_price(a2, random.randrange(10, 20))

    products = ['冰棍', '蒙奇奇', '钢铁侠', '美国队长', '黑寡妇', '红女巫']
    
    str = '{}价格{}，你付了{}，老板找你（  ）元（  ）角'.format(products[random.randrange(0, len(products) - 1)], price_a2, price_a1)
    return str

def get_price(a, do_add):
    bit_a = a % 10
    dec_a = int(a % 100 / 10)
    dec_a = dec_a + do_add
    price_a = ''
    if bit_a > 0:
        price_a = '{}角'.format(bit_a)
    if dec_a > 0:
        price_a = '{}元{}'.format(dec_a, price_a)
    return price_a

def get_a1():

    a1 = random.randrange(20, 90)
    bit_a1 = a1 % 10
    dec_a1 = int(a1 % 100 / 10)
    print(a1)
    print(bit_a1)
    print(dec_a1)
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

    if runType == 'minus':
        return minus_2(a1, a2)
    elif runType == 'money_minus':
        return money_minus(a1, a2)

def mul_2(a1, a2):
    
    str = '{} * (   ) = {}'.format(a1, a1*a2)
    return str

def gen_mul():
    
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

    return mul_2(a1,a2)
    # if runType == 'minus':
    #     return minus_2(a1, a2)
    # elif runType == 'money_minus':
    #     return money_minus(a1, a2)

def get_a1120():

    a1 = random.randrange(11, 30)
    return a1

def get_a110(a1):

    a2 = random.randrange(1, a1)
    while judge_a1120(a1, a2) == False:
        # a1 = get_a1120()
        a2 = random.randrange(1, a1)
    return a2
def judge_a1120(a1, a2):
    bit_a1 = a1 % 10
    bit_a2 = a2 % 10
    # if a1 <= a2:
    #     return False
    if a1 > 10 and a2 < 10 and bit_a1 >= a2:
        return False
    if a1 > 10 and a2 > 10 and (bit_a1 > bit_a2) and bit_a1 != 9:
        print(a1)
        print(a2)
        print(bit_a1)
        print(bit_a2)
        print('22222222')
        return False

    return True

def minus_3(a1, a2):
    
    str = '{} - {} = '.format(a1, a2)
    return str

def gen_q20():
    
    a1 = get_a1120()
    a2 = get_a110(a1)
    while a2 == 10:
        a2 = get_a110(a1)
    return minus_3(a1, a2)

def get_a9(a1):

    a2 = random.randrange(1, 9)
    
    while a1 == a2 or a2 == 1:
        a2 = random.randrange(1, 9)
    return a2

def mul_9(a1, a2):
    
    str = '{} × {} = '.format(a1, a2)
    return str

def gen_m9():
    
    a1 = random.randrange(2, 9)
    a2 = get_a9(a1)
    return mul_9(a1, a2)

def render():
    lines = []
    for i in range(66):
        # lines.append(gen_q())
        # lines.append(gen_mul())
        if i % 2 == 0:
            lines.append(gen_q20())
        else:
            lines.append(gen_m9())
    random.shuffle(lines)  
    
    return lines  

if __name__ == '__main__':
    
    lines = render()
    print('\n\n'.join(lines))
    



