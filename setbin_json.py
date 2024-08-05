import binascii
import struct
import os.path as osp
import sys
import json
from binascii import b2a_hex
from glob import glob

BILLY_DIR = r"C:\Users\yourt\Downloads\Billy Hatcher\\"
SET_OBJ_SIZE = 0x10000
ENE_STRUCT_SZ = 0x50
OBJ_STRUCT_SZ = 0x40
setfn = sys.argv[1]
fmt = ">I3f48s"
STRUCT_SZ = 0x40

db = {}
setfn =sys.argv[1]
def sanitize_param(p):
    if type(p) == bytes:
        return b2a_hex(p).decode("utf-8")
    return p
def parse_set(setf,db=None,entry_size=0x40,paramfmt=""):
    if db is not None:
        reverse_db = {v: k for k, v in db.items()}
    else:
        reverse_db = {}
        db = {}
    fmt = f">I3f{entry_size - 0x10}s"
    out_obj = {}
    datalist = []
    setf.seek(0,2)
    fsize = setf.tell()
    out_obj['fsize'] = fsize
    out_obj['entry_size'] = entry_size
    setf.seek(0, 0)
    while setf.tell() < fsize:
        currobj = {}
        entry = setf.read(entry_size)
        if entry == b'\x00' * entry_size:
            break
        objid, x, y, z, params = struct.unpack(fmt,entry)
        if str(objid) in db.keys():
            currobj['name'] = db[str(objid)]
        else:
            currobj["name"] = "unk" + str(objid)
        currobj["position"] = [x, -z, y]
        if paramfmt != "":
            currobj['params'] = list(map(sanitize_param, struct.unpack(paramfmt, params)))

        else:
            currobj['params'] = b2a_hex(params).decode("utf-8")

        datalist.append(currobj)
    out_obj['data'] = datalist
    return out_obj



obj_db = json.load(open('db/obj_db.json'))
ene_db = json.load(open('db/ene_db.json'))
for setfn in glob(osp.join(BILLY_DIR,"set_???_*.bin")):
    datalist = []
    if "obj" in setfn:
        with open(setfn,'rb') as setf:
            parsed_set = parse_set(setf,db=obj_db,entry_size=OBJ_STRUCT_SZ,paramfmt=">4H5i5f")
            setfn = osp.split(setfn)[-1]
            outfn = osp.join("obj_jsons", osp.splitext(setfn)[0] + ".json")
            print("Outputting obj set to " + outfn)
            json.dump(parsed_set, open(outfn, "w"), indent=2)
    elif "ene" in setfn:
        with open(setfn,"rb") as setf:
            parsed_set = parse_set(setf,db=ene_db,entry_size=ENE_STRUCT_SZ,paramfmt=">3s4s5s2H16s4I3f4s")
            setfn = osp.split(setfn)[-1]
            outfn = osp.join("ene_jsons", osp.splitext(setfn)[0] + ".json")
            print("Outputting ene set to " + outfn)
            json.dump(parsed_set, open(outfn, "w"), indent=2)
    else:
        print(f"Unrecognized filetype with name {setfn}")
print("Done")
""" elif setfn.endswith("json"):
        objdata = json.load(open(setfn))
        base, ext = osp.splitext(setfn)
        with open(base + "_out.bin",'wb') as binf:
            for obj in objdata['data']:
                if obj['name'].startswith("unk"):
                    id = int(obj['name'][3:])
                else:
                    id = int(reverse_db[obj['name']])
                x,nz,y = obj['position']

                extrabytes = struct.pack('>4H',*obj['shortparams'])
                extrabytes += struct.pack('>5i',*obj['intparams'])
                extrabytes += struct.pack('>5f', *obj['floatparams'])

                binf.write(struct.pack(fmt,id,x,y,-nz,extrabytes))
            while binf.tell() < objdata['fsize']:
                binf.write(empty_dat)
        print("Done")
    else:
        print("wtf did you give me man")
        """



