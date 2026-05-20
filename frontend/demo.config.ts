import { defineConfig, devices } from '@playwright/test'

export default defineConfig({
  testDir: '.',
  testMatch: 'demo-record.spec.ts',
  fullyParallel: false,
  workers: 1,
  reporter: 'line',
  use: {
    baseURL: 'https://d20n2etaaqstlw.cloudfront.net',
    video: 'on',
    viewport: { width: 1280, height: 720 },
    slowMo: 600,
  },
  outputDir: 'docs/demo/',
  projects: [
    {
      name: 'demo',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
})
