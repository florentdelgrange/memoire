# SSP-WE problem
storm --prism ssp_we.prism --prop "multi(Rmin=? [F \"T\"], Pmax>=1 [F{\"weights\"}<=5 \"T\"])"

# SSP-PQ problem
storm --prism ssp_pq.prism --prop "multi(Pmax=? [F{\"time\"}<=40 \"T\"], Pmax=? [F{\"money\"}<=10 \"T\"])"
