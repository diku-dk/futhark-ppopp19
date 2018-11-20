-- Rodinia's SRAD, but extended with another outer level of
-- parallelism, such that multiple SRAD instances are computed in
-- parallel.
--
-- ==
-- compiled input @ srad-data/train-D1.in
-- compiled input @ srad-data/train-D2.in
--
-- notune compiled input @ srad-data/D1.in
-- notune compiled input @ srad-data/D2.in

module srad = import "srad-baseline"

let main [num_images][rows][cols] (images: [num_images][rows][cols]u8): [num_images][rows][cols]f32 =
  let niter = 100
  let lambda = 0.5
  in map (\image -> srad.do_srad(niter, lambda, image)) images
