__kernel void matmul(__global const float *A, int lda,
                     __global const float *B, int ldb,
                     __global float* C, int ldc, int k)
{
  // Partial results
  float c[TILE_N];
  for (int i=0; i < TILE_N; i++)
    c[i] = 0.0f;

  int mid = get_local_id(1)*get_local_size(0)+get_local_id(0);
  int m = get_group_id(0) * TILE_M + mid;
  int n = get_group_id(1) * TILE_N + get_local_id(0);

  __local float b_s[TILE_TB_HEIGHT][TILE_N];

  for (int i = 0; i < k; i+=TILE_TB_HEIGHT) {
    float a;
    b_s[get_local_id(1)][get_local_id(0)] =
      n+(i+get_local_id(1))*ldb < k * ldb
      ? B[n+(i+get_local_id(1))*ldb]
      : 0;
    barrier(CLK_LOCAL_MEM_FENCE);
    for (int j = 0; j < TILE_TB_HEIGHT; j++) {
      a = m + (i+j)*lda < lda*k ? A[m + (i+j)*lda] : 0;
      for (int kk = 0; kk < TILE_N; kk++)
        c[kk] += a * b_s[j][kk];

    }
    barrier(CLK_LOCAL_MEM_FENCE);
  }
  int t = ldc * get_group_id(1) * TILE_N + m;
  for (int i = 0; i < TILE_N; i++) {
    if (t+i*ldc < lda * ldb) {
      C[t+i*ldc] = c[i];
    }
  }
}
