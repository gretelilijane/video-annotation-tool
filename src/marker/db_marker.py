from src.constants import 

class DbMarker:
    def __init__(self, frame, label):
        self.type = self.__class__.__name__
        self.frame = frame
        self.label = label
        self.id = None

    def save(self):
        params = self.get_params()

    def insert(self):
        db_cur.execute("INSERT INTO rect_markers VALUES (NULL, ?, ?, ?, ?, ?, ?)", (
            self.frame,
            self.label,
            *self.get_db_params()
        ))

        self.id = db_cur.lastrowid
