# AI Tetris

Game created on May 26, 2025 by Claude Sonnet 4. Prompt:

```text
Create a tetris game in python. Score should only increase when clearing a line. Use j to move left, l to move right , k to spin block clockwise and i to spin counterclockwise. Space drops the block. Make it flashy and colorful.
```

Initialised a python environment with:

```fish
uv init
uv add pygame
```

and we're good to go. Downloaded the first version and most things worked. One
problem was that the long 4x1 block did not rotate.