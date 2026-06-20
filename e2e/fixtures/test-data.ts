// Shelved — shared test data constants for @playwright/test specs.
// These mirror the mock state injected by e2e/servers/*_server.py --mock.

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

export const MOCK_SKETCH = {
  name: 'mysketch',
  path: '/tmp/e2e-test/sketches/MySketch',
  checksum: 'abc123def456',
  timestamp: '2026-06-19T00:00:00',
  hardware_id: 'HW-TEST-001',
};

export const MOCK_MEDICINES = [
  { name: 'Aspirin', hour: 8, minute: 0 },
  { name: 'VitaminD', hour: 12, minute: 30 },
  { name: 'Ibuprofen', hour: 18, minute: 0 },
];

export function daemonStatusUrl(baseURL: string) {
  return `${baseURL}/daemon/status`;
}

export function boardDetailUrl(baseURL: string, port: string) {
  return `${baseURL}/board/${encodeURIComponent(port)}`;
}
