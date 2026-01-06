# Task 04: Fix Modal Close Destinations

**Task ID:** NEXUS-NAV-005-T04
**Story:** NEXUS-NAV-005
**Estimate:** 15 minutes
**Type:** Implementation

---

## Objective

Fix modal flows that close to unexpected destinations, ensuring modals return users to their expected context.

---

## AI Implementation Prompt

```
You are implementing NEXUS-NAV-005-T04 for the Nexus UI Uplift project.

CONTEXT:
- Console: apps/threat-management/
- Issue: Modals close to wrong pages (e.g., assign modal closes to dashboard)
- Goal: Modals return to their parent context

INSTRUCTIONS:
1. Identify modal navigation pattern:

```tsx
// Current problematic pattern
function AssignModal({ incidentId }) {
  const handleSuccess = () => {
    navigate('/dashboard'); // WRONG - loses context
    closeModal();
  };
}

// Fixed pattern
function AssignModal({ incidentId }) {
  const handleSuccess = () => {
    closeModal();
    // Stay on current page - modal was just an overlay
  };

  const handleCancel = () => {
    closeModal();
    // Stay on current page
  };
}
```

2. Create modal navigation hook:

```tsx
// libs/shared/react-ui/src/lib/hooks/useModalNavigation.ts

interface UseModalNavigationOptions {
  /** Where to go after successful action (default: stay on page) */
  onSuccessPath?: string;
  /** Where to go on cancel (default: stay on page) */
  onCancelPath?: string;
  /** Callback after modal closes */
  onClose?: () => void;
}

export function useModalNavigation(options: UseModalNavigationOptions = {}) {
  const navigate = useNavigate();
  const location = useLocation();

  const handleSuccess = useCallback(() => {
    if (options.onSuccessPath) {
      navigate(options.onSuccessPath);
    }
    options.onClose?.();
  }, [navigate, options]);

  const handleCancel = useCallback(() => {
    if (options.onCancelPath) {
      navigate(options.onCancelPath);
    }
    options.onClose?.();
  }, [navigate, options]);

  // For route-based modals, return to parent
  const returnToParent = useCallback(() => {
    const parentPath = location.pathname.split('/').slice(0, -1).join('/');
    navigate(parentPath || '/');
  }, [navigate, location]);

  return { handleSuccess, handleCancel, returnToParent };
}
```

3. Fix specific modals in threat-management:

```tsx
// apps/threat-management/src/modals/AssignIncidentModal.tsx
function AssignIncidentModal({ incidentId, onClose }: AssignIncidentModalProps) {
  const { handleSuccess, handleCancel } = useModalNavigation({
    onClose,
    // After assign success, stay on incident detail page
  });

  return (
    <Modal onClose={handleCancel}>
      <form onSubmit={async (e) => {
        await assignIncident(incidentId, data);
        handleSuccess();
        toast.success('Incident assigned');
      }}>
        {/* ... */}
        <Button type="submit">Assign</Button>
        <Button type="button" onClick={handleCancel}>Cancel</Button>
      </form>
    </Modal>
  );
}

// apps/threat-management/src/modals/CreateResponseModal.tsx
function CreateResponseModal({ incidentId, onClose }: CreateResponseModalProps) {
  const navigate = useNavigate();

  const handleSuccess = (responseId: string) => {
    onClose();
    // Navigate to the new response detail
    navigate(`/threats/responses/${responseId}`);
  };

  return (
    <Modal onClose={onClose}>
      {/* ... */}
    </Modal>
  );
}
```

4. Audit and fix all modals:
   - AssignIncidentModal
   - CreateResponseModal
   - AddEvidenceModal
   - EscalateAlertModal
   - CloseIncidentModal

OUTPUT:
- useModalNavigation hook created
- All modals return to correct destination
- Route-based modals use returnToParent
```

---

## Checklist

- [ ] useModalNavigation hook created
- [ ] AssignIncidentModal fixed
- [ ] CreateResponseModal fixed
- [ ] AddEvidenceModal fixed
- [ ] EscalateAlertModal fixed
- [ ] CloseIncidentModal fixed
- [ ] All modals tested

---

## Modal Destinations

| Modal | Open From | On Success | On Cancel |
|-------|-----------|------------|-----------|
| AssignIncident | /threats/incidents/:id | Stay | Stay |
| CreateResponse | /threats/incidents/:id | Go to /threats/responses/:newId | Stay |
| AddEvidence | /threats/incidents/:id | Stay | Stay |
| EscalateAlert | /threats/alerts/:id | Stay | Stay |
| CloseIncident | /threats/incidents/:id | Go to /threats/incidents | Stay |
