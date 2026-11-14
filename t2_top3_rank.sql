-- T2 (version 2, RANK). The same question, with RANK() ordered by mean_rating
-- only, keeping rows with pos <= 3.
-- Required columns: occupation, pos, movie_id, title, n, mean_rating
--
-- Prediction (commit before running): _more rows, which is (more / the same / fewer)
-- than version 1, because RANK() assigns the same position number to ties, allowing multiple movies with identical ratings to share rank 3 or higher instead of being arbitrarily cut off.

-- YOUR QUERY HERE

WITH movie_occupation_stats AS (
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
),
ranked_movies AS (
    SELECT
        occupation,
        movie_id,
        title,
        n,
        mean_rating,
        RANK() OVER (PARTITION BY occupation ORDER BY mean_rating DESC) AS pos
    FROM movie_occupation_stats
)
SELECT
    occupation,
    pos,
    movie_id,
    title,
    n,
    mean_rating
FROM ranked_movies
WHERE pos <= 3;