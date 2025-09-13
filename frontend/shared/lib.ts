/**
 * Facade re-exports for shared library utilities and API client.
 *
 * Why this file exists:
 * - Some CI environments can fail to resolve a directory import
 *   like "@/shared/lib" → "./shared/lib/index.ts" under certain
 *   module resolution strategies. Exporting from a concrete file
 *   guarantees consistent resolution for imports of "@/shared/lib".
 *
 * Usage:
 * import { cn, httpClient } from '@/shared/lib'
 */
export { cn } from './lib/utils'
export { httpClient } from './lib/http-client'
