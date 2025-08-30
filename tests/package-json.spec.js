'use strict';
/**
 * Unit tests for package.json
 * Framework: Node.js built-in test runner (node:test) + node:assert/strict
 * How to run: jlpm test (added "test": "node --test") or npm test
 * Focus: No <diff> provided; exercising critical schema and values comprehensively.
 */

const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('fs');
const path = require('path');

const pkgPath = path.resolve(__dirname, '..', 'package.json');
const pkg = JSON.parse(fs.readFileSync(pkgPath, 'utf8'));

function isSemverRange(v) {
  return typeof v === 'string' && /^[~^]?\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?$/.test(v);
}
function hasKeys(obj, keys) {
  return !!obj && typeof obj === 'object' && keys.every(k => Object.prototype.hasOwnProperty.call(obj, k));
}

test('package.json parses and has required top-level fields', () => {
  assert.ok(pkg && typeof pkg === 'object');
  assert.equal(pkg.name, '@orbrx/auto-dashboards');
  assert.match(pkg.version, /^\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?$/);
  assert.equal(pkg.license, 'Apache-2.0');

  assert.ok(pkg.author && typeof pkg.author.name === 'string' && pkg.author.name.length > 0);
  assert.ok(Array.isArray(pkg.keywords), 'keywords must be an array');
  for (const k of ['jupyter', 'jupyterlab', 'jupyterlab-extension']) {
    assert.ok(pkg.keywords.includes(k), `keywords should include ${k}`);
  }

  assert.equal(pkg.homepage, 'https://github.com/orbrx/auto-dashboards');
  assert.ok(pkg.bugs && typeof pkg.bugs.url === 'string' && pkg.bugs.url.includes('github.com/orbrx/auto-dashboards/issues'));
  assert.ok(pkg.repository && pkg.repository.type === 'git' && typeof pkg.repository.url === 'string');
});

test('entry points and distribution fields are correct', () => {
  assert.equal(pkg.main, 'lib/index.js');
  assert.equal(pkg.types, 'lib/index.d.ts');
  assert.equal(pkg.style, 'style/index.css');
  assert.equal(pkg.styleModule, 'style/index.js');

  assert.ok(Array.isArray(pkg.files), 'files must be an array');
  assert.ok(pkg.files.includes('lib/**/*.{d.ts,eot,gif,html,jpg,js,js.map,json,png,svg,woff2,ttf}'));
  assert.ok(pkg.files.includes('style/**/*.{css,js,eot,gif,html,jpg,json,png,svg,woff2,ttf}'));

  assert.ok(Array.isArray(pkg.sideEffects), 'sideEffects must be an array');
  assert.ok(pkg.sideEffects.includes('style/*.css'));
  assert.ok(pkg.sideEffects.includes('style/index.js'));

  assert.ok(pkg.publishConfig && pkg.publishConfig.access === 'public');
});

test('scripts include expected commands and test scripts', () => {
  const s = pkg.scripts || {};
  const expected = {
    build: 'jlpm build:lib && jlpm build:labextension:dev',
    'build:prod': 'jlpm clean && jlpm build:lib && jlpm build:labextension',
    'build:labextension': 'jupyter labextension build .',
    'build:labextension:dev': 'jupyter labextension build --development True .',
    'build:lib': 'tsc',
    clean: 'jlpm clean:lib',
    'clean:lib': 'rimraf lib tsconfig.tsbuildinfo',
    'clean:lintcache': 'rimraf .eslintcache .stylelintcache',
    'clean:labextension': 'rimraf auto_dashboards/labextension',
    'clean:all': 'jlpm clean:lib && jlpm clean:labextension && jlpm clean:lintcache',
    eslint: 'jlpm eslint:check --fix',
    'eslint:check': 'eslint . --cache --ext .ts,.tsx',
    'install:extension': 'jlpm build',
    lint: 'jlpm stylelint && jlpm prettier && jlpm eslint',
    'lint:check': 'jlpm stylelint:check && jlpm prettier:check && jlpm eslint:check',
    prettier: 'jlpm prettier:base --write --list-different',
    'prettier:base': 'prettier "**/*{.ts,.tsx,.js,.jsx,.css,.json,.md}"',
    'prettier:check': 'jlpm prettier:base --check',
    stylelint: 'jlpm stylelint:check --fix',
    'stylelint:check': 'stylelint --cache "style/**/*.css"',
    watch: 'run-p watch:src watch:labextension',
    'watch:src': 'tsc -w',
    'watch:labextension': 'jupyter labextension watch .'
  };

  for (const [k, v] of Object.entries(expected)) {
    assert.equal(s[k], v, `scripts.${k} should be "${v}"`);
  }

  // Newly added tests scripts
  assert.equal(s.test, 'node --test', 'scripts.test should be "node --test"');
  assert.equal(s['test:package'], 'node --test tests/package-json.spec.js', 'scripts.test:package should target this spec');
});

test('dependencies use valid semver ranges and include required keys', () => {
  const deps = pkg.dependencies || {};
  assert.ok(Object.keys(deps).length > 0, 'dependencies should not be empty');

  for (const [name, ver] of Object.entries(deps)) {
    assert.ok(isSemverRange(ver), `dependency ${name} has invalid semver range: ${ver}`);
  }

  const requiredDeps = {
    '@jupyterlab/application': '^4.2.0',
    '@jupyterlab/apputils': '^4.2.0',
    '@jupyterlab/coreutils': '^4.2.0',
    '@jupyterlab/docregistry': '^4.2.0',
    '@jupyterlab/filebrowser': '^4.2.0',
    '@jupyterlab/fileeditor': '^4.2.0',
    '@jupyterlab/services': '^7.4.5',
    '@jupyterlab/ui-components': '^4.2.0',
    '@lumino/algorithm': '^2.0.0',
    '@lumino/commands': '^2.0.0',
    '@lumino/disposable': '^2.0.0'
  };
  assert.ok(hasKeys(deps, Object.keys(requiredDeps)), 'missing one or more required dependencies');
  for (const [name, ver] of Object.entries(requiredDeps)) {
    assert.equal(deps[name], ver, `dependency ${name} should be ${ver}`);
  }
});

test('devDependencies use valid semver ranges and include critical tooling', () => {
  const devDeps = pkg.devDependencies || {};
  assert.ok(Object.keys(devDeps).length > 0, 'devDependencies should not be empty');

  for (const [name, ver] of Object.entries(devDeps)) {
    assert.ok(isSemverRange(ver), `devDependency ${name} has invalid semver range: ${ver}`);
  }

  const requiredDevDeps = {
    '@jupyterlab/builder': '^4.2.0',
    '@types/node': '^17.0.41',
    '@typescript-eslint/eslint-plugin': '^4.8.1',
    '@typescript-eslint/parser': '^4.8.1',
    eslint: '^7.14.0',
    'eslint-config-prettier': '^6.15.0',
    'eslint-plugin-prettier': '^3.1.4',
    mkdirp: '^1.0.3',
    'npm-run-all': '^4.1.5',
    prettier: '^2.1.1',
    rimraf: '^3.0.2',
    stylelint: '^14.3.0',
    'stylelint-config-prettier': '^9.0.3',
    'stylelint-config-recommended': '^6.0.0',
    'stylelint-config-standard': '~24.0.0',
    'stylelint-prettier': '^2.0.0',
    typescript: '~5.7.3'
  };
  assert.ok(hasKeys(devDeps, Object.keys(requiredDevDeps)), 'missing one or more required devDependencies');
  for (const [name, ver] of Object.entries(requiredDevDeps)) {
    assert.equal(devDeps[name], ver, `devDependency ${name} should be ${ver}`);
  }
});

test('JupyterLab extension configuration is valid', () => {
  assert.ok(pkg.jupyterlab && typeof pkg.jupyterlab === 'object');
  assert.strictEqual(pkg.jupyterlab.extension, true);
  assert.strictEqual(pkg.jupyterlab.outputDir, 'auto_dashboards/labextension');

  const discovery = pkg.jupyterlab.discovery;
  assert.ok(discovery && discovery.server && discovery.server.base);
  assert.ok(Array.isArray(discovery.server.managers));
  assert.ok(discovery.server.managers.includes('pip'));
  assert.strictEqual(discovery.server.base.name, 'auto_dashboards');
});

test('jupyter-releaser hooks contain expected commands', () => {
  const jr = pkg['jupyter-releaser'];
  assert.ok(jr && jr.hooks, 'jupyter-releaser hooks must exist');

  const beforeNpm = jr.hooks['before-build-npm'] || [];
  assert.ok(Array.isArray(beforeNpm));
  assert.ok(beforeNpm.includes('python -m pip install jupyterlab~=4.1'));
  assert.ok(beforeNpm.includes('jlpm'));

  const beforePy = jr.hooks['before-build-python'] || [];
  assert.ok(Array.isArray(beforePy));
  assert.ok(beforePy.includes('jlpm clean:all'));
});