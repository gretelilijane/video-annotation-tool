import cv2

SELECT_EDGE_DISTANCE = 10


class Marker:
    def __init__(self, label, coords):
        self.label = label
        self.highlighted_edge = None
        self.set_coords(coords)

    def contains_coord(self, c):
        return c[0] >= self.p1[0] and c[0] <= self.p2[0] and c[1] >= self.p1[1] and c[1] <= self.p2[1]

    def get_closest_edge(self, c):
        if c[1] > self.p1[1] and c[1] < self.p2[1]:
            if abs(c[0] - self.p1[0]) < SELECT_EDGE_DISTANCE:
                return self.p1, self.p3
            elif abs(c[0] - self.p2[0]) < SELECT_EDGE_DISTANCE:
                return self.p4, self.p2

        if c[0] > self.p1[0] and c[0] < self.p2[0]:
            if abs(c[1] - self.p1[1]) < SELECT_EDGE_DISTANCE:
                return self.p1, self.p4
            elif abs(c[1] - self.p2[1]) < SELECT_EDGE_DISTANCE:
                return self.p3, self.p2

    def set_coords(self, coords):
        self.p1 = (min(coords[0], coords[2]), min(coords[1], coords[3]))
        self.p2 = (max(coords[0], coords[2]), max(coords[1], coords[3]))
        self.p3 = (min(coords[0], coords[2]), max(coords[1], coords[3]))
        self.p4 = (max(coords[0], coords[2]), min(coords[1], coords[3]))
    
    def update_coord(self, index, new_coord):
        if index == 0:
            self.p1 = new_coord
        elif index == 1:
            self.p2 = new_coord
        elif index == 2:
            self.p3 = new_coord
        elif index == 3:
            self.p4 = new_coord

    def highlight_edge(self, edge):
        self.highlighted_edge = edge

    def draw(self, frame):
        cv2.rectangle(frame, self.p1, self.p2, (255, 0, 0))

        if self.highlighted_edge:
            cv2.line(frame, self.highlighted_edge[0], self.highlighted_edge[1], (255, 0, 0), thickness=3)
