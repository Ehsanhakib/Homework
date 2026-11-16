-- T4d. Month range rewrite.
-- Rewrite the date filter to use a direct column range instead of functions
-- so SQLite can utilize the timestamp index.
--
-- Prediction (commit before running): 
-- using a direct date range prevents full table scans caused by column functions, 
-- enabling index search.
--
-- YOUR QUERY HERE

SELECT user_id, movie_id, rating, timestamp
FROM ratings
WHERE timestamp >= 882672000 AND timestamp < 885350400
ORDER BY timestamp ASC;