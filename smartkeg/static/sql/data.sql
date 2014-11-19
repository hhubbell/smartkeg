-- ---------------------------------------------------------------------------
-- Filename:    build.sql
-- Author:      Harrison Hubbell
-- Created:     11/18/2014
-- Description: Setup data for the smartkeg database
-- ---------------------------------------------------------------------------

INSERT INTO Fridge
    (name)
VALUES
    ('smartkeg')
;

INSERT INTO Sensor
    (name, type)
VALUES
    ('28-000005748f01', 'Fridge'),
    ('28-00000574d4ae', 'Fridge')
;
