# ferramentas/

Scripts reutilizáveis, um por etapa do processo. Quase todos têm caminhos e tempos fixos no topo
do arquivo (vieram de projetos reais): **copie para o projeto novo e ajuste o topo**.

| Pasta | Arquivo | O que faz |
|---|---|---|
| `cortes/` | `build_cut.py` | lê o `silencedetect` e monta a expressão que tira o meio das pausas (folga 0,12 s) |
| | `build_cuts_lote.py` | mesma ideia para vários vídeos de uma vez |
| `legendas/` | `srt_to_ass.py` | SRT do Whisper → ASS Campton branco, blocos de 2–3 palavras |
| | `make_ass_uniforme.py` + `ass_header.txt` | SRT → ASS de depoimento (branco uniforme, fade) |
| | `make_ass_blocos_live.py` | ASS para cortes de live (inclui tabela de correções) |
| | `juntar_srt_multiclipe.py` | junta SRTs de vários clipes na linha do tempo da montagem |
| `graficos/` | `make_ig_sticker.py`, `make_sticker.py` | headline estilo texto de Stories do Instagram |
| | `make_vinheta_mppro.py` | vinheta final MP PRO (degradê preto + logo + botão dourado) |
| | `make_pipmask.py` | máscara arredondada para câmera picture-in-picture |
| | `make_logo_sombra.py` | logo com sombra para sobrepor ao vídeo |
| `trilha/` | `make_piano_classico.py`, `make_piano_classico_v2.py` | trilha de piano gerada em código (sem direitos autorais) |
| | `make_sfx.py` | efeitos de transição (desligados por padrão) |
| `audio/` | `tratar_voz_e_trilha.sh` | RNNoise + EQ + compressor + −14 LUFS + piano com ducking |
| | `medir_audio.py`, `fix_audio.py` | medir volume/pico e corrigir |
| `montagem/` | `make_segments.sh`, `make_montagem.sh` | segmentos com Ken Burns + junção com xfade |
| | `zoom_punchin.py` | curva de zoom dinâmico (soma de gaussianas) |
| `render/` | `render_final_ads.sh` / `.py` | render final de anúncio: corte + hflip + sticker + legenda, CRF 14 |
| | `render_depoimento.sh` | render de depoimento: HDR→SDR, zoom, legenda, logo, trilha |
| `transcricao/` | `transcribe.py` | transcrição com Whisper |
| `aula-onboarding/` | `analyze.py` … `validate.py` | edição limpa de aula: detecta pausas, planeja cortes por frame, renderiza e valida |
| — | `baixar-modelos.sh` | baixa Whisper + RNNoise |
