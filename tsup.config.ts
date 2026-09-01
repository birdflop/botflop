import { defineConfig } from 'tsup';

export default defineConfig({
  entry: ['src/index.ts'],
  format: ['esm'],
  target: 'node22',
  outDir: '.',
  clean: false,
  bundle: true,
  sourcemap: true,
});
