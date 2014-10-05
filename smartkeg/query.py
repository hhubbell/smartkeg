# ----------------------------------------------------------------------------
# Filename:     query.py
# Author:       Harrison Hubbell
# Date:         10/04/2014
# Description:  SQL Queries used by various smartkeg processes
# ----------------------------------------------------------------------------

class Query:
    # --------------------
    # INSERTS
    # --------------------
    INSERT_POUR = """
        INSERT INTO Pour 
            (keg_id, volume)
        VALUES 
            (%s, %s)
    """
    INSERT_FRIDGE_TEMP = """
        INSERT INTO FridgeTemp 
            (fridge_id, sensor_id, temperature)
        VALUES 
            (%s, (SELECT id FROM Sensor WHERE name = %s), %s)
    """
    
    # --------------------
    # SELECTS
    # --------------------
    SELECT_KEG_ID = """
        SELECT id FROM Keg WHERE now_serving = 1
    """
    SELECT_SENSOR_ID = """
        SELECT id, name FROM Sensor WHERE name IN %s
    """
    SELECT_VOLUME_REMAINING = """
        SELECT *** FROM *** JOIN *** WHERE ***
    """
    SELECT_PERCENT_REMAINING = """
                
    """
