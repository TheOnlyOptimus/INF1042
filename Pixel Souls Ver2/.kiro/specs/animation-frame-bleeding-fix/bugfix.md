# Bugfix Requirements Document

## Introduction

This document specifies the requirements for fixing animation frame bleeding, clipping, and jittering issues in the Pygame knight character. The bug manifests as visual artifacts and character position instability during certain animations, caused by inconsistent frame dimensions when using independent per-frame cropping.

The fix will ensure smooth, stable animations by normalizing frame dimensions within each animation while maintaining proper anchoring at the character's feet position.

## Bug Analysis

### Current Behavior (Defect)

1.1 WHEN the Walk animation plays THEN the system exhibits severe frame bleeding and clipping, making the animation appear completely broken

1.2 WHEN the Run Attack animation plays THEN the system exhibits significant frame bleeding

1.3 WHEN the Attack 1 animation plays THEN the system exhibits minor frame bleeding

1.4 WHEN the Attack 3 animation plays THEN the system exhibits minor frame bleeding

1.5 WHEN the Jump animation plays THEN the system exhibits minor frame bleeding

1.6 WHEN any affected animation plays THEN the character appears to "jump around" or jitter on screen due to inconsistent frame anchoring

1.7 WHEN `load_sheet()` processes frames THEN each frame is cropped independently using `get_bounding_rect()`, resulting in different dimensions and pixel origins for each frame

1.8 WHEN frames with different dimensions are rendered THEN the `midbottom` anchor point varies relative to the character's actual feet position, causing visual jitter

### Expected Behavior (Correct)

2.1 WHEN the Walk animation plays THEN the system SHALL display smooth animation without frame bleeding or clipping

2.2 WHEN the Run Attack animation plays THEN the system SHALL display smooth animation without frame bleeding

2.3 WHEN the Attack 1 animation plays THEN the system SHALL display smooth animation without frame bleeding

2.4 WHEN the Attack 3 animation plays THEN the system SHALL display smooth animation without frame bleeding

2.5 WHEN the Jump animation plays THEN the system SHALL display smooth animation without frame bleeding

2.6 WHEN any animation plays THEN the character SHALL remain anchored consistently at the feet position without jittering or jumping around

2.7 WHEN `load_sheet()` processes frames THEN each frame SHALL be cropped to remove empty space AND normalized to consistent dimensions within the animation

2.8 WHEN frames are normalized THEN the character's feet position SHALL remain at the same relative location across all frames in the animation

### Unchanged Behavior (Regression Prevention)

3.1 WHEN animations that currently work correctly (Idle, Idle_2, Run, Roll, etc.) play THEN the system SHALL CONTINUE TO display them without introducing new visual artifacts

3.2 WHEN the `draw()` method renders frames THEN the system SHALL CONTINUE TO use `midbottom` anchoring at the character's feet position

3.3 WHEN sprite scaling is applied THEN the system SHALL CONTINUE TO scale frames by the `SPRITE_SCALE` factor (currently 4)

3.4 WHEN animation offsets from `ANIM_OFFSETS` are applied THEN the system SHALL CONTINUE TO apply them correctly for fine-tuning position

3.5 WHEN frames are flipped for left-facing direction THEN the system SHALL CONTINUE TO flip them correctly without introducing artifacts

3.6 WHEN the player moves, jumps, or performs actions THEN the system SHALL CONTINUE TO maintain correct collision detection and gameplay mechanics

3.7 WHEN different animations transition between each other THEN the system SHALL CONTINUE TO transition smoothly without position jumps beyond what the fix addresses
