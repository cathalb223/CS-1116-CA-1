SELECT * from characters

SELECT * FROM characters as c
JOIN owns_character as o
JOIN users as u
ON c.character_id = o.character_id
AND o.user_id = u.user_id

SELECT * FROM characters
WHERE name = 'benis' AND species is not null AND level is not null AND class is not null
