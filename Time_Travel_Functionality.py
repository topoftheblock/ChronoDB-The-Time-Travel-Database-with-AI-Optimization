# Add to your StorageEngine class
class TimeTravelStorageEngine(StorageEngine):
    def __init__(self, data_file: str = "database.db"):
        super().__init__(data_file)
        self.timeline = {}  # key -> list of (timestamp, value, operation)
        self.wal_file = data_file + ".wal"  # Write-Ahead Log
        
    def set(self, key: str, value: str) -> bool:
        timestamp = time.time_ns()
        # Store in WAL first for durability
        with open(self.wal_file, 'a') as wal:
            wal.write(f"{timestamp}|SET|{key}|{value}\n")
        
        # Then update main storage
        success = super().set(key, value)
        
        # Track in timeline
        if key not in self.timeline:
            self.timeline[key] = []
        self.timeline[key].append((timestamp, value, 'SET'))
        
        return success
    
    def get_at_time(self, key: str, target_timestamp: float) -> Optional[str]:
        """Get value of key at specific point in time"""
        if key not in self.timeline:
            return None
            
        # Binary search through timeline
        timeline = self.timeline[key]
        low, high = 0, len(timeline) - 1
        result = None
        
        while low <= high:
            mid = (low + high) // 2
            ts, value, op = timeline[mid]
            
            if ts <= target_timestamp:
                if op != 'DELETE':  # Ignore deleted values
                    result = value
                low = mid + 1
            else:
                high = mid - 1
                
        return result

# Extended query syntax: SELECT * FROM table AS OF TIMESTAMP 1635724800
class TimeTravelQueryParser(QueryParser):
    def _parse_time_travel_select(self, query: str):
        match = re.match(
            r"SELECT \* FROM (\w+) AS OF TIMESTAMP (\d+) WHERE (.+)", 
            query, re.IGNORECASE
        )
        if match:
            return {
                'type': QueryType.SELECT,
                'table': match.group(1),
                'timestamp': int(match.group(2)),
                'condition': match.group(3)
            }
        return None