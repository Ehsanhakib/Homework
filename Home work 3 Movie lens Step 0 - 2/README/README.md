Step 1

Data Provenance
**Source U**: `https://files.grouplens.org/datasets/movielens/ml-100k.zip **Download De**: 2026-10-28 09:15:- **SHA-256 Checum**: `50d2a982c66986937beb9ffb3aa76efe955bf3d5c6b761f4e3a7cd717c


Step 2(a)


```mermaid
erDiagram
    USERS {
        int user_id PK
        int age
        string gender
        string occupation
        string zip_code
    }
    MOVIES {
        int movie_id PK
        string movie_title
        string release_date
        string video_release_date
        string imdb_url
    }
    GENRES {
        int genre_id PK
        string genre_name
    }
    MOVIE_GENRES {
        int movie_id PK, FK
        int genre_id PK, FK
    }
    RATINGS {
        int user_id PK, FK
        int movie_id PK, FK
        int rating
        int timestamp
    }

    USERS ||--o{ RATINGS : rates
    MOVIES ||--o{ RATINGS : receives
    MOVIES ||--|{ MOVIE_GENRES : has
    GENRES



Step 2(b)


Storing Genres in Tidy Form:
  Instead of retaining 19 separate binary columns (`genre_0`, `genre_1`, etc.) in the `movies` table, the schema uses a junction table (`movie_genres`). This unpivots the data into a normalized (long) structure, satisfying First Normal Form (1NF). It avoids storing redundant sparse zeros and lets you add new genres in the future without changing the database schema.



Step 2(c)


Constraints & Unenforced Claims:
  Enforced Constraints:** Column-level checks restrict ratings to valid integers (`CHECK (rating >= 1 AND rating <= 5)`), gender to valid categorical strings (`'M'`, `'F'`, `'O'`), and foreign key constraints enforce referential integrity across all tables.
  Unenforced Claims: Claims such as strict sequential numbering (e.g., ensuring no missing IDs in the `user_id` sequence from 1 to 943) cannot be guaranteed by standard table constraints. This claim must be validated post-load by running queries that check for ID gaps or compare total row counts against `MAX(user_id)`.



Step 2(d)



Data Type for `zip_code`:
  The `zip_code` field is typed as `TEXT` (or `VARCHAR`) rather than `INTEGER`. This is necessary because:
  1. Standard numerical types strip leading zeros (e.g., U.S. ZIP code `02138` would incorrectly become `2138`).
  2. The MovieLens dataset contains alphanumeric and non-standard postal codes (e.g., international ZIP codes like `V7X 1C5` or alphanumeric strings like `E2A48`), which would fail to parse or cause data loss if cast to integers. ||--|{ MOVIE_GENRES : categorizes6a3
