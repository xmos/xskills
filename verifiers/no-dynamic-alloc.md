---
id: xmos-no-dynamic-alloc
scope: ["**/src/**/*.c", "**/src/**/*.h", "**/src/**/*.xc", "**/src/**/*.cpp"]
severity: warn
---
**Claim:** Firmware source uses no dynamic or variable-size memory
allocation: no malloc, calloc, realloc, free, strdup or alloca, no C++
new/delete, and no variable-length arrays. All buffers are statically sized
at compile time.

**Pass if:** none of the above appear in the scoped files.
**Fail if:** any of them appear, including inside macros or helper functions
defined in these files.
**Evidence:** quote each offending line with its file name.

Out of scope: code built for a host PC (e.g. host-side control apps or test
harnesses), even if it sits under a src/ directory.
