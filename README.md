# Optimize fillrate for atlas animations

## Setup

Install Python. Tested on Python 3, but should also work with 2. Then:

```
pip install deftree Pillow
```

## Usage:

```
python trim.py <path_to_project_root> <path_to_atlas_file> <path_to_output_directory>
```

This will output PNGs and an `animations.lua` in the output directory. To convert
the existing sprite to an optimized one:

1. Delete all the animations in the atlas and add the new PNGs (just the frames,
  without any animation).

2. Require the `animations.lua` in any script being initialized at the same
  time or earlier as your sprite component (renaming it as `.script` and attaching
  it to a game object in the same collection as your sprite also works).

3. Make sure your sprite component is positioned at `(0,0)` with no rotation or
  scale within a parent game object itself at `(x, y)` with no rotation or scale,
  where `(x, y)` is the offset of the default animation's first frame. The
  position and scale of this game object will be controlled by the animation
  controller, so don't touch them from code.

4. Add the animation controller script (`main/animations/sprite_animation.script`)
next to the sprite component and set the `texture_id` property to the name of
your original atlas file.

5. Send the `sprite_play_animation` message to this script instead of `play_animation`
to the sprite. Extra features are available (Read the code).

