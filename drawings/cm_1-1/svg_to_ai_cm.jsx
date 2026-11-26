// Converts every *_RevV.svg in this folder to .ai: new document in centimetres, drawing at real size, artboard fitted.
#target illustrator
(function () {
  var dir = Folder("/Users/nunt/gitroot/dreamcon2026/drawings/cm_1-1");
  var files = dir.getFiles("*_RevV.svg"), log = [];
  app.userInteractionLevel = UserInteractionLevel.DONTDISPLAYALERTS;
  function cmDoc(name) {
    var p = new DocumentPreset(); p.units = RulerUnits.Centimeters; p.width = 16383; p.height = 16383;
    p.colorMode = DocumentColorSpace.RGB; p.title = name;
    return app.documents.addDocument(DocumentColorSpace.RGB, p);
  }
  for (var i = 0; i < files.length; i++) {
    var f = files[i], name = decodeURI(f.name).replace(/\.svg$/i, ""), doc = null, how = "";
    try {
      doc = cmDoc(name);
      var g = doc.groupItems.createFromFile(f), b = g.geometricBounds;
      doc.artboards[0].artboardRect = [b[0], b[1], b[2], b[3]]; how = "import";
    } catch (e1) {
      try {                                    // fallback: open the SVG, copy everything into the cm document
        if (doc) doc.close(SaveOptions.DONOTSAVECHANGES);
        var src = app.open(f); app.executeMenuCommand("selectall"); app.copy();
        doc = cmDoc(name); app.paste(); doc.fitArtboardToSelectedArt(0);
        src.close(SaveOptions.DONOTSAVECHANGES); app.activeDocument = doc; how = "open+paste";
      } catch (e2) { log.push(name + " ERROR " + e1 + " / " + e2); continue; }
    }
    var r = doc.artboards[0].artboardRect;
    var o = new IllustratorSaveOptions(); o.pdfCompatible = true;
    doc.saveAs(File(dir.fsName + "/" + name.replace(/RevV$/, "RevW") + ".ai"), o);
    log.push(name.replace(/RevV$/, "RevW") + ".ai | " + how + " | " + doc.rulerUnits + " | " + ((r[2] - r[0]) / 72 * 2.54).toFixed(2) + " x " + ((r[1] - r[3]) / 72 * 2.54).toFixed(2) + " cm");
    doc.close(SaveOptions.DONOTSAVECHANGES);
  }
  app.userInteractionLevel = UserInteractionLevel.DISPLAYALERTS;
  var lf = File(dir.fsName + "/convert_log.txt"); lf.open("w"); lf.write(log.join("\n")); lf.close();
})();
