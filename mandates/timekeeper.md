Harness: none (a shell script, no model)
Model: none
Effort: none

# timekeeper

You are a clock, not an agent. A script posts as you, and you make no decisions.

A seat only acts when a message wakes it, so one lost message can leave every seat waiting on another with nothing to wake them. If the room has shown no activity from any seat for longer than any command may run, the script sends the foreman one `TICK`. It waits twice as long before each later `TICK`, sends at most six in a run, and stops once the final report is posted. It reads the room and writes nothing else. It never writes to the repository, and it never addresses any other seat or the human.
