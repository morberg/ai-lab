# AI Tetris

Game created on May 26, 2025 by Gemini Pro 2.5 in Canvas. Prompt:

```text
Create a tetris game in python. Score should only increase when clearing a line. Use j to move left, l to move right , k to spin block clockwise and i to spin counterclockwise. Space drops the block. Make it flashy and colorful.
```

Initialised a python environment with:

```fish
uv init
uv add pygame
```

and we're good to go. Downloaded the first version and it worked. One problem
was that the score was not visible. And then I wanted to see the final score on
Game Over. Also, I think the rotation directions are mixed up. Otherwise no
major problems.

I asked for an update (not caring about rotation order):

```text
Very nice. The score was off screen. I would also like to show the final score when the game is over.
```

Score is now visible, but cut-off. Game over screen shows score.
