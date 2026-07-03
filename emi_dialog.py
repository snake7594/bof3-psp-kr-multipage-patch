"""BoF3 EMI dialog text section parser + Korean injector with pointer recalc.
Format (verified, see memory bof3-emi-text-format):
 ToC: 0x800 bytes, 16B entries. entry0 = n_sections,u32=1,"MATH_TBL".
 entry i: +0 u32 size | +4 u32 ram-tag | +8 u32 first4 | +12 u16 unk | +14 ".."
 section layout: off starts 0x800, each running off += (size+0x7ff)&~0x7ff
 TEXT section: ram==0x00010000.
 text section internals (u16 LE, section-relative):
   word[0]=ptr-table size in bytes; word[1..]=body offsets; tail markers all == section size.
 terminator = standalone 0x00; 2-byte tokens (0x12/0x13 + idx) carry 0x00 mid-string.
Editing model: SPLICE one null-terminated string in place; shift only pointers whose
value is strictly greater than the edited string's start; markers (==old size) -> new size.
"""
import struct

MAGIC=b'MATH_TBL'; TOC=0x800; ALIGN=0x800; TEXT_TAG=0x00010000
# bytes that consume a following operand byte (game-side 2-byte tokens):
#   0x12/0x13 = kanji; 0x1e-0x24 (except 0x22) = twin-kanji / our bank leads;
#   0x04,0x05,0x07,0x0c,0x14,0x15,0x16 = 2-byte controls. 0x22 is 1-byte (handler 0x9ed8).
TOK2=(0x12,0x13,0x1e,0x1f,0x20,0x21,0x23,0x24,0x04,0x05,0x07,0x0c,0x14,0x15,0x16)
def align(n): return (n+ALIGN-1)&~(ALIGN-1)

def parse_toc(d):
    n=struct.unpack_from('<I',d,0)[0]; assert d[8:16]==MAGIC,'bad magic'
    secs=[]; off=TOC
    for i in range(1,n+1):
        sz,ram,first4,unk=struct.unpack_from('<IIIH',d,i*16)
        secs.append(dict(idx=i-1,size=sz,ram=ram,first4=first4,off=off)); off=align(off+sz)
    return n,secs

def parse_text_section(d, sec):
    o=sec['off']; size=sec['size']
    tbl_sz=struct.unpack_from('<H',d,o)[0]; nwords=tbl_sz//2
    words=[struct.unpack_from('<H',d,o+2*k)[0] for k in range(nwords)]
    ptrs=[]
    for k in range(1,nwords):
        if words[k]==size: break
        ptrs.append(words[k])
    bodies=[]
    for p in ptrs:
        e=p
        while e<size and d[o+e]!=0x00:
            e+= 2 if d[o+e] in TOK2 else 1
        e=min(e+1,size)
        bodies.append(bytes(d[o+p:o+e]))
    return dict(tbl_sz=tbl_sz,nwords=nwords,words=words,ptrs=ptrs,bodies=bodies,
                first_body=(ptrs[0] if ptrs else tbl_sz),size=size,off=o)

def edit_text_section(d, sec, edits):
    """edits = {body_index: new_body_bytes_incl_terminator}. Returns (new_section_bytes,new_size)."""
    o=sec['off']; size=sec['size']
    sb=bytearray(d[o:o+size]); ts=parse_text_section(d,sec)
    ops=[]
    for bi,newb in edits.items():
        ops.append((ts['ptrs'][bi], len(ts['bodies'][bi]), bytes(newb)))
    ops.sort(reverse=True)                      # splice high offset first (table at low offsets unaffected)
    deltas=[]
    for start,oldlen,newb in ops:
        sb[start:start+oldlen]=newb; deltas.append((start,len(newb)-oldlen))
    new_size=len(sb)
    nwords=ts['tbl_sz']//2
    for k in range(1,nwords):
        w=struct.unpack_from('<H',sb,2*k)[0]
        if w==size:                              # marker -> new size
            struct.pack_into('<H',sb,2*k,new_size&0xffff)
        else:                                     # body pointer -> shift by edits before it
            shift=sum(dl for (s,dl) in deltas if s<w)
            struct.pack_into('<H',sb,2*k,(w+shift)&0xffff)
    return bytes(sb), new_size

PAD=0x5f  # EMI inter-section/trailing filler byte ('_')

def patch_emi(d, sec_idx, edits):
    """Edit one section. In-place (preserve file length) when the new size stays within the
    section's 0x800 alignment block; else fall back to full re-emit."""
    n,secs=parse_toc(d); s=secs[sec_idx]
    new_sec,new_size=edit_text_section(d,s,edits)
    old_block=align(s['size']); new_block=align(new_size)
    if new_block==old_block:
        out=bytearray(d)
        out[s['off']:s['off']+old_block]=new_sec+bytes([PAD])*(old_block-len(new_sec))
        struct.pack_into('<I',out,(sec_idx+1)*16,new_size)
        struct.pack_into('<I',out,(sec_idx+1)*16+8,struct.unpack_from('<I',new_sec,0)[0])
        assert len(out)==len(d)
        return bytes(out)
    return rebuild_emi(d,{sec_idx:edits})

def rebuild_emi(d, edits_by_sec):
    """edits_by_sec = {sec_idx: {body_idx: new_bytes}}. Re-emit whole file (sizes recomputed, 0x800-aligned)."""
    n,secs=parse_toc(d)
    blobs={}
    for s in secs:
        if s['idx'] in edits_by_sec and edits_by_sec[s['idx']]:
            blob,_=edit_text_section(d,s,edits_by_sec[s['idx']])
        else:
            blob=d[s['off']:s['off']+s['size']]
        blobs[s['idx']]=blob
    out=bytearray(d[:TOC]); off=TOC
    for s in secs:
        i=s['idx']+1; blob=blobs[s['idx']]
        struct.pack_into('<I',out,i*16,len(blob))
        struct.pack_into('<I',out,i*16+8,struct.unpack_from('<I',blob,0)[0] if len(blob)>=4 else 0)
    for s in secs:
        blob=blobs[s['idx']]
        while len(out)<off: out.append(PAD)
        out+=blob; off=align(off+len(blob))
    while len(out)<off: out.append(PAD)
    return bytes(out)

if __name__=='__main__':
    path='PSP_GAME/USRDIR/JPN/WORLD00/AREA000.EMI'
    d=open(path,'rb').read()
    n,secs=parse_toc(d); texts=[s for s in secs if s['ram']==TEXT_TAG]
    print(f'{path}: {n} sections, text idx {[s["idx"] for s in texts]}')
    s=texts[0]; ts=parse_text_section(d,s)
    print(f'  sec[{s["idx"]}] off={s["off"]:#x} size={s["size"]:#x} tbl_sz={ts["tbl_sz"]:#x} bodies={len(ts["ptrs"])}')
    print(f'  distinct ptrs={len(set(ts["ptrs"]))}  ptr range {min(ts["ptrs"]):#x}..{max(ts["ptrs"]):#x}')
    # round-trip: zero edits -> identical section AND identical file
    blob,nsz=edit_text_section(d,s,{})
    print('round-trip section identical:', blob==d[s['off']:s['off']+s['size']])
    print('round-trip full EMI identical:', rebuild_emi(d,{})==d)
    # length-changing edit sanity: prepend one 3-byte token (가) to body[0] (+3 bytes)
    nb=b'\x12\x00\x00'+ts['bodies'][0]
    start0=ts['ptrs'][0]; delta=len(nb)-len(ts['bodies'][0])
    blob2,nsz2=edit_text_section(d,s,{0:nb})
    print(f'edit body0 +{delta}B -> new size {nsz2:#x} (orig {s["size"]:#x})')
    # verify pointer shift: ptr<=start0 unchanged, ptr>start0 +=delta; markers->new size
    nw=ts['tbl_sz']//2; ok=True
    for k in range(1,nw):
        old=struct.unpack_from('<H',d,s['off']+2*k)[0]
        new=struct.unpack_from('<H',blob2,2*k)[0]
        if old==s['size']: exp=nsz2
        elif old>start0:   exp=old+delta
        else:              exp=old
        if new!=exp: ok=False; print(f'  MISMATCH word{k}: old={old:#x} new={new:#x} exp={exp:#x}')
    print('pointer/marker recalc correct:', ok)
