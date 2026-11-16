# Clean onboarding / training video

## Scope
- For this user's onboarding requests, preserve original aspect ratio, full slides and full teaching content. No captions, music, logos, stickers, zooms or end card unless requested. Keep the original file untouched.
- A 720p screen recording remains 720p; upscaling cannot restore fine slide detail. Evaluate native-resolution frames before altering color. An already correct branded slide should not receive a global talking-head color grade. Very light sharpening can be tested, not assumed necessary.

## Inspect and transcribe
- Probe streams, timestamps, FPS, color and duration; inspect a contact sheet plus native-resolution frames of speaker and slides. Measure integrated loudness, true peak and dynamic range.
- Check actual executable capability with `ffmpeg -h filter=whisper`. Hermes' bundled ffmpeg may lack Whisper even when the installed Gyan full build has it. On Windows, inspect `AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg_*/.../bin/ffmpeg.exe`; do not assume the first PATH binary matches an old workflow.
- Reuse an existing local Whisper model. Transcribe in short, independently timestamped chunks (e.g. exact 90-second windows, one window per inference queue). Read all chunks to identify retakes or off-script setup. Transcription is an editorial aid, not a promise of listening and not word-accurate cut boundaries.

## Conservative pause removal
- Calibrate the silence threshold against the actual low-level speech/noise distribution. A fixed -38 dBFS threshold can eat quiet speech on a -31 LUFS recording. A more conservative -44 dBFS peak threshold is a useful candidate for quiet, otherwise clean voice, not a universal constant.
- Prefer shortening pauses of roughly one second or longer, leaving 0.6–0.85 seconds total breathing room. Preserve extra time around slide changes. Do not strip every breath or shorten all 0.3-second hesitations.
- Remove only the middle of measured silence. Pad both sides before quantizing inward to video frames. Inspect any merged silence intervals: a short gap may contain a click, breath OR speech. RMS checks and transcript context are supporting evidence; do not treat ASR phrase spans as exact alignment.
- Trim idle tail only after the final spoken content plus a small hold. Keep natural opening speech intact.

## Sample-accurate implementation for constant-FPS sources
- Confirm both streams start at zero; otherwise resolve their true offset first.
- Define each removed range as integer frame interval [a,b). For 30fps and 48kHz, each frame corresponds to 1600 samples. Compute this relationship programmatically and verify sample rate/FPS suitability; do not assume it for VFR or fractional FPS.
- Video: `select='not(between(n,a,b-1)+...)',setpts=N/(30*TB)` and CFR output.
- Audio: process voice continuously on the original timeline first, then slice PCM at those exact frame-derived sample indices. Concatenate retained sections, applying tiny (~5ms) fade-out/fade-in at edits to prevent clicks, without overlapping samples or changing duration. Avoid audio `aselect` at arbitrary AAC-frame boundaries, which can accumulate sync drift.
- Bound the final output with an explicit `-t` computed from retained frames / FPS. In a multi-input video + loudnorm/AAC render, the final audio track can extend past its exact-length PCM input by a few hundredths of a second. Probe both output track durations rather than blaming loudnorm blindly. If the video is already valid, re-mux it with `-c:v copy` and the normalized PCM audio, re-encode only AAC and apply the exact bound; verify frame count and A/V durations again.
- Export the edit list and original-to-output timeline mapping to JSON/CSV for repeatable revision.

## Audio and QA
- Already quiet recordings do not need aggressive RNNoise. Start with highpass near 70Hz, light denoise, gentle low-level expansion, minimal EQ/compression; preserve quiet syllables. Set gating based on measured levels, not hard presets.
- Normalize the edited timeline with measured two-pass loudnorm, e.g. -16 LUFS and -1.5 dBTP. Measure the encoded AAC output too; the delivered file, not the intermediate, must pass loudness and peak checks.
- Test a short rendered clip before the full pass. Validate frame count equals summed retained frame lengths; audio/video start and end times should agree to within one frame. Decode the entire final file with the null muxer and require no errors. Inspect sampled frames including the end from the actual final file.
- Keep a local master in project out/. Deliver a clearly named edited copy in an Editados subfolder alongside the original, plus Downloads if following the umbrella delivery convention. Verify delivered copies via checksums and the required delivered-path decode check.
- Report concrete edits and measured duration, without implying that every breath was manually auditioned or that source resolution was recovered.
