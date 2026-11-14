-- T1c. Rewrite t1c_week6_chain.sql with a window function: no genre_means
-- step and no join back. It must return the same rows.
-- Required columns: genre_id, movie_id, movie_mean, genre_mean
--
-- Prediction (commit before running): which two steps of the chain disappear? the genre_means CTE step and the join back step disappear, because window functions calculate group averages inline without collapsing rows.

-- YOUR QUERY HERE

WITH movie_stats AS (
    SELECT 
        mg.genre_id,
        r.movie_id,
        AVG(r.rating) AS movie_mean,
        COUNT(r.rating) AS rating_count
    FROM ratings r
    JOIN movie_genres mg ON r.movie_id = mg.movie_id
    GROUP BY mg.genre_id, r.movie_id
    HAVING COUNT(r.rating) >= 30
),
windowed_stats AS (
    SELECT 
        genre_id,
        movie_id,
        movie_mean,
        AVG(movie_mean) OVER (PARTITION BY genre_id) AS genre_mean
    FROM movie_stats
)
SELECT 
    genre_id,
    movie_id,
    movie_mean,
    genre_mean
FROM windowed_stats
WHERE movie_mean >= genre_mean + 0.5;
