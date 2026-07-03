// Shared test data constants for @playwright/test specs.
// These mirror the mock state injected by e2e/servers/*_server.py --mock.

/** Mock board ports mirroring e2e/servers/*_server.py --mock state. Two boards: Uno (/dev/ttyTEST0) and Mega (/dev/ttyTEST1). */
export const MOCK_PORTS = {
  uno: {
    port: '/dev/ttyTEST0',
    board: 'TestBoard Uno',
    fqbn: 'arduino:avr:uno',
    hardware_id: 'HW-TEST-001',
  },
  mega: {
    port: '/dev/ttyTEST1',
    board: 'TestBoard Mega',
    fqbn: 'arduino:avr:mega',
    hardware_id: 'HW-TEST-002',
  },
} as const;

/** Mock sketch metadata for compile/upload test scenarios. */
export const MOCK_SKETCH = {
  name: 'mysketch',
  path: '/tmp/e2e-test/sketches/MySketch',
  checksum: 'abc123def456',
  timestamp: '2026-06-19T00:00:00',
  hardware_id: 'HW-TEST-001',
};

/** Mock medicine list with dosage schedules for medicine CRUD test scenarios. */
export const MOCK_MEDICINES = [
  { name: 'Aspirin', hour: 8, minute: 0 },
  { name: 'VitaminD', hour: 12, minute: 30 },
  { name: 'Ibuprofen', hour: 18, minute: 0 },
];

/** Build the daemon status URL for a given base URL.
 * @param baseURL - Server base URL (e.g. http://localhost:8765)
 * @returns Full daemon status endpoint URL
 */
export function daemonStatusUrl(baseURL: string) {
  return `${baseURL}/daemon/status`;
}

/** Build the board detail page URL for a given port.
 * @param baseURL - Server base URL
 * @param port - Board port path (e.g. /dev/ttyTEST0)
 * @returns Full board detail URL with encoded port
 */
export function boardDetailUrl(baseURL: string, port: string) {
  return `${baseURL}/board/${encodeURIComponent(port)}`;
}
