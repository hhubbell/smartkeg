USE Kegerator;

INSERT INTO Brewer
    (name)
VALUES
    ('Rookies')
;

INSERT INTO Beer
    (brewer_id, type_id, name, abv, ibu)
VALUES
    ((SELECT id FROM Brewer WHERE name='Rookies'), (SELECT id FROM BeerType WHERE subtype='Brown'), 'Rookies Root Beer', 0.0, NULL)
;

UPDATE Keg SET now_serving = 0;

INSERT INTO Keg
    (fridge_id, beer_id, volume, date_started, now_serving)
VALUES
    (1, (SELECT id FROM Beer WHERE name='Rookies Root Beer'), 35, '2014-11-30 00:00:00', 1)
;
