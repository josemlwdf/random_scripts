extensions = [ 
    ".phar", ".php", ".php2", ".php3", ".php4", ".php5", ".php6", ".php7", ".php8", ".phps", ".phpt", ".pht", ".phtm", ".phtml", ".shtml", ".asp", ".aspx", ".jhtml", ".jsa", ".jsp"
]

chars =  ['%20', '%0a', '%00', '%0d0a', '/', '.\\', '.', '…', ':']

def tofile(ext):
    with open("wordlist.txt", "ab") as fh:
        fh.write(bytes(ext, encoding='utf-8'))

def main():
    img_extension = ".jpg"
    for ext in extensions:
        tofile("shell{}{}\n".format(img_extension, ext))
        tofile("shell{}{}\n".format(ext, img_extension))
        tofile("shell{}\n".format(ext.upper()))
        for char in chars:     
            tofile("shell{}{}{}\n".format(ext, char, img_extension))
            tofile("shell{}{}{}\n".format(char, ext, img_extension))
            tofile("shell{}{}{}\n".format(img_extension, ext, char))
            tofile("shell{}{}{}\n".format(img_extension, char, ext))            


main()