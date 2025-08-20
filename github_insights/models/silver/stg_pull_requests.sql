SELECT DISTINCT
  repository,
  feat_classifier,
  prs.additions,
  prs.deletions,
  prs.changed_files,
  prs.commits,
  prs.author,
  prs.closed_at,
  prs.created_at
FROM {{ ref('stg_repository_base') }}
WHERE prs IS NOT NULL