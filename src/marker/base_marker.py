from src import db, SELECT_EDGE_DISTANCE, ASSET_ID


class BaseMarker:
    def __init__(self, id, frame, label_id, trackable, *args):
        self.id = id
        self.frame = frame
        self.label_id = label_id
        self.trackable = trackable
        self.init(*args)
    
    def set_untrackable(self):
        self.trackable = 0
        self.save()

    def save(self):
        if self.id is None:
            self.insert()
        else:
            self.update()

    def insert(self):
        query = "INSERT INTO %s VALUES (NULL, ?, ?, ?, ?, %s)" % (self.DB_TABLE, ", ".join(["?"] * len(self.DB_COLUMNS.keys())))
        print(query)

        db.execute(query, (
            ASSET_ID,
            self.frame,
            self.label_id,
            self.trackable,
            *self.get_db_values()
        ))
        db.commit()

        self.id = db.lastrowid()

    def update(self):
        columns = ", ".join([column + "=?" for column in self.DB_COLUMNS.keys()])
        query = "UPDATE %s SET trackable=?, %s WHERE id=?" % (self.DB_TABLE, columns)
        print(query)

        db.execute(query, (self.trackable, *self.get_db_values(), self.id))
        db.commit()

    def remove(self):
        query = "DELETE FROM %s WHERE id=?" % (self.DB_TABLE,)
        print(query)

        db.execute(query, (self.id,))
        db.execute("DELETE FROM interpolated_markers WHERE src_marker_table=? AND src_marker_id=?", (self.DB_TABLE, self.id))
        db.execute("DELETE FROM interpolated_markers WHERE dst_marker_table=? AND dst_marker_id=?", (self.DB_TABLE, self.id))
        db.commit()
