-- Important: assumes that FFT edge sizes are powers of two.
-- ==
-- compiled input @ fft-data/edge_2pow2
-- output @ fft-data/edge_2pow2.out
-- compiled input @ fft-data/edge_2pow3
-- output @ fft-data/edge_2pow3.out
-- compiled input @ fft-data/edge_2pow4
-- output @ fft-data/edge_2pow4.out
-- compiled input @ fft-data/edge_2pow5
-- output @ fft-data/edge_2pow5.out
-- compiled input @ fft-data/edge_2pow6
-- output @ fft-data/edge_2pow6.out
-- compiled input @ fft-data/edge_2pow7
-- output @ fft-data/edge_2pow7.out
-- compiled input @ fft-data/edge_2pow8
-- output @ fft-data/edge_2pow8.out
-- compiled input @ fft-data/edge_2pow9
-- output @ fft-data/edge_2pow9.out
-- compiled input @ fft-data/edge_2pow10
-- output @ fft-data/edge_2pow10.out

import "/futlib/complex"

module complex = complex f32
type complex = complex.complex

let radix = 2

let fft_iteration [n] (forward: f32) (ns: i32) (data: [n]complex) (j: i32)
                : (i32, complex, i32, complex) =
  let angle = (-2f32 * forward * f32.pi * r32 (j % ns)) / r32 (ns * radix)
  let (v0, v1) = (data[j],
                  data[j+n/radix] complex.* (complex.mk (f32.cos angle) (f32.sin angle)))

  let (v0, v1) =  (v0 complex.+ v1, v0 complex.- v1)
  let idxD = ((j/ns)*ns*radix) + (j % ns)
  in (idxD, v0, idxD+ns, v1)

let fft' [n] (forward: f32) (input: [n]complex) (bits: i32) : []complex =
  let input = copy input
  let output = copy input
  let ix = iota(n/radix)
  let NS = map (radix**) (iota bits)
  let (res,_) =
    loop (input': *[n]complex, output': *[n]complex) = (input, output) for ns in NS do
      let (i0s, v0s, i1s, v1s) =
        unsafe (unzip (map (fft_iteration forward ns input') ix))
      in (scatter output' (concat i0s i1s) (concat v0s v1s), input')
  in res

let log2 (n: i32) : i32 =
  let r = 0
  let (r, _) = loop (r,n) while 1 < n do
    let n = n / 2
    let r = r + 1
    in (r,n)
  in r

let generic_fft2 [n][m] (forward: bool) (data: [n][m](f32, f32)): [n][m](f32, f32) =
  let n_bits = log2 n
  let m_bits = log2 m
  let forward' = if forward then 1f32 else -1f32
  let data = map (\r -> fft' forward' r m_bits) data
  let data = map (\c -> fft' forward' c n_bits) (transpose data)
  in transpose data

let fft2 [n][m] (data: [n][m](f32, f32)): [n][m](f32, f32) =
  generic_fft2 true data

let main [k][n][m] (data: [k][n][m]f32): [k][n][m]f32 =
  map (\array ->
       map (\r -> map complex.re r)
           (fft2 (map (\r -> map complex.mk_re r) array)))
      data
