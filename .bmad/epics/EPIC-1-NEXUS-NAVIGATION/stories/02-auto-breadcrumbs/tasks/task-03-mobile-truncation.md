# Task 03: Add Mobile Truncation Behavior

**Task ID:** NEXUS-NAV-002-T03
**Story:** NEXUS-NAV-002
**Estimate:** 30 minutes
**Type:** Implementation

---

## Objective

Implement responsive truncation for breadcrumbs on mobile viewports, showing first and last segments with an ellipsis menu for intermediate items.

---

## AI Implementation Prompt

```
You are implementing NEXUS-NAV-002-T03 for the Nexus UI Uplift project.

CONTEXT:
- Component: libs/shared/react-ui/src/lib/components/AutoBreadcrumbs/
- Goal: Graceful truncation on mobile (< 768px)
- Pattern: Show [Home] ... [Current Page] with dropdown for middle items

INSTRUCTIONS:
1. Implement responsive truncation logic:

```typescript
interface TruncationConfig {
  /** Viewport width to trigger truncation */
  breakpoint?: number; // default: 768
  /** Always show first N segments */
  keepFirst?: number; // default: 1
  /** Always show last N segments */
  keepLast?: number; // default: 1
}
```

2. Create ellipsis dropdown for hidden segments:

```tsx
function BreadcrumbEllipsis({ hiddenSegments }: { hiddenSegments: BreadcrumbSegment[] }) {
  const [open, setOpen] = useState(false);

  return (
    <div className="relative">
      <button
        onClick={() => setOpen(!open)}
        aria-label={`Show ${hiddenSegments.length} more navigation levels`}
        aria-expanded={open}
      >
        ...
      </button>
      {open && (
        <ul role="menu" className="absolute bg-surface shadow-lg rounded">
          {hiddenSegments.map(segment => (
            <li key={segment.path}>
              <Link to={segment.path} role="menuitem">
                {segment.label}
              </Link>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
```

3. Use CSS container queries or useMediaQuery hook:

```typescript
function useIsMobile(breakpoint = 768) {
  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    const query = window.matchMedia(`(max-width: ${breakpoint}px)`);
    setIsMobile(query.matches);

    const handler = (e: MediaQueryListEvent) => setIsMobile(e.matches);
    query.addEventListener('change', handler);
    return () => query.removeEventListener('change', handler);
  }, [breakpoint]);

  return isMobile;
}
```

4. Accessibility requirements:
   - Ellipsis button must be keyboard accessible
   - Dropdown must trap focus
   - Escape closes dropdown
   - aria-expanded state

CONSTRAINTS:
- Touch-friendly tap targets (min 44px)
- Smooth transition animations
- Works with variable segment counts

OUTPUT:
- Responsive truncation implemented
- Ellipsis dropdown component
- Mobile-specific styling
```

---

## Checklist

- [ ] Truncation logic implemented
- [ ] Ellipsis dropdown working
- [ ] Keyboard navigation working
- [ ] Touch targets verified (44px min)
- [ ] Animation/transitions smooth
- [ ] Tested on iOS Safari and Chrome Android

---

## Visual Specification

**Desktop (>768px):**
```
Home > Infrastructure > Assets > asset-123 > Details
```

**Mobile (<768px):**
```
Home > ... > Details
        ↓
    [Infrastructure]
    [Assets]
    [asset-123]
```
