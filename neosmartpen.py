import os, sys, re
import struct
from zipfile import ZipFile

def parse_pagedata(raw):
    '''
    Parse the binary page.data format into python structure
    '''
    # Spec from https://github.com/NeoSmartpen/Documentations/blob/master/NeoNote_data_Eng_V1.0.pdf
    # Appears to be little endian
    # page.data:
    #
    # bytes desc
    # 3  'neo' (verification string)
    # 4  File version
    # 4  Note type
    # 4  Page Number
    # 4  (Float 32) notebook width
    # 4  (Float 32) notebook height
    # 8  created timestamp (millisecond)
    # 8  modified timestamp (millisecond)
    # 1  Flag if data modified
    # 4  number of strokes
    # ... stroke data ...
    # 4  Length of guid string
    # *  Page guid string (for evernote?)
    #
    # stroke:
    # 1  Type (0=stroke, 1=voice memo)
    # 4  Color 32 bits RGBA
    # 1  Thickness (0,1,2)
    # 4  Number of dots
    # 8  Start timestamp (millisecond)
    # ... dots ...
    # 1  Length of extra data (0-255)
    # ... extra data ... (Pen type: 0=Neo smart pen, 1=pem from neo notes, 2=highlighter from neo notes)
    #
    # dot data 13 bytes:
    # 4  x (float 32)
    # 4  y (Float 32)
    # 4  pressure (Float 32)
    # 1  time diff from previous dot
    #
    # x and y where normalised by max(width,height)

    o = struct.unpack('<3s3i2f2Q?I', raw[:44])

    if o[0]!=b'neo':
        raise Exception("Not a valid neopen data file")

    data = {'neo':o[0], 'file_version':o[1], 'note_type':o[2], 'page':o[3],
            'width':o[4], 'height':o[5], 'ctime':o[6], 'mtime':o[7],
            'modified':o[8], 'strokes':[]}

    nstrokes = o[9]

    start = 44
    for n in range(nstrokes):
        o = struct.unpack('<BIBIQ', raw[start:start+18])
        #import pudb; pudb.set_trace()

        if o[0]==1:
            # audio registration, not a pen stroke, skip it.
            start+=108
            continue

        col = [(o[1]>>(8*i))&0xff for i in range(3,-1,-1)]

        stroke = {'type':o[0], 'color':col, 'thickness':o[2], 'time':o[4]}
        ndots = o[3]
        start2 = start+18
        dots = []
        if ndots > 1000:
            # something has gone wrong
            raise Exception('Something has gone wrong parsing dots in stroke')
        for m in range(ndots):
            d = struct.unpack('<fffB', raw[start2:start2+13])
            dots.append(d)  #x,y,pressure,dt
            start2 += 13

        stroke['dots'] = dots

        N = struct.unpack('<B', raw[start2:start2+1])[0]
        extra = struct.unpack('<%dc'%(N), raw[start2+1:start2+N+1])
        data['strokes'].append(stroke)
        start=start2+1+N

    return data

def parse_pages(path):
    '''
    Parse zip file and extract stroke data on each page
    '''

    zip = ZipFile(path)
    pages = [p for p in zip.namelist() if p.endswith('page.data')] 
    pagepaths = []
    for p in zip.namelist():
        if p.endswith('page.data'):
            so = re.search('Data/(\d+)\.page_store', p)
            n=int(so.group(1))
            pagepaths.append((n,p))

    pagepaths.sort(key=lambda x: x[1])

    pages = []
    for n,p in pagepaths:
        zp = zip.open(p)
        raw = zp.read()
        zp.close()
        data = parse_pagedata(raw)
        pages.append(data)

    return pages


if __name__ == "__main__":
    pages = parse_pages(sys.argv[1])

    for n,data in enumerate(pages):
        print('Page ', n+1)
        for m,s in enumerate(data['strokes']):
            print('\nStroke {}'.format(m))
            if s['type']==0:
                print('col:',s['color'], ' thickness:', s['thickness'])
                for x,y,p,dt in s['dots']:
                    print('x:{x:.2f}, y:{y:.2f}, p:{p:.2f}, dt:{dt:2d}'.format(**locals()))
            else:
                print('audio')
