import time, os

from Xlib.display import Display

dpy = Display()
root = dpy.screen().root

sequence = [
    [1599, None, '=='],
    [1450, None, '<='],
    [1599, None, '=='],
]
matched = 0
done = False
lastmatch = 0

while 1:
    time.sleep(0.05)
    p = root.query_pointer()
    x, y = p.root_x, p.root_y

    if time.time()-lastmatch > 0.5:
        matched = 0
        lastmatch = 0
        done = False

    if matched == len(sequence):
        matched -= 2

    xmatch = sequence[matched][0] is None or eval('%d %s %d' % (x, sequence[matched][2], sequence[matched][0]))
    ymatch = sequence[matched][1] is None or eval('%d %s %d' % (x, sequence[matched][2], sequence[matched][1]))

    if xmatch and ymatch:
        matched += 1
        lastmatch = time.time()
        done = False

    if matched == len(sequence) and not done:
        os.system('aterm &')
        done = True

