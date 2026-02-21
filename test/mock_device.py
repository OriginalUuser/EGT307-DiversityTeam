import pandas as pd
import random
import time
import requests

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
temperature     = ColumnData('temperature', float, 25, 5)
turbidity       = ColumnData('turbidity', int, 50, 50)
dissolved_oxygen= ColumnData('dissolved_oxygen', float, 50, 50)
ph              = ColumnData('ph', float, 50, 50)
ammonia         = ColumnData('ammonia', float, 50, 50)
nitrate         = ColumnData('nitrate', int, 50, 50)
population      = ColumnData('population', int, 50, 50)
fish_length     = ColumnData('fish_length', float, 50, 50)
fish_weight     = ColumnData('fish_weight', float, 50, 50)

columns = [
    created_at,
    entry_id,     
    temperature,
    turbidity,
    dissolved_oxygen,
    ph,
    ammonia,
    nitrate,
    population,
    fish_length,
    fish_weight
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
            
            return str(self.startTime + delta)
        
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
        rowData = {col.name: self.generateColumnData(col) for col in columns}
        rowData["entry_id"] = "default"
        return rowData
    
    def dataStream(self):
        while True:
            out = self.compileRowData()
            yield out            
            


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

if __name__ == "__main__":
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