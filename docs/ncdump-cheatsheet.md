# ncdump Cheatsheet

Part of `netcdf-bin`. Inspects netCDF files from the command line.

Examples use: `output/barotropic_stirring-T85/run0001/atmos_daily.nc`

## Header (dimensions, variables, attributes)

```bash
ncdump -h file.nc
```

Shows dimensions (lon=256, lat=128, time=7), all variables with their
attributes (units, long_name, missing_value), and global attributes.

## File format

```bash
ncdump -k file.nc
```

Returns format type: `classic`, `64-bit offset`, `netCDF-4`, etc.

## Dump a specific variable

```bash
ncdump -v time file.nc
```

Prints header + data for that variable only. Example output:

```
 time = 0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5 ;
```

Multiple variables:

```bash
ncdump -v time,lat file.nc
```

## Dump coordinate variables only

```bash
ncdump -c file.nc
```

Prints header + data for all coordinate variables (lon, lat, time, etc.)
without dumping large data arrays.

## Dimensions only

```bash
ncdump -h file.nc | grep -E '^\t\w+ ='
```

Example output:

```
	lon = 256 ;
	lat = 128 ;
	time = UNLIMITED ; // (7 currently)
```

## List variable names

```bash
ncdump -h file.nc | grep -E '^\t(float|double|int|short|byte|char) '
```

## Inspect a single variable's attributes

```bash
ncdump -h file.nc | sed -n '/float vor/,/^$/p'
```

## Suppress global attributes (less noise)

```bash
ncdump -h file.nc | sed '/^\/\/ global/,$d'
```

## Full data dump (careful with large files)

```bash
ncdump file.nc
```

Pipe to less for large files:

```bash
ncdump file.nc | less
```

## Compare two files (headers only)

```bash
diff <(ncdump -h file1.nc) <(ncdump -h file2.nc)
```

## Quick size check

```bash
ncdump -h file.nc | head -10
```

Shows dimensions at the top, which tells you the data shape
(e.g., time=7, lat=128, lon=256 means each 3D variable is 7x128x256).
