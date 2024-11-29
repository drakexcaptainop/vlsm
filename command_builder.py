import argparse 

parser = argparse.ArgumentParser(description='Command Scripter')
parser.add_argument('--destination', type=str)

char_map = {

}

with open('commands.txt', 'r') as f:
    for l in f.readlines():
        l = l.strip('\n')
        if len(l) >= 3:
            if '-' in l:
                [s, e] = l.split('-')
                char_map[f'{s[0]}-{e[0]}'] = l.strip()
            else:
                char_map[l[:3]] = l.strip()
        else:
            char_map[l.strip()] = l.strip()

print(char_map)
args = parser.parse_args()

f = open(args.destination, 'w')

while 1:
    inp = input('>>')
    if not inp:
        break
    
    def initials_replace(inp: str):
        if '$' in inp:
            si = inp.find('$')
            ei = inp[si+1:].find('$') + si + 1
            sub = inp[si+1:ei]
            initials = sub.split(' ')
            new = ''
            for wrd in initials:
                val = char_map.get(wrd, wrd)
                if not val:
                    raise Exception()
                new += val + ' '
            new = new.strip()
            inp = inp.replace(f'${sub}$', new) 
            print(inp)

            inp = initials_replace(inp)
        return inp     
    inp = initials_replace(inp)

    if ('[' in inp) and (']' in inp):
        s = inp.index('[')
        e = inp.index(']')
        sub = inp[s+1:e]
         
        if '-' in sub:
            [rs, re] = sub.split('-')
            rep_list = range(int(rs), int(re)+1)
        elif ',' in sub:
            rep_list = sub.split(',')

        for i in rep_list:
            hdr = inp[:s]
            tail = inp[e+1:]
            strp = f'{hdr}{i}{tail}\n'
            f.write(strp)
            f.flush()
    else:
        f.write(inp+'\n')
        f.flush()
f.close()   


#
#
#
#
#



