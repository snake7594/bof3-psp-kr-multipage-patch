"""BoF3 byte<->JP decoder for dialog text (kana ranges + kanji table + control codes).
Tables parsed from bof3text.txt (hiragana 0x5b-0xaa, katakana 0xab-0xfb) and
ENDKANJI_kr_table.txt (kanji 0x1200+). For DIALOG context bytes 0x5b-0xfb are kana.
"""
import re

def _parse_kana():
    txt=open('bof3text.txt',encoding='utf-8').read().splitlines()
    m={}
    for ln in txt:
        g=re.match(r'\s*0x([0-9a-fA-F]{2})\s+(\S)\s*$',ln)
        if g:
            b=int(g.group(1),16)
            if 0x5b<=b<=0xfb: m[b]=g.group(2)
    return m

def _parse_kanji():
    m={}
    for ln in open('ENDKANJI_kr_table.txt',encoding='utf-8'):
        g=re.match(r'\s*0x([0-9a-fA-F]{4})\s+(\S)',ln)
        if g: m[int(g.group(1),16)]=g.group(2)
    return m

KANA=_parse_kana()
KANJI=_parse_kanji()
CTRL={0x00:'<END>',0x01:'\n',0x0b:'<PAUSE>',0x20:'<BOX>'}

def decode(b):
    out=[]; i=0; n=len(b)
    while i<n:
        c=b[i]
        if c in (0x12,0x13):                 # kanji 2-byte
            code=(c<<8)|(b[i+1] if i+1<n else 0)
            out.append(KANJI.get(code, '{%04x}'%code)); i+=2
        elif c==0x00:
            out.append('<END>'); i+=1; break
        elif c in CTRL:
            out.append(CTRL[c]); i+=1
        elif c in (0x04,0x05,0x07,0x0c,0x14,0x15,0x16):  # control + operand
            out.append('{c%02x:%02x}'%(c,b[i+1] if i+1<n else 0)); i+=2
        elif 0x5b<=c<=0xfb:
            out.append(KANA.get(c,'{k%02x}'%c)); i+=1
        elif 0x20<=c<=0x7e:
            out.append(chr(c)); i+=1
        else:
            out.append('{%02x}'%c); i+=1
    return ''.join(out)

if __name__=='__main__':
    print('kana entries:',len(KANA),' kanji entries:',len(KANJI))
    import emi_dialog as E
    d=open('PSP_GAME/USRDIR/JPN/WORLD00/AREA000.EMI','rb').read()
    n,secs=E.parse_toc(d); s=[x for x in secs if x['ram']==0x10000][0]
    ts=E.parse_text_section(d,s)
    # decode the area-name gap + first several distinct bodies
    print('--- gap (area-name region) ---')
    print(' ',decode(ts['_gap']) if '_gap' in ts else decode(d[s['off']+ts['tbl_sz']:s['off']+ts['first_body']]))
    print('--- first 8 distinct bodies ---')
    seen=set()
    for bi,(p,body) in enumerate(zip(ts['ptrs'],ts['bodies'])):
        if p in seen: continue
        seen.add(p)
        print(' [%3d] @%#x (%dB): %s'%(bi,p,len(body),decode(body)[:90]))
        if len(seen)>=8: break
