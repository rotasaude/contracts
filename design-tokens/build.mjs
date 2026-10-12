#!/usr/bin/env node
// Gerador dos tokens: lê src/ (base, roles, themes) e emite dist/tokens.css e
// dist/tokens.ts. Sem dependências. build() é puro; só o CLI grava arquivos.
import { readFileSync, readdirSync, writeFileSync, mkdirSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const root = dirname(fileURLToPath(import.meta.url));
const read = (p) => JSON.parse(readFileSync(join(root, p), "utf8"));
const HEADER = "Gerado por design-tokens/build.mjs a partir de src/. Não edite.";
export const DEFAULT_THEME = "govbr";

export const loadBase = () => read("src/base.json");
export const loadRoles = () => read("src/roles.json");
export function loadThemes() {
  return readdirSync(join(root, "src/themes"))
    .filter((f) => f.endsWith(".json"))
    .sort()
    .map((f) => read(`src/themes/${f}`));
}

export function resolveThemes() {
  const base = loadBase();
  const { colors } = loadRoles();
  const out = {};
  for (const theme of loadThemes()) {
    out[theme.name] = {};
    for (const role of colors) {
      const key = theme.colors[role];
      if (key === undefined) throw new Error(`${theme.name}: papel ${role} sem valor`);
      const hex = base.colors[key];
      if (hex === undefined) throw new Error(`${theme.name}.${role}: ${key} não existe na base`);
      out[theme.name][role] = hex.toLowerCase();
    }
  }
  return out;
}

function themeBlock(theme, resolved, fonts) {
  const lines = Object.entries(resolved).map(([role, hex]) => `  --${role}: ${hex};`);
  for (const [prop, key] of Object.entries(theme.fonts)) {
    if (fonts[key] === undefined) throw new Error(`${theme.name}.${prop}: fonte ${key} não existe na base`);
    lines.push(`  --${prop}: ${fonts[key]};`);
  }
  return lines.join("\n");
}

export function build() {
  const base = loadBase();
  const roles = loadRoles();
  const themes = loadThemes();
  const resolved = resolveThemes();

  const faces = roles.fontFaces.map((f) =>
    `@font-face {\n  font-family: "${f.family}";\n  src: url("./fonts/${f.file}") format("woff2");\n` +
    `  font-weight: ${f.weight};\n  font-style: normal;\n  font-display: swap;\n}`
  );

  const shared = [
    ...Object.entries(roles.constants).map(([k, v]) => `  --${k}: ${v};`),
    ...Object.entries(roles.aliases).map(([k, v]) => `  --${k}: var(--${v});`)
  ].join("\n");

  const ordered = [
    ...themes.filter((t) => t.name === DEFAULT_THEME),
    ...themes.filter((t) => t.name !== DEFAULT_THEME)
  ];
  const blocks = ordered.map((t) => {
    const selector = t.name === DEFAULT_THEME
      ? `:root:not([data-theme]),\n:root[data-theme="${t.name}"]`
      : `:root[data-theme="${t.name}"]`;
    return `${selector} {\n${themeBlock(t, resolved[t.name], base.fonts)}\n}`;
  });

  const css = [`/* ${HEADER} */`, ...faces, `:root {\n${shared}\n}`, ...blocks].join("\n\n") + "\n";

  const names = themes.map((t) => t.name).sort();
  const ts = [
    `// ${HEADER}`,
    `export const THEMES = ${JSON.stringify(names)} as const;`,
    `export type ThemeName = (typeof THEMES)[number];`,
    `export const DEFAULT_THEME: ThemeName = "${DEFAULT_THEME}";`,
    `export const COLOR_ROLES = ${JSON.stringify(roles.colors)} as const;`,
    `export type ColorRole = (typeof COLOR_ROLES)[number];`,
    ""
  ].join("\n");

  return { css, ts };
}

if (process.argv[1] && fileURLToPath(import.meta.url) === process.argv[1]) {
  const { css, ts } = build();
  mkdirSync(join(root, "dist"), { recursive: true });
  writeFileSync(join(root, "dist/tokens.css"), css);
  writeFileSync(join(root, "dist/tokens.ts"), ts);
  console.log("dist/tokens.css e dist/tokens.ts gerados");
}
