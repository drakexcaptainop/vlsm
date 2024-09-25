import math
import argparse

parser = argparse.ArgumentParser()

parser.add_argument('--net', type=str)
parser.add_argument('--hosts', type=str)

args = parser.parse_args()

class addr:
    def __init__(self, base, mask) -> None:
        self.base: list[int] = base 
        self.mask: list[int] = mask

    def __str__(self) -> str:
        return ".".join( [str(v) for v in self.base] ) + F" /{
            '.'.join( [str(v) for v in self.mask] ) + F" / {list2id_mask(self.mask)}"
        }" 
    
    def copy(self):
        return addr( [*self.base], [*self.mask] )

    def step(self, v):
        while v>0:
            iav = 256 - self.base[-1]
            if v > iav:
                self.base[-2] += 1 
                if self.base[-2] == 256:
                    self.base[-1] = 0
                    self.base[-2] = 0
                    self.base[-3] += 1
                else:
                    self.base[-1] = 0
            elif iav > v:
                self.base[-1] += v
                v = 0
            elif v == iav:
                self.base[-2] += 1 
                self.base[-1] = 0
                v = 0
            v -= iav 
                
    def __repr__(self) -> str:
        return str(self)

def int2list_mask( id ):
    m = ("1"*id).zfill(32)[::-1]
    mask = []
    for i in range(0,32,8):
        mask.append(int(m[i:i+8], 2))
    return mask

def bin2dec_net(net):
    if isinstance(net, list):
        return [ int(v, 2) for v in net ] 
    elif isinstance(net, str):
        return [ int(v, 2) for v in net.split('.') ]

def str2list_addr(ad: str):
    return [int(v) for v in ad.split('.')]

def list2id_mask(mask):
    return ''.join( bin(v) for v in mask ).count('1')

mask = 24

_addr = addr( str2list_addr(args.net), int2list_mask(mask) )
hosts = [int(v) for v in args.hosts.split(",")]




def vlsm( net: addr, hosts ):
    hosts = sorted(hosts, reverse=True)
    int_net = net.base
    addrs = []
    next = int_net[-1]
    temp = net.copy()
    for host in hosts:
        ex = math.ceil(math.log2( host + 2 ))
        temp.mask = int2list_mask( 32 - ex ) 
        addrs.append( temp )
        temp = temp.copy()
        skip = 2**ex 
        temp.step(skip)
    return addrs
        
        

print("\n".join(str(a) for a in vlsm(_addr, hosts)))