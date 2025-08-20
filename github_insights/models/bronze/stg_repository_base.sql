SELECT
  repository,
  prs,
  releases,
  statistics,
  feat_classifier
FROM read_parquet('s3://tech-intelligence-data-new/share/llm_output_feature_v3.parquet')