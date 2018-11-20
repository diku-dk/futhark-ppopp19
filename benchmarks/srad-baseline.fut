-- Specialised SRAD for the single-image case to create a sensible
-- reference point for showing the results.
--
-- ==
-- input @ srad-data/D1.in

let indexN(_rows: i32, i: i32): i32 =
  if i == 0 then i else i - 1

let indexS(rows: i32, i: i32): i32 =
  if i == rows-1 then i else i + 1

let indexW(_cols: i32, j: i32): i32 =
  if j == 0 then j else j - 1

let indexE(cols: i32, j: i32): i32 =
  if j == cols-1 then j else j + 1

let do_srad [rows][cols] (niter: i32, lambda: f32, image: [rows][cols]u8): [rows][cols]f32 =
  let r1 = 0
  let r2 = rows - 1
  let c1 = 0
  let c2 = cols - 1

  -- ROI image size
  let neROI = (r2-r1+1)*(c2-c1+1)

  -- SCALE IMAGE DOWN FROM 0-255 TO 0-1 AND EXTRACT
  let image = map (map1 (\pixel -> f32.exp(f32.u8(pixel)/255.0))) image
  let image = loop image for _i < niter do
    -- ROI statistics for entire ROI (single number for ROI)
    let sum = f32.sum (flatten image)
    let sum2 = f32.sum (map (**2.0) (flatten image))
    -- get mean (average) value of element in ROI
    let meanROI = sum / r32 neROI
    -- gets variance of ROI
    let varROI = (sum2 / r32 neROI) - meanROI*meanROI
    -- gets standard deviation of ROI
    let q0sqr = varROI / (meanROI*meanROI)

    let (dN, dS, dW, dE, c) =
      unzip5 (map2 (\i row ->
                unzip5 (map2 (\j jc ->
                        let dN_k = unsafe image[indexN(rows,i),j] - jc
                        let dS_k = unsafe image[indexS(rows,i),j] - jc
                        let dW_k = unsafe image[i, indexW(cols,j)] - jc
                        let dE_k = unsafe image[i, indexE(cols,j)] - jc
                        let g2 = (dN_k*dN_k + dS_k*dS_k +
                                  dW_k*dW_k + dE_k*dE_k) / (jc*jc)
                        let l = (dN_k + dS_k + dW_k + dE_k) / jc
                        let num = (0.5*g2) - ((1.0/16.0)*(l*l))
                        let den = 1.0 + 0.25*l
                        let qsqr = num / (den*den)
                        let den = (qsqr-q0sqr) / (q0sqr * (1.0+q0sqr))
                        let c_k = 1.0 / (1.0+den)
                        let c_k = if c_k < 0.0
                                  then 0.0
                                  else if c_k > 1.0
                                       then 1.0 else c_k
                        in (dN_k, dS_k, dW_k, dE_k, c_k))
                      (iota cols) row))
             (iota rows) image)

    let image =
      map4 (\i image_row c_row (dN_row, dS_row, dW_row, dE_row) ->
                map4 (\j pixel c_k (dN_k, dS_k, dW_k, dE_k)  ->
                          let cN = c_k
                          let cS = unsafe c[indexS(rows, i), j]
                          let cW = c_k
                          let cE = unsafe c[i, indexE(cols,j)]
                          let d = cN*dN_k + cS*dS_k + cW*dW_k + cE*dE_k
                          in pixel + 0.25 * lambda * d)
                     (iota cols) image_row c_row (zip4 dN_row dS_row dW_row dE_row))
           (iota rows) image c (zip4 dN dS dW dE)
    in image

  -- SCALE IMAGE UP FROM 0-1 TO 0-255 AND COMPRESS
  let image = map (map1 (\pixel  ->
                          -- Take logarithm of image (log compress).
                          -- This is where the original implementation
                          -- would round to i32.
                         f32.log(pixel)*255.0)) image
  in image

let main [rows][cols] (images: [1][rows][cols]u8): [1][rows][cols]f32 =
  let niter = 100
  let lambda = 0.5
  in [do_srad(niter, lambda, images[0])]
