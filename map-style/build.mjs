// Gera dist/style-light.json, dist/style-dark.json e dist/manifest.json a
// partir do @protomaps/basemaps e de src/manifest.json. As fontes e os sprites
// de dist/ não são gerados: são cópias do protomaps/basemaps-assets, no commit
// de src/manifest.json, conferidas pelo teste.
//
// Uso: node build.mjs (grava dist/). build() é puro.
import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import { layers, namedFlavor } from "@protomaps/basemaps";

const root = dirname(fileURLToPath(import.meta.url));

export const serialize = (value) => JSON.stringify(value, null, 2) + "\n";

export function loadManifest() {
  return JSON.parse(readFileSync(join(root, "src", "manifest.json"), "utf8"));
}

function style(theme, manifest) {
  const [pmtiles, glyphs, sprite] = manifest.placeholders;
  return {
    version: 8,
    sources: { protomaps: { type: "vector", url: pmtiles, attribution: "© OpenStreetMap" } },
    glyphs: `${glyphs}/{fontstack}/{range}.pbf`,
    sprite: `${sprite}/${theme}`,
    layers: layers("protomaps", namedFlavor(theme), { lang: manifest.lang }),
  };
}

export function build() {
  const manifest = loadManifest();
  const out = {};
  for (const theme of manifest.themes) out[`style-${theme}.json`] = style(theme, manifest);
  out["manifest.json"] = manifest;
  return out;
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  mkdirSync(join(root, "dist"), { recursive: true });
  for (const [file, value] of Object.entries(build())) writeFileSync(join(root, "dist", file), serialize(value));
}
