# A/V Sync and Transcript Reconciliation for Silence-Cut Clips

Use this when a short phone clip has non-zero per-stream `start_time`, especially when audio starts later than video, and you are cutting pauses with `select`/`aselect`.

## Why this matters

`aselect=...,asetpts=N/SR/TB` makes the first decoded audio sample start at zero. If the source audio originally begins later than video, this silently collapses the offset and shifts speech early relative to the mouth. A 0.5–0.7 s offset is plainly visible.

## Reliable procedure

1. Probe per-stream timing, not only container duration:
   ```bash
   ffprobe -v error -show_entries stream=index,codec_type,start_time,duration -of json "IN.MOV"
   ```
2. Compute `delta = audio_start_time - video_start_time`.
3. Build one KEEP expression for pause removal and reuse it for the cut proxy and final render.
4. If `delta > 0`, turn the offset into real silence after resetting audio timestamps:
   ```text
   [0:a]aselect='KEEP',asetpts=N/SR/TB,adelay=DELTA_MS|DELTA_MS[a]
   ```
   where `DELTA_MS = round(delta * 1000)`. For mono use one value; for more channels provide one value per channel.
5. Do audio cleanup/mastering from this padded cut. The master should start at zero and contain the delay as samples, so remuxing cannot collapse it.
6. Verify cut video/audio durations are effectively equal and decode the delivered file with the null muxer.

Do not add `adelay` if the source streams already start together. Do not apply the offset twice.

## Subtitle reconciliation

Use two ASR passes when cuts or clipped words make one transcript unreliable:

- **Original-source transcript:** lexical reference. It preserves words around edit points and is better for reconstructing complete sentences.
- **Cut-proxy transcript:** timing reference. Its cue timestamps match the edited timeline.

Rebuild the final SRT using corrected text from the original pass and timestamps from the cut pass. Review dates, proper names, certification terms, and CTA wording manually.

Whisper may anchor the first cue at `00:00:00,000` even when the cut audio contains inserted leading silence. Inspect the first spoken frame/audio onset and move that cue start forward if needed.

If the recording itself starts mid-word, restore the intended word only when another take of the same scripted campaign clearly confirms it. Otherwise caption only the audible content or ask the user; do not invent copy.

## Trailing silence with unequal stream lengths

Phone files can have audio ending before the video container. When trimming a final detected pause, remove video through the container/video duration, not merely through the audio stream end. After adding the original positive audio offset as physical silence, confirm final A/V durations still match within roughly one frame/audio packet.
