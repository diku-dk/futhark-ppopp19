// Based on the opencl_nvidia version of the sgemm benchmark from
// Parboil, (c) 2010 The Board of Trustees of the University of
// Illinois.
//
// Despite the name, it is not actually NVIDIA-specific, but rather
// uses an efficient form of register tiling that also works fine on
// AMD hardware.
//
// This does not perform any validation.

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

static int64_t get_wall_time() {
  struct timeval time;
  assert(gettimeofday(&time,NULL) == 0);
  return time.tv_sec * 1000000 + time.tv_usec;
}

// Parameters of tile sizes
#define TILE_N 16
#define TILE_TB_HEIGHT 8
#define TILE_M (TILE_N*TILE_TB_HEIGHT)

int divRoundingUp(int x, int y) {
  return (x + y - 1) / y;
}

void regtileMatmul(int m, int n, int k,
                   cl_mem A, cl_mem B, cl_mem C,
                   cl_kernel clKernel, cl_command_queue clCommandQueue )
{
  size_t dg[2] = {TILE_N*divRoundingUp(m,TILE_M),
                  TILE_TB_HEIGHT*divRoundingUp(n,TILE_N)};
  size_t db[2] = {TILE_N,
                  TILE_TB_HEIGHT};

  cl_int clStatus;

  clStatus = clSetKernelArg(clKernel,0,sizeof(cl_mem),(void*)&A);
  clStatus = clSetKernelArg(clKernel,1,sizeof(int),(void*)&m);
  clStatus = clSetKernelArg(clKernel,2,sizeof(cl_mem),(void*)&B);
  clStatus = clSetKernelArg(clKernel,3,sizeof(int),(void*)&n);
  clStatus = clSetKernelArg(clKernel,4,sizeof(cl_mem),(void*)&C);
  clStatus = clSetKernelArg(clKernel,5,sizeof(int),(void*)&m);
  clStatus = clSetKernelArg(clKernel,6,sizeof(int),(void*)&k);
  OPENCL_SUCCEED(clStatus);

  OPENCL_SUCCEED(clEnqueueNDRangeKernel(clCommandQueue, clKernel, 2, NULL,
                                        dg, db,
                                        0, NULL, NULL));

  OPENCL_SUCCEED(clFinish(clCommandQueue));
}

char *slurpFile(const char *fname) {
  FILE *f = fopen(fname, "r");
  assert(f != NULL);
  fseek(f, 0, SEEK_END);
  size_t src_size = ftell(f);
  fseek(f, 0, SEEK_SET);
  char *src = malloc(src_size+1);
  fread(src, 1, src_size, f);
  src[src_size] = 0;
  fclose(f);
  return src;
}

int main (int argc, char *argv[]) {
  if (argc != 2 && ((argc-2)%3!=0)) {
    fprintf(stderr, "%s usage: <outfile> < <n> <m> <k> >...\n", argv[0]);
    exit(1);
  }

  const char *outfile = argv[1];

  cl_int clStatus;
  cl_platform_id clPlatform;
  cl_device_id clDevice;

  const char *device_pref = getenv("FUTHARK_OPENCL_DEVICE");
  if (device_pref == NULL) {
    fprintf(stderr, "Warning: FUTHARK_OPENCL_DEVICE not set.\n");
    device_pref = "";
  }
  cl_uint num_platforms;

  // Find the number of platforms.
  OPENCL_SUCCEED(clGetPlatformIDs(0, NULL, &num_platforms));

  // Make room for them.
  cl_platform_id *platforms = calloc(num_platforms, sizeof(cl_platform_id));

  // Fetch all the platforms.
  OPENCL_SUCCEED(clGetPlatformIDs(num_platforms, platforms, NULL));

  // Go through all the platforms.
  int ok = 0;
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
        clPlatform = platforms[i];
        clDevice = devices[j];
        printf("Using OpenCL device '%s'\n", device_name);
        ok = 1;
        break;
      }
      free(device_name);
    }
  }

  if (!ok) {
    fprintf(stderr, "No device matching '%s' found\n", device_pref);
    return 1;
  }

  cl_context_properties clCps[] = {
    CL_CONTEXT_PLATFORM,
    (cl_context_properties) clPlatform,
    0
  };

  cl_context clContext = clCreateContext(clCps, 1, &clDevice, NULL, NULL, &clStatus);
  OPENCL_SUCCEED(clStatus);

  cl_command_queue clCommandQueue = clCreateCommandQueue(clContext, clDevice, CL_QUEUE_PROFILING_ENABLE, &clStatus);
  OPENCL_SUCCEED(clStatus);

  const char* clSource[] = {slurpFile("kernel.cl")};
  cl_program clProgram = clCreateProgramWithSource(clContext,1,clSource,NULL,&clStatus);
  OPENCL_SUCCEED(clStatus);

  char clOptions[50];
  sprintf(clOptions,"-D TILE_N=%d -D TILE_TB_HEIGHT=%d -D TILE_M=%d",TILE_N,TILE_TB_HEIGHT,TILE_M);

  OPENCL_SUCCEED(clBuildProgram(clProgram,1,&clDevice,clOptions,NULL,NULL));

  cl_kernel clKernel = clCreateKernel(clProgram, "matmul", &clStatus);
  OPENCL_SUCCEED(clStatus);

  FILE *f = fopen(outfile, "w");
  assert(f != NULL);

  // For simplicity of plotting, we create a JSON file similar to what
  // futhark-bench would produce.
  fprintf(f, "{\"benchmarks/matmul.fut\":{\"datasets\":{\n");
  for (int i = 2; i < argc; i += 3) {
    int n = atoi(argv[i]);
    int m = atoi(argv[i+1]);
    int k = atoi(argv[i+2]);

    for (int x = n; x <= m; x++) {
      int y = k - (x+x);
      int matArow = 1 << x;
      int matAcol = 1 << y;
      int matBrow = 1 << y;
      int matBcol = 1 << x;

      printf("Multiplying [%d][%d] and [%d][%d] matrices\n",
             matArow, matAcol, matBrow, matBcol);

      int A_sz = matArow*matAcol*sizeof(float);
      int B_sz = matBrow*matBcol*sizeof(float);
      int C_sz = matArow*matBcol*sizeof(float);

      cl_mem dA = clCreateBuffer(clContext,CL_MEM_READ_ONLY,A_sz,NULL,&clStatus);
      OPENCL_SUCCEED(clStatus);
      cl_mem dB = clCreateBuffer(clContext,CL_MEM_READ_ONLY,B_sz,NULL,&clStatus);
      OPENCL_SUCCEED(clStatus);
      cl_mem dC = clCreateBuffer(clContext,CL_MEM_WRITE_ONLY,C_sz,NULL,&clStatus);
      OPENCL_SUCCEED(clStatus);

      float v = 0.1;
      OPENCL_SUCCEED(clEnqueueFillBuffer(clCommandQueue,
                                         dA, &v, sizeof(v),
                                         0, A_sz,
                                         0, NULL, NULL));
      OPENCL_SUCCEED(clEnqueueFillBuffer(clCommandQueue,
                                         dB, &v, sizeof(v),
                                         0, B_sz,
                                         0, NULL, NULL));

      OPENCL_SUCCEED(clFinish(clCommandQueue));

      /* Warmup run. */
      regtileMatmul(matArow, matBcol, matAcol,
                    dA, dB, dC,
                    clKernel, clCommandQueue);
      OPENCL_SUCCEED(clFinish(clCommandQueue));

      int64_t bef = get_wall_time();
      int runs = 10;
      for (int i = 0; i < runs; i++) {
        regtileMatmul(matArow, matBcol, matAcol,
                      dA, dB, dC,
                      clKernel, clCommandQueue);
      }
      int64_t aft = get_wall_time();

      int runtime = ((double)(aft-bef))/runs;
      printf("Runtime in microseconds based on %d runs:\n%d\n",
             runs, runtime);

      if (x != n || i != 2) {
        fprintf(f, ", ");
      } else {
        fprintf(f, "  ");
      }
      fprintf(f, "\"matmul-data/2pow%d_work_2pow%d_outer\":{\"runtimes\": [%d]}\n", k, x, runtime);

      clReleaseMemObject(dA);
      clReleaseMemObject(dB);
      clReleaseMemObject(dC);
    }
  }
  fprintf(f, "}}}\n");
  fclose(f);

  free((void*)clSource[0]);
  clReleaseKernel(clKernel);
  clReleaseProgram(clProgram);
  clReleaseCommandQueue(clCommandQueue);
  clReleaseContext(clContext);

  return 0;
}
