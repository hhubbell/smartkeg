USE Kegerator;

INSERT INTO Brewer
    (name)
VALUES
    ('Smuttynose')
;

INSERT INTO Beer
    (brewer_id, type_id, name, abv, ibu)
VALUES
    ((SELECT id FROM Brewer WHERE name='Smuttynose'), (SELECT id FROM BeerType WHERE subtype='Brown'), 'Old Brown Dog Ale', 6.7, 29.5)
;

UPDATE Keg SET now_serving = 0;

INSERT INTO Keg
    (fridge_id, beer_id, volume, date_started, now_serving)
VALUES
    (1, (SELECT id FROM Beer WHERE name='Old Brown Dog Ale'), 41, '2014-11-20 00:00:00', 1)
;
