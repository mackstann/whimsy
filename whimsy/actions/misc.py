# Written by Nick Welch in the years 2005-2008.  Author disclaims copyright.

def socksend(host, port, text):
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        s.send(text)
        s.close()
    except socket.error:
        pass

