// Gerador: todo tema define todos os papéis com nomes que existem na base, e o
// dist/ versionado é exatamente a saída do gerador (ninguém edita o dist à mão).
import { test } from "node:test";
import assert from "node:assert/strict";
import { existsSync, readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import { build, loadRoles, loadThemes, resolveThemes } from "../build.mjs";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");

test("todo tema define exatamente os papéis de roles.json", () => {
  const { colors } = loadRoles();
  for (const theme of loadThemes()) {
    assert.deepEqual(Object.keys(theme.colors).sort(), [...colors].sort(), theme.name);
  }
});

test("todo valor de tema existe na paleta e vira #rrggbb", () => {
  for (const [name, roles] of Object.entries(resolveThemes())) {
    for (const [role, hex] of Object.entries(roles)) {
      assert.match(hex, /^#[0-9a-f]{6}$/, `${name}.${role}`);
    }
  }
});

test("os quatro temas existem e o govbr é o padrão do CSS", () => {
  assert.deepEqual(loadThemes().map(t => t.name).sort(), ["alto-contraste", "govbr", "govbr-escuro", "rota"]);
  const { css } = build();
  assert.match(css, /:root:not\(\[data-theme\]\),\n:root\[data-theme="govbr"\] \{/);
});

test("apelidos apontam para papéis e saem como var()", () => {
  const { css } = build();
  assert.match(css, /--line: var\(--rule2\);/);
  assert.match(css, /--danger: var\(--down\);/);
  assert.match(css, /--surface: var\(--sunken\);/);
});

test("dist/ versionado é igual à saída do gerador", () => {
  const { css, ts } = build();
  assert.equal(readFileSync(join(root, "dist/tokens.css"), "utf8"), css);
  assert.equal(readFileSync(join(root, "dist/tokens.ts"), "utf8"), ts);
});

test("cada @font-face aponta para um arquivo que existe em dist/fonts", () => {
  const { fontFaces } = loadRoles();
  assert.ok(fontFaces.length >= 3, "faces da fonte do govbr declaradas");
  for (const f of fontFaces) {
    assert.ok(existsSync(join(root, "dist/fonts", f.file)), f.file);
  }
  assert.ok(existsSync(join(root, "dist/fonts/OFL.txt")), "licença junto da fonte");
});
