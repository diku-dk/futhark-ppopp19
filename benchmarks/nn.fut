-- Code and comments based on
-- https://github.com/kkushagra/rodinia/blob/master/openmp/nn
--
-- ==
-- compiled input @ nn-data/train-D1.in
-- compiled input @ nn-data/train-D2.in
--
-- notune compiled input @ nn-data/D1.in
-- notune compiled input @ nn-data/D2.in

let emptyRecord: (i32, f32) = (0, 0.0f32)

let nn [m]
       (k: i32)
       (lat: f32) (lng: f32)
       (locations_lat: [m]f32)
       (locations_lng: [m]f32)
       : ([k]i32, [k]f32) =
  let locations = zip locations_lat locations_lng
  let distance (lat_i: f32, lng_i: f32) =
    f32.sqrt((lat-lat_i)*(lat-lat_i) + (lng-lng_i)*(lng-lng_i))
  let distances = map distance locations

  let results = replicate k emptyRecord
  let (results, _) =
    loop ((results, distances)) for i < k do unsafe
      let (minDist, minLoc) =
        reduce_comm (\(d1, i1) (d2,i2) ->
                         if      d1 < d2 then (d1, i1)
                         else if d2 < d1 then (d2, i2)
                         else if i1 < i2 then (d1, i1)
                         else                 (d2, i2))
                    (f32.inf, 0) (zip distances (iota m))

      let distances[minLoc] = f32.inf
      let results[i] = (minLoc, minDist)
      in (results, distances)
  in unzip results

let main [n] [m]
         (k: i32)
         (lats: [n]f32) (lngs: [n]f32)
         (locations_lats: [n][m]f32)
         (locations_lngs: [n][m]f32)
        : ([n][k]i32, [n][k]f32) =
  unzip (map4 (nn k) lats lngs locations_lats locations_lngs)
