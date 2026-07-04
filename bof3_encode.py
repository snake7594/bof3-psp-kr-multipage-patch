"""Encode a markup string (decoder format + Korean) back into BoF3 text bytes.
Inverse of bof3_codec.decode, extended for Korean 2-byte font-image tokens.
Markup tokens (as emitted by decoder):
  \n            -> 0x01 (newline)
  <END>         -> 0x00 ;  <PAUSE> -> 0x0b ;  <BOX> -> 0x20
  {cXX:NN}      -> bytes 0xXX 0xNN  (2-byte control + operand)
  {XX}          -> single byte 0xXX (e.g. {ff} space, {fe} comma, {02} new-box, {0d}..)
  ' ' (space)   -> 0xff (full-width space) ; ',' -> 0xfe
  Korean syllable -> LEAD + glyph_idx[syllable]  (needs cmap)
  hiragana/katakana -> kana byte (reverse table)   [for round-trip of JP]
  kanji char    -> 2-byte 0x12/0x13 token (reverse KANJI table)
  other ASCII 0x20-0x7e -> that byte
"""
import re, struct
import bof3_codec as C

KANA_REV={v:k for k,v in C.KANA.items()}
KANJI_REV={v:k for k,v in C.KANJI.items()}   # char -> code (0x1200..)
SB=0xAC00; LEAD=0x12
LEADS=[0x12,0x13,0x1e,0x1f,0x23,0x24]   # expanded precomposed font pages

def encode(markup, cmap=None, space=0xff):
    """cmap: dict syllable->glyph_idx (multi-bank: token = LEADS[idx//256] + idx%256). Returns bytes."""
    out=bytearray(); i=0; n=len(markup)
    while i<n:
        ch=markup[i]
        if ch=='{':
            j=markup.index('}',i); tok=markup[i+1:j]; i=j+1
            if ':' in tok:                       # cXX:NN
                a,b=tok.split(':'); out+=bytes([int(a[1:],16),int(b,16)])
            else:
                out.append(int(tok,16))
            continue
        if ch=='<':
            # only <END>/<PAUSE>/<BOX> are special; any other '<' is a literal glyph (0x3c).
            for tok,b in (('<END>',0x00),('<PAUSE>',0x0b),('<BOX>',0x20)):
                if markup.startswith(tok,i): out.append(b); i+=len(tok); break
            else: out.append(0x3c); i+=1   # literal '<'
            continue
        i+=1
        if ch=='\n': out.append(0x01)
        elif ch==' ': out.append(space)
        elif ch==',' or ch=='、': out.append(0xfe)
        elif SB<=ord(ch)<=0xD7A3:                # Korean syllable -> bank token
            assert cmap is not None and ch in cmap, 'no cmap entry for %r'%ch
            ci=cmap[ch]; out+=bytes([LEADS[ci//256], ci%256])
        elif ch in KANA_REV: out.append(KANA_REV[ch])
        elif ch in KANJI_REV:
            code=KANJI_REV[ch]; out+=bytes([code>>8, code&0xff])
        elif 0x20<=ord(ch)<=0x7e: out.append(ord(ch))
        else: raise ValueError('cannot encode %r (U+%04X)'%(ch,ord(ch)))
    return bytes(out)

if __name__=='__main__':
    # round-trip verify on AREA007 JP bodies: decode -> encode == original
    import emi_dialog as E
    d=open('PSP_GAME/USRDIR/JPN/WORLD00/AREA007.EMI','rb').read()
    n,secs=E.parse_toc(d); s=[x for x in secs if x['ram']==0x10000][0]
    ts=E.parse_text_section(d,s)
    ok=0; bad=0
    for bi,body in enumerate(ts['bodies']):
        mk=C.decode(body)                    # decoder markup (\n for 0x01)
        # decoder uses real '\n' for 0x01; our encode maps '\n'->0x01. good.
        try:
            re_enc=encode(mk)
            if re_enc==body: ok+=1
            else: bad+=1
        except Exception as ex:
            bad+=1
            if bad<=3: print('body%d encode err: %s'%(bi,ex))
    print('round-trip JP: %d ok, %d mismatch (of %d)'%(ok,bad,len(ts['bodies'])))
