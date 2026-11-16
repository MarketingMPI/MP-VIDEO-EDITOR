const sharp = require('sharp');
const fs = require('fs');

const SRC = "C:/Users/phenr/OneDrive/Imagens/Logos MP/Logo MP PRO SVG.svg";
const OUT = "C:/Users/phenr/mp-live-maisretorno/out/logo_mppro.png";

const svg = fs.readFileSync(SRC);
// render at high density for a crisp 6x raster (554x115 -> ~3324x690)
sharp(svg, { density: 900 })
  .resize({ width: 3324 })
  .png()
  .toFile(OUT)
  .then(info => console.log("saved", OUT, info.width + "x" + info.height))
  .catch(err => { console.error(err); process.exit(1); });
