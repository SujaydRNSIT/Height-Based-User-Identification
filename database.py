height_database = {
    "Veerendra": 175,
    "Sharvil": 168,
    "Divyesh": 172,
    "Sujay": 160
}

def find_person_by_height(measured_height, tolerance=2):
    """
    Finds the person in the database with a height close to the measured height.
    
    Args:
        measured_height (int): The height measured by the sensor.
        tolerance (int): The allowed difference between measured and stored height.
        
    Returns:
        str: The name of the person, if found within the tolerance; else 'Unknown'.
    """
    for name, height in height_database.items():
        if abs(height - measured_height) <= tolerance:
            return name
    return "Unknown"