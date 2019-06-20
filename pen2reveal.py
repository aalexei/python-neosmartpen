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

# <?xml version="1.0"?>
# <!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.0//EN" 
#               "http://www.w3.org/TR/2001/REC-SVG-20010904/DTD/svg10.dtd">
# <svg width="134" height="38" xmlns="http://www.w3.org/2000/svg">

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
               <section>
%s
               </section>
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

def makeFragment(page, strokes, S=10):
    paths = []

    if len(strokes)==0:
        return ''

    # Find limits of fragment
    xm,ym,xM,yM = neosmartpen.bounding_box(strokes)

    for s in strokes:
        dots = s['dots']
        x0,y0,p0,dt0 = dots[0]
        D=[]

        for x,y,p,dt in dots[1:]:
            L='<line x1="%.2f" y1="%.2f" x2="%.2f" y2="%.2f" stroke-width="%.2f"/>\n'%((S*(x0-xm)), (S*(y0-ym)), (S*(x-xm)), (S*(y-ym)), (s['thickness']+4)*p)

            D.append( L )
            x0,y0,p0=x,y,p

        hexcol = neosmartpen.col2hex(s['color'])
        g = '<g stroke="%s" stroke-linecap="round">%s</g>'%(hexcol, ' '.join(D))
        paths.append(g)

    # style="position: fixed; left: 0px; top: 0px;"
    svg = '<div class="fragment">\n<svg width="%d" height="%d">\n'%(round(S*(xM-xm)), round(S*(yM-ym)))
    for p in paths:
        svg+=p
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

