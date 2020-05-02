from photoshop import PhotoshopConnection


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
            //doc.activeLayer.translate(
            //    x + doc.layers[doc.layers.length-1].bounds[0] - doc.activeLayer.bounds[0],
            //    y + doc.layers[doc.layers.length-1].bounds[1] - doc.activeLayer.bounds[1]);
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
        print(filename)
        script += f'pasteImage("{filename}", "{name}", "{x}", "{y}")'
        conn.execute(script)