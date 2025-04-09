from ultralytics.solutions import ObjectCounter

class TrafficCounter(ObjectCounter):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.default_v_in="downward"
        self.default_h_in="right"

    def update_default_in(self, default_v_in, default_h_in):
        self.default_v_in=default_v_in
        self.default_h_in=default_h_in

    def count_objects(self, current_centroid, track_id, prev_position, cls):
        """
        Counts objects within a polygonal or linear region based on their tracks.

        Args:
            current_centroid (Tuple[float, float]): Current centroid coordinates (x, y) in the current frame.
            track_id (int): Unique identifier for the tracked object.
            prev_position (Tuple[float, float]): Last frame position coordinates (x, y) of the track.
            cls (int): Class index for classwise count updates.

        Examples:
            >>> counter = ObjectCounter()
            >>> track_line = {1: [100, 200], 2: [110, 210], 3: [120, 220]}
            >>> box = [130, 230, 150, 250]
            >>> track_id_num = 1
            >>> previous_position = (120, 220)
            >>> class_to_count = 0  # In COCO model, class 0 = person
            >>> counter.count_objects((140, 240), track_id_num, previous_position, class_to_count)
        """
        if prev_position is None or track_id in self.counted_ids:
            return

        if len(self.region) == 2:  # Linear region (defined as a line segment)
            line = self.LineString(self.region)  # Check if the line intersects the trajectory of the object
            if line.intersects(self.LineString([prev_position, current_centroid])):
                # Determine orientation of the region (vertical or horizontal)
                if abs(self.region[0][0] - self.region[1][0]) < abs(self.region[0][1] - self.region[1][1]): # 水平距离 < 垂直距离
                    # Vertical region: Compare x-coordinates to determine direction
                    if current_centroid[0] > prev_position[0]:  # 默认右进
                        if self.default_h_in == "right":
                            self.in_count += 1
                            self.classwise_counts[self.names[cls]]["IN"] += 1
                        else:
                            self.out_count += 1
                            self.classwise_counts[self.names[cls]]["OUT"] += 1
                    else:  # Moving left
                        if self.default_h_in == "right":
                            self.out_count += 1
                            self.classwise_counts[self.names[cls]]["OUT"] += 1
                        else:
                            self.in_count += 1
                            self.classwise_counts[self.names[cls]]["IN"] += 1
                # Horizontal region: Compare y-coordinates to determine direction
                elif current_centroid[1] > prev_position[1]:  # 默认下进
                    if self.default_v_in == "downward":
                        self.in_count += 1
                        self.classwise_counts[self.names[cls]]["IN"] += 1
                    else:
                        self.out_count += 1
                        self.classwise_counts[self.names[cls]]["OUT"] += 1
                else:  # Moving upward
                    if self.default_v_in == "downward":
                        self.out_count += 1
                        self.classwise_counts[self.names[cls]]["OUT"] += 1
                    else:
                        self.in_count += 1
                        self.classwise_counts[self.names[cls]]["IN"] += 1
                self.counted_ids.append(track_id)
