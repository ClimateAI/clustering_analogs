import intake
col_url = "https://ncar-cesm-lens.s3-us-west-2.amazonaws.com\
    /catalogs/aws-cesm1-le.json"
col = intake.open_esm_datastore(col_url)
col_subset = col.search(
    frequency=["monthly"],
    component="atm",
    variable=["TREFHT", "PRECC"],
    experiment=["RCP85", "HIST", "20C"]
)
col_subset.serialize(name="cesm1-l1", catalog_type="file")