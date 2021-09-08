import numpy as np
import os
import time
import pkgutil
from collections import namedtuple
from . import netpbm
import logging
from .log import log_msg

# Create a map from ascii characters to their image representation.
# Here are some scaled-down examples of the mappings in CHAR_TO_IMG.
#
#            0 0 0 0 0 0 0             0 0 1 0 1 0 0
#            0 0 1 0 0 0 0             0 1 1 1 1 1 0
#    ~  ->   0 1 0 1 0 1 0     #  ->   0 0 1 0 1 0 0
#            0 0 0 0 1 0 0             0 1 1 1 1 1 0
#            0 0 0 0 0 0 0             0 0 1 0 1 0 0

file = pkgutil.get_data(__name__, "resources/ascii.pgm").decode().split('\n')
ascii_M = netpbm._parse_ascii_netpbm(file).M
char_images = [np.pad(M,((0,0),(6,6))) for M in np.split(ascii_M, 13, axis=1)]
CHAR_TO_IMG = dict(zip(list(" .,-~:;=!*#$@"), char_images))

Ascii = namedtuple('Ascii', ['M'])
Ascii.__doc__ = '''\
Ascii image.
- M (np.ndarray): Numpy array of ascii characters.'''


def netpbm_to_ascii(image: netpbm.Netpbm) -> Ascii:
    """Return an ASCII representation of the given image.

    This function uses a particular style of
    `ASCII art <https://en.wikipedia.org/wiki/ASCII_art>`_
    in which "symbols with various intensities [are used for] creating
    gradients or contrasts."

    Args:
        image (netpbm.Netpbm): Netpbm image.

    Returns:
        Ascii: ASCII representation of image.
    """
    chars = "  -~:;=!*#$@"
    M = netpbm.change_gradient(image, len(chars)-1).M.astype(int)
    M = np.array([[chars[i] for i in row] for row in M])
    return Ascii(M=M)


def write(ascii:Ascii, path:str, type:str):
    """Write the ASCII image to the given path.

    Args:
        ascii (Ascii): An ASCII image.
        path (str): Path to write the ASCII image to.
        type (string): {"png", "txt"}
    """
    then = time.time()

    if type == "txt":
        with open(path, "w") as f:
            lines = ascii.M.astype(str).tolist()
            f.write('\n'.join([' '.join(line) for line in lines]))
            f.write('\n')
    else:
        A = np.array([[' ', '$'],['#', ' '],['~', ',']])
        A = ascii.M
        n,m = A.shape
        M = []
        for i in range(n):
            M.append([CHAR_TO_IMG[A[i,j]] for j in range(m)])
        M = np.block(M)
        n,m = M.shape
        image = netpbm.Netpbm(P=2, w=m, h=n, k=255, M=M)
        image.to_png(path, 1)

    t = time.time() - then
    size = os.stat(path).st_size
    name = path.split('/')[-1]
    logging.info(log_msg(name, t, size))
