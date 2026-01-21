/**
 * Custom hooks for MyLib Dashboard.
 */
import { useMemo } from 'react'

/**
 * Compute alert counts from loans data.
 * Returns counts for recalled, overdue, and due soon items.
 */
export function useLoanAlerts(loansData) {
  return useMemo(() => {
    if (!loansData) {
      return { recalledCount: 0, overdueCount: 0, dueSoonCount: 0, hasAlerts: false }
    }

    const { recalledCount = 0, overdueCount = 0, dueSoonCount = 0 } = loansData
    const hasAlerts = recalledCount > 0 || overdueCount > 0 || dueSoonCount > 0

    return { recalledCount, overdueCount, dueSoonCount, hasAlerts }
  }, [loansData])
}

/**
 * Compute tab counts from all data sources.
 * Returns counts for each tab badge.
 */
export function useTabCounts(loansData, holdsData) {
  return useMemo(() => {
    const checkedOutCount = loansData?.totalLoans || 0
    const availableForPickupCount = holdsData?.totalHolds || 0

    return {
      checkedOut: checkedOutCount,
      availableForPickup: availableForPickupCount,
    }
  }, [loansData, holdsData])
}

/**
 * Format currency for display.
 */
export function formatCurrency(amount) {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
  }).format(amount)
}

/**
 * Format date for display (e.g., "Jan 15, 2025").
 */
export function formatDate(dateString) {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  })
}
