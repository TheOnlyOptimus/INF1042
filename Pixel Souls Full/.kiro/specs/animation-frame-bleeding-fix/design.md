# Animation Frame Bleeding Fix - Bugfix Design

## Overview

This design addresses animation frame bleeding, clipping, and jittering issues in the Pygame knight character by implementing a hybrid two-pass normalization approach in the `load_sheet()` function. The bug manifests when animations like Walk, Run Attack, Attack 1, Attack 3, and Jump display visual artifacts and character position instability due to inconsistent frame dimensions.

The fix ensures all frames within an animation have identical dimensions while maintaining proper foot anchoring, eliminating visual jitter caused by varying `midbottom` anchor points across frames. The solution crops individual frames to remove empty space, then normalizes them to a common size with consistent foot positioning.

## Glossary

- **Bug_Condition (C)**: The condition that triggers the bug - when animation frames have inconsistent dimensions after independent cropping, causing the `midbottom` anchor point to vary relative to the character's actual feet position
- **Property (P)**: The desired behavior - all frames in an animation have identical dimensions with the character's feet at the same relative position (bottom of frame)
- **Preservation**: Existing functionality that must remain unchanged - animations that currently work correctly, `midbottom` anchoring behavior, sprite scaling, animation offsets, flipping, collision detection, and gameplay mechanics
- **load_sheet()**: The function in `utils.py` that loads sprite sheet images, slices them into individual frames, crops them, and scales them
- **get_bounding_rect()**: Pygame method that returns the smallest rectangle containing all non-transparent pixels in a surface
- **midbottom**: Pygame rect anchor point at the horizontal center and bottom edge, used in `Player.draw()` to position frames at the character's feet
- **SPRITE_SCALE**: Scaling factor (currently 4) applied to all frames after processing
- **Frame bleeding**: Visual artifact where pixels from one animation frame appear to "bleed" into adjacent frames or positions
- **Frame jittering**: Visual instability where the character appears to "jump around" on screen due to inconsistent frame anchoring
- **Two-pass processing**: Algorithm approach where the first pass analyzes all frames to find maximum dimensions, and the second pass normalizes each frame to those dimensions
- **Baseline anchoring**: Positioning technique where all frames align their bottom edge to a common reference point (the lowest bottom position across all frames)

## Bug Details

### Bug Condition

The bug manifests when animations with varying frame content (Walk, Run Attack, Attack 1, Attack 3, Jump) are processed by `load_sheet()`. The current implementation crops each frame independently using `get_bounding_rect()`, resulting in different dimensions and pixel origins for each frame. When these frames are rendered using `midbottom` anchoring, the anchor point varies relative to the character's actual feet position, causing visual jitter and frame bleeding.

**Formal Specification:**
```
FUNCTION isBugCondition(input)
  INPUT: input of type AnimationFrameSet
  OUTPUT: boolean
  
  RETURN input.frames.length > 1
         AND hasInconsistentDimensions(input.frames)
         AND hasInconsistentFootPositions(input.frames)
         AND renderedWithMidbottomAnchoring(input.frames)
END FUNCTION

FUNCTION hasInconsistentDimensions(frames)
  widths := [frame.width FOR frame IN frames]
  heights := [frame.height FOR frame IN frames]
  RETURN NOT (allEqual(widths) AND allEqual(heights))
END FUNCTION

FUNCTION hasInconsistentFootPositions(frames)
  bottomPositions := [frame.height FOR frame IN frames]
  RETURN NOT allEqual(bottomPositions)
END FUNCTION
```

### Examples

- **Walk animation (8 frames)**: Severe frame bleeding and clipping. Each frame has different dimensions after cropping (e.g., frame 1: 45x78, frame 2: 52x81, frame 3: 48x79). When rendered with `midbottom` anchoring, the character's feet jump between different Y positions, creating severe visual instability.

- **Run Attack animation (6 frames)**: Significant frame bleeding. Attack frames extend further horizontally than run frames, causing width variations (e.g., frame 1: 60x85, frame 4: 75x88). The character appears to shift position during the attack sequence.

- **Attack 1 animation (5 frames)**: Minor frame bleeding. Sword swing frames have different bounding boxes than idle stance frames (e.g., frame 1: 50x82, frame 3: 58x82). The character's body appears to shift slightly during the attack.

- **Jump animation (6 frames)**: Minor frame bleeding. Frames at the peak of the jump have different heights than takeoff/landing frames (e.g., frame 1: 55x90, frame 3: 55x85, frame 5: 55x88). The character's vertical position appears unstable during the jump arc.

- **Edge case - Single frame animation (Block)**: Expected behavior - no bleeding or jittering since there's only one frame, dimensions are consistent by definition.

## Expected Behavior

### Preservation Requirements

**Unchanged Behaviors:**
- Animations that currently work correctly (Idle, Idle_2, Run, Roll, etc.) must continue to display without introducing new visual artifacts
- The `draw()` method must continue to use `midbottom` anchoring at the character's feet position
- Sprite scaling must continue to scale frames by the `SPRITE_SCALE` factor (currently 4)
- Animation offsets from `ANIM_OFFSETS` must continue to be applied correctly for fine-tuning position
- Frames must continue to flip correctly for left-facing direction without introducing artifacts
- Player movement, jumping, and actions must continue to maintain correct collision detection and gameplay mechanics
- Animation transitions must continue to work smoothly without position jumps beyond what the fix addresses

**Scope:**
All inputs that do NOT involve animations with inconsistent frame dimensions should be completely unaffected by this fix. This includes:
- Single-frame animations (Block)
- Animations that already have consistent dimensions after cropping
- The rendering pipeline outside of `load_sheet()`
- Game logic, physics, and collision detection
- Input handling and state transitions

## Hypothesized Root Cause

Based on the bug description and code analysis, the root cause is:

1. **Independent Frame Cropping**: The current `load_sheet()` implementation crops each frame independently using `get_bounding_rect()`. This removes empty space efficiently but results in different dimensions for each frame:
   ```python
   pixel_rect = raw_frame.get_bounding_rect()
   if pixel_rect.width > 0 and pixel_rect.height > 0:
       trimmed = raw_frame.subsurface(pixel_rect).copy()
   ```

2. **Inconsistent Anchor Point Positioning**: When frames have different dimensions, the `midbottom` anchor point in `Player.draw()` positions each frame's bottom edge at the same screen coordinate. However, because the cropped frames have different heights and the character's feet are at different positions within each cropped frame, the character's actual feet position varies across frames:
   ```python
   img_rect = img.get_rect()
   img_rect.midbottom = (foot_x, foot_y)
   ```

3. **No Dimension Normalization**: The current implementation scales each frame independently without normalizing dimensions first. This preserves the dimension inconsistencies through the scaling operation:
   ```python
   new_w = int(trimmed.get_width() * scale)
   new_h = int(trimmed.get_height() * scale)
   scaled = pygame.transform.scale(trimmed, (new_w, new_h))
   ```

4. **Lack of Baseline Anchoring**: There is no mechanism to ensure that the character's feet are at the same relative position (e.g., bottom of frame) across all frames in an animation. Each frame's bottom edge represents a different part of the character's body depending on how much empty space was cropped.

## Correctness Properties

Property 1: Bug Condition - Frame Dimension Consistency

_For any_ animation frame set where the bug condition holds (frames have inconsistent dimensions after cropping), the fixed load_sheet function SHALL produce frames with identical dimensions within that animation, with the character's feet positioned at the same relative location (bottom of frame) across all frames, eliminating visual jitter and frame bleeding.

**Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8**

Property 2: Preservation - Existing Functionality

_For any_ animation processing that does NOT involve the dimension normalization logic (single-frame animations, already-consistent animations, rendering pipeline, game logic), the fixed code SHALL produce exactly the same behavior as the original code, preserving all existing functionality including correct display of working animations, midbottom anchoring, sprite scaling, animation offsets, flipping, collision detection, and gameplay mechanics.

**Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7**

## Fix Implementation

### Changes Required

Assuming our root cause analysis is correct:

**File**: `utils.py`

**Function**: `load_sheet()`

**Specific Changes**:

1. **First Pass - Analyze All Frames**: After slicing and cropping individual frames, iterate through all frames to find:
   - Maximum width across all cropped frames
   - Maximum height across all cropped frames
   - Lowest bottom position (highest height value) to determine the baseline for foot anchoring
   
   ```python
   # First pass: crop all frames and find max dimensions
   cropped_frames = []
   max_width = 0
   max_height = 0
   
   for i in range(frame_count):
       # ... existing slicing code ...
       pixel_rect = raw_frame.get_bounding_rect()
       if pixel_rect.width > 0 and pixel_rect.height > 0:
           trimmed = raw_frame.subsurface(pixel_rect).copy()
       else:
           trimmed = raw_frame.copy()
       
       cropped_frames.append(trimmed)
       max_width = max(max_width, trimmed.get_width())
       max_height = max(max_height, trimmed.get_height())
   ```

2. **Second Pass - Normalize Frame Dimensions**: Create a new surface for each frame with the maximum dimensions found in the first pass. Position each cropped frame so its bottom edge aligns with the common baseline (bottom of the normalized frame):
   
   ```python
   # Second pass: normalize all frames to max dimensions
   normalized_frames = []
   
   for cropped in cropped_frames:
       # Create surface with max dimensions
       normalized = pygame.Surface((max_width, max_height), pygame.SRCALPHA)
       normalized.fill((0, 0, 0, 0))  # Transparent background
       
       # Position cropped frame with bottom alignment
       x_offset = (max_width - cropped.get_width()) // 2  # Center horizontally
       y_offset = max_height - cropped.get_height()  # Align bottom
       
       normalized.blit(cropped, (x_offset, y_offset))
       normalized_frames.append(normalized)
   ```

3. **Scale Normalized Frames**: Apply the sprite scale to the normalized frames instead of the cropped frames:
   
   ```python
   # Scale the normalized frames
   frames = []
   for normalized in normalized_frames:
       new_w = int(normalized.get_width() * scale)
       new_h = int(normalized.get_height() * scale)
       scaled = pygame.transform.scale(normalized, (new_w, new_h))
       frames.append(scaled)
   ```

4. **Preserve Existing Error Handling**: Maintain the try-except block and error logging:
   
   ```python
   try:
       # ... all processing code ...
   except Exception as e:
       print(f"[ERROR] {filename}: {e}")
   
   return frames
   ```

5. **Maintain Function Signature**: Keep the function signature unchanged to preserve compatibility with existing code:
   
   ```python
   def load_sheet(filename, declared_w, declared_h, frame_count, scale):
       # ... implementation ...
   ```

## Testing Strategy

### Validation Approach

The testing strategy follows a two-phase approach: first, surface counterexamples that demonstrate the bug on unfixed code by measuring frame dimensions and observing visual artifacts, then verify the fix produces consistent dimensions and eliminates jitter while preserving existing behavior.

### Exploratory Bug Condition Checking

**Goal**: Surface counterexamples that demonstrate the bug BEFORE implementing the fix. Confirm or refute the root cause analysis by measuring frame dimensions and observing visual behavior. If we refute, we will need to re-hypothesize.

**Test Plan**: Write tests that load animations using the UNFIXED `load_sheet()` function, measure the dimensions of each frame, and verify that dimensions are inconsistent. Also run the game and visually observe frame bleeding and jittering. Run these tests on the UNFIXED code to observe failures and understand the root cause.

**Test Cases**:
1. **Walk Animation Dimension Test**: Load Walk animation frames and measure dimensions. Assert that frames have different widths or heights. (will fail on unfixed code - dimensions will be inconsistent)
2. **Run Attack Animation Dimension Test**: Load Run Attack animation frames and measure dimensions. Assert that frames have different widths or heights. (will fail on unfixed code - dimensions will be inconsistent)
3. **Attack 1 Animation Dimension Test**: Load Attack 1 animation frames and measure dimensions. Assert that frames have different widths or heights. (will fail on unfixed code - dimensions will be inconsistent)
4. **Visual Observation Test**: Run the game and observe Walk animation. Document the visual jitter and frame bleeding. (will show artifacts on unfixed code)
5. **Baseline Position Test**: Load Walk animation frames and measure the position of the character's feet relative to the frame bottom. Assert that feet positions vary across frames. (will fail on unfixed code - feet positions will be inconsistent)

**Expected Counterexamples**:
- Walk animation frames will have dimensions like: frame 0: (180x312), frame 1: (208x324), frame 2: (192x316), etc. (after scaling by 4)
- Run Attack animation frames will have varying widths: frame 0: (240x340), frame 3: (300x352), etc.
- Visual observation will show the character's feet jumping up and down during Walk animation
- Possible causes: independent cropping without normalization, no baseline anchoring, inconsistent anchor point positioning

### Fix Checking

**Goal**: Verify that for all inputs where the bug condition holds (animations with inconsistent frame dimensions), the fixed function produces the expected behavior (consistent dimensions with baseline anchoring).

**Pseudocode:**
```
FOR ALL animation WHERE isBugCondition(animation) DO
  frames := load_sheet_fixed(animation.filename, animation.w, animation.h, animation.count, SPRITE_SCALE)
  
  // Check dimension consistency
  first_width := frames[0].width
  first_height := frames[0].height
  
  FOR ALL frame IN frames DO
    ASSERT frame.width = first_width
    ASSERT frame.height = first_height
  END FOR
  
  // Visual verification
  ASSERT noVisibleJitter(frames)
  ASSERT noFrameBleeding(frames)
END FOR
```

**Test Cases**:
1. **Walk Animation Consistency Test**: Load Walk animation with fixed code, verify all frames have identical dimensions
2. **Run Attack Animation Consistency Test**: Load Run Attack animation with fixed code, verify all frames have identical dimensions
3. **Attack 1 Animation Consistency Test**: Load Attack 1 animation with fixed code, verify all frames have identical dimensions
4. **Jump Animation Consistency Test**: Load Jump animation with fixed code, verify all frames have identical dimensions
5. **Visual Verification Test**: Run the game with fixed code, verify Walk animation displays smoothly without jitter or bleeding

### Preservation Checking

**Goal**: Verify that for all inputs where the bug condition does NOT hold (animations that already work correctly, single-frame animations, game logic), the fixed function produces the same result as the original function.

**Pseudocode:**
```
FOR ALL animation WHERE NOT isBugCondition(animation) DO
  frames_original := load_sheet_original(animation.filename, animation.w, animation.h, animation.count, SPRITE_SCALE)
  frames_fixed := load_sheet_fixed(animation.filename, animation.w, animation.h, animation.count, SPRITE_SCALE)
  
  ASSERT frames_original.length = frames_fixed.length
  
  FOR i := 0 TO frames_original.length - 1 DO
    ASSERT frames_original[i].width = frames_fixed[i].width
    ASSERT frames_original[i].height = frames_fixed[i].height
    ASSERT pixelDataEqual(frames_original[i], frames_fixed[i])
  END FOR
END FOR
```

**Testing Approach**: Property-based testing is recommended for preservation checking because:
- It generates many test cases automatically across the input domain (all animations in ANIM_MANIFEST)
- It catches edge cases that manual unit tests might miss (single-frame animations, animations with already-consistent dimensions)
- It provides strong guarantees that behavior is unchanged for all non-buggy inputs

**Test Plan**: Observe behavior on UNFIXED code first for animations that currently work correctly (Idle, Idle_2, Run, Roll, Block), then write property-based tests capturing that behavior. Verify the fixed code produces identical results.

**Test Cases**:
1. **Idle Animation Preservation**: Observe Idle animation on unfixed code (works correctly), verify fixed code produces identical frames
2. **Run Animation Preservation**: Observe Run animation on unfixed code (works correctly), verify fixed code produces identical frames
3. **Roll Animation Preservation**: Observe Roll animation on unfixed code (works correctly), verify fixed code produces identical frames
4. **Block Animation Preservation**: Observe Block animation (single frame) on unfixed code, verify fixed code produces identical frame
5. **Midbottom Anchoring Preservation**: Verify `Player.draw()` continues to use `midbottom` anchoring correctly with fixed frames
6. **Sprite Scaling Preservation**: Verify frames are scaled by SPRITE_SCALE (4) correctly after normalization
7. **Animation Offsets Preservation**: Verify ANIM_OFFSETS are applied correctly to fixed frames
8. **Flipping Preservation**: Verify frames flip correctly for left-facing direction with fixed code
9. **Collision Detection Preservation**: Verify player collision detection continues to work correctly with fixed frames
10. **Gameplay Mechanics Preservation**: Verify player movement, jumping, and actions work correctly with fixed frames

### Unit Tests

- Test `load_sheet()` with Walk animation, verify all frames have identical dimensions
- Test `load_sheet()` with Run Attack animation, verify all frames have identical dimensions
- Test `load_sheet()` with single-frame animation (Block), verify frame is processed correctly
- Test `load_sheet()` with animation that already has consistent dimensions, verify no changes
- Test dimension calculation logic (max_width, max_height) with various frame sets
- Test baseline anchoring logic (y_offset calculation) with various frame heights
- Test horizontal centering logic (x_offset calculation) with various frame widths
- Test error handling with invalid file paths, verify graceful failure

### Property-Based Tests

- Generate random animation configurations (frame counts, dimensions) and verify all output frames have consistent dimensions
- Generate random frame dimension sets and verify normalization produces correct max dimensions
- Generate random cropped frame sets and verify baseline anchoring positions all frames correctly
- Test that all animations in ANIM_MANIFEST produce consistent frame dimensions after fix
- Test that sprite scaling is applied correctly to all normalized frames across many scenarios
- Test that preservation holds for all animations that currently work correctly

### Integration Tests

- Test full game flow with Walk animation, verify smooth display without jitter or bleeding
- Test full game flow with Run Attack animation, verify smooth display during attack sequence
- Test full game flow with Jump animation, verify smooth display during jump arc
- Test animation transitions (Idle → Walk → Run → Jump), verify smooth transitions without position jumps
- Test left-facing and right-facing animations, verify flipping works correctly with normalized frames
- Test collision detection during various animations, verify hitboxes align correctly with normalized frames
- Test visual feedback during combat (attack animations), verify weapon swing positions are correct
- Test all animations in ANIM_MANIFEST in actual gameplay, verify no regressions introduced
