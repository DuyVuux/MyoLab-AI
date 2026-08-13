#!/usr/bin/env python3
"""Minimal, deterministic reader for the exact DAY68 flat Parquet evidence table.

Scope: evidence replay only. This is NOT a general project Parquet adapter.
It intentionally supports the encodings/types emitted by pyarrow 25 for the
DAY68 feature table and uses system libsnappy through ctypes.
"""
from __future__ import annotations
import argparse, csv, ctypes, ctypes.util, hashlib, struct
from pathlib import Path

CT_STOP=0; CT_TRUE=1; CT_FALSE=2; CT_BYTE=3; CT_I16=4; CT_I32=5; CT_I64=6; CT_DOUBLE=7; CT_BINARY=8; CT_LIST=9; CT_SET=10; CT_MAP=11; CT_STRUCT=12

def read_uvar(data: bytes, pos: int):
    x=0; shift=0
    while True:
        b=data[pos]; pos+=1; x|=(b&0x7F)<<shift
        if not b&0x80: return x,pos
        shift+=7

def zigzag(n:int)->int: return (n>>1) ^ -(n&1)

def read_value(data:bytes,pos:int,t:int):
    if t==CT_TRUE: return True,pos
    if t==CT_FALSE: return False,pos
    if t==CT_BYTE:
        b=data[pos]; pos+=1; return (b-256 if b>=128 else b),pos
    if t in (CT_I16,CT_I32,CT_I64):
        n,pos=read_uvar(data,pos); return zigzag(n),pos
    if t==CT_DOUBLE: return struct.unpack_from('<d',data,pos)[0],pos+8
    if t==CT_BINARY:
        n,pos=read_uvar(data,pos); return data[pos:pos+n],pos+n
    if t in (CT_LIST,CT_SET):
        h=data[pos]; pos+=1; size=h>>4; et=h&0xF
        if size==15: size,pos=read_uvar(data,pos)
        vals=[]
        for _ in range(size):
            v,pos=read_value(data,pos,et); vals.append(v)
        return {'values':vals},pos
    if t==CT_MAP:
        size,pos=read_uvar(data,pos)
        if size==0: return {'map':[]},pos
        h=data[pos]; pos+=1; kt=h>>4; vt=h&0xF; arr=[]
        for _ in range(size):
            k,pos=read_value(data,pos,kt); v,pos=read_value(data,pos,vt); arr.append((k,v))
        return {'map':arr},pos
    if t==CT_STRUCT: return read_struct(data,pos)
    raise ValueError(f'unsupported compact type {t}')

def read_struct(data:bytes,pos:int):
    out={}; last=0
    while True:
        h=data[pos]; pos+=1
        if h==0: break
        delta=h>>4; t=h&0xF
        if delta: fid=last+delta
        else:
            n,pos=read_uvar(data,pos); fid=zigzag(n)
        last=fid; v,pos=read_value(data,pos,t); out[fid]=(t,v)
    return out,pos

def val(s,f,default=None): return s.get(f,(None,default))[1]
def blist(x): return x['values'] if isinstance(x,dict) and 'values' in x else []
def bstr(x): return x.decode() if isinstance(x,(bytes,bytearray)) else x

def snappy_decompress(payload:bytes)->bytes:
    name=ctypes.util.find_library('snappy')
    if not name: raise RuntimeError('libsnappy is required for this evidence replay utility')
    lib=ctypes.CDLL(name)
    lib.snappy_uncompressed_length.argtypes=[ctypes.c_char_p,ctypes.c_size_t,ctypes.POINTER(ctypes.c_size_t)]
    lib.snappy_uncompressed_length.restype=ctypes.c_int
    lib.snappy_uncompress.argtypes=[ctypes.c_char_p,ctypes.c_size_t,ctypes.c_char_p,ctypes.POINTER(ctypes.c_size_t)]
    lib.snappy_uncompress.restype=ctypes.c_int
    n=ctypes.c_size_t()
    if lib.snappy_uncompressed_length(payload,len(payload),ctypes.byref(n))!=0: raise RuntimeError('invalid snappy payload')
    out=ctypes.create_string_buffer(n.value); nn=ctypes.c_size_t(n.value)
    if lib.snappy_uncompress(payload,len(payload),out,ctypes.byref(nn))!=0: raise RuntimeError('snappy decompression failed')
    return out.raw[:nn.value]

def read_varint(buf:bytes,pos=0):
    x=0; s=0
    while True:
        b=buf[pos]; pos+=1; x|=(b&127)<<s
        if not b&128: return x,pos
        s+=7

def hybrid_decode(buf:bytes,bit_width:int,count:int):
    out=[]; pos=0; byte_width=(bit_width+7)//8
    while len(out)<count:
        h,pos=read_varint(buf,pos)
        if h&1==0:
            run=h>>1; v=int.from_bytes(buf[pos:pos+byte_width],'little') if byte_width else 0; pos+=byte_width
            out.extend([v]*min(run,count-len(out)))
        else:
            groups=h>>1; nvals=groups*8; nbytes=groups*bit_width; raw=buf[pos:pos+nbytes]; pos+=nbytes
            acc=int.from_bytes(raw,'little') if raw else 0; mask=(1<<bit_width)-1 if bit_width else 0
            for i in range(min(nvals,count-len(out))): out.append((acc>>(i*bit_width))&mask if bit_width else 0)
    return out,pos

def parse_plain(payload:bytes,typ:int,n:int):
    vals=[]; pos=0
    for _ in range(n):
        if typ==6:
            ln=struct.unpack_from('<I',payload,pos)[0]; pos+=4; vals.append(payload[pos:pos+ln].decode()); pos+=ln
        elif typ==5: vals.append(struct.unpack_from('<d',payload,pos)[0]); pos+=8
        elif typ==2: vals.append(struct.unpack_from('<q',payload,pos)[0]); pos+=8
        elif typ==1: vals.append(struct.unpack_from('<i',payload,pos)[0]); pos+=4
        else: raise RuntimeError(f'unsupported parquet primitive type {typ}')
    return vals

def extract(path:Path):
    data=path.read_bytes()
    if data[:4]!=b'PAR1' or data[-4:]!=b'PAR1': raise RuntimeError('not parquet')
    mlen=struct.unpack_from('<I',data,len(data)-8)[0]; meta,_=read_struct(data,len(data)-8-mlen)
    if val(meta,3)!=12: raise RuntimeError('DAY68 evidence table must contain exactly 12 rows')
    rg=blist(val(meta,4))[0]; columns={}
    for cc in blist(val(rg,1)):
        md=val(cc,3); path_names=[bstr(x) for x in blist(val(md,3))]
        if len(path_names)!=1: continue  # reason_codes list is known-empty in DAY68 summary
        name=path_names[0]; typ=val(md,1); codec=val(md,4)
        if codec!=1: raise RuntimeError('expected SNAPPY codec')
        dict_off=val(md,11); data_off=val(md,9)
        ph,pp=read_struct(data,dict_off); dn=val(val(ph,7),1); raw=snappy_decompress(data[pp:pp+val(ph,3)])
        dictionary=parse_plain(raw,typ,dn)
        ph,pp=read_struct(data,data_off); dh=val(ph,5); count=val(dh,1); enc=val(dh,2)
        raw=snappy_decompress(data[pp:pp+val(ph,3)])
        level_len=struct.unpack_from('<I',raw,0)[0]; defs,_=hybrid_decode(raw[4:4+level_len],1,count); rest=raw[4+level_len:]
        nonnull=sum(x==1 for x in defs)
        if enc not in (8,2): raise RuntimeError(f'expected dictionary encoding for {name}')
        bw=rest[0]; indices,_=hybrid_decode(rest[1:],bw,nonnull); it=iter(dictionary[i] for i in indices)
        columns[name]=[next(it) if d==1 else None for d in defs]
    required=['source_id','signal_name','fs_hz','unit','sample_count','status','rms','mav','mdf_hz','mnf_hz','benchmark_version']
    missing=[x for x in required if x not in columns]
    if missing: raise RuntimeError(f'missing columns: {missing}')
    rows=[]
    for i in range(12): rows.append({k:columns[k][i] for k in required})
    return rows

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('parquet'); ap.add_argument('csv'); ap.add_argument('--expected-sha256',required=True); ns=ap.parse_args()
    p=Path(ns.parquet); actual=hashlib.sha256(p.read_bytes()).hexdigest()
    if actual!=ns.expected_sha256: raise SystemExit(f'SHA mismatch: {actual}')
    rows=extract(p); out=Path(ns.csv); out.parent.mkdir(parents=True,exist_ok=True)
    with out.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    print(f'DAY68_PARQUET_REPLAY_OK rows={len(rows)} sha256={actual}')
if __name__=='__main__': main()
