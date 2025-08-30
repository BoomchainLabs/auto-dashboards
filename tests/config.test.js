/**
 * Tests for package.json configuration integrity.
 * Framework: Jest-style API (describe/it/expect). Compatible with Vitest.
 *
 * These tests focus on validating critical fields and structures relevant to the
 * labextension packaging, scripts, and dependencies.
 */

const fs = require('fs');
const path = require('path');

function readPackageJson() {
  const pkgPath = path.resolve(__dirname, '..', 'package.json');
  if (!fs.existsSync(pkgPath)) {
    throw new Error(`package.json not found at ${pkgPath}`);
  }
  const raw = fs.readFileSync(pkgPath, 'utf8');
  return JSON.parse(raw);
}

function isSemver(v) {
  // basic semver with optional pre-release/build
  return /^\d+\.\d+\.\d+(?:-[0-9A-Za-z-.]+)?(?:\+[0-9A-Za-z-.]+)?$/.test(v);
}

describe('package.json configuration', () => {
  let pkg;

  beforeAll(() => {
    pkg = readPackageJson();
  });

  describe('basic metadata', () => {
    it('has expected name', () => {
      expect(pkg.name).toBe('@orbrx/auto-dashboards');
    });

    it('has a valid semver version string', () => {
      expect(typeof pkg.version).toBe('string');
      expect(isSemver(pkg.version)).toBe(true);
    });

    it('has required descriptive fields', () => {
      expect(typeof pkg.description).toBe('string');
      expect(Array.isArray(pkg.keywords)).toBe(true);
      expect(pkg.keywords).toEqual(
        expect.arrayContaining(['jupyter', 'jupyterlab', 'jupyterlab-extension'])
      );
      expect(pkg.homepage).toBe('https://github.com/orbrx/auto-dashboards');
      expect(pkg.bugs && pkg.bugs.url).toBe('https://github.com/orbrx/auto-dashboards/issues');
      expect(pkg.license).toBe('Apache-2.0');
      expect(pkg.author && pkg.author.name).toBe('Orange Bricks');
    });
  });

  describe('entry points and distribution', () => {
    it('defines main/types/style fields properly', () => {
      expect(pkg.main).toBe('lib/index.js');
      expect(pkg.types).toBe('lib/index.d.ts');
      expect(pkg.style).toBe('style/index.css');
    });

    it('limits published files to lib and style bundles', () => {
      expect(Array.isArray(pkg.files)).toBe(true);
      expect(pkg.files).toEqual(
        expect.arrayContaining([
          'lib/**/*.{d.ts,eot,gif,html,jpg,js,js.map,json,png,svg,woff2,ttf}',
          'style/**/*.{css,js,eot,gif,html,jpg,json,png,svg,woff2,ttf}'
        ])
      );
    });

    it('declares sideEffects and styleModule for bundlers', () => {
      expect(pkg.sideEffects).toEqual(expect.arrayContaining(['style/*.css', 'style/index.js']));
      expect(pkg.styleModule).toBe('style/index.js');
    });

    it('is configured for public publishing', () => {
      expect(pkg.publishConfig && pkg.publishConfig.access).toBe('public');
    });
  });

  describe('repository and links', () => {
    it('has a proper repository object', () => {
      expect(pkg.repository && pkg.repository.type).toBe('git');
      expect(pkg.repository && pkg.repository.url).toBe('https://github.com/orbrx/auto-dashboards.git');
    });
  });

  describe('scripts', () => {
    const expectedScripts = [
      'build',
      'build:prod',
      'build:labextension',
      'build:labextension:dev',
      'build:lib',
      'clean',
      'clean:lib',
      'clean:lintcache',
      'clean:labextension',
      'clean:all',
      'eslint',
      'eslint:check',
      'install:extension',
      'lint',
      'lint:check',
      'prettier',
      'prettier:base',
      'prettier:check',
      'stylelint',
      'stylelint:check',
      'watch',
      'watch:src',
      'watch:labextension'
    ];

    it('includes all critical scripts', () => {
      expect(pkg.scripts).toBeTruthy();
      for (const key of expectedScripts) {
        expect(pkg.scripts[key]).toBeTruthy();
      }
    });

    it('has correct eslint:check command', () => {
      expect(pkg.scripts['eslint:check']).toBe('eslint . --cache --ext .ts,.tsx');
    });

    it('has correct prettier base globbing', () => {
      expect(pkg.scripts['prettier:base']).toBe(
        'prettier "**/*{.ts,.tsx,.js,.jsx,.css,.json,.md}"'
      );
    });

    it('defines watch scripts for src and labextension', () => {
      expect(pkg.scripts['watch:src']).toBe('tsc -w');
      expect(pkg.scripts['watch:labextension']).toBe('jupyter labextension watch .');
    });
  });

  describe('dependencies', () => {
    it('includes required JupyterLab/Lumino runtime deps with caret ranges', () => {
      const d = pkg.dependencies || {};
      const caret = (v) => typeof v === 'string' && v.startsWith('^');

      // Core JupyterLab packages
      [
        '@jupyterlab/application',
        '@jupyterlab/apputils',
        '@jupyterlab/coreutils',
        '@jupyterlab/docregistry',
        '@jupyterlab/filebrowser',
        '@jupyterlab/fileeditor',
        '@jupyterlab/services',
        '@jupyterlab/ui-components',
        '@lumino/algorithm',
        '@lumino/commands',
        '@lumino/disposable'
      ].forEach((dep) => {
        expect(d[dep]).toBeTruthy();
        expect(caret(d[dep])).toBe(true);
      });
    });
  });

  describe('devDependencies', () => {
    it('includes toolchain for building and linting', () => {
      const dd = pkg.devDependencies || {};
      // Spot-check a representative subset
      [
        '@jupyterlab/builder',
        '@types/node',
        '@typescript-eslint/eslint-plugin',
        '@typescript-eslint/parser',
        'eslint',
        'eslint-config-prettier',
        'eslint-plugin-prettier',
        'mkdirp',
        'npm-run-all',
        'prettier',
        'rimraf',
        'stylelint',
        'stylelint-config-prettier',
        'stylelint-config-recommended',
        'stylelint-config-standard',
        'stylelint-prettier',
        'typescript'
      ].forEach((dep) => {
        expect(dd[dep]).toBeTruthy();
      });
    });

    it('pins TypeScript using a tilde range for stability', () => {
      const v = pkg.devDependencies?.typescript;
      expect(typeof v).toBe('string');
      expect(v.startsWith('~')).toBe(true);
    });
  });

  describe('JupyterLab extension config', () => {
    it('marks package as a JupyterLab extension with correct outputDir', () => {
      expect(pkg.jupyterlab && pkg.jupyterlab.extension).toBe(true);
      expect(pkg.jupyterlab && pkg.jupyterlab.outputDir).toBe('auto_dashboards/labextension');
    });

    it('has discovery settings configured for pip manager and server base name', () => {
      const discovery = pkg.jupyterlab && pkg.jupyterlab.discovery;
      const managers = discovery && discovery.server && discovery.server.managers;
      const base = discovery && discovery.server && discovery.server.base;
      expect(Array.isArray(managers)).toBe(true);
      expect(managers).toEqual(expect.arrayContaining(['pip']));
      expect(base && base.name).toBe('auto_dashboards');
    });
  });

  describe('jupyter-releaser hooks', () => {
    it('defines before-build hooks to prep npm and python builds', () => {
      const hooks = pkg['jupyter-releaser'] && pkg['jupyter-releaser'].hooks;
      expect(hooks).toBeTruthy();
      expect(Array.isArray(hooks['before-build-npm'])).toBe(true);
      expect(hooks['before-build-npm']).toEqual(
        expect.arrayContaining([
          'python -m pip install jupyterlab~=4.1',
          'jlpm'
        ])
      );
      expect(Array.isArray(hooks['before-build-python'])).toBe(true);
      expect(hooks['before-build-python']).toEqual(
        expect.arrayContaining(['jlpm clean:all'])
      );
    });
  });

  describe('sanity checks and invariants', () => {
    it('does not duplicate packages across dependencies and devDependencies', () => {
      const d = Object.keys(pkg.dependencies || {});
      const dd = Object.keys(pkg.devDependencies || {});
      const overlap = d.filter((k) => dd.includes(k));
      expect(overlap).toEqual([]);
    });

    it('has no empty required fields', () => {
      ['name', 'version', 'license', 'main', 'types', 'style'].forEach((key) => {
        expect(pkg[key]).toBeTruthy();
        expect(typeof pkg[key]).toBe('string');
      });
    });
  });
});