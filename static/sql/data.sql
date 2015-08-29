-- ---------------------------------------------------------------------------
-- Filename:    data.sql
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

-- Some Brewers
INSERT INTO Brewer
    (name, city, state, country)
VALUES
    ('The Alchemist', 'Waterbury', 'VT', 'United States'),
    ('Fiddlehead Brewing Company', 'Shelburne', 'VT', 'United States'),
    ('Harpoon Brewery', 'Windsor', 'VT', 'United States'),
    ('Hill Farmstead Brewery', 'Greensboro Bend', 'VT', 'United States'),
    ('Long Trail Brewing Company', 'Bridgewater Corners', 'VT', 'United States'),
    ('Magic Hat Brewing Company', 'Burlington', 'VT', 'United States'),
    ('Otter Creek Brewing Company', 'Middlebury', 'VT', 'United States'),
    ('Switchback Brewing Company', 'Burlington', 'VT', 'United States'),
    ('Smuttynose Brewing Company', 'Hampton', 'NH', 'United States'),
;

INSERT INTO BeerType
    (type, subtype)
VALUES
    ('Ale', 'Stout'),
    ('Ale', 'Porter'),
    ('Ale', 'Altbier'),
    ('Ale', 'American Pale Ale'),
    ('Ale', 'English Bitter Pale Ale'),
    ('Ale', 'India Pale Ale'),
    ('Ale', 'Double IPA'),
    ('Ale', 'Saison'),
    ('Ale', 'Belgian'),
    ('Ale', 'Amber'),
    ('Ale', 'Brown'),
    ('Ale', 'Hefeweizen'),
    ('Lager', 'Bock'),
    ('Lager', 'Pilsner'),
    ('Lager', 'Vienna'),
    ('Lager', 'Dunkel')
;

INSERT INTO Beer
    (brewer_id, type_id, name, abv, ibu)
VALUES
    ((SELECT id FROM Brewer WHERE name = 'The Alchemist'), (SELECT id FROM BeerType WHERE subtype = 'Double IPA'), 'Heady Topper', 8.0, 75),
    ((SELECT id FROM Brewer WHERE name = 'Fiddlehead Brewing Company'), (SELECT id FROM BeerType WHERE subtype = 'India Pale Ale'), 'Fiddlehead IPA', 6.2, 53),
    ((SELECT id FROM Brewer WHERE name = 'Fiddlehead Brewing Company'), (SELECT id FROM BeerType WHERE subtype = 'Porter'), 'Hodad', 5.5, NULL),
    ((SELECT id FROM Brewer WHERE name = 'Fiddlehead Brewing Company'), (SELECT id FROM BeerType WHERE subtype = 'Double IPA'), 'Mastermind', 8.1, NULL),
    ((SELECT id FROM Brewer WHERE name = 'Harpoon Brewery'), (SELECT id FROM BeerType WHERE subtype = 'India Pale Ale'), 'Harpoon IPA', 5.9, 42),
    ((SELECT id FROM Brewer WHERE name = 'Hill Farmstead Brewery'), (SELECT id FROM BeerType WHERE subtype = 'American Pale Ale'), 'Edward', 5.2, 85),
    ((SELECT id FROM Brewer WHERE name = 'Long Trail Brewing Company'), (SELECT id FROM BeerType WHERE subtype = 'Altbier'), 'Long Trail Ale', 4.6, 25),
    ((SELECT id FROM Brewer WHERE name = 'Long Trail Brewing Company'), (SELECT id FROM BeerType WHERE subtype = 'Altbier'), 'Double Bag', 7.2, 33),
    ((SELECT id FROM Brewer WHERE name = 'Magic Hat Brewing Company'), (SELECT id FROM BeerType WHERE subtype = 'Stout'), 'Heart of Darkness', 5.7, 30),
    ((SELECT id FROM Brewer WHERE name = 'Otter Creek Brewing Company'), (SELECT id FROM BeerType WHERE subtype = 'India Pale Ale'), 'Otter Creek Black IPA', 6.0, 60),
    ((SELECT id FROM Brewer WHERE name = 'Switchback Brewing Company'), (SELECT id FROM BeerType WHERE subtype = 'American Pale Ale'), 'Switchback Ale', 5.0, NULL),
    ((SELECT id FROM Brewer WHERE name = 'Smuttynose Brewing Company'), (SELECT id FROM BeerType WHERE subtype = 'Brown'), 'Old Brown Dog Ale', 6.7, 29.5)
;
