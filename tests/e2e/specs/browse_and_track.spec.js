// tests/e2e/specs/browse_menu.spec.js
// Author: Salma Hani | ID: 120210255

const { test, expect } = require('@playwright/test');
const { MenuPage } = require('../pages/MenuPage');

test.describe('Feature: Browse Menu', () => {

  // Scenario: Customer views the full menu
  test('Customer sees all available categories and items', async ({ page }) => {
    const menu = new MenuPage(page);
    await menu.goto();

    const items = await page.locator('.menu-item').count();
    expect(items).toBeGreaterThan(0);

    const categories = await page.locator('.menu-category').count();
    expect(categories).toBeGreaterThan(0);
  });

  // Scenario: Item is out of stock
  test('Out of stock item shows badge and disabled button', async ({ page }) => {
    const menu = new MenuPage(page);
    await menu.goto();

    const isDisabled = await menu.isItemDisabled('Grilled Salmon');
    expect(isDisabled).toBe(true);

    const badge = page.locator('.menu-item', { hasText: 'Grilled Salmon' }).locator('.out-of-stock-badge');
    await expect(badge).toBeVisible();
  });

});


// tests/e2e/specs/track_order.spec.js
// Gherkin → Playwright: Feature: Track Order Status

// NOTE: This spec assumes an order has been placed in a prior fixture.
// In a real CI environment, a seeded order ID would be injected.
const { TrackingPage } = require('../pages/TrackingPage');

test.describe('Feature: Track Order Status', () => {

  test('Customer sees correct status steps for their order', async ({ page }) => {
    const tracking = new TrackingPage(page);
    await tracking.gotoOrder('ORD-TEST01');

    const steps = await tracking.getAllStepNames();
    expect(steps.some(s => s.includes('Received'))).toBe(true);
    expect(steps.some(s => s.includes('Preparing'))).toBe(true);
    expect(steps.some(s => s.includes('Ready'))).toBe(true);
  });

});
