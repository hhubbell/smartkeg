#
# Filename:     query.py
# Author:       Harrison Hubbell
# Date:         10/04/2014
# Description:  SQL Queries used by various smartkeg processes
#

def format_where(params):
    """
    @Author:        Harrison Hubbell
    @Created:       02/18/2015
    @Description:   Format query params for a WHERE clause
    """
    fmt = ' AND '.join(['{}=%s'.format(x) for x in params.keys()])

    return 'WHERE ' + fmt if fmt else fmt

def format_values(params):
    """
    @Author:        Harrison Hubbell
    @Created:       02/18/2015
    @Description:   Format query params for an INSERT VALUES clause
    """
    return '({}) VALUES ({})'.format(
        ', '.join(params.keys()),
        ', '.join(['%s' for x in params.values()])
    )

def get_beers(params):
    """
    @Author:        Harrison Hubbell
    @Created:       02/18/2015
    @Description:   Format a query to get beers based on params
    """        
    query = """
        SELECT
            b.id        AS id,
            b.name      AS name,
            b.abv       AS abv,
            b.ibu       AS ibu,
            bt.type     AS type,
            bt.subtype  AS subtype,
            br.name     AS brewer
        FROM Beer AS b
        LEFT JOIN BeerType AS bt ON b.type_id = bt.id
        LEFT JOIN Brewer AS br ON b.brewer_id = br.id
        {}
        ORDER BY b.name
    """.format(format_where(params))
    
    return query, list(params.values())

def get_brewers(params):
    """
    @Author:        Harrison Hubbell
    @Created:       02/18/2015
    @Description:   Format a query to get brewers based on params
    """
    query = """
        SELECT
            id,
            name,
            city,
            state,
            country
        FROM Brewer
        ORDER BY name
    """.format(format_where(params))

    return query, list(params.values())

def get_daily():
    """
    @Author:        Harrison Hubbell
    @Created:       03/30/2015
    @Description:   Format a query to get daily consumption
    XXX: Needs work
    """
    query = """
        SELECT
            DATE(pour_time) AS day,
            SUM(volume)     AS amount
        FROM Pour
        GROUP BY DATE(pour_time)
        ORDER BY pour_time
    """
    
    return query, []

def get_now_serving():
    """
    @Author:        Harrison Hubbell
    @Created:       03/30/2015
    @Description:   Format a query to get currently served kegs
    """
    query = """
        SELECT 
            bs.*,
            k.id        AS keg_id,
            k.volume    AS volume,
            (k.volume - SUM(IFNULL(p.volume, 0))) / k.volume AS remaining
        FROM (
            SELECT
                b.id        AS beer_id,
                b.name      AS name,
                b.abv       AS abv,
                b.ibu       AS ibu,
                br.name     AS brewer,
                bt.type     AS type,
                bt.subtype  AS subtype,
                AVG(bra.rating) AS rating
            FROM Beer AS b
            JOIN Brewer AS br ON b.brewer_id = br.id
            JOIN BeerType AS bt ON b.type_id = bt.id
            LEFT JOIN BeerRating AS bra ON b.id = bra.beer_id
            GROUP BY b.id
        ) AS bs
        JOIN Keg AS k ON bs.beer_id = k.beer_id
        LEFT JOIN Pour AS p on k.id = p.keg_id
        WHERE k.now_serving = 1
        GROUP BY k.id
    """

    return query, []

def get_percent_remaining():
    """
    @Author:        Harrison Hubbell
    @Created:       03/30/2015
    @Description:   Format a query to get percent of keg remaining
    """
    query = """
        SELECT (k.volume - SUM(p.volume)) / k.volume
        FROM Keg AS k
        JOIN Pour AS p ON k.id = p.keg_id
        WHERE k.now_serving = 1
        GROUP BY k.id
    """

    return query, []

def get_volume_remaining():
    """
    @Author:        Harrison Hubbell
    @Created:       03/30/2015
    @Description:   Format a query to get volume of keg remaining
    """
    query = """
        SELECT k.volume - SUM(p.volume)
        FROM Keg AS k
        JOIN Pour AS p ON k.id = p.keg_id
        WHERE k.now_serving = 1
        GROUP BY k.id
    """

    return query, []

def set_keg(params):
    """
    @Author:        Harrison Hubbell
    @Created:       02/18/2015
    @Description:   Format a query to set a new keg based on params
    """
    query = """
        INSERT INTO Keg {}        
    """.format(format_values(params))

    return query, list(params.values())

def set_pour(params):
    """
    @Author:        Harrison Hubbell
    @Created:       03/05/2015
    @Description:   Format a query to insert a new pour
    """
    query = """
        INSERT INTO Pour {}
    """.format(format_values(params))

    return query, list(params.values())

def set_rating(params):
    """
    @Author:        Harrison Hubbell
    @Created:       02/18/2015
    @Description:   Format a query to set a new rating based on params
    """
    query = """
        INSERT INTO Keg {}        
    """.format(format_values(params))

    return query, list(params.values())

def rem_keg(params):
    """
    @Author:        Harrison Hubbell
    @Created:       02/18/2015
    @Description:   Format a query to stop a keg based on params
    """
    query = """
        UPDATE Keg
        SET now_serving = 0
        WHERE id IN (%s)
    """
    return query, params

'''        
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

    INSERT_BEER_RATING = """
        INSERT INTO BeerRating
            (beer_id, rating, comments)
        VALUES
            (%s, %s, %s)
    """

    # --------------------
    # UPDATES
    # --------------------
    UPDATE_STOP_KEG = """
        UPDATE Keg
        SET now_serving = 0
        WHERE id IN (%s)
            
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
        ORDER BY name
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
        ORDER BY b.name
    """
    
    SELECT_CURRENT_KEGS = """
        SELECT 
            bs.*,
            k.id        AS keg_id,
            k.volume    AS volume,
            (k.volume - SUM(IFNULL(p.volume, 0))) / k.volume AS remaining          
        FROM (
            SELECT
                b.id        AS beer_id,
                b.name      AS name,
                b.abv       AS abv,
                b.ibu       AS ibu,
                br.name     AS brewer,
                bt.type     AS type,
                bt.subtype  AS subtype,
                AVG(bra.rating) AS rating
            FROM Beer AS b
            JOIN Brewer AS br ON b.brewer_id = br.id
            JOIN BeerType AS bt ON b.type_id = bt.id
            LEFT JOIN BeerRating AS bra ON b.id = bra.beer_id
            GROUP BY b.id
        ) AS bs
        JOIN Keg AS k ON bs.beer_id = k.beer_id
        LEFT JOIN Pour AS p on k.id = p.keg_id
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

    SELECT_CONSUMPTION_FROM_START = """
        SELECT
            DATEDIFF(DATE(p.pour_time), DATE(k.date_started)) AS day,
            SUM(p.volume) AS amount,
            k.volume AS keg_volume
        FROM Pour AS p
        JOIN Keg AS k ON p.keg_id = k.id
        WHERE k.now_serving = 1
        GROUP BY DATE(p.pour_time)
        ORDER BY day ASC
    """
'''
