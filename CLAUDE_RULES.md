# Claude Implementation Rules

> **Living document of patterns and rules discovered during implementation**
>
> When Claude discovers or creates a pattern during implementation, add it here.
> All future Claude instances MUST follow these rules.

---

## How to Use This Document

1. **Before implementing**: Check if a relevant pattern exists here
2. **During implementation**: Follow patterns exactly as documented
3. **After implementation**: If you created a new pattern, ADD IT HERE
4. **During code review**: Verify patterns were followed

---

## Mandatory Rules

### Rule 1: Component Structure

When creating React components, follow this structure:

```typescript
// WRONG - inline styles, no typing
function Button({ onClick }) {
  return <button style={{color: 'blue'}} onClick={onClick}>Click</button>
}

// RIGHT - typed props, tailwind/design system
interface ButtonProps {
  onClick: () => void;
  variant?: 'primary' | 'secondary';
  children: React.ReactNode;
}

export function Button({ onClick, variant = 'primary', children }: ButtonProps) {
  return (
    <button
      className={cn('btn', variant === 'primary' ? 'btn-primary' : 'btn-secondary')}
      onClick={onClick}
    >
      {children}
    </button>
  );
}
```

**Why:** Type safety, consistent styling, maintainable components.

---

### Rule 2: Error Handling

All async operations MUST have proper error handling:

```typescript
// WRONG
const data = await fetchData();

// RIGHT
try {
  const data = await fetchData();
} catch (error) {
  if (error instanceof ApiError) {
    toast.error(error.message);
  } else {
    console.error('Unexpected error:', error);
    toast.error('An unexpected error occurred');
  }
}
```

---

### Rule 3: Secret Handling

Never log, commit, or expose secrets:

```typescript
// WRONG
console.log('API key:', apiKey);
const config = { apiKey: 'sk-xxx' };

// RIGHT
console.log('Using API key:', apiKey.slice(0, 8) + '...');
const config = { apiKey: process.env.NEXT_PUBLIC_API_KEY };
```

---

### Rule 4: State Management

Use appropriate state for the scope:

```typescript
// Component state - useState
const [isOpen, setIsOpen] = useState(false);

// Form state - react-hook-form
const { register, handleSubmit } = useForm<FormData>();

// Server state - tanstack-query
const { data, isLoading } = useQuery({ queryKey: ['users'], queryFn: fetchUsers });

// Global state - zustand/context (only when truly needed)
const user = useAuthStore(state => state.user);
```

---

### Rule 5: API Calls

Always use typed API hooks with proper error handling:

```typescript
// WRONG
fetch('/api/users').then(r => r.json());

// RIGHT
const { data, isLoading, error } = useQuery({
  queryKey: ['users'],
  queryFn: async () => {
    const response = await fetch('/api/users');
    if (!response.ok) {
      throw new ApiError(response.status, await response.text());
    }
    return response.json() as Promise<User[]>;
  }
});
```

---

### Rule 6: Configuration

All configurable values MUST come from environment or config files:

```typescript
// WRONG
const API_URL = 'https://api.example.com';

// RIGHT
const API_URL = process.env.NEXT_PUBLIC_API_URL;
if (!API_URL) throw new Error('NEXT_PUBLIC_API_URL is required');
```

---

### Rule 7: Testing

Every component MUST have tests covering:
- Render without crashing
- User interactions
- Error states
- Loading states

```typescript
describe('Button', () => {
  it('renders without crashing', () => {
    render(<Button onClick={() => {}}>Click</Button>);
    expect(screen.getByRole('button')).toBeInTheDocument();
  });

  it('calls onClick when clicked', async () => {
    const onClick = vi.fn();
    render(<Button onClick={onClick}>Click</Button>);
    await userEvent.click(screen.getByRole('button'));
    expect(onClick).toHaveBeenCalledTimes(1);
  });
});
```

---

### Rule 8: Accessibility

All interactive elements MUST be accessible:

```typescript
// WRONG
<div onClick={handleClick}>Click me</div>

// RIGHT
<button onClick={handleClick}>Click me</button>

// If div is necessary
<div
  role="button"
  tabIndex={0}
  onClick={handleClick}
  onKeyDown={(e) => e.key === 'Enter' && handleClick()}
  aria-label="Click me"
>
  Click me
</div>
```

---

### Rule 9: Submodule Documentation

When making changes to any submodule, ALWAYS update:

1. **STATE_OF_CODE.md** - Current state, recent changes, known issues
2. **CHANGELOG.md** - Version history with semantic versioning

**Format for STATE_OF_CODE.md**:
```markdown
# State of Code

Last Updated: YYYY-MM-DD

## Current State
- Brief description of current functionality
- Build status, test coverage

## Recent Changes
- List of recent modifications

## Known Issues
- Any outstanding bugs or technical debt
```

**Format for CHANGELOG.md**:
```markdown
## [X.Y.Z] - YYYY-MM-DD

### Added
- New features

### Changed
- Modifications to existing functionality

### Fixed
- Bug fixes

### Removed
- Removed features
```

**Submodules requiring documentation**:
- `submodules/platform`
- `submodules/Armor-Dash`
- `submodules/jira-mcp`

**Why:** Submodules are independent repositories. Maintaining their documentation ensures:
- Other developers can understand current state
- Changes are tracked independently
- Version history is preserved

---

## Pattern Registry

Add patterns discovered during implementation here.

| Pattern Name | File | Added By | Date |
|--------------|------|----------|------|
| Error Boundary | `.bmad/patterns/error-boundary.md` | Initial | 2026-01-03 |
| Form Validation | `.bmad/patterns/form-validation.md` | Initial | 2026-01-03 |

---

## Anti-Pattern Registry

Patterns that MUST be avoided.

| Anti-Pattern | Why It's Wrong | Discovered In | Date |
|--------------|----------------|---------------|------|
| `any` type | Defeats TypeScript | - | 2026-01-03 |
| Inline styles | Hard to maintain | - | 2026-01-03 |
| `console.log` in prod | Leaks info, clutter | - | 2026-01-03 |
| Untyped props | Runtime errors | - | 2026-01-03 |
| Missing error boundaries | Crashes whole app | - | 2026-01-03 |
| Prop drilling > 2 levels | Use context/store | - | 2026-01-03 |

---

## Adding New Rules

When you discover a pattern during implementation:

1. **Create pattern file** in `.bmad/patterns/` (if complex):
   ```
   .bmad/patterns/{category}-{name}.md
   ```

2. **Add to this document**:
   - Add mandatory rule if it applies broadly
   - Add to Pattern Registry table
   - Add anti-pattern if discovered

3. **Update CLAUDE.md** if needed

4. **Notify team** in PR comment

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.1 | 2026-01-03 | Added Rule 9: Submodule Documentation requirements |
| 1.0 | 2026-01-03 | Initial rules document for UI-Uplift |

---

**Maintained by:** All Claude instances during implementation
**Review frequency:** Every sprint retrospective
