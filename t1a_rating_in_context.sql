-- T1a. Every rating next to its user's mean and its movie's mean.
-- Required columns: user_id, movie_id, rating, user_mean, movie_mean
-- One query, no join, no GROUP BY.
--
-- Prediction (commit before running):this query returns 100000 rows, because it preserves every single individual rating in the ratings table while attaching its user and movie averages via window functions.

-- YOUR QUERY HERE

SELECT
    user_id,
    movie_id,
    rating,
    AVG(rating) OVER (PARTITION BY user_id) AS user_mean,
    AVG(rating) OVER (PARTITION BY movie_id) AS movie_mean
FROM ratings;
