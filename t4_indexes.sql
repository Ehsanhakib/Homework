-- T4. Indexes and query plans.
-- Create any indexes needed to optimize queries A, B, C.
--
-- Prediction (commit before running): 
-- creating indexes on foreign keys and timestamps will change table scans to index searches, 
-- dramatically reducing execution time.
--
-- YOUR QUERY HERE

CREATE INDEX IF NOT EXISTS idx_ratings_user_id ON ratings(user_id);
CREATE INDEX IF NOT EXISTS idx_ratings_movie_id ON ratings(movie_id);
CREATE INDEX IF NOT EXISTS idx_ratings_timestamp ON ratings(timestamp);

-- Query A: User profile lookup (ordered deterministically to avoid check failure)
SELECT movie_id, rating, timestamp
FROM ratings
WHERE user_id = 1
ORDER BY timestamp DESC, movie_id ASC;

-- Query B: Movie page lookup
SELECT user_id, rating, timestamp
FROM ratings
WHERE movie_id = 1
ORDER BY timestamp DESC, user_id ASC;

-- Query C: Recent ratings lookup
SELECT user_id, movie_id, rating, timestamp
FROM ratings
ORDER BY timestamp DESC, user_id ASC, movie_id ASC
LIMIT 10;