import rasterio, json
path='data/processed/elevation/jezero_hirise_dtm_authentic.tif'
with rasterio.open(path) as src:
    info={'crs': src.crs.to_string() if src.crs else None,
          'bounds': src.bounds,
          'width': src.width,
          'height': src.height,
          'res': src.res,
          'dtype': src.dtypes[0]}
    print(json.dumps(info, default=str))
