from .migrator_dsv import MigratorDSV


class MigratorCSV(MigratorDSV):
    def __init__(self):
        super().__init__()
        self._delimiter = ','
