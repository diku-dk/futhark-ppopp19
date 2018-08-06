// Based on https://stackoverflow.com/a/23743838/6131552

#include <stdio.h>
#include <cuda_runtime.h>
#include <cublas_v2.h>
#include <assert.h>
#include <sys/time.h>

#define cudaCheckErrors(msg)                                    \
  do {                                                          \
    cudaError_t __err = cudaGetLastError();                     \
    if (__err != cudaSuccess) {                                 \
      fprintf(stderr, "Fatal error: %s (%s at %s:%d)\n",        \
              msg, cudaGetErrorString(__err),                   \
              __FILE__, __LINE__);                              \
      fprintf(stderr, "*** FAILED - ABORTING\n");               \
      exit(1);                                                  \
    }                                                           \
  } while (0)


int GPU_Single(float *h_M, float *h_N, float *h_P, size_t ROWM, size_t COLM, size_t COLN, float alpha, float beta)
{

  float *d_M;
  float *d_N;
  float *d_P;

  size_t N_size =sizeof(float) *ROWM*COLM;
  size_t M_size =sizeof(float) *COLM*COLN;
  size_t P_size =sizeof(float) *ROWM*COLN;

  cublasHandle_t myhandle;
  cublasStatus_t cublas_result;

  cudaMalloc(&d_M, M_size);
  cudaMalloc(&d_N, N_size);
  cudaMalloc(&d_P, P_size);
  cudaCheckErrors("cudaMalloc fail");

  cudaMemcpy(d_M, h_M, M_size , cudaMemcpyHostToDevice);
  cudaMemcpy(d_N, h_N, N_size , cudaMemcpyHostToDevice);
  cudaMemcpy(d_P, h_P, P_size , cudaMemcpyHostToDevice);
  cudaCheckErrors("cudaMemcpy H2D fail");

  cublas_result = cublasCreate(&myhandle);
  assert(cublas_result == CUBLAS_STATUS_SUCCESS);

  struct timeval t_start, t_end;
  gettimeofday(&t_start, NULL);
  int runtime, runs = 10;
  for (int i = 0; i < runs; i++) {
    cublas_result = cublasSgemm(myhandle, CUBLAS_OP_N, CUBLAS_OP_N, ROWM, COLN, COLM, &alpha, d_M, ROWM, d_N, COLM, &beta, d_P, ROWM);
    cudaDeviceSynchronize();
  }
  gettimeofday(&t_end, NULL);
  assert(cublas_result == CUBLAS_STATUS_SUCCESS);

  runtime = ((t_end.tv_sec*1000000+t_end.tv_usec) - (t_start.tv_sec*1000000+t_start.tv_usec))/runs;

  cudaMemcpy(h_P, d_P, P_size, cudaMemcpyDeviceToHost);
  cudaFree(d_M);
  cudaFree(d_N);
  cudaFree(d_P);
  cudaCheckErrors("cudaMemcpy D2H fail");

  return runtime;
}

int main(int argc, char** argv) {
  if (argc != 2 && ((argc-2)%3!=0)) {
    fprintf(stderr, "%s usage: <outfile> < <n> <m> <k> >...\n", argv[0]);
    exit(1);
  }

  const char *outfile = argv[1];
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
      int ROWM = 1 << x;
      int COLM = 1 << y;
      int COLN = 1 << x;

      float *h_M1 = (float*) malloc(ROWM*COLM*sizeof(float));
      float *h_N1 = (float*) malloc(COLM*COLN*sizeof(float));
      float *h_P1 = (float*) malloc(ROWM*COLN*sizeof(float));

      printf("Multiplying [2**%d][2**%d] and [2**%d][2**%d] matrices\n", x, y, y, x);
      int runtime = GPU_Single(h_M1, h_N1, h_P1, ROWM, COLM, COLN, 1.0f, 0.0f);
      printf("Runtime in microseconds based on %d runs:\n%d\n",
             10, runtime);

      if (x != n || i != 2) {
        fprintf(f, ", ");
      } else {
        fprintf(f, "  ");
      }
      fprintf(f, "\"matmul-data/2pow%d_work_2pow%d_outer\":{\"runtimes\": [%d]}\n", k, x, runtime);

      free(h_M1);
      free(h_N1);
      free(h_P1);
    }
  }

  fprintf(f, "}}}\n");
  fclose(f);

  return 0;
}
