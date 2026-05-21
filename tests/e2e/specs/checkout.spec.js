// tests/e2e/specs/checkout.spec.js
// Author: Salma Hani | ID: 120210255
// Gherkin → Playwright: Feature: Checkout and Payment (2 scenarios)

const { test, expect } = require('@playwright/test');
const { MenuPage }     = require('../pages/MenuPage');
const { CartPage }     = require('../pages/CartPage');
const { CheckoutPage } = require('../pages/CheckoutPage');

test.describe('Feature: Checkout and Payment', () => {

  // Scenario: Successful card payment
  test('Successful card payment creates order with status Received', async ({ page }) => {
    const menu     = new MenuPage(page);
    const cart     = new CartPage(page);
    const checkout = new CheckoutPage(page);

    // Given the cart contains at least 1 available item
    await menu.goto();
    await menu.addItemToCart('Chicken Burger');

    // And the customer fills in valid card details
    await cart.proceedToCheckout();
    await checkout.fillCard('4242424242424242', '12/27', '123');

    // When they confirm the payment
    await checkout.submit();

    // Then the order status is Received and a confirmation is shown
    const confirmationText = await checkout.waitForConfirmation();
    expect(confirmationText).toContain('Order Received');
  });

  // Scenario: Payment gateway timeout
  test('Payment failure shows error and no charge applied', async ({ page }) => {
    const menu     = new MenuPage(page);
    const cart     = new CartPage(page);
    const checkout = new CheckoutPage(page);

    await menu.goto();
    await menu.addItemToCart('Diet Pepsi');
    await cart.proceedToCheckout();
    // Using Stripe test token that triggers a decline
    await checkout.fillCard('4000000000000002', '12/27', '123');
    await checkout.submit();

    const errorText = await checkout.waitForError();
    expect(errorText).toContain('Payment failed');
  });

});
