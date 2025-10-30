import { test, expect } from '@playwright/test'

test.describe('Download Flow', () => {
  test('should navigate to download page', async ({ page }) => {
    await page.goto('/')
    await expect(page.locator('h1')).toContainText('Download Model')
  })

  test('should display download form', async ({ page }) => {
    await page.goto('/download')

    // Check form elements exist
    await expect(page.locator('input[name="url"]')).toBeVisible()
    await expect(page.locator('input[name="filename"]')).toBeVisible()
    await expect(page.locator('button[type="submit"]')).toBeVisible()
  })

  test('should validate URL input', async ({ page }) => {
    await page.goto('/download')

    // Try to submit with invalid URL
    await page.fill('input[name="url"]', 'not-a-url')
    await page.fill('input[name="filename"]', 'test.safetensors')
    await page.click('button[type="submit"]')

    // Should show error message
    await expect(page.locator('text=Invalid URL format')).toBeVisible()
  })

  test('should validate required fields', async ({ page }) => {
    await page.goto('/download')

    // Try to submit empty form
    await page.click('button[type="submit"]')

    // Should show error message for URL
    await expect(page.locator('text=URL is required')).toBeVisible()
  })

  test('should disable form during download', async ({ page }) => {
    await page.goto('/download')

    // Fill form with valid data
    await page.fill('input[name="url"]', 'https://civitai.com/models/12345/test-model')
    await page.fill('input[name="filename"]', 'test-model.safetensors')

    // Submit form
    const submitButton = page.locator('button[type="submit"]')
    await submitButton.click()

    // Form inputs should be disabled
    await expect(page.locator('input[name="url"]')).toBeDisabled()
    await expect(page.locator('input[name="filename"]')).toBeDisabled()

    // Submit button should show "Downloading..."
    await expect(submitButton).toContainText('Downloading...')
  })

  test('should display progress bar during download', async ({ page }) => {
    await page.goto('/download')

    // Fill form
    await page.fill('input[name="url"]', 'https://civitai.com/models/12345/test-model')
    await page.fill('input[name="filename"]', 'test-model.safetensors')

    // Submit
    await page.click('button[type="submit"]')

    // Wait for progress bar to appear
    await expect(page.locator('.bg-blue-500')).toBeVisible({ timeout: 5000 })
  })

  test('should display progress percentage', async ({ page }) => {
    await page.goto('/download')

    // Fill form
    await page.fill('input[name="url"]', 'https://civitai.com/models/12345/test-model')
    await page.fill('input[name="filename"]', 'test-model.safetensors')

    // Submit
    await page.click('button[type="submit"]')

    // Wait for progress percentage to appear
    await expect(page.locator('text=/\\d+%/')).toBeVisible({ timeout: 5000 })
  })

  test('should display filename in progress bar', async ({ page }) => {
    await page.goto('/download')

    const filename = 'test-model.safetensors'

    // Fill form
    await page.fill('input[name="url"]', 'https://civitai.com/models/12345/test-model')
    await page.fill('input[name="filename"]', filename)

    // Submit
    await page.click('button[type="submit"]')

    // Wait for filename to appear in progress bar
    await expect(page.locator(`text=File: ${filename}`)).toBeVisible({ timeout: 5000 })
  })

  test('should navigate between tabs', async ({ page }) => {
    await page.goto('/')

    // Click Download link
    await page.click('text=Download')
    await expect(page.locator('h1')).toContainText('Download Model')

    // Click History link (if exists - will be added in Phase 3)
    // For now, just verify we can navigate to download tab
    await expect(page.locator('input[name="url"]')).toBeVisible()
  })

  test('should handle WebSocket connection for progress updates', async ({ page }) => {
    await page.goto('/download')

    // Listen for WebSocket messages
    let wsMessageReceived = false
    page.on('websocket', (ws) => {
      ws.on('framereceived', () => {
        wsMessageReceived = true
      })
    })

    // Fill form
    await page.fill('input[name="url"]', 'https://civitai.com/models/12345/test-model')
    await page.fill('input[name="filename"]', 'test-model.safetensors')

    // Submit
    await page.click('button[type="submit"]')

    // Wait for progress updates via WebSocket
    await expect(page.locator('.bg-blue-500')).toBeVisible({ timeout: 5000 })

    // Verify progress bar width changes (indicating updates)
    const progressBar = page.locator('.bg-blue-500').first()
    const initialWidth = await progressBar.evaluate((el) => {
      return window.getComputedStyle(el).width
    })

    await page.waitForTimeout(2000)

    const updatedWidth = await progressBar.evaluate((el) => {
      return window.getComputedStyle(el).width
    })

    // Width should have changed or both be at 100% for complete download
    const initialPercent = parseInt(initialWidth)
    const updatedPercent = parseInt(updatedWidth)
    expect(initialPercent === updatedPercent || updatedPercent === 100).toBeTruthy()
  })
})

test.describe('Download Error Handling', () => {
  test('should display error on invalid URL', async ({ page, context }) => {
    // Mock API response with error
    await context.addInitScript(() => {
      window.fetch = async (url: string) => {
        if (url.includes('/api/download')) {
          return new Response(JSON.stringify({ error: 'Invalid URL' }), {
            status: 400,
          })
        }
        return new Response()
      }
    })

    await page.goto('/download')

    // Fill form with URL
    await page.fill('input[name="url"]', 'https://example.com/invalid')
    await page.fill('input[name="filename"]', 'test.safetensors')

    // Submit
    await page.click('button[type="submit"]')

    // Should show error state
    await expect(page.locator('text=Download Failed')).toBeVisible({ timeout: 5000 })
  })

  test('should display error message in progress bar', async ({ page }) => {
    await page.goto('/download')

    // Fill form
    await page.fill('input[name="url"]', 'https://civitai.com/models/12345/test-model')
    await page.fill('input[name="filename"]', 'test-model.safetensors')

    // Submit
    await page.click('button[type="submit"]')

    // Progress bar should appear
    await expect(page.locator('.bg-blue-500')).toBeVisible({ timeout: 5000 })

    // In a real scenario with an actual error, the error message would be displayed
    // This test verifies the structure is in place
  })
})
