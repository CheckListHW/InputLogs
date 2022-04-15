from mvc.Model.map_export import ExportLogs
from mvc.Model.map_property import MapProperty


class Map(MapProperty):
    __slots__ = 'columns', 'body_names', 'attach_logs', '_visible_names', 'core_samples', 'settings', \
                'interval_data', 'max_x', 'max_y', 'max_z', 'path', 'owc', 'all_logs', 'export', 'percent_safe_core'

    def __init__(self, path: str = None, data: dict = None):
        super(Map, self).__init__(path, data)

        self.export = ExportLogs(self)
