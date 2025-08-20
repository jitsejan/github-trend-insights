WITH exploded AS (
  SELECT 
    repository,
    UNNEST(releases) AS release_struct
  FROM {{ ref('stg_repository_base') }}
),

flattened AS (
  SELECT
    repository,
    release_struct.author AS release_author,
    release_struct.name AS release_name,
    release_struct.tag_name AS tag,
    release_struct.published_at AS published_at,
    release_struct.created_at AS created_at,
    release_struct.updated_at AS updated_at,
    release_struct.url AS release_url,
    release_struct.body AS body,
    release_struct.draft AS is_draft,
    release_struct.prerelease AS is_prerelease
  FROM exploded
),

ranked AS (
  SELECT *,
    ROW_NUMBER() OVER (
      PARTITION BY repository, tag, release_url
      ORDER BY updated_at DESC
    ) AS row_num
  FROM flattened
)

SELECT *
FROM ranked
WHERE row_num = 1