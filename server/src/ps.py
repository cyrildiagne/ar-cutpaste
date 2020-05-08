from photoshop import PhotoshopConnection
from os.path import dirname, basename

# TODO: This offset should be detected by getTopLeft() but the new version
# of Photoshop doesn't seem to support executeActionGet so we put it
# manually here in the meantime.
SCREEN_PIXELS_DENSITY = 2
DOC_OFFSET_X = 74 * SCREEN_PIXELS_DENSITY
DOC_OFFSET_Y = 130 * SCREEN_PIXELS_DENSITY
DOC_WIDTH = 2121
DOC_HEIGHT = 1280

def paste(filename, name, x, y, password='123456'):

    # There seem to be a bug on Windows where the path must be using unix separators.
    # https://github.com/cyrildiagne/ar-cutpaste/issues/5
    filename = filename.replace('\\', '/')

    with PhotoshopConnection(password=password) as conn:
        script = open(basename(dirname(__file__)) + '/script.js', 'r').read()
        x -= DOC_WIDTH * 0.5 + DOC_OFFSET_X
        y -= DOC_HEIGHT * 0.5 + DOC_OFFSET_Y
        script += f'pasteImage("{filename}", "{name}", {x}, {y})'
        result = conn.execute(script)
        print(result)
        if result['status'] != 0:
            return result
    
    return None
