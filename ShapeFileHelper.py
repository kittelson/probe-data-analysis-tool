import pandas as pd
import pyshp


class ShapeData():
    def __init__(self):
        self.data = None

    def read_shapefile(self, shp_path):
        """
        Read a shapefile into a Pandas dataframe with a 'polyline' column holding
        the geometry information. This uses the pyshp package
        Credit: https://gist.github.com/aerispaha/f098916ac041c286ae92d037ba5c37ba
        """
        import shapefile

        # read file, parse out the records and shapes
        sf = shapefile.Reader(shp_path)
        fields = [x[0] for x in sf.fields][1:]
        records = sf.records()
        shps = [s.points for s in sf.shapes()]

        # write into a dataframe
        self.data = pd.DataFrame(columns=fields, data=records)
        self.data = self.data.assign(polyline=shps)
