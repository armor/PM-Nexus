# Task 04: Add ESLint Rule for Absolute Paths

**Task ID:** NEXUS-NAV-003-T04
**Story:** NEXUS-NAV-003
**Estimate:** 30 minutes
**Type:** Implementation

---

## Objective

Add an ESLint rule that prevents relative paths in navigation code, ensuring the standard is enforced automatically in CI.

---

## AI Implementation Prompt

```
You are implementing NEXUS-NAV-003-T04 for the Nexus UI Uplift project.

CONTEXT:
- ESLint config: .eslintrc.js or eslint.config.js
- Goal: Prevent relative paths in Link/NavLink/navigate
- CI should fail on violation

INSTRUCTIONS:
1. Create custom ESLint rule or use existing plugin:

Option A: Use eslint-plugin-no-relative-paths (if available)
```javascript
// .eslintrc.js
module.exports = {
  plugins: ['no-relative-paths'],
  rules: {
    'no-relative-paths/no-relative-import': 'error',
  },
};
```

Option B: Create custom rule
```javascript
// eslint-rules/no-relative-navigation.js
module.exports = {
  meta: {
    type: 'problem',
    docs: {
      description: 'Disallow relative paths in navigation',
    },
    schema: [],
  },
  create(context) {
    const NAVIGATION_COMPONENTS = ['Link', 'NavLink'];
    const NAVIGATION_FUNCTIONS = ['navigate', 'useNavigate'];

    return {
      JSXAttribute(node) {
        if (
          node.name.name === 'to' &&
          NAVIGATION_COMPONENTS.includes(node.parent.name.name)
        ) {
          const value = node.value;
          if (value && value.type === 'Literal') {
            if (value.value.startsWith('./') || value.value.startsWith('../')) {
              context.report({
                node,
                message: 'Use absolute paths for navigation. Found: "{{ path }}"',
                data: { path: value.value },
              });
            }
          }
        }
      },
      CallExpression(node) {
        if (
          node.callee.name === 'navigate' &&
          node.arguments[0]?.type === 'Literal'
        ) {
          const path = node.arguments[0].value;
          if (path.startsWith('./') || path.startsWith('../')) {
            context.report({
              node,
              message: 'Use absolute paths for navigation. Found: "{{ path }}"',
              data: { path },
            });
          }
        }
      },
    };
  },
};
```

2. Register the rule:

```javascript
// .eslintrc.js
module.exports = {
  plugins: ['local-rules'],
  rules: {
    'local-rules/no-relative-navigation': 'error',
  },
};
```

3. Add to CI config (if separate):

```yaml
# .github/workflows/ci.yml
- name: Lint
  run: npm run lint
  # ESLint will fail on relative paths
```

4. Test the rule:

```bash
# Should fail
echo '<Link to="./details">Test</Link>' | npx eslint --stdin

# Should pass
echo '<Link to="/assets/123/details">Test</Link>' | npx eslint --stdin
```

OUTPUT:
- ESLint rule created/configured
- Rule documentation added
- CI integration verified
- All existing code passes (after task-03 fixes)
```

---

## Checklist

- [ ] ESLint rule created
- [ ] Rule registered in config
- [ ] Rule documentation added
- [ ] Existing code passes
- [ ] CI integration verified
- [ ] Test cases for rule added

---

## Rule Configuration

```javascript
// Add to .eslintrc.js
{
  rules: {
    // Custom navigation rules
    'local-rules/no-relative-navigation': ['error', {
      // Allow relative paths in specific files (e.g., tests)
      ignorePatterns: ['**/*.test.tsx', '**/*.spec.tsx'],
    }],
  }
}
```
