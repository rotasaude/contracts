// O estilo versionado em dist/ é exatamente a saída do gerador, não chama
// nenhum serviço de terceiros e só pede fontes e sprites que estão na cópia.
import { test } from "node:test";
import assert from "node:assert/strict";
import { lstatSync, readFileSync, readdirSync, statSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join, relative } from "node:path";
import { build, serialize } from "../build.mjs";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const dist = join(root, "dist");
const THEMES = ["light", "dark"];
const readText = (file) => readFileSync(join(dist, file), "utf8");
const readJson = (file) => JSON.parse(readText(file));
const styles = () => THEMES.map((theme) => [theme, readJson(`style-${theme}.json`)]);
// Toda faixa de 256 pontos de código de 0 a 65535: uma faixa sem arquivo faz o
// MapLibre Native desistir do mapa inteiro (medido no app; Q61).
const RANGES = Array.from({ length: 256 }, (_, i) => `${i * 256}-${i * 256 + 255}`);

// As pilhas de fonte de uma camada: text-font pode ser a lista de pilhas ou
// uma expressão, e text-field pode trazer {"text-font": expressão} dentro de
// um format. Em expressão, a pilha vem em ["literal", [pilhas]].
function literalStacks(expression, out) {
  if (Array.isArray(expression)) {
    if (expression[0] === "literal" && Array.isArray(expression[1])) expression[1].forEach((stack) => out.add(stack));
    else expression.forEach((item) => literalStacks(item, out));
  } else if (expression && typeof expression === "object") {
    Object.values(expression).forEach((item) => literalStacks(item, out));
  }
}

function fontStacks(layer, out) {
  const font = layer.layout?.["text-font"];
  if (Array.isArray(font) && font.every((item) => typeof item === "string")) font.forEach((stack) => out.add(stack));
  else literalStacks(font, out);
  literalStacks(layer.layout?.["text-field"], out);
}

function walk(dir) {
  return readdirSync(dir).flatMap((name) => {
    const path = join(dir, name);
    return statSync(path).isDirectory() ? walk(path) : [relative(dist, path)];
  });
}

test("nenhuma URL http(s) nos dois estilos", () => {
  for (const [theme, style] of styles()) {
    assert.doesNotMatch(JSON.stringify(style), /https?:\/\//, theme);
  }
});

test("os três marcadores, a fonte protomaps e a atribuição", () => {
  for (const [theme, style] of styles()) {
    assert.equal(style.version, 8, theme);
    assert.deepEqual(style.sources, {
      protomaps: { type: "vector", url: "__PMTILES__", attribution: "© OpenStreetMap" },
    }, theme);
    assert.equal(style.glyphs, "__GLYPHS__/{fontstack}/{range}.pbf", theme);
    assert.equal(style.sprite, `__SPRITE__/${theme}`, theme);
  }
  assert.deepEqual(readJson("manifest.json").placeholders, ["__PMTILES__", "__GLYPHS__", "__SPRITE__"]);
});

test("rótulos em português: toda camada que mostra um nome usa name:pt", () => {
  for (const [theme, style] of styles()) {
    const named = style.layers.filter((layer) => JSON.stringify(layer.layout?.["text-field"] ?? "").includes('"name'));
    assert.ok(named.length >= 10, `${theme}: poucas camadas de nome (${named.length})`);
    for (const layer of named) {
      assert.match(JSON.stringify(layer.layout["text-field"]), /"name:pt"/, `${theme}.${layer.id}`);
    }
  }
});

test("toda pilha pedida pelas camadas está no manifesto, com as 256 faixas em arquivo", () => {
  const { fonts, glyph_ranges: glyphRanges } = readJson("manifest.json");
  assert.equal(glyphRanges, RANGES.length);
  for (const [theme, style] of styles()) {
    const used = new Set();
    for (const layer of style.layers) fontStacks(layer, used);
    assert.deepEqual([...used].sort(), [...fonts].sort(), theme);
  }
  for (const stack of fonts) {
    for (const range of RANGES) {
      const file = join(dist, "fonts", stack, `${range}.pbf`);
      const stat = lstatSync(file, { throwIfNoEntry: false });
      assert.ok(stat?.isFile() && stat.size > 0, `${stack}/${range}.pbf ausente, vazio ou atalho`);
    }
  }
});

test("sprites completos, licença das fontes e nenhum arquivo fora do manifesto", () => {
  const manifest = readJson("manifest.json");
  const expected = new Set(["manifest.json", "fonts/OFL.txt"]);
  for (const theme of manifest.themes) expected.add(`style-${theme}.json`);
  for (const sprite of manifest.sprites) {
    for (const suffix of [".json", ".png", "@2x.json", "@2x.png"]) expected.add(`sprites/${sprite}${suffix}`);
  }
  for (const stack of manifest.fonts) {
    for (const range of RANGES) expected.add(`fonts/${stack}/${range}.pbf`);
  }
  assert.deepEqual(walk(dist).sort(), [...expected].sort());
  assert.deepEqual(manifest.themes, THEMES);
  assert.deepEqual(manifest.sprites, THEMES);
});

test("o manifesto fixa a versão instalada do @protomaps/basemaps e o commit dos assets", () => {
  const manifest = readJson("manifest.json");
  const pkg = JSON.parse(readFileSync(join(root, "package.json"), "utf8"));
  assert.equal(manifest.basemaps, pkg.dependencies["@protomaps/basemaps"]);
  assert.match(manifest.assets, /^[0-9a-f]{40}$/);
  assert.equal(manifest.lang, "pt");
});

test("build() reproduz dist/style-*.json e dist/manifest.json byte a byte", () => {
  const out = build();
  assert.deepEqual(Object.keys(out).sort(), ["manifest.json", "style-dark.json", "style-light.json"]);
  for (const [file, value] of Object.entries(out)) {
    assert.equal(readText(file), serialize(value), file);
  }
});
