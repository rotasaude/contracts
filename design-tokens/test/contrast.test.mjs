// Mínimos de contraste WCAG 2.2 por tema. Texto 4,5:1 e borda/foco 3:1; no
// alto-contraste (minContrast 7) todo par sobe para 7:1. --ink4 fica fora:
// só aparece em texto desabilitado ou decorativo.
import { test } from "node:test";
import assert from "node:assert/strict";
import { loadRoles, loadThemes, resolveThemes } from "../build.mjs";

function luminance(hex) {
  const c = [1, 3, 5].map((i) => parseInt(hex.slice(i, i + 2), 16) / 255)
    .map((v) => (v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4));
  return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2];
}

export function contrastRatio(a, b) {
  const [x, y] = [luminance(a), luminance(b)];
  return (Math.max(x, y) + 0.05) / (Math.min(x, y) + 0.05);
}

test("contrastRatio confere com valores conhecidos", () => {
  assert.equal(Math.round(contrastRatio("#000000", "#ffffff") * 100) / 100, 21);
  assert.equal(Math.round(contrastRatio("#767676", "#ffffff") * 100) / 100, 4.54);
});

const { pairs } = loadRoles();
const resolved = resolveThemes();

for (const theme of loadThemes()) {
  const textMin = theme.minContrast ?? 4.5;
  const nonTextMin = theme.minContrast ?? 3;
  const roles = resolved[theme.name];

  test(`${theme.name}: texto atinge ${textMin}:1`, () => {
    for (const [fg, bg] of pairs.text) {
      const r = contrastRatio(roles[fg], roles[bg]);
      assert.ok(r >= textMin, `${fg} sobre ${bg} = ${r.toFixed(2)}:1`);
    }
  });

  test(`${theme.name}: borda e foco atingem ${nonTextMin}:1`, () => {
    for (const [fg, bg] of pairs.nonText) {
      const r = contrastRatio(roles[fg], roles[bg]);
      assert.ok(r >= nonTextMin, `${fg} contra ${bg} = ${r.toFixed(2)}:1`);
    }
  });
}
