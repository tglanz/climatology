# h5dump Cheatsheet

Part of `hdf5-tools`. Inspects HDF5 files from the command line.

Examples use: `ml/data/train.h5`

## Header (structure, datasets, attributes)

```bash
h5dump -H file.h5
```

Shows groups, dataset names, shapes, types, and attributes. Equivalent to `ncdump -h`.

## List datasets

```bash
h5ls file.h5
```

Quick listing of top-level datasets with shapes and types.

```bash
h5ls -v file.h5
```

Verbose: includes storage layout, compression, chunk size.

## Dump a specific dataset

```bash
h5dump -d x file.h5
```

Prints full data for dataset `x`. Pipe to `less` for large datasets.

## Inspect shape only

```bash
h5ls -v file.h5 | grep -E 'Size|Type'
```

## Read a single sample (first row)

```bash
h5dump -d x -s "0,0,0,0" -c "1,2,128,256" file.h5
```

`-s` = start indices, `-c` = count per dimension. Matches dataset shape `(N, C, lat, lon)`.

## Read N samples from offset

```bash
h5dump -d x -s "10,0,0,0" -c "5,2,128,256" file.h5
```

Reads 5 samples starting at index 10.

## Full data dump (careful with large files)

```bash
h5dump file.h5 | less
```

## Compare two files (structure only)

```bash
h5diff --no-data file1.h5 file2.h5
```

## Quick size check

```bash
h5ls -v file.h5 | grep -A2 'x '
```

Shows shape and storage size of dataset `x`.

## Check number of samples

```bash
h5ls -v file.h5 | grep 'Size'
```

First dimension of `x` or `y` is N (number of pairs).
