/**
 * API functions for MyLib Dashboard.
 * Uses React Query for data fetching and caching.
 */

/**
 * Fetch JSON from an API endpoint.
 * Throws on non-ok responses with error message from server.
 */
async function fetchJson(url) {
  const response = await fetch(url)
  if (!response.ok) {
    const data = await response.json().catch(() => ({}))
    throw new Error(data.error || `Request failed: ${response.status}`)
  }
  return response.json()
}

/**
 * Create API fetcher functions bound to a base URL.
 */
export default function createApi(baseUrl) {
  return {
    fetchProfile: () => fetchJson(`${baseUrl}/profile/`),
    fetchLoans: () => fetchJson(`${baseUrl}/loans/`),
    fetchHolds: () => fetchJson(`${baseUrl}/holds/`),
    fetchFines: () => fetchJson(`${baseUrl}/fines/`),
    fetchBlocks: () => fetchJson(`${baseUrl}/account-blocks/`),
  }
}
