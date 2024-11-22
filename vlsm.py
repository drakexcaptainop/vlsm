import math
import argparse
#import regex as re

parser = argparse.ArgumentParser()

parser.add_argument('--net', type=str)
parser.add_argument('--hosts', type=str)
parser.add_argument('--use_parser', action='store_true', default=False)
parser.add_argument('--use_experimental', action='store_true', default=False)
parser.add_argument('--hosts_from_file', type=str, default=False)
parser.add_argument('--host_sep', type=str, default=",")
parser.add_argument('--concat_multiline', action='store_true', default=False)


args = parser.parse_args()


def experimental(f):
    def wrapper(*qargs, **kwargs):
        if args.use_experimental:
            return f(*qargs, **kwargs)
        else:
            return addr.step(*qargs, **kwargs)
    return wrapper

class addr:
    def __init__(self, base, mask, host_requested=None) -> None:
        self.base: list[int] = base 
        self.mask: list[int] = mask; self.host_requested = host_requested

    def __str__(self) -> str:
        return ".".join( [str(v) for v in self.base] ) +" / " + F"[{
            '.'.join( [str(v) for v in self.mask] ) + F" - {list2id_mask(self.mask)}]" + ("" if self.host_requested is None else F", #RequestedHosts = {self.host_requested}")
        }" 
    
    def copy(self):
        return addr( [*self.base], [*self.mask] )

    def step_next_usable_net(self, for_hosts=None):
        _addr = self.copy()
        _addr.step( 256 - self.base[-1] )
        if for_hosts is not None:
            _addr.mask = int2list_mask( host_requested_to_mask(for_hosts) )
        return _addr

    def _set_mask(self, mask):
        if isinstance(mask, int):
            mask = int2list_mask(mask)
        self.mask = mask

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
    
    @experimental
    def step_optimized(self, v):
        base_change_index = 1
        q = v + self.base[-1]
        zero_center_div = v
        while q >= 256:
            q //= 256
            zero_center_div //= 256
            self.base[-base_change_index] = 0
            base_change_index += 1
            q += self.base[-base_change_index]
        self.base[-base_change_index] += zero_center_div
                
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

def host_requested_to_mask( host ):
    return 32 - math.ceil(math.log2( host + 2 ))


def vlsm( net: addr, hosts ):
    hosts = sorted(hosts, reverse=True)
    int_net = net.base
    addrs = []
    next = int_net[-1]
    temp = net.copy()
    for host in hosts:
        ex = math.ceil(math.log2( host + 2 ))
        temp.mask = int2list_mask( 32 - ex ); 
        temp.host_requested = host
        addrs.append( temp )
        temp = temp.copy()
        skip = 2**ex 
        temp.step_optimized(skip)
    return addrs
        

def parse_hosts(  ):
    vlsm_hosts = []
    if args.hosts_from_file:
        with open(args.hosts_from_file) as f:
            items = []
            for hl in f.readlines():
                if args.concat_multiline:
                    items.extend(hl.split(args.host_sep))
                else:
                    items.append(hl.split(args.host_sep))
            
            if args.concat_multiline:
                vlsm_hosts = [items]
            else:
                vlsm_hosts = items
            
    else:
        vlsm_hosts = [args.hosts.split(",")]

    for i, items in enumerate(vlsm_hosts):
        hosts = []
        for _str in items:
            if '*' in _str:
                [ nhosts, count ] = _str.split('*')
            else:
                nhosts = _str
                count = 1
            hosts.extend([int(nhosts)]*int(count))
        vlsm_hosts[i] = hosts
    return vlsm_hosts


mask = 24
_addr = addr( str2list_addr(args.net), int2list_mask(mask) )
hosts = [int(v) for v in args.hosts.split(",")] if not args.use_parser else parse_hosts()

if isinstance(hosts[0], list):
    _addr._set_mask( host_requested_to_mask( sum(hosts[0]) ) )
    for i, hostsarr in enumerate(hosts):
        print(F"VLSM {i+1} - #BaseAddress [{".".join( [str(v) for v in _addr.base] )} / {list2id_mask(_addr.mask)}]:")
        _vlsm = vlsm(_addr, hostsarr)
        print("\n".join(f"{i+1}) {str(a)}" for i, a in enumerate(_vlsm)),end="\n\n")
        _addr = _vlsm[-1].step_next_usable_net( sum(hostsarr) )
        
        
else:
    print("\n".join(f"{i+1}) {str(a)}" for i, a in enumerate(vlsm(_addr, hosts))))