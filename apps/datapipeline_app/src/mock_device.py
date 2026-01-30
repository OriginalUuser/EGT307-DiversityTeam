import pandas as pd
import random
import time

class ColumnData:
    """
    Column Object defining column name, data type, and value range
    """

    def __init__(self, name: str, dataType: type, average: float = 0, delta: float = 0):
        self.name = name
        self.dataType = dataType
        self.average = average
        self.delta = delta

created_at      = ColumnData('created_at', pd.Timestamp)
entry_id        = ColumnData('entry_id', int)
TEMPERATURE     = ColumnData('TEMPERATURE', float, 25, 5)
TURBIDITY       = ColumnData('TURBIDITY', int, 50, 50)
DISOLVED_OXYGEN = ColumnData('DISOLVED OXYGEN', float, 50, 50)
pH              = ColumnData('pH', float, 50, 50)
AMMONIA         = ColumnData('AMMONIA', float, 50, 50)
NITRATE         = ColumnData('NITRATE', int, 50, 50)
Population      = ColumnData('Population', int, 50, 50)
Length          = ColumnData('Length', float, 50, 50)
Weight          = ColumnData('Weight', float, 50, 50)

columns = [
    created_at,
    entry_id,     
    TEMPERATURE,
    TURBIDITY,
    DISOLVED_OXYGEN,
    pH,
    AMMONIA,
    NITRATE,
    Population,
    Length,
    Weight
]

class Pond:
    """
    Pond Object representing sensor network of a pond.
    Generate random data points simulating the pond data at set frequency,
    Future improvement: (then bridge/link them with set number of sub-points)
    """

    startTime = pd.Timestamp.today()
    entry_id = 0

    def __init__(self, frequencyMillisecond: int, dataPointDistance: int):
        self.freq = frequencyMillisecond
        self.dataPointDistance = dataPointDistance

    def generateColumnData(self, columnData: ColumnData) -> pd.Timestamp | int | float | None:
        """
        Generates column data of correct type:
            - created_at & entry_id columns:
                Always accurate

            - remaining columns:
                Random pick data aspect: null(10%), outlier(10%) or normal(70%)
        """

        if columnData.name == 'created_at':
            delta = self.entry_id * pd.Timedelta(milliseconds=self.freq)
            
            return self.startTime + delta
        
        if columnData.name == 'entry_id':
            self.entry_id += 1

            return self.entry_id

        aspectDict = {'null': 1, 'outlier': 2, 'normal': 7}
        dataAspect = random.choices(list(aspectDict.keys()), weights=list(aspectDict.values()), k=1)[0]

        match dataAspect:
            case 'null':
                return None
            
            case 'outlier':
                minimum = columnData.average - 2*columnData.delta
                maximum = columnData.average + 2*columnData.delta
                
            case 'normal':
                minimum = columnData.average - columnData.delta
                maximum = columnData.average + columnData.delta
        
        output = random.uniform(minimum, maximum)
        
        return columnData.dataType(output)

    def compileRowData(self) -> list:
        rowData = []
        for col in columns:
            rowData.append(self.generateColumnData(col))

        return rowData
    
    def dataStream(self):
        while True:
            out = self.compileRowData()
            print(out)
            # yield out
            # yield self.compileRowData()
            time.sleep(self.freq/1000)
            
            


""""
-----------------
Overall structure
-----------------

overarching class
    func

create class instance
call class func to generate data
let darren sort out the sending of raw data to database/straight to ingestion
"""

pond1 = Pond(500, 0)
# print(next(pond1.pondDataStream()))
# print(next(pond1.pondDataStream()))

# while True:
    # print(pond1.pondDataStream())
    # print(next(pond1.pondDataStream()))

# print(next(pond1.pondDataStream()))
# time.sleep(5)
# print(next(pond1.pondDataStream()))
# asyncio.create_task(pond1.dataStream())
pond1.dataStream()
time.sleep(50)
# pond2.dataStream()

