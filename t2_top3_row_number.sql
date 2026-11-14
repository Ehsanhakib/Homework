-- T2 (version 1, ROW_NUMBER). The three highest-rated movies for each
-- occupation, among movies rated at least 20 times by users with that occupation.
-- Required columns: occupation, pos, movie_id, title, n, mean_rating
-- Order the window so that the result is the same on every run (state your
-- tie-breaker in WRITEUP.md).
--
-- Prediction (commit before running): typically around 60–80 rows depending on the number of unique occupations in the dataset

-- YOUR QUERY HERE

WITH occ_movie_stats AS (
    SELECT
        u.occupation,
        m.movie_id,
        m.title,
        COUNT(r.rating) AS n,
        AVG(r.rating) AS mean_rating
    FROM users u
    JOIN ratings r ON u.user_id = r.user_id
    JOIN movies m ON r.movie_id = m.movie_id
    GROUP BY u.occupation, m.movie_id, m.title
    HAVING COUNT(r.rating) >= 20
),
row_numbered AS (
    SELECT
        occupation,
        movie_id,
        title,
        n,
        mean_rating,
        ROW_NUMBER() OVER (
            PARTITION BY occupation 
            ORDER BY mean_rating DESC, n DESC, movie_id ASC
        ) AS pos
    FROM occ_movie_stats
)
SELECT
    occupation,
    pos,
    movie_id,
    title,
    n,
    mean_rating
FROM row_numbered
WHERE pos <= 3;
