#!/usr/bin/env python3
import sys
import neosmartpen
import argparse
import logging
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)

parser = argparse.ArgumentParser(description='Convert Neo SmatPen file to reveal.js slides')
parser.add_argument('input',  help='Input smartpen file')
parser.add_argument('output', help='Output html file')
parser.add_argument('-t', nargs=4, default=(0,0,10,10), metavar=('x1','y1','x2','y2'), type=int, help='Transition trigger region')

args = parser.parse_args()

TRANSITION_REGION = args.t

def transition(x,y):
    if TRANSITION_REGION[0]<x<TRANSITION_REGION[2] and \
       TRANSITION_REGION[1]<y<TRANSITION_REGION[3]:
        return True
    else:
        return False

TEMPLATE = '''<html>
	<head>
		<meta charset="utf-8">
		<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">

		<title>reveal.js</title>

		<link rel="stylesheet" href="css/reset.css">
		<link rel="stylesheet" href="css/reveal.css">
		<link rel="stylesheet" href="css/theme/white.css">

		<!-- Theme used for syntax highlighting of code -->
		<link rel="stylesheet" href="lib/css/monokai.css">

		<!-- Printing and PDF exports -->
		<script>
			var link = document.createElement( 'link' );
			link.rel = 'stylesheet';
			link.type = 'text/css';
			link.href = window.location.search.match( /print-pdf/gi ) ? 'css/print/pdf.css' : 'css/print/paper.css';
			document.getElementsByTagName( 'head' )[0].appendChild( link );
		</script>
	</head>
	<body>
		<div class="reveal">
			<div class="slides">
%s
			</div>
		</div>

		<script src="js/reveal.js"></script>

		<script>
			// More info about config & dependencies:
			// - https://github.com/hakimel/reveal.js#configuration
			// - https://github.com/hakimel/reveal.js#dependencies
			Reveal.initialize({
				dependencies: [
					{ src: 'plugin/markdown/marked.js' },
					{ src: 'plugin/markdown/markdown.js' },
					{ src: 'plugin/notes/notes.js', async: true },
					{ src: 'plugin/highlight/highlight.js', async: true }
				]
			});
		</script>
	</body>

</html>
'''

pages = neosmartpen.parse_pages(args.input)

def makeFragment(page, strokes):
    # if page['height']>page['width']:
    #     PAGE=(A4[0],A4[1])
    # else:
    #     PAGE=(A4[1],A4[0])

    # canvas.setPageSize(PAGE)
    # S = PAGE[0]/page['width']
    paths = []
    S = 10

    if len(strokes)==0:
        return ''

    # Find limits of fragment
    xm,ym=None,None
    xM,yM=None,None

    for s in strokes:
        for x,y,p,dt in s['dots']:
            if xm==None:
                xm,ym=x,y
                xM,yM=x,y
            else:
                xm,ym=min(xm,x),min(ym,y)
                xM,yM=max(xM,x),max(yM,y)

    for s in strokes:
        dots = s['dots']
        x0,y0,p0,dt0 = dots[0]
        D = ['M',str(int(S*(x0-xm))),str(int(S*(y0-ym)))]

        for x,y,p,dt in dots[1:]:
            # canvas.setLineWidth((s['thickness']+2)*p)
            # col = s['color']
            # canvas.setStrokeColorRGB(col[1]/255,col[2]/255,col[3]/255)
            # canvas.line(S*x0,S*y0,S*x,S*y)

            D.extend( ['L',str(int(S*(x-xm))),str(int(S*(y-ym)))] )
            x0,y0,p0=x,y,p

        paths.append(' '.join(D))

    svg = '<div class="fragment"><svg width="%d" height="%d">\n'%(int(S*(xM-xm)), int(S*(yM-ym)))
    for p in paths:
        svg+='<path d="%s" stroke="#d85b49" stroke-width="1"/>\n'%p
    svg+='</svg></div>\n'

    return svg

for n,data in enumerate(pages):
    logging.info('Generating Slide: %d', n+1)
    fragments = []
    strokes = []
    for s in data['strokes']:
        dots = s['dots']
        x0,y0,p0,dt0 = dots[0]
        if transition(x0,y0):
            f = makeFragment(data, strokes)
            fragments.append(f)
            strokes = []
        else:
            strokes.append(s)
    f = makeFragment(data, strokes)
    fragments.append(f)

frags = '\n'.join(fragments)

fp = open(args.output, 'w')
fp.write(TEMPLATE%frags)
fp.close()

