-- Code and comments based on
-- https://github.com/kkushagra/rodinia/blob/master/openmp/pathfinder/
--
-- ==
--
-- input @ pathfinder-data/391_100_256.in
-- output @ pathfinder-data/391_100_256.out

let pathfinder [rows][cols] (wall: [rows][cols]i32): [cols]i32 =
  let (_, res) =
    loop (input: *[cols]i32, output: *[cols]i32) = (copy wall[0], copy wall[0]) for t < (rows-1) do
      let output' = scatter output (iota cols)
                    (map (\i ->
                            let res = input[i]
                            let res = if i >  0     then i32.min res (unsafe input[i-1]) else res

                            let res = if i < cols-1 then i32.min res (unsafe input[i+1]) else res

                            in wall[t+1, i] + res)
                     (iota(cols)))
      in (output', input)
  in res

let main [batches][rows][cols] (mazes: [batches][rows][cols]i32) =
  map pathfinder mazes
