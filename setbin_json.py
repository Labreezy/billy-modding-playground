import binascii
import struct
import os.path as osp
import sys
import json
from binascii import hexlify
from glob import glob

BILLY_DIR = r"C:\Users\yourt\Downloads\Billy Hatcher\\"
SET_OBJ_SIZE = 0x10000

setfn = sys.argv[1]
fmt = ">I3f48s"
empty_dat = b'\x00' * 0x40
db = {}
setfn =sys.argv[1]
if "obj" in setfn:
    db = json.load(open('db/obj_db.json'))
    reverse_db = {v:k for k,v in db.items()}

for setfn in glob(osp.join(BILLY_DIR,"set_obj*.bin")):
    datalist = []
    if setfn.endswith('bin'):
        out_obj = {}

        with open(setfn,"rb") as setf:
            setf.seek(0,2)
            fsize = setf.tell()
            out_obj['fsize'] = fsize
            setf.seek(0,0)
            while setf.tell() < fsize:
                currobj = {}
                entry = setf.read(0x40)
                if entry == empty_dat:
                    break
                objid, x, y, z, params = struct.unpack(fmt,entry)
                if str(objid) in db.keys():
                    currobj['name'] = db[str(objid)]
                else:
                    currobj["name"] = "unk" + str(objid)
                currobj["position"] = [x,-z,y]
                if objid == 0x24:
                    print(currobj["position"])
                currobj['shortparams'] = list(struct.unpack('>4H',params[:8]))
                currobj['intparams'] = list(struct.unpack('>5i',params[8:0x1C]))
                currobj['floatparams'] = list(struct.unpack('>5f',params[0x1C:]))
                datalist.append(currobj)
        setfn = osp.split(setfn)[-1]
        outfn = osp.join("base_setjsons", osp.splitext(setfn)[0] + ".json")
        print("Outputting to " + outfn)
        out_obj['data'] = datalist
        json.dump(out_obj,open(outfn,"w"),indent=2)
        """print("IDs:")
        print(list(set([o['name'] for o in datalist])))
        print("done")"""
    elif setfn.endswith("json"):
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



