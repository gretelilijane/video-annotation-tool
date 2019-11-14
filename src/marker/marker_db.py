from src.constants import ASSET_ID, db, db_cur

# Marker tables
marker_tables = {}

# Add marker class
def add_marker_class(Marker):
    marker_tables[Marker.DB_TABLE] = Marker

    columns = ", ".join([" ".join(column) for column in Marker.DB_COLUMNS.items()])
    query = "CREATE TABLE IF NOT EXISTS %s (id INTEGER PRIMARY KEY, asset_id INTEGER, frame INTEGER, label_id INTEGER, trackable INTEGER, %s)" % (Marker.DB_TABLE, columns)
    print(query)
    #db_cur.execute("DROP TABLE %s" % (Marker.DB_TABLE,))
    db_cur.execute(query)
    db.commit()


# Get all markers on frame
def get_markers_on_frame(frame):
    markers = []

    for table, Marker in marker_tables.items():
        db_cur.execute("SELECT * FROM %s WHERE asset_id=? AND frame=?" % table, (ASSET_ID, frame))

        for row in db_cur.fetchall():
            markers.append(Marker(row[0], frame, row[3], *row[4:]))

    return markers


# Get marker by id
def get_marker_by_id(table, id):
    db_cur.execute("SELECT * FROM %s WHERE id=?" % table, (id, ))
    row = db_cur.fetchone()
    Marker = marker_tables[table]

    return Marker(row[0], row[2], row[3], *row[4:])
