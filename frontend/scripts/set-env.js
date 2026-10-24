const fs = require('fs');
const path = require('path');

const envFile = path.join(__dirname, '..', '.env');
const vars = { ...process.env };
if (fs.existsSync(envFile)) {
  for (const line of fs.readFileSync(envFile, 'utf8').split('\n')) {
    const m = line.match(/^\s*([A-Z0-9_]+)\s*=\s*(.*)\s*$/);
    if (m) vars[m[1]] = m[2].replace(/^["']|["']$/g, '');
  }
}
const apiUrl = (vars.REACT_APP_BACKEND_URL || '').replace(/\/$/, '');
const outDir = path.join(__dirname, '..', 'src', 'environments');
fs.mkdirSync(outDir, { recursive: true });
fs.writeFileSync(
  path.join(outDir, 'environment.ts'),
  `export const environment = { apiUrl: '${apiUrl}' };\n`
);
