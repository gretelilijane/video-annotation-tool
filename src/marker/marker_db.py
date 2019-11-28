from src import db, ASSET_ID

# Marker tables
marker_tables = {}

# Add marker class
def add_marker_class(Marker):
    marker_tables[Marker.DB_TABLE] = Marker

    columns = ", ".join([" ".join(column) for column in Marker.DB_COLUMNS.items()])
    query = "CREATE TABLE IF NOT EXISTS %s (id INTEGER PRIMARY KEY, asset_id INTEGER, frame INTEGER, label_id INTEGER, trackable INTEGER, %s)" % (Marker.DB_TABLE, columns)
    print(query)
    #db.execute("DROP TABLE %s" % (Marker.DB_TABLE,))
    db.execute(query)
    db.commit()


# Convert table row to marker instance
def row_to_marker(table, row):
    return marker_tables[table](row[0], row[2], row[3], *row[4:])


# Get marker by id
def get_marker_by_id(table, id):
    db.execute("SELECT * FROM %s WHERE id=?" % table, (id, ))
    row = db.fetchone()

    return row_to_marker(table, row)


# Get markers by clause
def get_markers_by_clause(clause, parameters):
    markers = []

    for table in marker_tables.keys():
        db.execute("SELECT * FROM %s %s" % (table, clause), parameters)

        for row in db.fetchall():
            markers.append(row_to_marker(table, row))

    return markers


# Get all markers on frame
def get_markers_on_frame(frame):
    return get_markers_by_clause("WHERE asset_id=? AND frame=?", (ASSET_ID, frame))


# Delete markers by clause
def delete_markers_by_clause(clause, parameters):
    markers = []

    for table in marker_tables.keys():
        print("DELETE FROM %s %s" % (table, clause))
        db.execute("DELETE FROM %s %s" % (table, clause), parameters)

    return markers