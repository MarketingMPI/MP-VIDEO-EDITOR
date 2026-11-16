# Vertical social-ad batch (talking-head Reels ads)

Validated on a batch of 11 MP PRO "Ads Live" clips (720x1280 30fps SDR H.264,
front-camera selfie footage). The ask was: cut breaths / make it dynamic, burn
subtitles, and add a headline that "looks like a normal Instagram post, not an
ad." This is the reusable pipeline for that class.

## Per-clip pipeline (order that works)
1. **Probe** — confirm resolution/fps/color. These were already vertical SDR, so
   NO tonemap/color chain needed (skip the HDR machinery for phone-in-app exports).
2. **Detect breaths:** `ffmpeg -i asr.wav -af "silencedetect=noise=-30dB:d=0.35" -f null -`.
3. **Build a keep-expression** removing the MIDDLE of each silence, leaving ~0.12s
   pad on each side so it doesn't sound robotic. Also trim a leading dead-air gap
   (silence starting at t=0) down to a tiny lead-in. Typical yield: 5-10% shorter.
   ```
   KEEP="not(between(t\,A1\,B1)+between(t\,A2\,B2)+...)"
   [0:v]select='$KEEP',setpts=N/FRAME_RATE/TB[v];[0:a]aselect='$KEEP',asetpts=N/SR/TB[a]
   ```
   (Escape the commas as `\,` inside a bash-passed filter string.)
4. **Cut once to an intermediate** (crf 18, pcm audio) ONLY to re-transcribe from —
   the final render still goes straight from the original (step 8).
5. **Transcribe the CUT clip**, not the original — subtitle timing must match the
   post-cut timeline. Re-run whisper on the trimmed audio.
6. **Fix whisper errors before burning.** Real hits this batch: "machismo" -> the
   speaker said "achismo" (vendendo no achismo); "MPPRO" -> "MP PRO". Proper nouns
   and brand terms need a hand pass. Confirm ambiguous names with the user.
7. **Headline sticker** — see below.
8. **Final render straight from the ORIGINAL** in ONE encode (cut + hflip + sticker
   overlay + subtitles + audio), CRF 14 / preset veryslow / AAC 256k, so there's no
   generational loss from the intermediate. Verify integrity with the null muxer.

## hflip: front-camera footage is MIRRORED
Selfie/in-app recordings come mirrored: any on-body logo or wall text reads
backwards ("oinomirtaP"). ALWAYS add `hflip` to the video chain and verify against
the shirt logo / background text via a vision frame. Apply it to EVERY clip in a
selfie batch by default; note it once and stop re-checking whether it's needed.

## Instagram "sticker" headline (looks organic, not an ad)
The convincing "normal post" look is the Stories **text sticker**: white (or dark)
rounded boxes, one per line, in an Instagram-Sans-like face. **Segoe UI Bold**
(`C:/Windows/Fonts/segoeuib.ttf`) is a close stand-in on Windows. Generate a PNG
with Pillow (supersample x3 for clean rounded corners), one `rounded_rectangle`
per line + text, transparent margins:
- White block: fill `(255,255,255)`, text `(15,15,15)`.
- Dark block:  fill `(24,24,24)`,   text `(255,255,255)`.
- MP green:    fill `(0,80,60)` = #00503c, text white (reads as brand, still sticker-like).
Overlay top-third, ~0.82-0.86 of width, and **fade it out at the end of the spoken
hook** (`enable='between(t,0,HOOK_END)'` + an alpha `fade=t=out`), so it behaves
like a caption the poster typed, then disappears. Base the text on the actual
opening hook of the speech, not the file name.

### Per-clip Y position — validate on a real frame
Face height varies between takes. Composite the sticker onto an actual (hflipped)
frame and check via vision that it clears the hair/forehead BEFORE rendering.
Values that worked ranged y=H*0.015 (tight framing, face high) to H*0.06 (roomy).
Don't hardcode one offset across a batch.

### Alternate the block colour across versions (user preference)
When a COPY has several versions (VS01..VSNN), rotate the block colour
white -> black -> green so a stack of near-identical takes doesn't look copy-pasted.
The user explicitly asked for this ("se não fica tudo igual").

## Subtitles
Reuse the brand ASS style from `ffmpeg-recipes.md` §5 but PlayRes 720x1280 and
Fontsize ~44 for this resolution: uniform white Campton, subtle outline+shadow,
2-3 words per block, `{\fad(90,90)}`. No colour highlights, no italics.

## Delivery
Copy each finished clip to the user's Downloads with a `<COPY>_<VS>_editado.mp4`
name; null-muxer-check the delivered path.
