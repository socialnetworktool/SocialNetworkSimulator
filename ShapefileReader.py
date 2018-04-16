"""
reading shapefiles into memory and construct a set of Points, Polylines or Polygons.
"""
import struct

# constants for shape types
SHP_TYPE_POINT,SHP_TYPE_LINE,SHP_TYPE_POLYGON = 1, 3, 5

# Classes for Point, Polyline and Polygon
class Point:
    """
    The Point class

    Attributes
    ----------

    x             : float
                    coordinate x
    y             : float
                    coordinate y
    color         : string
                    color for rendering
    """
    def __init__(self, x = 0.0, y = 0.0):
        self.x = x
        self.y = y
        self.color = 'white'
        self.outline = "white"

class Polyline:
    """
    The Polyline class

    Attributes
    ----------

    points        : array
                    coordinates
    partsNum      : integer
                    number of parts
    color         : string
                    color for rendering
    """
    def __init__(self, points= [], partsNum = 0):
        self.points = points
        self.partsNum = partsNum
        self.color = 'black'

class Polygon:
    """
    The Polygon class

    Attributes
    ----------

    points        : array
                    coordinates
    partsNum      : integer
                    number of parts
    color         : string
                    color for rendering
    """
    def __init__(self, points= [], partsNum = 0):
        self.points = points
        self.partsNum = partsNum
        self.color = '#008141'

    def getCentroid(self):
        """
        Get the centroid
        """
        index = 0
        xBar = 0.0
        yBar = 0.0
        """
        Fomula to calcuate the xbar and ybar
        ## xbar = sum of ((x[i+1]+x[i])*(x[i+1]*y[i]-x[i]*y[i+1]))/6*area
        ## ybar = sum of ((y[i+1]+y[i])*(x[i+1]*y[i]-x[i]*y[i+1]))/6*area
        """
        area = self.getArea()
        while index < len(self.points)-1:
            #Sagar Jha - Comment added
            #print self.points[index+1].x
            curentXBar = (1.0/(6.0*area))*(self.points[index+1].x + self.points[index].x)\
                         *(self.points[index+1].x * self.points[index].y - \
                            self.points[index].x * self.points[index+1].y)
            xBar = xBar + curentXBar
            curentYBar = (1.0/(6.0*area))*(self.points[index+1].y + self.points[index].y)\
                         *(self.points[index+1].x * self.points[index].y - \
                            self.points[index].x * self.points[index+1].y)
            yBar = yBar + curentYBar
            index += 1
        #Sagar Jha - Comment added
        #print 'xBar, yBar', xBar, yBar
        centroid = Point(xBar, yBar)
        return centroid

    def getArea(self):
        """
        Get the area
        """
        index = 0
        area = 0
        """
        Fomula to calcuate the area
        ## area = sum of ((x[i+1]*y[i]-x[i]*y[i+1]))/2
        """
        while index < len(self.points)-1:
            currentArea = (1.0/2.0)*(self.points[index+1].x * self.points[index].y - \
                          self.points[index].x * self.points[index+1].y)
            area = area + currentArea
            index += 1
        return area

def read_shp(shp_file_path):
    """
    Read in the shapefile

    Parameters
    ----------

    shp_file_path    : string
                       File path of the input shapefile

    Returns
    --------

    shapes           : array
                      The spatial units
    bbox             : array
                      The bounding box: minX, minY, maxX, maxY
    shp_type         : integer
                      The shape types: SHP_TYPE_POINT,SHP_TYPE_LINE,SHP_TYPE_POLYGON

    """
    recordsOffset, bbox = read_shx(shp_file_path)
    # open the main file for read in binary
    shpFile = open(shp_file_path,"rb")
    shpread = shpFile.read(100)        # first 100 bytes contain header
    shp_type = struct.unpack('<l',shpread[32:36])[0]   # type of shape file

    # read data according to its type
    shapes = []
    if shp_type == SHP_TYPE_POINT:
        shapes = read_points(shpFile)
    elif shp_type == SHP_TYPE_LINE:
        shapes = read_polylines(shpFile,recordsOffset)
    elif shp_type == SHP_TYPE_POLYGON:
        shapes = read_polygons(shpFile,recordsOffset)

    return shapes,shp_type,bbox

def read_shx(shp_file_path):
    """
    Read in the shx file and construct the offsets of records and the bounding box

    Parameters
    ----------

    shp_file_path    : string
                       File path of the input shapefile

    Returns
    --------

    recordsOffset    : array
                      The offsets of records
    bbox             : array
                      The bounding box: minX, minY, maxX, maxY

    """
    shxFile = open(shp_file_path[:-3] + 'shx',"rb")
    # read first 28 bytes
    s = shxFile.read(28)
    # convert into 7 integers
    header = struct.unpack(">iiiiiii",s)
    # get file length
    fileLength = header[len(header)-1]
    # calculate numbers in the shape file based on index file length
    num = (fileLength*2-100)/8
    print 'fileLength, number of units:',fileLength, num
    # read other 72 bytes in header
    s = shxFile.read(72)
    # convert into values
    header = struct.unpack("<iidddddddd",s)
    # get bounding box for the shape file
    bbox = header[2],header[3],header[4],header[5]
    # define an empty list for holding offset of each feature in main file
    recordsOffset = []
    # loop through each feature
    for i in range(0,num):
        # jump to beginning of each record
        shxFile.seek(100+i*8)
        # read out 4 bytes as offset
        s = shxFile.read(4)
        offset = struct.unpack('>i',s)
        # keep the offset in the list
        recordsOffset.append(offset[0]*2)
    # close the index file
    shxFile.close()
    return recordsOffset, bbox

def read_points(shpFile):
    """
    Read points from shape file

    Parameters
    ----------

    shp_file_path    : string
                       File path of the input shapefile
    recordsOffset    : array
                      The offsets of records

    Returns
    --------

    shapes           : array
                      The points

    """
    # define an empty list for points
    points = []
    shpFile.seek(24)
    s = shpFile.read(4) #Get the file length
    b = struct.unpack('>i',s)
    featNum = (b[0]*2-100)/28

    for i in range(0,featNum):
        shpFile.seek(100+12+i*28) ## 12 bytes = Record Number + Content Length + Shape Type
        s = shpFile.read(16)
        x,y = struct.unpack('dd',s)
        points.append(Point(x, y))
    return points

def read_polylines(shpFile,recordsOffset):
    """
    Read polylines from shape file

    Parameters
    ----------

    shp_file_path    : string
                       File path of the input shapefile
    recordsOffset    : array
                      The offsets of records

    Returns
    --------

    shapes           : array
                      The polylines

    """
    # define an empty list for polylines
    polylines = []
    # loop through each offset of all polylines
    for offset in recordsOffset:
        # define two lists for holding values
        x, y = [], []
        # jump to partsNum and pointsNum of the polyline and read them out
        shpFile.seek(offset+8+36)
        s = shpFile.read(8)
        # generate an empty polyline object
        polyline = Polyline()
        partsNum, pointsNum = struct.unpack('ii',s)
        polyline.partsNum = partsNum

        # read the list of parts holding the starting sequential number of point in that part
        s = shpFile.read(4*partsNum)
        # compose the unpack format based on number of parts
        str_num = ''
        for _ in range(partsNum):
            str_num += "i"
        # get the starting point number of each part and keep in a partsIndex list
        polyline.partsIndex = struct.unpack(str_num,s)
        # loop through each point in the polyline
        for _ in range(pointsNum):
            # read out polyline coordinates and add to the points' x, y coordinates' lists
            s = shpFile.read(16)
            pointx, pointy = struct.unpack('dd',s)
            #print ' pointx, pointy: ', pointx, pointy
            x.append(pointx)
            y.append(pointy)

        # assign x, y lists to the polyline
        polyline.x, polyline.y = x, y
        # add the polyline read to the
        polylines.append(polyline)
    return polylines

def read_polygons(shpFile,recordsOffset):
    """
    Read polygons from shape file

    Parameters
    ----------

    shp_file_path    : string
                       File path of the input shapefile
    recordsOffset    : array
                      The offsets of records

    Returns
    --------

    shapes           : array
                      The polygons

    """
    # define an empty list for polygons
    polygons = []
    # loop through each offset of all polygons
    for offset in recordsOffset:
        # define two lists for holding values
        x, y = [], []
        # jump to partsNum and pointsNum of the polygons and read them out
        shpFile.seek(offset+8+36)
        s = shpFile.read(8)
        # generate an empty polygon object
        polygon = Polygon()
        partsNum, pointsNum = struct.unpack('ii',s)
        polygon.partsNum = partsNum
        # read the list of parts holding the starting sequential number of point in that part
        s = shpFile.read(4*partsNum)
        """
        Compose the unpack format based on number of parts
        When we unpack a binary string, we need use a format eg., 'i' for one integer,
        'ii' for two integer. However, we do not know how many integer(partsNum) we need
        to unpack, therefore we need to use a loop to iterate the partsNum,
        for each partsNum, we add one 'i' to the str.
        Therefore if the partsNum equal to, for example, 2,
        the str will equal to 'ii' after the loop
        """
        str_num = ''
        for _ in range(partsNum):
            str_num += "i"
        # get the starting point number of each part and keep in a partsIndex list
        polygon.partsIndex = struct.unpack(str_num,s)
        # loop through each point in the polyline
        points = []
        for _ in range(pointsNum):
            # read out polygon coordinates and add to the points' x, y coordinates' lists
            s = shpFile.read(16)
            x, y = struct.unpack('dd',s)
            point = Point(x, y)
            points.append(point)
        # assign points lists to the polygon
        polygon.points = points
        # add the polygon read to the
        polygons.append(polygon)
    return polygons
