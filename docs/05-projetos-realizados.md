# 05 · Projetos já realizados

Os scripts reais de cada projeto estão em [`exemplos/`](../exemplos/) (só código; vídeos, áudios,
legendas e frames ficam na máquina, nas pastas originais em `C:\Users\phenr\`).

| Pasta | O que foi | Técnicas que vale copiar |
|---|---|---|
| `mp-video-cliente01` | Depoimento de cliente, evento MFO (iPhone 4K HDR) | HDR→SDR, punch-ins com zoompan, RNNoise, piano com ducking, concat de segmentos |
| `mp-video-cliente02` | Segundo depoimento do mesmo evento | reaproveitamento do pipeline do 01 |
| `mp-video-herdeira` | Várias respostas da mesma pessoa viraram um depoimento contínuo | `make_srt.py` junta SRTs na linha do tempo da montagem com crossfade |
| `mp-video-eventos` | Montagem institucional de evento | xfade com offset acumulado, trilha, SFX (depois removidos a pedido) |
| `mp-video-jpmorgan` | Montagem de evento MFO | segmentos com Ken Burns, correção de luz quente |
| `mp-video-salume` | Montagem de evento MFO | Ken Burns parametrizado, piano clássico v2 |
| `mp-video-ogat` | Clipe único já editado: só cor + música | grade + trilha, entrega 4K e 1080 |
| `mp-ads-maisretorno` | 11 anúncios (5 copys) da live Mais Retorno | corte de respiros, sticker IG, legenda, hflip |
| `mp-ads-xpinc` | Anúncios da live com XP Inc | scripts de preparo/render por versão, medição de áudio |
| `mp-ads-polo-capital` | Anúncios da live com Polo Capital | correção de nomes próprios na legenda (Marabraz, Tok&Stok) |
| `mp-live-maisretorno` | Cortes A–K da live "Diagnóstico com IA" + cortes de Crédito Privado | relatório como destaque, PiP arredondado, câmeras empilhadas, vinheta MP PRO |
| `mp-onboarding-mariana` | Aula de onboarding MP PRO (horizontal, limpa) | corte conservador de pausas por frame, limpeza leve de voz, validação |

Os caminhos dentro desses scripts apontam para as pastas originais desta máquina. Para reutilizar,
copie o script para o projeto novo e troque os caminhos e tempos no topo do arquivo.
