from photoshop import PhotoshopConnection

# TODO: This offset should be detected by getTopLeft() but the new version
# of Photoshop doesn't seem to support executeActionGet so we put it
# manually here in the meantime.
DOC_OFFSET_X = 440
DOC_OFFSET_Y = 240
DOC_WIDTH = 1697
DOC_HEIGHT = 1024

def paste(filename, name, x, y, password='123456'):

    with PhotoshopConnection(password=password) as conn:
        script = """
        function pasteImage(filename, layerName, x, y) {
            var fileRef = new File(filename);
            var doc = app.activeDocument;
            
            var currentLayer = doc.artLayers.add();
            var curr_file = app.open(fileRef);
            curr_file.selection.selectAll();
            curr_file.selection.copy();
            curr_file.close();

            doc.paste();
            doc.activeLayer.name = layerName;
            doc.activeLayer.translate(x, y);
            doc.activeLayer.move(doc.layers[0], ElementPlacement.PLACEBEFORE);
        }
        function getTopLeft() {
            try {
                var r = new ActionReference();
                var bounds = executeActionGet(r)
                    .getObjectValue(stringIDToTypeID("viewInfo"))
                    .getObjectValue(stringIDToTypeID("activeView"))
                    .getObjectValue(stringIDToTypeID("globalBounds"));
                alert(t)
            } catch (e) {
                alert(e);
            }
        }
        """
        x -= DOC_WIDTH * 0.5 + DOC_OFFSET_X
        y -= DOC_HEIGHT * 0.5 + DOC_OFFSET_Y
        script += f'pasteImage("{filename}", "{name}", {x}, {y})'
        conn.execute(script)