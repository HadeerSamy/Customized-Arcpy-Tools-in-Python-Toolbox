# -*- coding: utf-8 -*-

import arcpy
from arcpy import metadata as md

class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Toolbox"
        self.alias = "toolbox"

        # List of tool classes associated with this toolbox
        self.tools = [CopySubtype, GDB_Metadata, deleteRandomPoints,upstreamCatchments]


class CopySubtype(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Copy Subtype"
        self.description = "This tool copy subtypes between different layers"
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        param0 = arcpy.Parameter(
            displayName="Input Features",
            name="in_features",
            datatype=["DEFeatureClass", "GPFeatureLayer"],
            parameterType="Required",
            direction="Input")
        param1 = arcpy.Parameter(
            displayName="Subtype Field",
            name="subtype_field",
            datatype="Field",
            parameterType="Required",
            direction="Input")
        param2 = arcpy.Parameter(
            displayName="Subtype Layer",
            name="subtype_layer",
            datatype=["DEFeatureClass", "GPFeatureLayer"],
            parameterType="Required",
            direction="Input")

        param1.filter.list = ['Short', 'Long']

        param1.parameterDependencies = [param0.name]

        params = [param0, param1, param2]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        in_features = parameters[0].valueAsText
        subtypeField = parameters[1].valueAsText
        subtypeLayer = parameters[2].valueAsText

        subtypes = arcpy.da.ListSubtypes(subtypeLayer)
        SubtypesDictionary = {}
        
        for stcode, stdict in list(subtypes.items()):
            for stkey in list(stdict.keys()):
                if stkey == "Name":
                    SubtypesDictionary[stcode] = stdict[stkey]

        
        arcpy.management.SetSubtypeField(in_features, subtypeField)
        
        for code in SubtypesDictionary:
            arcpy.management.AddSubtype(in_features, code, SubtypesDictionary[code])

    def postExecute(self, parameters):
        """This method takes place after outputs are processed and
        added to the display."""
        return


class GDB_Metadata(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "GDB Metadata"
        self.description = "This tool exports all the Metadata of all the layers into a table"
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        param0 = arcpy.Parameter(
            displayName="Geodatabase",
            name="GDB",
            datatype="DEWorkspace",
            parameterType="Required",
            direction="Input")
        param1 = arcpy.Parameter(
            displayName="Output Table",
            name="outputTable",
            datatype="DETable",
            parameterType="Required",
            direction="Output")


        params = [param0, param1]
        return params

    def insertingRows(self, featuresArray, createdTable, tableFields, datasetName):
        if (featuresArray == None):
            pass
        else:
            for j in range(len(featuresArray)):

                featureName = featuresArray[j]


                featureGeometry = arcpy.Describe(featuresArray[j]).shapeType

                    

                try:
                    featureCredits = md.Metadata(featureName).credits
                    if featureCredits != None and len(featureCredits) > 255:
                        featureCredits = featureCredits[:255]
                except RuntimeError:
                    featureCredits = "***Metadata Error***"
                    
                try:
                    featureTitle = md.Metadata(featureName).title
                    if featureTitle != None and len(featureTitle) > 255:
                        featureTitle = featureTitle[:255]
                except RuntimeError:
                    featureTitle = "***Metadata Error***"
                    
                try:
                    featureTags = md.Metadata(featureName).tags
                    if featureTags != None and len(featureTags) > 255:
                        featureTags = featureTags[:255]
                except RuntimeError:
                    featureTags = "***Metadata Error***"
                    
                try:
                    featureSummary = md.Metadata(featureName).summary
                    if featureSummary != None and len(featureSummary) > 255:
                        featureSummary = featureTags[:255]
                except RuntimeError:
                    featureSummary = "***Metadata Error***"
                    
            
                try:
                    featureDescription = md.Metadata(featureName).description
                    if featureDescription:
                        featureDescription = re.sub(r'<[^>]*>', '', featureDescription)
                    if featureDescription != None and len(featureDescription) > 255:
                        featureDescription = featureTags[:255]
                except RuntimeError:
                    featureDescription = "***Metadata Error***"
                    

                    

                    
                with arcpy.da.InsertCursor(createdTable, tableFields) as cursor:
                    cursor.insertRow((datasetName, featureName, featureGeometry, featureCredits, featureTitle, featureTags, featureSummary, featureDescription))    
     
    def execute(self, parameters, messages):
        Geodatabase = parameters[0].valueAsText
        outputTable = parameters[1].valueAsText
        arcpy.env.workspace = Geodatabase

        arcpy.management.CreateTable(os.path.dirname(outputTable), os.path.basename(outputTable))

        fields = ["featureDataset", "featureClass", "GeometryType", "Credits", "Title", "Tags", "Summary", "Description" ]

        for k in range(len(fields)):
            arcpy.management.AddField(outputTable, fields[k], "TEXT")

        # Get a list of all feature datasets in the GDB
        feature_datasets = arcpy.ListDatasets()

        for i in range(len(feature_datasets)):

            datasetName = feature_datasets[i]

            
            
            featureLayers = arcpy.ListFeatureClasses("*", "All", datasetName)

            self.insertingRows(featureLayers, outputTable, fields, datasetName)


        aloneFeatureLayers = arcpy.ListFeatureClasses("*","All",None)

        self.insertingRows(aloneFeatureLayers, outputTable, fields,"NO Dataset")

    def postExecute(self, parameters):
        """This method takes place after outputs are processed and
        added to the display."""
        return


class deleteRandomPoints(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Remove Near Points "
        self.description = "This tool removes near points within a specific distance"
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        param0 = arcpy.Parameter(
            displayName="Input Features",
            name="in_features",
            datatype=["DEFeatureClass", "GPFeatureLayer"],
            parameterType="Required",
            direction="Input")
        
        param1 = arcpy.Parameter(
            displayName="Search radius in Meters",
            name="searchRadius",
            datatype="GPDouble",
            parameterType="Required",
            direction="Input")
        
        param2 = arcpy.Parameter(
            displayName="Output Near Table",
            name="near_table",
            datatype="DETable",
            parameterType="Required",
            direction="Output")
        
        param3 = arcpy.Parameter(
            displayName="Output Features",
            name="out_features",
            datatype=["DEFeatureClass", "GPFeatureLayer"],
            parameterType="Required",
            direction="Output")





        params = [param0, param1, param2, param3]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        if parameters[0].value:
            desc = arcpy.Describe(parameters[0].value)
            if desc.shapeType != "Point":
                parameters[0].setErrorMessage("Only point features are allowed.")

    def execute(self, parameters, messages):
        in_features = parameters[0].valueAsText
        searchRadius = parameters[1].valueAsText
        near_table = parameters[2].valueAsText
        out_features = parameters[3].valueAsText


        arcpy.analysis.GenerateNearTable(in_features, in_features, near_table, f"{searchRadius} Meters", 
                                         'NO_LOCATION', 'NO_ANGLE', 'ALL')

        keep_set = set()
        delete_set = set()
        with arcpy.da.SearchCursor(near_table, ["IN_FID", "NEAR_FID"]) as cursor:
            for in_fid, near_fid in cursor:
                if in_fid not in keep_set and in_fid not in delete_set:
                    keep_set.add(in_fid)
                if near_fid not in delete_set and near_fid not in keep_set:
                    delete_set.add(near_fid)

        oid_field = arcpy.Describe(in_features).OIDFieldName
        # arcpy.AddMessage(delete_set)
        oids_to_delete = list(delete_set)
        # arcpy.AddMessage("List is")
        # arcpy.AddMessage(oids_to_delete)
        if oids_to_delete:
            oid_list_str = ",".join(str(oid) for oid in oids_to_delete)
            arcpy.AddMessage(oid_list_str)
            where_clause = f"{oid_field} NOT IN ({oid_list_str})"
            arcpy.AddMessage(where_clause)
        else:
            # If nothing to delete, keep all features
            where_clause = "1=1"

        arcpy.conversion.ExportFeatures(in_features, out_features, where_clause)


    def postExecute(self, parameters):
        """This method takes place after outputs are processed and
        added to the display."""
        return
    




class upstreamCatchments(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "upstream Catchments"
        self.description = "Defines all the updtream catchments of manholes"
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        param0 = arcpy.Parameter(
            displayName="Manholes",
            name="manholes",
            datatype=["DEFeatureClass", "GPFeatureLayer"],
            parameterType="Required",
            direction="Input")
        
        param1 = arcpy.Parameter(
            displayName="Manhole ID",
            name="Manhole_ID",
            datatype="Field",
            parameterType="Required",
            direction="Input")
        
        param2 = arcpy.Parameter(
            displayName="Conduits/Pipes",
            name="Conduits",
            datatype=["DEFeatureClass", "GPFeatureLayer"],
            parameterType="Required",
            direction="Input")

        param3 = arcpy.Parameter(
            displayName="upstream Node",
            name="upstreamNode",
            datatype="Field",
            parameterType="Required",
            direction="Input")   

        param4 =arcpy.Parameter(
            displayName="downstream Node",
            name="downstreamNode",
            datatype="Field",
            parameterType="Required",
            direction="Input")  
        
        param5 = arcpy.Parameter(
            displayName="Catchments",
            name="Catchments",
            datatype=["DEFeatureClass", "GPFeatureLayer"],
            parameterType="Required",
            direction="Input")
        
        param6 = arcpy.Parameter(
            displayName="Catchments Name",
            name="catchmentName",
            datatype="Field",
            parameterType="Required",
            direction="Input")
        

        param7 = arcpy.Parameter(
            displayName="Output Feature",
            name="out_features",
            datatype=["DEFeatureClass"],
            parameterType="Required",
            direction="Output")


        # param0.filter.list = ["Point"]
        # param2.filter.list = ["Line"]
        # param5.filter.list = ["Polygon"]


        param1.parameterDependencies = [param0.name]
        param3.parameterDependencies = [param2.name]
        param4.parameterDependencies = [param2.name]
        param6.parameterDependencies = [param5.name]


        params = [param0, param1, param2, param3, param4, param5, param6,param7]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        if parameters[0].value:
            desc = arcpy.Describe(parameters[0].value)
            if desc.shapeType != "Point":
                parameters[0].setErrorMessage("Only point features are allowed.")
        
        if parameters[2].value:
            desc = arcpy.Describe(parameters[2].value)
            if desc.shapeType != "Polyline":
                parameters[2].setErrorMessage("Only Polyline features are allowed.")

        if parameters[5].value:
            desc = arcpy.Describe(parameters[5].value)
            if desc.shapeType != "Polygon":
                parameters[5].setErrorMessage("Only polygon features are allowed.")

    def execute(self, parameters, messages):
        manholes = parameters[0].valueAsText
        manholesID = parameters[1].valueAsText
        pipes = parameters[2].valueAsText
        upstreamNode = parameters[3].valueAsText
        downstreamNode = parameters[4].valueAsText
        catchment = parameters[5].valueAsText
        catchmentName = parameters[6].valueAsText
        manholesFinalized = parameters[7].valueAsText

        
        arcpy.env.workspace = "in_memory"
        tempJoin = "manholes_joined"

        arcpy.analysis.SpatialJoin(manholes, 
                                catchment, 
                                tempJoin, 
                                "JOIN_ONE_TO_MANY", 
                                "KEEP_ALL", 
                                None, 
                                "INTERSECT")

        arcpy.management.DeleteIdentical(tempJoin, [manholesID,catchmentName])

        arcpy.management.Dissolve(tempJoin, 
                                manholesFinalized, 
                                manholesID, 
                                [[catchmentName, "CONCATENATE"]], 
                                "MULTI_PART", 
                                "DISSOLVE_LINES", 
                                " *-+ ")

        arcpy.management.Delete(tempJoin)

        G = nx.DiGraph()
        
        #building the network

        with arcpy.da.SearchCursor(pipes, [upstreamNode, downstreamNode]) as cursor:

            for up, down in cursor:

                if up and down:

                    G.add_edge(up, down)
                    
                    
        arcpy.management.AddField(manholesFinalized, 
                                "All_Catchments", 
                                "TEXT", 
                                None, 
                                None, 
                                1000)
                    
                    
        with arcpy.da.UpdateCursor(manholesFinalized, [manholesID,"All_Catchments"]) as Manholecursor:

            for mn in Manholecursor:

                if mn[0] in G:
                    upstream_nodes = nx.ancestors(G, mn[0])
                    upstream_nodes.add(mn[0])
                else:
                    upstream_nodes = {mn[0]}
        
        
        
                catchment = set()

                #bmsk kol node mn elly 2blo w aktb l catchments beto3ha gowa set 34an myb2a4 feeh duplications

                for i in upstream_nodes:
        
                    with arcpy.da.SearchCursor(manholesFinalized, [f"CONCATENATE_{catchmentName}"], where_clause=f"{manholesID} = '{i}'") as cursor:

                        for row in cursor:
        
                            parts = row[0].split(" *-+ ")

                            catchment.update(parts)
        
                print(catchment)

                mn[1] = " , ".join(catchment)

                Manholecursor.updateRow(mn)           

   


    def postExecute(self, parameters):
        """This method takes place after outputs are processed and
        added to the display."""
        return


#This script is written by Hadeer Samy 

# hadeersamy730@gmail.com

