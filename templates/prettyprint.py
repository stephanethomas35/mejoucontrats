# -*- coding: utf-8 -*-
'''
@copyright Stephane Thomas - 2018-2021
Generateur de contrat pour Le Mejou - https://mejou.fr
'''

from os.path            import splitext
from glob               import glob
# from xml.dom.minidom    import parse
import xml.etree.ElementTree as ET

for filename in glob('**/content*.xml', recursive=True):
    print(filename)

    tree = ET.parse(filename)
    root = tree.getroot()
    ET.indent(root, space="  ", level=0)

    basename, extension = splitext(filename)
    newname = basename + '_' + extension

    tree.write(newname)
    # with open(newname, 'wb') as outfile:
    #     outfile.write(pretty.encode(encoding='utf-8'))
    # # end with
# end for
