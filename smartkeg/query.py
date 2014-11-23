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
            ((SELECT id FROM Keg WHERE now_serving = 1), %s)
    """
    INSERT_FRIDGE_TEMP = """
        INSERT INTO FridgeTemp 
            (fridge_id, sensor_id, temperature)
        VALUES 
            (%s, (SELECT id FROM Sensor WHERE name = %s AND type = 'Fridge'), %s)
    """

    INSERT_NEW_KEG = """
        INSERT INTO Keg
            (fridge_id, beer_id, volume, now_serving)
        VALUES
            (%s, %s, %s, 1)
    """
    
    # --------------------
    # SELECTS
    # --------------------
    SELECT_FRIDGE_ID = """
        SELECT id
        FROM Fridge
        WHERE name = %s
    """

    SELECT_KEG_ID = """
        SELECT id
        FROM Keg
        WHERE now_serving = 1
    """

    SELECT_BREWERS = """
        SELECT
            id,
            name,
            city,
            state,
            country
        FROM Brewer
    """

    SELECT_BREWER_OFFERING = """
        SELECT
            b.id,
            b.name,
            b.abv,
            b.ibu,
            bt.type,
            bt.subtype
        FROM Beer AS b
        LEFT JOIN BeerType AS bt ON b.type_id = bt.id
        WHERE b.brewer_id = %s
    """
    
    SELECT_CURRENT_KEGS = """
        SELECT
            k.id        AS keg_id,
            k.volume    AS volume,
            (k.volume - SUM(IFNULL(p.volume, 0))) / k.volume AS remaining,
            b.name      AS name,
            b.abv       AS abv,
            b.ibu       AS ibu,
            br.name     AS brewer,
            bt.type     AS type,
            bt.subtype  AS subtype,
            bra.rating  AS rating
        FROM Keg AS k
        JOIN Beer AS b ON k.beer_id = b.id
        JOIN BeerType AS bt ON b.type_id = bt.id
        JOIN Brewer AS br ON b.brewer_id = br.id
        LEFT JOIN BeerRating AS bra ON b.id = bra.beer_id        
        LEFT JOIN Pour AS p ON k.id = p.keg_id
        WHERE k.now_serving = 1
        GROUP BY k.id
    """

    SELECT_SENSOR_ID = """
        SELECT
            id,
            name
        FROM Sensor
        WHERE name IN %s
    """
    
    SELECT_DAILY_CONSUMPTION = """
        SELECT
            DATE(pour_time) AS day,
            SUM(volume)     AS amount
        FROM Pour
        GROUP BY DATE(pour_time)
        ORDER BY pour_time
    """

    SELECT_VOLUME_REMAINING = """
        SELECT k.volume - SUM(p.volume)
        FROM Keg AS k
        JOIN Pour AS p ON k.id = p.keg_id
        WHERE k.now_serving = 1
        GROUP BY k.id
    """
    
    SELECT_PERCENT_REMAINING = """
        SELECT (k.volume - SUM(p.volume)) / k.volume
        FROM Keg AS k
        JOIN Pour AS p ON k.id = p.keg_id
        WHERE k.now_serving = 1
        GROUP BY k.id        
    """
