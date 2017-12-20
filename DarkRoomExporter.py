import adsk.core
import adsk.fusion
import adsk.cam
import traceback

constructionPoints = []

def constructionPointsInOccurrences(occurrences,currentLevel):
    global constructionPoints
    for occurrence in occurrences:
        constructionPoints.append(occurrence.component.constructionPoints)
        if occurrence.childOccurrences:
            constructionPointsInOccurrences(occurrence.childOccurrences,currentLevel+1)
# This function creates the button in Fusions UI. It connects the event
# that is called when the button is created.
def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface
        # get active design        
        product = app.activeProduct
        global design
        design = adsk.fusion.Design.cast(product)
        global exportMgr
        exportMgr = design.exportManager
        global rootComp
        # get root component in this design
        rootComp = design.rootComponent
        
        fileDialog = ui.createFileDialog()
        fileDialog.isMultiSelectEnabled = False
        fileDialog.title = "Specify result filename"
        fileDialog.filter = 'yaml files (*.yaml)'
        fileDialog.filterIndex = 0
        dialogResult = fileDialog.showSave()
        if dialogResult == adsk.core.DialogResults.DialogOK:
            filename = fileDialog.filename
        else:
            return

        f = open(filename, 'w')
        
        name = rootComp.occurrences[0].name
        name.replace(":","_")
        f.write('name: ' + name + '\n');
        f.write('ObjectID: 0\n');
        f.write('mesh: ' + name + '\n');

        # Get construction points
        level = 0
        constructionPointsInOccurrences(rootComp.occurrences,0)
        global constructionPoints
        f.write('sensor_relative_locations:\n');
        i = 0
        for points in constructionPoints:
            for point in points:
                if point.name[:2] == "LS":
                    line = '- [' + str (i) + ', ' + str(point.geometry.x/100) + ', ' + str(point.geometry.y/100) + ', ' + str(point.geometry.z/100) + ']\n'
                    f.write(line);
                    i = i+1
        f.close()
        dialogResult = ui.messageBox('Cooridates of all construction points written to file: ' + filename) 

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
