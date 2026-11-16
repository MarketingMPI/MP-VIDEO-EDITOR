# 04 · Conferência e entrega

Nada é entregue sem passar por todos os itens.

## Checklist técnico

```sh
OUT="C:/caminho/out/video_final.mp4"
# 1. Integridade: precisa sair vazio (0 erros)
ffmpeg -v error -i "$OUT" -f null -
# 2. Volume final: alvo -14 LUFS, pico <= -1 dBTP
ffmpeg -i "$OUT" -af loudnorm=print_format=summary -f null - 2>&1 | grep -E "Input (Integrated|True Peak)"
# 3. Formato
ffprobe -v error -show_entries stream=codec_name,width,height,r_frame_rate,sample_rate -of compact "$OUT"
# 4. Duração
ffprobe -v error -show_entries format=duration -of default=nk=1:nw=1 "$OUT"
```

## Checklist visual (frames extraídos do vídeo final)

- [ ] Cor natural (pele sem laranja/verde, branco lê branco)
- [ ] Rosto centralizado, cabeça inteira, sem espaço sobrando em cima
- [ ] Logo da camisa lendo certo (não espelhado)
- [ ] Legenda: fonte Campton (não Arial/serifada), sem vírgula grudada no início, sem erro de palavra
- [ ] Sticker não cobre rosto nem cabelo
- [ ] Vinheta entra com crossfade, sem corte seco
- [ ] Nenhum nome próprio errado

## Checklist de áudio

- [ ] Voz limpa, sem chiado
- [ ] Trilha baixa, nunca some no meio, não "bombeia" na abertura
- [ ] Sem efeitos sonoros nem ambiente (a não ser que pedidos)
- [ ] Boca em sincronia com a fala do começo ao fim

## Entrega

1. Master em `out/<nome>_final.mp4` dentro do projeto.
2. Cópia em `C:\Users\phenr\Downloads` (anúncios: `COPY0N_VS0M_editado.mp4`).
3. Rodar o teste de integridade **no arquivo copiado**.
4. Se o usuário voltar depois: conferir se os arquivos ainda estão em Downloads (OneDrive já
   sumiu com entregas) e recopiar do `out/` se preciso.
