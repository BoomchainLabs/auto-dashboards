/**
 * Framework: Jest
 * Purpose: Validate jest.config.js shape and sensible values.
 * If the file is absent, tests are skipped.
 */

/* eslint-disable no-undef */
const fs = require('fs');
const path = require('path');

const configPath = path.resolve(process.cwd(), 'jest.config.js');
const hasConfig = fs.existsSync(configPath);
const D = hasConfig ? describe : describe.skip;

async function loadJestConfigIfPresent() {
  if (!hasConfig) return null;
  try {
    // Try CommonJS
    // eslint-disable-next-line global-require, import/no-dynamic-require
    const cjs = require(configPath);
    return cjs && cjs.default ? cjs.default : cjs;
  } catch (e) {
    // Fallback to ESM dynamic import
    const { pathToFileURL } = require('url');
    const esm = await import(pathToFileURL(configPath).href);
    return esm && esm.default ? esm.default : esm;
  }
}

function isPlainObject(o) {
  return o !== null && typeof o === 'object' && Object.getPrototypeOf(o) === Object.prototype;
}

D('jest.config.js', () => {
  let cfg;

  beforeAll(async () => {
    cfg = await loadJestConfigIfPresent();
  });

  test('exports a configuration object or function', () => {
    expect(cfg).toBeTruthy();
    if (typeof cfg === 'function') {
      const result = cfg();
      expect(isPlainObject(result)).toBe(true);
      cfg = result;
    } else {
      expect(isPlainObject(cfg)).toBe(true);
    }
  });

  test('testEnvironment is valid (node or jsdom) when specified', () => {
    if ('testEnvironment' in cfg) {
      expect(typeof cfg.testEnvironment).toBe('string');
      expect(['node', 'jsdom']).toContain(cfg.testEnvironment);
    }
  });

  test('locates tests via testMatch or testRegex when provided', () => {
    if ('testMatch' in cfg) {
      expect(Array.isArray(cfg.testMatch)).toBe(true);
      expect(cfg.testMatch.length).toBeGreaterThan(0);
      cfg.testMatch.forEach((p) => expect(typeof p).toBe('string'));
    } else if ('testRegex' in cfg) {
      if (Array.isArray(cfg.testRegex)) {
        expect(cfg.testRegex.length).toBeGreaterThan(0);
        cfg.testRegex.forEach((r) => expect(typeof r).toBe('string'));
      } else {
        expect(typeof cfg.testRegex).toBe('string');
      }
    }
  });

  test('transform (if present) uses known transformers or functions', () => {
    if ('transform' in cfg) {
      expect(isPlainObject(cfg.transform)).toBe(true);
      const allowed = ['babel-jest', 'ts-jest', '@swc/jest'];
      for (const [pattern, transformer] of Object.entries(cfg.transform)) {
        expect(typeof pattern).toBe('string');
        if (typeof transformer === 'string') {
          expect(allowed.some((pkg) => transformer.includes(pkg))).toBe(true);
        } else if (Array.isArray(transformer)) {
          expect(transformer.length).toBeGreaterThan(0);
          const tf = transformer[0];
          if (typeof tf === 'string') {
            expect(allowed.some((pkg) => tf.includes(pkg))).toBe(true);
          } else {
            expect(tf).toBeTruthy();
          }
        } else {
          // function/class transformer
          expect(transformer).toBeTruthy();
        }
      }
    }
  });

  test('moduleNameMapper (if present) maps strings to strings or arrays', () => {
    if ('moduleNameMapper' in cfg) {
      expect(isPlainObject(cfg.moduleNameMapper)).toBe(true);
      for (const [key, val] of Object.entries(cfg.moduleNameMapper)) {
        expect(typeof key).toBe('string');
        expect(['string', 'object'].includes(typeof val) || Array.isArray(val)).toBe(true);
      }
    }
  });

  test('setupFiles / setupFilesAfterEnv (if present) are arrays of strings', () => {
    ['setupFiles', 'setupFilesAfterEnv'].forEach((k) => {
      if (k in cfg) {
        expect(Array.isArray(cfg[k])).toBe(true);
        cfg[k].forEach((v) => expect(typeof v).toBe('string'));
      }
    });
  });

  test('coverage options (if present) have valid types and ranges', () => {
    if ('collectCoverage' in cfg) {
      expect(typeof cfg.collectCoverage).toBe('boolean');
    }
    if ('collectCoverageFrom' in cfg) {
      expect(Array.isArray(cfg.collectCoverageFrom)).toBe(true);
      cfg.collectCoverageFrom.forEach((v) => expect(typeof v).toBe('string'));
    }
    if ('coverageDirectory' in cfg) {
      expect(typeof cfg.coverageDirectory).toBe('string');
      expect(cfg.coverageDirectory.length).toBeGreaterThan(0);
    }
    if ('coverageReporters' in cfg) {
      expect(Array.isArray(cfg.coverageReporters)).toBe(true);
      cfg.coverageReporters.forEach((v) => expect(typeof v).toBe('string'));
    }
    if ('coverageThreshold' in cfg) {
      expect(isPlainObject(cfg.coverageThreshold)).toBe(true);
      const checkThresholdObj = (o) => {
        for (const v of Object.values(o)) {
          if (isPlainObject(v)) checkThresholdObj(v);
          else if (typeof v === 'number') {
            expect(v).toBeGreaterThanOrEqual(0);
            expect(v).toBeLessThanOrEqual(100);
          }
        }
      };
      checkThresholdObj(cfg.coverageThreshold);
    }
  });

  test('ignore patterns (if present) are arrays of strings', () => {
    ['testPathIgnorePatterns', 'modulePathIgnorePatterns'].forEach((k) => {
      if (k in cfg) {
        expect(Array.isArray(cfg[k])).toBe(true);
        cfg[k].forEach((v) => expect(typeof v).toBe('string'));
      }
    });
  });

  test('watchPlugins (if present) is an array of strings', () => {
    if ('watchPlugins' in cfg) {
      expect(Array.isArray(cfg.watchPlugins)).toBe(true);
      cfg.watchPlugins.forEach((v) => expect(typeof v).toBe('string'));
    }
  });

  test('rootDir (if present) is a string and resolves', () => {
    if ('rootDir' in cfg) {
      expect(typeof cfg.rootDir).toBe('string');
      const resolved = path.resolve(cfg.rootDir);
      expect(resolved.length).toBeGreaterThan(0);
    }
  });

  test('testTimeout (if present) is a positive integer', () => {
    if ('testTimeout' in cfg) {
      expect(Number.isInteger(cfg.testTimeout)).toBe(true);
      expect(cfg.testTimeout).toBeGreaterThan(0);
    }
  });
});

// If missing, provide explicit skip notice
(!hasConfig ? describe : describe.skip)('jest.config.js missing', () => {
  test('skipped because jest.config.js not found at project root', () => {
    expect(hasConfig).toBe(false);
  });
});