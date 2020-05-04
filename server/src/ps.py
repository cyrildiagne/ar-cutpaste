from photoshop import PhotoshopConnection


def paste(filename, name, x, y, password='123456'):

    with PhotoshopConnection(password=password) as conn:
        script = """
        function pasteImage(filename, layerName, x, y) {
            var fileRef = new File(filename);
            var doc = app.activeDocument;

            app.preferences.rulerUnits = Units.PIXELS;
            
            var currentLayer = doc.artLayers.add();
            var curr_file = app.open(fileRef);
            curr_file.selection.selectAll();
            curr_file.selection.copy();
            curr_file.close();

            doc.paste();
            doc.activeLayer.name = layerName;

            var doc_x = Number(doc.width);
            var doc_y = Number(doc.height);
            
            // Some magic numbers in here, but works well
            var new_x = x - ((doc_x * 0.5) + (74 * 2));
            var new_y = y - ((doc_y * 0.5) + (130 * 2));

            doc.activeLayer.translate(new_x, new_y);
            try {
                doc.activeLayer.move(doc.layers[doc.layers.length - 1], ElementPlacement.PLACEBEFORE);
            } catch(e) {
                alert(e);
            }
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
        script += f'pasteImage("{filename}", "{name}", {x}, {y})'
        conn.execute(script)
