// Given a device name, the index of that device in the list of all
// devices.  This is necessary for non-Futhark benchmarks.

#include <assert.h>
#include <stdio.h>
#include <math.h>
#include <stdlib.h>
#include <string.h>
#include <sys/time.h>

#ifdef __APPLE__
#include <OpenCL/cl.h>
#else
#include <CL/cl.h>
#endif

#define OPENCL_SUCCEED(e) opencl_succeed(e, #e, __FILE__, __LINE__)

static const char* opencl_error_string(unsigned int err)
{
  switch (err) {
  case CL_SUCCESS:                            return "Success!";
  case CL_DEVICE_NOT_FOUND:                   return "Device not found.";
  case CL_DEVICE_NOT_AVAILABLE:               return "Device not available";
  case CL_COMPILER_NOT_AVAILABLE:             return "Compiler not available";
  case CL_MEM_OBJECT_ALLOCATION_FAILURE:      return "Memory object allocation failure";
  case CL_OUT_OF_RESOURCES:                   return "Out of resources";
  case CL_OUT_OF_HOST_MEMORY:                 return "Out of host memory";
  case CL_PROFILING_INFO_NOT_AVAILABLE:       return "Profiling information not available";
  case CL_MEM_COPY_OVERLAP:                   return "Memory copy overlap";
  case CL_IMAGE_FORMAT_MISMATCH:              return "Image format mismatch";
  case CL_IMAGE_FORMAT_NOT_SUPPORTED:         return "Image format not supported";
  case CL_BUILD_PROGRAM_FAILURE:              return "Program build failure";
  case CL_MAP_FAILURE:                        return "Map failure";
  case CL_INVALID_VALUE:                      return "Invalid value";
  case CL_INVALID_DEVICE_TYPE:                return "Invalid device type";
  case CL_INVALID_PLATFORM:                   return "Invalid platform";
  case CL_INVALID_DEVICE:                     return "Invalid device";
  case CL_INVALID_CONTEXT:                    return "Invalid context";
  case CL_INVALID_QUEUE_PROPERTIES:           return "Invalid queue properties";
  case CL_INVALID_COMMAND_QUEUE:              return "Invalid command queue";
  case CL_INVALID_HOST_PTR:                   return "Invalid host pointer";
  case CL_INVALID_MEM_OBJECT:                 return "Invalid memory object";
  case CL_INVALID_IMAGE_FORMAT_DESCRIPTOR:    return "Invalid image format descriptor";
  case CL_INVALID_IMAGE_SIZE:                 return "Invalid image size";
  case CL_INVALID_SAMPLER:                    return "Invalid sampler";
  case CL_INVALID_BINARY:                     return "Invalid binary";
  case CL_INVALID_BUILD_OPTIONS:              return "Invalid build options";
  case CL_INVALID_PROGRAM:                    return "Invalid program";
  case CL_INVALID_PROGRAM_EXECUTABLE:         return "Invalid program executable";
  case CL_INVALID_KERNEL_NAME:                return "Invalid kernel name";
  case CL_INVALID_KERNEL_DEFINITION:          return "Invalid kernel definition";
  case CL_INVALID_KERNEL:                     return "Invalid kernel";
  case CL_INVALID_ARG_INDEX:                  return "Invalid argument index";
  case CL_INVALID_ARG_VALUE:                  return "Invalid argument value";
  case CL_INVALID_ARG_SIZE:                   return "Invalid argument size";
  case CL_INVALID_KERNEL_ARGS:                return "Invalid kernel arguments";
  case CL_INVALID_WORK_DIMENSION:             return "Invalid work dimension";
  case CL_INVALID_WORK_GROUP_SIZE:            return "Invalid work group size";
  case CL_INVALID_WORK_ITEM_SIZE:             return "Invalid work item size";
  case CL_INVALID_GLOBAL_OFFSET:              return "Invalid global offset";
  case CL_INVALID_EVENT_WAIT_LIST:            return "Invalid event wait list";
  case CL_INVALID_EVENT:                      return "Invalid event";
  case CL_INVALID_OPERATION:                  return "Invalid operation";
  case CL_INVALID_GL_OBJECT:                  return "Invalid OpenGL object";
  case CL_INVALID_BUFFER_SIZE:                return "Invalid buffer size";
  case CL_INVALID_MIP_LEVEL:                  return "Invalid mip-map level";
  default:                                    return "Unknown";
  }
}

static void opencl_succeed(unsigned int ret,
                           const char *call,
                           const char *file,
                           int line) {
  if (ret != CL_SUCCESS) {
    fprintf(stderr, "%s:%d: OpenCL call\n  %s\nfailed with error code %d (%s)\n",
            file, line, call, ret, opencl_error_string(ret));
    exit(1);
  }
}

int main(int argc, char** argv) {
  if (argc != 2) {
    fprintf(stderr, "Usage: %s <device name>\n", argv[0]);
    return 1;
  }

  const char* device_pref = argv[1];

  cl_int clStatus;
  cl_platform_id clPlatform;
  cl_device_id clDevice;

  cl_uint num_platforms;

  // Find the number of platforms.
  OPENCL_SUCCEED(clGetPlatformIDs(0, NULL, &num_platforms));

  // Make room for them.
  cl_platform_id *platforms = calloc(num_platforms, sizeof(cl_platform_id));

  // Fetch all the platforms.
  OPENCL_SUCCEED(clGetPlatformIDs(num_platforms, platforms, NULL));

  // Go through all the platforms.
  int ok = 0;
  int device_id = 0;
  for (cl_uint i = 0; !ok && i < num_platforms; i++) {
    cl_uint num_devices;

    // Fetch all the devices.
    OPENCL_SUCCEED(clGetDeviceIDs(platforms[i], CL_DEVICE_TYPE_ALL,
                                  0, NULL, &num_devices));
    cl_device_id *devices = calloc(num_devices, sizeof(cl_device_id));
    OPENCL_SUCCEED(clGetDeviceIDs(platforms[i], CL_DEVICE_TYPE_ALL,
                                  num_devices, devices, NULL));

    // Go through all the devices for this platform.
    for (int j = 0; !ok && j < num_devices; j++) {
      size_t name_bytes;
      OPENCL_SUCCEED(clGetDeviceInfo(devices[j], CL_DEVICE_NAME, 0, NULL, &name_bytes));
      char *device_name = malloc(name_bytes);
      OPENCL_SUCCEED(clGetDeviceInfo(devices[j], CL_DEVICE_NAME, name_bytes, device_name, NULL));
      if (strstr(device_name, device_pref) != NULL) {
        printf("%d\n", device_id);
        return 0;
      }
      free(device_name);
      device_id++;
    }
  }

  fprintf(stderr, "No OpenCL device matching '%s' found\n", device_pref);
  return 1;
}
