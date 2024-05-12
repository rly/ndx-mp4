import h5py
import numpy as np

dtype = np.float32
shape = (10, 20, 50)
data = np.random.rand(*shape).astype(dtype)
offset = 100

raw_file = "filename.raw"
with open(raw_file, "wb") as f:
    f.seek(offset)
    f.write(data.tobytes())

output_file = "filename.h5"
size = 4 * shape[0] * shape[1] * shape[2] # 4 bytes per element

with h5py.File(output_file, "w") as f:
    dataset = f.create_dataset(
        "data",
        shape=shape,
        dtype=np.float32,
        external=((raw_file, offset, size),)
    )

with h5py.File(output_file, "r") as f:
    print(f['data'][:])
    print(f['data'].external)
    np.testing.assert_array_equal(f['data'][:], data)

# added in h5py 2.9.0
# external datasets are relative to the current working directory of the calling program's current process
# To make the location of the external dataset file relative to the HDF5 file, H5Pset_efile_prefix should set
# the prefix to "${ORIGIN}". in h5py, this can be done by setting the efile_prefix property on create_dataset,
# as of h5py 3.7.0.

# hdf5 also supports virtual datasets, which are similar to external datasets, but the data is generated on the fly
# by a user-defined function. This is useful for creating datasets that are too large to fit in memory, or for datasets
# that are generated by a simulation or other process. Virtual datasets are created using the H5Pset_virtual function
# in the C API. In h5py, virtual datasets are created using the virtual property on create_dataset. The virtual property
# takes a function that generates the data for the dataset. The function should take a single argument, which is a list
# of slices that define the region of the dataset being accessed. The function should return a numpy array containing
# the data for that region of the dataset. The function can also take additional arguments, which are passed as keyword
# arguments to create_dataset. The virtual property can also take a shape argument, which specifies the shape of the
# dataset. If the shape argument is not provided, the shape of the dataset is determined by calling the function with
# a single slice that selects the entire dataset. The function should return a numpy array with the same shape as the
# slice. The function can also take additional arguments, which are passed as keyword arguments to create_dataset.
# ^ from copilot. to confirm.