# -*- coding: utf-8 -*-
"""Translate the executable's menu/system string tables to Korean.
Pool kinds:
  'ptr'    : packed strings + a trailing pointer table (vaddrs). Repack KO + repoint.
  'fixed'  : fixed-stride slots (e.g. battle cmd = 8 bytes). Overwrite in place.
  'repack' : packed strings accessed by base+scan; repack KO (total must fit original).
All instances of a pool are found by its JP byte signature, so duplicated tables are patched too.
patch_menus(b) mutates the eboot bytearray in place; returns a textual report.
"""
import struct, json
import bof3_encode as Enc
LB=0x80
CMAP=json.load(open('compact_map.json',encoding='utf-8'))['map']
def enc(s): return Enc.encode(s, cmap=CMAP)

# (label, kind, primary_off, JP-list, KO-list, extra)
POOLS=[
 ('main-menu','ptr',0x2ec6cc,
   ['使う','整理','捨てる','装備','最強','特能','買う','売る','入替','よむ','大事','終了','シフト','ボタン','初期化'],
   ['사용','정리','버리기','장비','최강','특능','구입','판매','교체','읽기','중요','종료','시프트','버튼','초기화'], None),
 ('sort','ptr',0x2ed1be,
   ['整理','自分で整理','通常アイテム','戦闘アイテム','攻撃力','防御力','しゅるい','AP大','AP小','通常魔法','戦闘魔法'],
   ['정리','직접정리','일반도구','전투도구','공격력','방어력','종류','AP대','AP소','일반마법','전투마법'], None),
 ('battle-cmd','fixed',0x2f03c9,
   ['特能','道具','見る','防御','突撃','逃走'],
   ['특능','도구','보기','방어','돌격','도주'], 8),
 ('status','repack',0x2ec66e,
   ['攻撃','防御','賢さ','素早さ'],
   ['공격','방어','지혜','민첩'], None),
]

def jp_pool_bytes(b, off, n):
    """Read n consecutive null-terminated strings starting at off -> the raw signature bytes."""
    TWO=(0x12,0x13,0x1e,0x1f,0x20,0x21,0x23,0x24,0x04,0x05,0x07,0x0c,0x14,0x15,0x16)
    p=off; end=off
    for _ in range(n):
        while b[end]!=0x00: end+= 2 if b[end] in TWO else 1
        end+=1
    return bytes(b[off:end])

def find_all(b, sig):
    out=[]; i=b.find(sig)
    while i!=-1: out.append(i); i=b.find(sig,i+1)
    return out

def find_ptr_table(b, first_off):
    va=first_off-LB; pat=struct.pack('<I',va)
    for i in range(0,len(b)-4,4):
        if b[i:i+4]==pat: return i
    return None

def patch_menus(b):
    rep=[]
    for label,kind,prim,jp,ko,extra in POOLS:
        n=len(jp); sig=jp_pool_bytes(b,prim,n)
        insts=find_all(b,sig)
        rep.append('POOL %-10s kind=%-6s instances=%d'%(label,kind,len(insts)))
        for inst in insts:
            if kind=='fixed':
                stride=extra
                ok=True
                for i,s in enumerate(ko):
                    by=enc(s)+b'\x00'
                    if len(by)>stride: ok=False; break
                    b[inst+i*stride:inst+i*stride+len(by)]=by
                    for k in range(len(by),stride): b[inst+i*stride+k]=0
                rep.append('  @%08x fixed  %s'%(inst,'ok' if ok else 'OVERFLOW'))
            elif kind=='ptr':
                pt=find_ptr_table(b,inst)
                if pt is None or not (len(sig)<=pt-inst<=len(sig)+96):
                    rep.append('  @%08x ptr    no/this pointer-table (pt=%s) -> SKIP'%(inst,pt and hex(pt)))
                    continue
                cap=pt-inst; blob=bytearray(); vas=[]
                for s in ko:
                    vas.append(inst+len(blob)-LB); blob+=enc(s)+b'\x00'
                if len(blob)>cap:
                    rep.append('  @%08x ptr    OVERFLOW %d>%d'%(inst,len(blob),cap)); continue
                b[inst:inst+cap]=blob+b'\x00'*(cap-len(blob))
                for i,va in enumerate(vas): struct.pack_into('<I',b,pt+4*i,va)
                rep.append('  @%08x ptr    ok (pt=%#x cap=%d used=%d)'%(inst,pt,cap,len(blob)))
            elif kind=='repack':
                blob=bytearray()
                for s in ko: blob+=enc(s)+b'\x00'
                if len(blob)>len(sig):
                    rep.append('  @%08x repack OVERFLOW %d>%d'%(inst,len(blob),len(sig))); continue
                b[inst:inst+len(sig)]=blob+b'\x00'*(len(sig)-len(blob))
                rep.append('  @%08x repack ok (%d/%d bytes)'%(inst,len(blob),len(sig)))
    return '\n'.join(rep)

if __name__=='__main__':
    b=bytearray(open('PSP_GAME/SYSDIR/BOOT.BIN.orig','rb').read())
    print(patch_menus(b))
