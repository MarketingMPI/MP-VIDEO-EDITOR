---
name: voicestudio-local-tts
description: Use for local PT-BR TTS/ASR via VoiceStudio API.
---

# VoiceStudio — locução e transcrição local (PT-BR)

App Electron open-source (AGPL-3.0) instalado em `%LOCALAPPDATA%\Programs\VoiceStudio`.
Dados e modelos em `%LOCALAPPDATA%\OmniVoice`. Engine padrão: `omnivoice` (k2-fsa/OmniVoice).
Faz clonagem de voz, voice design, dublagem de vídeo, ditado, transcrição e audiolivros.

## Regra central: use a API, não a GUI

A janela Electron **rejeita clique automatizado** (`foreground_unavailable`, classe
`Chrome_WidgetWin_1`). Não insista no computer_use para acionar botões — o app expõe
uma API HTTP local compatível com OpenAI (276 endpoints). Use-a sempre.

O app precisa estar **aberto** (a API morre junto com a janela).

## Achar a porta

A porta varia por sessão (foi 3900 na primeira instalação). Descubra assim:

```powershell
Get-NetTCPConnection -State Listen | ForEach-Object {
  $p = Get-Process -Id $_.OwningProcess -ErrorAction SilentlyContinue
  if ($p -and $p.ProcessName -match 'python') { "$($_.LocalPort)" }
} | Sort-Object -Unique
```

Confirme qual é a certa: `GET /health` devolve `{"status":"ok","device":"cpu","version":"..."}`.
Cuidado: o próprio backend do Hermes também escuta em localhost — cheque o `/openapi.json`
(`info.title` deve ser `VoiceStudio API`).

## Gerar locução

`POST /v1/audio/speech` (formato OpenAI):

```python
import json, urllib.request
payload = json.dumps({"model":"omnivoice", "input": texto,
                      "voice":"alloy", "response_format":"wav"}).encode()
req = urllib.request.Request(f"http://127.0.0.1:{porta}/v1/audio/speech",
        data=payload, headers={"Content-Type":"application/json"})
wav = urllib.request.urlopen(req, timeout=900).read()
```

- Use `timeout=900`: em CPU é lento e o default estoura.
- Saída: WAV mono 24 kHz.
- Números por extenso saem corretos ("MP trezentos e sessenta" → "MP360" na volta).
- As vozes de `/v1/audio/voices` (alloy, ash, echo…) são **aliases OpenAI**, todas mapeiam
  para a voz padrão da engine. Voz própria exige clonagem via perfil (`/profiles/...`).

## Transcrever

`POST /v1/audio/transcriptions`, multipart com `file`, `model=whisper-1`, `language=pt`.
Monte o multipart na mão com stdlib — não há `requests` garantido no ambiente.

Valide TTS fechando o ciclo: gere o áudio, transcreva de volta e compare com o texto
de origem. É a verificação objetiva mais barata de que a pronúncia PT-BR saiu certa.

## Desempenho real (Intel Core Ultra 7 258V, sem NVIDIA, CPU-only)

| Operação | Medido |
|---|---|
| TTS, modelo frio | 7,8 s de áudio em 48,6 s (~6,2× tempo real) |
| TTS, modelo quente | 10,2 s de áudio em 36,6 s (~3,6× tempo real) |
| ASR (whisper) | 10,2 s de áudio em 31,3 s (~3,1× tempo real) |

Regra de bolso: **~4× a duração do áudio**. Um reel de 40 s leva ~2,5 min.
Avise antes de lotes grandes. A Arc 140V não acelera nada — PyTorch no Windows
só usa GPU NVIDIA/CUDA.

## Compliance (Meu Patrimônio)

- O app tem modo `auto` de espelho do Hugging Face que **cai para hf-mirror.com (China)**
  quando a sondagem do huggingface.co demora. Mantenha fixado no oficial:
  `PUT /api/settings/hf-mirror` com `{"url":"","mode":"manual"}` (url vazia = oficial).
  Confira com `GET /api/settings/hf-mirror`.
- AGPL-3.0 cobre o app, **não** os pesos dos modelos. Antes de usar áudio gerado em
  material público da MP, cheque a licença do modelo em `docs/licensing/model-inventory.md`.
- Clonagem de voz só com autorização expressa da pessoa.

## Instalação (se precisar refazer)

Baixe o `.exe` do release oficial, **confira o SHA-256** contra o `SHA256SUMS.txt` do
mesmo release, e rode com `/S` (NSIS silencioso, instala por usuário, sem admin).
O binário **não é assinado** (Authenticode `NotSigned`) — SmartScreen vai avisar.
Primeira execução baixa ~3,6 GB de PyTorch CPU; pacotes de áudio completos ocupam ~11 GB.
